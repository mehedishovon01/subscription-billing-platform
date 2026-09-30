<template>
  <div class="layout">
    <header class="navbar">
      <div class="nav-brand">
        <span class="brand-title">ISP Customer Portal</span>
        <span class="brand-role badge badge-info">Customer</span>
      </div>
      <nav class="nav-links">
        <router-link to="/user/profile" active-class="active">My Profile</router-link>
        <router-link to="/user/subscriptions" active-class="active">My Subscriptions</router-link>
        <router-link to="/user/invoices" active-class="active">My Invoices</router-link>
      </nav>
      <div class="nav-user">
        <span class="user-email">{{ user ? user.email : '' }}</span>
        <button class="btn btn-secondary btn-sm" @click="handleLogout">Logout</button>
      </div>
    </header>

    <main class="main-content container">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'UserLayout',
  computed: {
    user() {
      return this.$store.getters.currentUser
    },
  },
  methods: {
    async handleLogout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    },
  },
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  height: 60px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-title {
  font-weight: 700;
  font-size: 1.1rem;
  color: #0f172a;
}

.nav-links {
  display: flex;
  gap: 16px;
}

.nav-links a {
  color: #475569;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.15s;
}

.nav-links a:hover {
  color: var(--primary);
  text-decoration: none;
  background: #f1f5f9;
}

.nav-links a.active {
  color: var(--primary);
  background: #eff6ff;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-email {
  font-size: 13px;
  color: #64748b;
}

.main-content {
  flex: 1;
}
</style>
