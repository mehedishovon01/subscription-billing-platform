<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">Package Catalog Management</h2>
        <button class="btn btn-primary btn-sm" @click="openCreate">+ Create Package</button>
      </div>

      <form class="catalog-filters" @submit.prevent="applyFilters">
        <div class="form-group">
          <label for="package-search">Search package name</label>
          <input id="package-search" v-model="filters.search" type="search" placeholder="Search packages" />
        </div>
        <div class="form-group">
          <label for="package-type-filter">Type</label>
          <select id="package-type-filter" v-model="filters.type">
            <option value="">All types</option>
            <option value="isp">ISP</option>
            <option value="realip">Real IP</option>
            <option value="tv">TV</option>
          </select>
        </div>
        <div class="form-group">
          <label for="package-status-filter">Status</label>
          <select id="package-status-filter" v-model="filters.is_active">
            <option value="">All statuses</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>
        <div class="form-group">
          <label for="package-ordering">Sort by</label>
          <select id="package-ordering" v-model="filters.ordering">
            <option value="">Default order</option>
            <option value="name">Name A–Z</option>
            <option value="-name">Name Z–A</option>
            <option value="price">Price low to high</option>
            <option value="-price">Price high to low</option>
            <option value="-created_at">Newest created</option>
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
              <th>Name</th>
              <th>Type</th>
              <th>Price</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading && packages.length === 0">
              <td colspan="6" style="text-align: center; padding: 24px;">Loading packages...</td>
            </tr>
            <tr v-else-if="packages.length === 0">
              <td colspan="6" style="text-align: center; padding: 24px;">No packages found.</td>
            </tr>
            <tr v-for="pkg in packages" :key="pkg.id">
              <td>#{{ pkg.id }}</td>
              <td><strong>{{ pkg.name }}</strong></td>
              <td><span class="badge badge-info">{{ pkg.type }}</span></td>
              <td><strong>${{ pkg.price }}</strong></td>
              <td>
                <span :class="pkg.is_active ? 'badge badge-success' : 'badge badge-neutral'">
                  {{ pkg.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td style="display: flex; gap: 6px;">
                <button class="btn btn-secondary btn-sm" @click="openEdit(pkg)">Edit</button>
                <button
                  class="btn btn-secondary btn-sm"
                  @click="toggleStatus(pkg)"
                  :disabled="togglingId === pkg.id"
                >
                  {{ pkg.is_active ? 'Deactivate' : 'Activate' }}
                </button>
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

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="card-header">
          <h3 class="card-title">{{ editingId ? 'Edit Package' : 'Create New Package' }}</h3>
          <button class="btn btn-secondary btn-sm" @click="closeModal">✕</button>
        </div>

        <div v-if="modalError" class="alert alert-danger">{{ modalError }}</div>

        <form @submit.prevent="submitPackage">
          <div class="form-group">
            <label>Package Name *</label>
            <input v-model="form.name" type="text" placeholder="e.g. Fiber 100 Mbps" required />
          </div>

          <div class="form-group">
            <label>Service Type *</label>
            <select v-model="form.type" required>
              <option value="isp">ISP (Internet)</option>
              <option value="realip">Real IP</option>
              <option value="tv">TV / Cable</option>
            </select>
          </div>

          <div class="form-group">
            <label>Price ($) *</label>
            <input v-model="form.price" type="number" step="0.01" min="0" placeholder="1200.00" required />
          </div>

          <div class="form-group">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="checkbox" v-model="form.is_active" />
              <span>Package is active for assignment</span>
            </label>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px;">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              {{ submitting ? 'Saving...' : (editingId ? 'Save Changes' : 'Create Package') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../api'
import PaginationControls from '../../components/PaginationControls.vue'
import { formatApiError } from '../../errors'

export default {
  components: { PaginationControls },
  name: 'PackagesView',
  data() {
    return {
      packages: [],
      filters: { search: '', type: '', is_active: '', ordering: '' },
      page: 1,
      pageSize: 10,
      pagination: { count: 0, next: null, previous: null },
      loading: false,
      submitting: false,
      togglingId: null,
      error: '',
      modalError: '',
      showModal: false,
      editingId: null,
      form: {
        name: '',
        type: 'isp',
        price: '',
        is_active: true,
      },
    }
  },
  created() {
    this.fetchPackages()
  },
  methods: {
    async fetchPackages() {
      this.loading = true
      this.error = ''
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.filters.search.trim()) params.search = this.filters.search.trim()
        if (this.filters.type) params.type = this.filters.type
        if (this.filters.is_active !== '') params.is_active = this.filters.is_active
        if (this.filters.ordering) params.ordering = this.filters.ordering
        const res = await api.get('/packages/', { params })
        this.packages = res.data.results || res.data
        this.pagination = {
          count: res.data.count !== undefined ? res.data.count : this.packages.length,
          next: res.data.next || null,
          previous: res.data.previous || null,
        }
      } catch (err) {
        this.error = formatApiError(err, 'Failed to load packages.')
      } finally {
        this.loading = false
      }
    },
    async applyFilters() {
      this.page = 1
      await this.fetchPackages()
    },
    async clearFilters() {
      this.filters = { search: '', type: '', is_active: '', ordering: '' }
      this.page = 1
      await this.fetchPackages()
    },
    async changePage(page) {
      if (page < 1 || page === this.page) return
      this.page = page
      await this.fetchPackages()
    },
    openCreate() {
      this.editingId = null
      this.form = { name: '', type: 'isp', price: '', is_active: true }
      this.modalError = ''
      this.showModal = true
    },
    openEdit(pkg) {
      this.editingId = pkg.id
      this.form = {
        name: pkg.name,
        type: pkg.type,
        price: pkg.price,
        is_active: pkg.is_active,
      }
      this.modalError = ''
      this.showModal = true
    },
    closeModal() {
      this.showModal = false
      this.modalError = ''
      this.editingId = null
    },
    async submitPackage() {
      this.submitting = true
      this.modalError = ''
      try {
        if (this.editingId) {
          const { name, type, price, is_active } = this.form
          await api.patch(`/packages/${this.editingId}/`, { name, type, price, is_active })
        } else {
          await api.post('/packages/', this.form)
        }
        this.closeModal()
        await this.fetchPackages()
      } catch (err) {
        this.modalError = formatApiError(err, 'Failed to save package.')
      } finally {
        this.submitting = false
      }
    },
    async toggleStatus(pkg) {
      this.togglingId = pkg.id
      try {
        await api.patch(`/packages/${pkg.id}/`, { is_active: !pkg.is_active })
        await this.fetchPackages()
      } catch (err) {
        this.error = formatApiError(err, 'Failed to update package status.')
      } finally {
        this.togglingId = null
      }
    },
  },
}
</script>

<style scoped>
.catalog-filters { display: flex; align-items: flex-end; flex-wrap: wrap; gap: 12px; padding: 16px; border-bottom: 1px solid var(--border); }
.catalog-filters .form-group { min-width: 160px; margin: 0; }
.catalog-filters .filter-actions { display: flex; gap: 8px; }
</style>
