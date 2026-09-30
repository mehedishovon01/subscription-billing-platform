<template>
  <form class="invoice-filters" @submit.prevent="submit">
    <div class="form-group">
      <label for="invoice-search">Search invoice, customer, or package</label>
      <input id="invoice-search" v-model="filters.search" type="search" placeholder="Invoice number, name, email, or package" />
    </div>
    <div v-if="showUserFilter" class="form-group">
      <label for="invoice-user-filter">Customer / User</label>
      <select id="invoice-user-filter" v-model="filters.user">
        <option value="">All users</option>
        <option v-for="user in users" :key="user.id" :value="String(user.id)">
          {{ user.full_name || user.email }} ({{ user.email }})
        </option>
      </select>
    </div>
    <div class="form-group">
      <label for="invoice-created-after">Created after</label>
      <input id="invoice-created-after" v-model="filters.created_after" type="datetime-local" />
    </div>
    <div class="form-group">
      <label for="invoice-created-before">Created before</label>
      <input id="invoice-created-before" v-model="filters.created_before" type="datetime-local" />
    </div>
    <div class="filter-actions">
      <button class="btn btn-primary btn-sm" type="submit">Apply filters</button>
      <button class="btn btn-secondary btn-sm" type="button" @click="clear">Clear</button>
    </div>
    <p v-if="validationError" class="filter-error" role="alert">{{ validationError }}</p>
  </form>
</template>

<script>
const emptyFilters = () => ({ search: '', user: '', created_after: '', created_before: '' })

export default {
  name: 'InvoiceFilterControls',
  props: {
    users: { type: Array, default: () => [] },
    showUserFilter: { type: Boolean, default: false },
  },
  data() {
    return { filters: emptyFilters(), validationError: '' }
  },
  methods: {
    submit() {
      this.validationError = ''
      if (this.filters.created_after && this.filters.created_before &&
          new Date(this.filters.created_after) > new Date(this.filters.created_before)) {
        this.validationError = 'Created after must be earlier than created before.'
        return
      }
      this.$emit('apply', { ...this.filters })
    },
    clear() {
      this.filters = emptyFilters()
      this.validationError = ''
      this.$emit('apply', { ...this.filters })
    },
  },
}
</script>

<style scoped>
.invoice-filters { display: flex; align-items: flex-end; flex-wrap: wrap; gap: 12px; padding: 16px; border-bottom: 1px solid var(--border); }
.form-group { min-width: 190px; margin: 0; }
.filter-actions { display: flex; gap: 8px; }
.filter-error { flex-basis: 100%; margin: 0; color: #b91c1c; font-size: 13px; }
</style>
