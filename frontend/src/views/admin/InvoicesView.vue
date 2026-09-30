<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">All Customer Invoices</h2>
      </div>

<InvoiceFilterControls
        :users="users"
        show-user-filter
        @apply="applyFilters"
      />

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Invoice #</th>
              <th>Customer</th>
              <th>Items</th>
              <th>Total Amount</th>
              <th>Created Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading && invoices.length === 0">
              <td colspan="6" style="text-align: center; padding: 24px;">Loading invoices...</td>
            </tr>
            <tr v-else-if="invoices.length === 0">
              <td colspan="6" style="text-align: center; padding: 24px;">No invoices found.</td>
            </tr>
            <tr v-for="inv in invoices" :key="inv.id">
              <td><strong>{{ inv.invoice_number }}</strong></td>
              <td>
                <strong>{{ inv.user_full_name || '—' }}</strong>
                <div style="font-size: 12px; color: #64748b;">{{ inv.user_email }}</div>
              </td>
              <td>{{ inv.items ? inv.items.length : 0 }} items</td>
              <td><strong>${{ inv.total_amount }}</strong></td>
              <td>{{ formatDate(inv.created_at) }}</td>
              <td>
                <button class="btn btn-secondary btn-sm" @click="selectedInvoice = inv">
                  View Details
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

    <div v-if="selectedInvoice" class="modal-overlay" @click.self="selectedInvoice = null">
      <div class="modal-content">
        <div class="card-header">
          <h3 class="card-title">{{ selectedInvoice.invoice_number }}</h3>
          <button class="btn btn-secondary btn-sm" @click="selectedInvoice = null">✕</button>
        </div>

        <div style="margin-bottom: 16px; font-size: 13px;">
          <div>
            <strong>Customer:</strong>
            {{ selectedInvoice.user_full_name }} ({{ selectedInvoice.user_email }})
          </div>
          <div><strong>Date:</strong> {{ formatDate(selectedInvoice.created_at) }}</div>
        </div>

        <table style="margin-bottom: 20px;">
          <thead>
            <tr>
              <th>Service / Item</th>
              <th>Type</th>
              <th style="text-align: right;">Snapshot Price</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in selectedInvoice.items" :key="item.id">
              <td>{{ item.package_name }}</td>
              <td><span class="badge badge-info">{{ item.package_type }}</span></td>
              <td style="text-align: right;">${{ item.unit_price }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <th colspan="2" style="text-align: right; font-size: 14px;">Total Amount:</th>
              <th style="text-align: right; font-size: 15px; color: var(--primary);">
                ${{ selectedInvoice.total_amount }}
              </th>
            </tr>
          </tfoot>
        </table>

        <div style="display: flex; justify-content: flex-end;">
          <button class="btn btn-secondary" @click="selectedInvoice = null">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api, { fetchAllResults } from '../../api'
import PaginationControls from '../../components/PaginationControls.vue'
import InvoiceFilterControls from '../../components/InvoiceFilterControls.vue'
import { formatApiError } from '../../errors'

export default {
  components: { PaginationControls, InvoiceFilterControls },
  name: 'InvoicesView',
  data() {
    return {
      invoices: [],
      users: [],
      filters: { search: '', user: '', created_after: '', created_before: '' },
      page: 1,
      pageSize: 10,
      pagination: { count: 0, next: null, previous: null },
      loading: false,
      error: '',
      selectedInvoice: null,
    }
  },
  created() {
    this.fetchInvoices()
    this.fetchUsers()
  },
  methods: {
    async fetchInvoices() {
      this.loading = true
      this.error = ''
      try {
        const params = { page: this.page, page_size: this.pageSize }
        if (this.filters.search.trim()) params.search = this.filters.search.trim()
        if (this.filters.user) params.user = this.filters.user
        if (this.filters.created_after) params.created_after = new Date(this.filters.created_after).toISOString()
        if (this.filters.created_before) params.created_before = new Date(this.filters.created_before).toISOString()
        const res = await api.get('/invoices/', { params })
        this.invoices = res.data.results || res.data
        this.pagination = {
          count: res.data.count !== undefined ? res.data.count : this.invoices.length,
          next: res.data.next || null,
          previous: res.data.previous || null,
        }
      } catch (err) {
        this.error = formatApiError(err, 'Failed to load invoices.')
      } finally {
        this.loading = false
      }
    },
    async fetchUsers() {
      try {
        this.users = await fetchAllResults('/users/')
      } catch (err) {
        this.error = formatApiError(err, 'Failed to load users for invoice filtering.')
      }
    },
    async applyFilters(filters) {
      this.filters = filters
      this.page = 1
      await this.fetchInvoices()
    },
    async changePage(page) {
      if (page < 1 || page === this.page) return
      this.page = page
      await this.fetchInvoices()
    },
    formatDate(str) {
      if (!str) return '—'
      return new Date(str).toLocaleString()
    },
  },
}
</script>
