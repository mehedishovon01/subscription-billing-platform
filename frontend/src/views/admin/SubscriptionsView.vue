<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">Subscriptions Management</h2>
        <button class="btn btn-primary btn-sm" @click="showModal = true">+ Assign Packages</button>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <form class="subscription-filters" @submit.prevent="applyFilters">
        <div class="form-group">
          <label for="subscription-search">Search customer or package</label>
          <input id="subscription-search" v-model="filters.search" type="search" placeholder="Name, email, or package" />
        </div>
        <div class="form-group">
          <label for="subscription-user-filter">Customer</label>
          <select id="subscription-user-filter" v-model="filters.user">
            <option value="">All customers</option>
            <option v-for="user in users" :key="user.id" :value="String(user.id)">{{ user.full_name || user.email }} ({{ user.email }})</option>
          </select>
        </div>
        <div class="form-group">
          <label for="subscription-package-filter">Package</label>
          <select id="subscription-package-filter" v-model="filters.package">
            <option value="">All packages</option>
            <option v-for="pkg in filterPackages" :key="pkg.id" :value="String(pkg.id)">{{ pkg.name }} ({{ pkg.type }})</option>
          </select>
        </div>
        <div class="form-group">
          <label for="subscription-status-filter">Status</label>
          <select id="subscription-status-filter" v-model="filters.status">
            <option value="">All statuses</option>
            <option value="active">Active</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div class="form-group">
          <label for="subscription-ordering">Sort by</label>
          <select id="subscription-ordering" v-model="filters.ordering">
            <option value="">Default order</option>
            <option value="-assigned_at">Newest assigned</option>
            <option value="assigned_at">Oldest assigned</option>
          </select>
        </div>
        <div class="filter-actions">
          <button class="btn btn-primary btn-sm" type="submit">Apply filters</button>
          <button class="btn btn-secondary btn-sm" type="button" @click="clearFilters">Clear</button>
        </div>
      </form>



      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Customer</th>
              <th>Package</th>
              <th>Type</th>
              <th>Status</th>
              <th>Assigned Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading && subscriptions.length === 0">
              <td colspan="7" style="text-align: center; padding: 24px;">Loading subscriptions...</td>
            </tr>
            <tr v-else-if="subscriptions.length === 0">
              <td colspan="7" style="text-align: center; padding: 24px;">No subscriptions found.</td>
            </tr>
            <tr v-for="sub in subscriptions" :key="sub.id">
              <td>#{{ sub.id }}</td>
              <td>
                <strong>{{ sub.user_full_name || '—' }}</strong>
                <div style="font-size: 12px; color: #64748b;">{{ sub.user_email }}</div>
              </td>
              <td>
                {{ sub.package ? sub.package.name : '' }}
                (${{ sub.package ? sub.package.price : '' }})
              </td>
              <td>
                <span class="badge badge-info">{{ sub.package ? sub.package.type : '' }}</span>
              </td>
              <td>
                <span :class="sub.status === 'active' ? 'badge badge-success' : 'badge badge-danger'">
                  {{ sub.status }}
                </span>
              </td>
              <td>{{ formatDate(sub.assigned_at) }}</td>
              <td>
                <button
                  v-if="sub.status === 'active'"
                  class="btn btn-secondary btn-sm"
                  style="margin-right: 6px;"
                  @click="openEdit(sub)"
                >Edit</button>
                <button
                  v-if="sub.status === 'active'"
                  class="btn btn-danger btn-sm"
                  :disabled="cancellingId === sub.id"
                  @click="cancelSubscription(sub)"
                >
                  {{ cancellingId === sub.id ? 'Cancelling...' : 'Cancel' }}
                </button>
                <span v-else style="color: #94a3b8; font-size: 12px;">Cancelled</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <PaginationControls
        :count="pagination.count"
        :page="page"
        :page-size="pageSize"
        :has-previous="!!pagination.previous"
        :has-next="!!pagination.next"
        @change="changePage"
      />
    </div>

    <div v-if="editingSubscription" class="modal-overlay" @click.self="closeEdit">
      <div class="modal-content">
        <div class="card-header">
          <h3 class="card-title">Update Subscription #{{ editingSubscription.id }}</h3>
          <button class="btn btn-secondary btn-sm" @click="closeEdit">✕</button>
        </div>

        <div v-if="editError" class="alert alert-danger">{{ editError }}</div>
        <p class="edit-note">Changing the customer or package assigns the selected package and creates an invoice at its current price.</p>

        <form @submit.prevent="submitEdit">
          <div class="form-group">
            <label>Customer *</label>
            <select v-model.number="editForm.user" required>
              <option v-for="u in users" :key="u.id" :value="u.id">
                {{ u.full_name }} ({{ u.email }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Package *</label>
            <select v-model.number="editForm.package" required>
              <option
                v-for="pkg in editPackages"
                :key="pkg.id"
                :value="pkg.id"
                :disabled="!pkg.is_active"
              >
                {{ pkg.name }} ({{ pkg.type }}) — ${{ pkg.price }}{{ pkg.is_active ? '' : ' (inactive)' }}
              </option>
            </select>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px;">
            <button type="button" class="btn btn-secondary" @click="closeEdit">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="editSaving || !editChanged">
              {{ editSaving ? 'Saving...' : 'Save & Update Invoice' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="card-header">
          <h3 class="card-title">Assign Packages to Customer</h3>
          <button class="btn btn-secondary btn-sm" @click="closeModal">✕</button>
        </div>

        <div v-if="modalError" class="alert alert-danger">{{ modalError }}</div>

        <form @submit.prevent="submitAssign">
          <div class="form-group">
            <label>Customer *</label>
            <select v-model="form.user" required>
              <option :value="null" disabled>Select a customer</option>
              <option v-for="u in users" :key="u.id" :value="u.id">
                {{ u.full_name }} ({{ u.email }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Packages to Assign * (generates an immutable invoice)</label>
            <div class="packages-selection">
              <label v-for="pkg in packages" :key="pkg.id" class="pkg-checkbox-item">
                <input type="checkbox" :value="pkg.id" v-model="form.package_ids" />
                <span class="pkg-label-name">{{ pkg.name }}</span>
                <span class="badge badge-neutral">{{ pkg.type }}</span>
                <span class="pkg-price">${{ pkg.price }}</span>
              </label>
              <div v-if="packages.length === 0" style="color: #64748b; font-size: 13px;">
                No active packages available.
              </div>
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px;">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="submitting || form.package_ids.length === 0 || !form.user"
            >
              {{ submitting ? 'Assigning...' : 'Assign & Generate Invoice' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api, { fetchAllResults } from '../../api'
import PaginationControls from '../../components/PaginationControls.vue'
import { formatApiError } from '../../errors'

export default {
  components: { PaginationControls },
  name: 'SubscriptionsView',
  data() {
    return {
      subscriptions: [],
      filters: { search: '', user: '', package: '', status: '', ordering: '' },
      filterPackages: [],
      page: 1,
      pageSize: 10,
      pagination: { count: 0, next: null, previous: null },
      users: [],
      packages: [],
      loading: false,
      submitting: false,
      cancellingId: null,
      error: '',
      success: '',
      editingSubscription: null,
      editForm: { user: null, package: null },
      editSaving: false,
      editError: '',
      modalError: '',
      showModal: false,
      form: {
        user: null,
        package_ids: [],
      },
    }
  },
  computed: {
    editPackages() {
      const options = this.packages.slice()
      const current = this.editingSubscription && this.editingSubscription.package
      if (current && !options.some((pkg) => pkg.id === current.id)) {
        options.push(current)
      }
      return options
    },
    editChanged() {
      return !!this.editingSubscription && (
        Number(this.editForm.user) !== Number(this.editingSubscription.user) ||
        Number(this.editForm.package) !== Number(this.editingSubscription.package.id)
      )
    },
  },
  created() {
    this.fetchSubscriptions()
    this.fetchUsers()
    this.fetchPackages()
    this.fetchFilterPackages()
  },
  methods: {
    async fetchSubscriptions() {
      this.loading = true
      this.error = ''
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.filters.search.trim()) params.search = this.filters.search.trim()
        if (this.filters.user) params.user = this.filters.user
        if (this.filters.package) params.package = this.filters.package
        if (this.filters.status) params.status = this.filters.status
        if (this.filters.ordering) params.ordering = this.filters.ordering
        const res = await api.get('/subscriptions/', { params })
        this.subscriptions = res.data.results || res.data
        this.pagination = {
          count: res.data.count !== undefined ? res.data.count : this.subscriptions.length,
          next: res.data.next || null,
          previous: res.data.previous || null,
        }
      } catch (err) {
        this.error = formatApiError(err, 'Failed to load subscriptions.')
      } finally {
        this.loading = false
      }
    },
    async fetchUsers() {
      try {
        this.users = await fetchAllResults('/users/', { is_staff: false })
      } catch (err) {
        /* list stays empty; assign form will show no customers */
      }
    },
    async fetchPackages() {
      try {
        this.packages = await fetchAllResults('/packages/', { is_active: true })
      } catch (err) {
        /* assign form will show no packages */
      }
    },
    async fetchFilterPackages() {
      try {
        this.filterPackages = await fetchAllResults('/packages/')
      } catch (err) {
        /* package filter stays at All packages */
      }
    },
    async applyFilters() {
      this.page = 1
      await this.fetchSubscriptions()
    },
    async clearFilters() {
      this.filters = { search: '', user: '', package: '', status: '', ordering: '' }
      this.page = 1
      await this.fetchSubscriptions()
    },
    async changePage(page) {
      if (page < 1 || page === this.page) return
      this.page = page
      await this.fetchSubscriptions()
    },
    formatDate(str) {
      if (!str) return '—'
      return new Date(str).toLocaleDateString()
    },
    openEdit(sub) {
      this.success = ''
      this.editError = ''
      this.editingSubscription = sub
      this.editForm = { user: sub.user, package: sub.package.id }
    },
    closeEdit() {
      this.editingSubscription = null
      this.editError = ''
      this.editForm = { user: null, package: null }
    },
    async submitEdit() {
      if (!this.editChanged) return
      this.editSaving = true
      this.editError = ''
      try {
        const response = await api.patch(`/subscriptions/${this.editingSubscription.id}/`, {
          user: this.editForm.user,
          package_id: this.editForm.package,
        })
        const invoice = response.data.invoice
        this.success = invoice
          ? `Subscription updated. Invoice ${invoice.invoice_number} generated for $${invoice.total_amount}.`
          : 'Subscription updated.'
        this.closeEdit()
        await this.fetchSubscriptions()
      } catch (err) {
        this.editError = formatApiError(err, 'Failed to update subscription.')
      } finally {
        this.editSaving = false
      }
    },
    closeModal() {
      this.showModal = false
      this.modalError = ''
      this.form = { user: null, package_ids: [] }
    },
    async submitAssign() {
      this.submitting = true
      this.modalError = ''
      try {
        await api.post('/subscriptions/', {
          user: this.form.user,
          package_ids: this.form.package_ids,
        })
        this.closeModal()
        await this.fetchSubscriptions()
      } catch (err) {
        this.modalError = formatApiError(err, 'Failed to assign packages.')
      } finally {
        this.submitting = false
      }
    },
    async cancelSubscription(sub) {
      const pkgName = sub.package ? sub.package.name : 'this package'
      if (!confirm(`Cancel ${pkgName} for ${sub.user_email}?`)) {
        return
      }
      this.cancellingId = sub.id
      try {
        await api.patch(`/subscriptions/${sub.id}/`, { status: 'cancelled' })
        await this.fetchSubscriptions()
      } catch (err) {
        this.error = formatApiError(err, 'Failed to cancel subscription.')
      } finally {
        this.cancellingId = null
      }
    },
  },
}
</script>

<style scoped>
.packages-selection {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px;
  max-height: 160px;
  overflow-y: auto;
  background: #f8fafc;
}

.pkg-checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 4px;
  margin-bottom: 4px;
  cursor: pointer;
  border-bottom: 1px solid #f1f5f9;
}

.pkg-label-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
}

.pkg-price {
  font-weight: 600;
  color: #1e293b;
  font-size: 13px;
}
.edit-note {
  margin: 0 0 16px;
  color: #64748b;
  font-size: 13px;
}
</style>

<style scoped>
.subscription-filters { display: flex; align-items: flex-end; flex-wrap: wrap; gap: 12px; padding: 16px; border-bottom: 1px solid var(--border); }
.subscription-filters .form-group { min-width: 180px; margin: 0; }
.subscription-filters .filter-actions { display: flex; gap: 8px; }
</style>
