<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">My Subscriptions & Services</h2>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="table-responsive">
        <table>
          <thead>
            <tr>
              <th>Package Name</th>
              <th>Service Type</th>
              <th>Price</th>
              <th>Status</th>
              <th>Assigned Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading && subscriptions.length === 0">
              <td colspan="5" style="text-align: center; padding: 24px;">Loading subscriptions...</td>
            </tr>
            <tr v-else-if="subscriptions.length === 0">
              <td colspan="5" style="text-align: center; padding: 24px;">No active or past subscriptions found.</td>
            </tr>
            <tr v-for="sub in subscriptions" :key="sub.id">
              <td><strong>{{ sub.package ? sub.package.name : '' }}</strong></td>
              <td><span class="badge badge-info">{{ sub.package ? sub.package.type : '' }}</span></td>
              <td><strong>${{ sub.package ? sub.package.price : '' }}</strong></td>
              <td>
                <span :class="sub.status === 'active' ? 'badge badge-success' : 'badge badge-neutral'">
                  {{ sub.status }}
                </span>
              </td>
              <td>{{ formatDate(sub.assigned_at) }}</td>
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
  </div>
</template>

<script>
import api from '../../api'
import PaginationControls from '../../components/PaginationControls.vue'
import { formatApiError } from '../../errors'

export default {
  components: { PaginationControls },
  name: 'UserSubscriptionsView',
  data() {
    return {
      subscriptions: [],
      page: 1,
      pageSize: 10,
      pagination: { count: 0, next: null, previous: null },
      loading: false,
      error: '',
    }
  },
  created() {
    this.fetchSubscriptions()
  },
  methods: {
    async fetchSubscriptions() {
      this.loading = true
      this.error = ''
      try {
        const res = await api.get('/subscriptions/', { params: { page: this.page, page_size: this.pageSize } })
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
    async changePage(page) {
      if (page < 1 || page === this.page) return
      this.page = page
      await this.fetchSubscriptions()
    },
    formatDate(str) {
      if (!str) return '—'
      return new Date(str).toLocaleDateString()
    },
  },
}
</script>
