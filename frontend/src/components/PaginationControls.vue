<template>
  <nav v-if="count > pageSize" class="pagination" aria-label="Pagination">
    <span class="pagination-summary">Showing {{ firstItem }}–{{ lastItem }} of {{ count }}</span>
    <div class="pagination-actions">
      <button class="btn btn-secondary btn-sm" :disabled="page <= 1" @click="$emit('change', 1)">First</button>
      <button class="btn btn-secondary btn-sm" :disabled="!hasPrevious" @click="$emit('change', page - 1)">Previous</button>
      <span class="pagination-page">Page {{ page }} of {{ pageCount }}</span>
      <button class="btn btn-secondary btn-sm" :disabled="!hasNext" @click="$emit('change', page + 1)">Next</button>
      <button class="btn btn-secondary btn-sm" :disabled="!hasNext" @click="$emit('change', pageCount)">Last</button>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'PaginationControls',
  props: {
    count: { type: Number, default: 0 },
    page: { type: Number, default: 1 },
    pageSize: { type: Number, default: 10 },
    hasPrevious: { type: Boolean, default: false },
    hasNext: { type: Boolean, default: false },
  },
  computed: {
    pageCount() { return Math.max(1, Math.ceil(this.count / this.pageSize)) },
    firstItem() { return this.count ? ((this.page - 1) * this.pageSize) + 1 : 0 },
    lastItem() { return Math.min(this.page * this.pageSize, this.count) },
  },
}
</script>

<style scoped>
.pagination { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 14px 16px; border-top: 1px solid var(--border); }
.pagination-actions { display: flex; align-items: center; gap: 6px; }
.pagination-page, .pagination-summary { color: #64748b; font-size: 13px; }
@media (max-width: 640px) { .pagination { align-items: flex-start; flex-direction: column; } .pagination-actions { flex-wrap: wrap; } }
</style>
