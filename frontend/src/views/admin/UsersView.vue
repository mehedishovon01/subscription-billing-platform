<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">Customer Management & Onboarding</h2>
        <button class="btn btn-primary btn-sm" @click="showModal = true">+ Onboard Customer</button>
      </div>

      <form class="customer-filters" @submit.prevent="applyFilters">
        <div class="form-group">
          <label for="customer-search">Search name or email</label>
          <input id="customer-search" v-model="filters.search" type="search" placeholder="Search customers" />
        </div>
        <div class="form-group">
          <label for="customer-role">Role</label>
          <select id="customer-role" v-model="filters.is_staff">
            <option value="">All roles</option>
            <option value="false">Customers</option>
            <option value="true">Admins</option>
          </select>
        </div>
        <div class="form-group">
          <label for="customer-status">Status</label>
          <select id="customer-status" v-model="filters.is_active">
            <option value="">All statuses</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
        <div class="form-group">
          <label for="customer-ordering">Sort by</label>
          <select id="customer-ordering" v-model="filters.ordering">
            <option value="">Default order</option>
            <option value="-date_joined">Newest joined</option>
            <option value="date_joined">Oldest joined</option>
            <option value="email">Email A–Z</option>
            <option value="-email">Email Z–A</option>
          </select>
        </div>
        <div class="filter-actions">
          <button class="btn btn-primary btn-sm" type="submit">Apply filters</button>
          <button class="btn btn-secondary btn-sm" type="button" @click="clearFilters">Clear</button>
        </div>
      </form>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Full Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Staff / Role</th>
              <th>Active</th>
              <th>Joined Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading && users.length === 0">
              <td colspan="7" style="text-align: center; padding: 24px;">Loading customers...</td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="7" style="text-align: center; padding: 24px;">No users found.</td>
            </tr>
            <tr v-for="u in users" :key="u.id">
              <td>#{{ u.id }}</td>
              <td><strong>{{ u.full_name || '—' }}</strong></td>
              <td>{{ u.email }}</td>
              <td>{{ u.phone || '—' }}</td>
              <td>
                <span :class="u.is_staff ? 'badge badge-danger' : 'badge badge-info'">
                  {{ u.is_staff ? 'Admin' : 'Customer' }}
                </span>
              </td>
              <td>
                <span :class="u.is_active ? 'badge badge-success' : 'badge badge-neutral'">
                  {{ u.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>{{ formatDate(u.date_joined) }}</td>
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

    <!-- Onboard Customer Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="card-header">
          <h3 class="card-title">Onboard New Customer</h3>
          <button class="btn btn-secondary btn-sm" @click="closeModal">✕</button>
        </div>

        <div v-if="modalError" class="alert alert-danger">{{ modalError }}</div>

        <form @submit.prevent="submitOnboard">
          <div class="form-group">
            <label>Full Name *</label>
            <input v-model="form.full_name" type="text" placeholder="John Doe" required />
          </div>

          <div class="form-group">
            <label>Email Address *</label>
            <input v-model="form.email" type="email" placeholder="customer@example.com" required />
          </div>

          <div class="form-group">
            <label>Password *</label>
            <input v-model="form.password" type="password" placeholder="At least 8 characters" required />
          </div>

          <div class="form-group">
            <label>Phone</label>
            <input v-model="form.phone" type="text" placeholder="+8801700000000" />
          </div>

          <div class="form-group">
            <label>Address</label>
            <input v-model="form.address" type="text" placeholder="Street, City" />
          </div>

          <div class="form-group">
            <label>Initial Packages (creates onboarding invoice)</label>
            <div class="packages-selection">
              <label
                v-for="pkg in availablePackages"
                :key="pkg.id"
                class="pkg-checkbox-item"
              >
                <input
                  type="checkbox"
                  :value="pkg.id"
                  v-model="form.package_ids"
                />
                <span class="pkg-label-name">{{ pkg.name }}</span>
                <span class="badge badge-neutral">{{ pkg.type }}</span>
                <span class="pkg-price">${{ pkg.price }}</span>
              </label>
              <div v-if="availablePackages.length === 0" style="color: #64748b; font-size: 13px;">
                No active packages available.
              </div>
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px;">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Onboarding...' : 'Create Customer' }}
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
  name: 'UsersView',
  data() {
    return {
      users: [],
      filters: { search: '', is_staff: '', is_active: '', ordering: '' },
      page: 1,
      pageSize: 10,
      pagination: { count: 0, next: null, previous: null },
      availablePackages: [],
      loading: false,
      submitting: false,
      error: '',
      modalError: '',
      showModal: false,
      form: {
        email: '',
        password: '',
        full_name: '',
        phone: '',
        address: '',
        package_ids: [],
      },
    }
  },
  created() {
    this.fetchUsers()
    this.fetchPackages()
  },
  methods: {
    async fetchUsers() {
      this.loading = true
      this.error = ''
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.filters.search.trim()) params.search = this.filters.search.trim()
        if (this.filters.is_staff !== '') params.is_staff = this.filters.is_staff
        if (this.filters.is_active !== '') params.is_active = this.filters.is_active
        if (this.filters.ordering) params.ordering = this.filters.ordering
        const res = await api.get('/users/', { params })
        this.users = res.data.results || res.data
        this.pagination = {
          count: res.data.count !== undefined ? res.data.count : this.users.length,
          next: res.data.next || null,
          previous: res.data.previous || null,
        }
      } catch (err) {
        this.error = formatApiError(err, 'Failed to load customers.')
      } finally {
        this.loading = false
      }
    },
    async fetchPackages() {
      try {
        this.availablePackages = await fetchAllResults('/packages/', { is_active: true })
      } catch (err) {
        // ignore
      }
    },
    async applyFilters() {
      this.page = 1
      await this.fetchUsers()
    },
    async clearFilters() {
      this.filters = { search: '', is_staff: '', is_active: '', ordering: '' }
      this.page = 1
      await this.fetchUsers()
    },
    async changePage(page) {
      if (page < 1 || page === this.page) return
      this.page = page
      await this.fetchUsers()
    },
    formatDate(str) {
      if (!str) return '—'
      return new Date(str).toLocaleDateString()
    },
    closeModal() {
      this.showModal = false
      this.modalError = ''
      this.form = {
        email: '',
        password: '',
        full_name: '',
        phone: '',
        address: '',
        package_ids: [],
      }
    },
    async submitOnboard() {
      this.submitting = true
      this.modalError = ''
      try {
        await api.post('/users/', this.form)
        this.closeModal()
        await this.fetchUsers()
      } catch (err) {
        this.modalError = formatApiError(err, 'Failed to onboard customer.')
      } finally {
        this.submitting = false
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

.customer-filters {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--border);
}
.customer-filters .form-group { min-width: 160px; margin: 0; }
.customer-filters .filter-actions { display: flex; gap: 8px; }
</style>
