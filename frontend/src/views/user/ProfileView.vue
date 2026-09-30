<template>
  <div>
    <div class="card">
      <div class="card-header">
        <h2 class="card-title">My Account Profile</h2>
      </div>

      <div v-if="successMsg" class="alert alert-success">{{ successMsg }}</div>
      <div v-if="errorMsg" class="alert alert-danger">{{ errorMsg }}</div>

      <form @submit.prevent="updateProfile" style="max-width: 500px;">
        <div class="form-group">
          <label>Email Address</label>
          <input :value="profile.email" type="email" disabled style="background-color: #f1f5f9; cursor: not-allowed;" />
          <small style="color: #64748b;">Email cannot be changed.</small>
        </div>

        <div class="form-group">
          <label>Full Name</label>
          <input v-model="profile.full_name" type="text" placeholder="Your name" />
        </div>

        <div class="form-group">
          <label>Phone Number</label>
          <input v-model="profile.phone" type="text" placeholder="+880..." />
        </div>

        <div class="form-group">
          <label>Address</label>
          <textarea v-model="profile.address" rows="3" placeholder="Billing & installation address"></textarea>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Saving Changes...' : 'Save Profile' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import api from '../../api'
import { formatApiError } from '../../errors'

export default {
  name: 'UserProfileView',
  data() {
    return {
      profile: {
        email: '',
        full_name: '',
        phone: '',
        address: '',
      },
      saving: false,
      successMsg: '',
      errorMsg: '',
    }
  },
  async created() {
    try {
      const res = await api.get('/auth/me/')
      this.profile = { ...res.data }
    } catch (err) {
      this.errorMsg = 'Could not load profile.'
    }
  },
  methods: {
    async updateProfile() {
      this.saving = true
      this.successMsg = ''
      this.errorMsg = ''
      try {
        const res = await api.patch('/auth/me/', {
          full_name: this.profile.full_name,
          phone: this.profile.phone,
          address: this.profile.address,
        })
        this.profile = { ...res.data }
        this.$store.commit('SET_USER', res.data)
        this.successMsg = 'Profile updated successfully.'
      } catch (err) {
        this.errorMsg = formatApiError(err, 'Failed to update profile.')
      } finally {
        this.saving = false
      }
    },
  },
}
</script>
