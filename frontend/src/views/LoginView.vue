<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h2>ISP Billing Portal</h2>
        <p>Sign in with your email and password</p>
      </div>

      <div v-if="error" class="alert alert-danger">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email Address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="admin@isp.test or customer@isp.test"
            required
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter password"
            required
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <div class="demo-hints">
        <strong>Demo Accounts (after seed):</strong>
        <div>Admin: <code>admin@isp.test</code> / <code>AdminPass!2345</code></div>
        <div>Customer: <code>customer@isp.test</code> / <code>Customer!2345</code></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginView',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: '',
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      this.loading = true
      try {
        const user = await this.$store.dispatch('login', {
          email: this.email,
          password: this.password,
        })
        const redirect = this.$route.query.redirect
        if (redirect) {
          this.$router.push(redirect)
        } else if (user.is_staff) {
          this.$router.push('/admin/users')
        } else {
          this.$router.push('/user/profile')
        }
      } catch (err) {
        if (err.response && err.response.data) {
          const data = err.response.data
          this.error = data.detail || 'Invalid email or password.'
        } else {
          this.error = 'Network error or server unavailable.'
        }
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f5f9;
  padding: 16px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  padding: 32px;
  border-radius: 8px;
  border: 1px solid var(--border);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-header h2 {
  font-size: 1.5rem;
  margin-bottom: 6px;
  color: var(--text-main);
}

.login-header p {
  color: var(--text-muted);
  font-size: 13px;
}

.btn-block {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  margin-top: 8px;
}

.demo-hints {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px dashed var(--border);
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.6;
}

.demo-hints code {
  background: #f1f5f9;
  padding: 2px 4px;
  border-radius: 4px;
  color: #1e293b;
}
</style>
