import Vue from 'vue'
import Vuex from 'vuex'
import api from './api'

Vue.use(Vuex)

const getStoredUser = () => {
  try {
    const raw = localStorage.getItem('isp_user')
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    return null
  }
}

export default new Vuex.Store({
  state: {
    accessToken: localStorage.getItem('isp_access_token') || '',
    refreshToken: localStorage.getItem('isp_refresh_token') || '',
    user: getStoredUser(),
  },
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
        isAdmin: (state) => !!(state.user && (state.user.is_staff || state.user.is_admin)),
    currentUser: (state) => state.user,
  },
  mutations: {
    SET_TOKENS(state, { access, refresh }) {
      state.accessToken = access
      localStorage.setItem('isp_access_token', access)
      if (refresh) {
        state.refreshToken = refresh
        localStorage.setItem('isp_refresh_token', refresh)
      }
    },
    SET_USER(state, user) {
      state.user = user
      if (user) {
        localStorage.setItem('isp_user', JSON.stringify(user))
      } else {
        localStorage.removeItem('isp_user')
      }
    },
    CLEAR_AUTH(state) {
      state.accessToken = ''
      state.refreshToken = ''
      state.user = null
      localStorage.removeItem('isp_access_token')
      localStorage.removeItem('isp_refresh_token')
      localStorage.removeItem('isp_user')
    },
  },
  actions: {
    async login({ commit, dispatch }, { email, password }) {
      const response = await api.post('/auth/login/', { email, password })
      commit('SET_TOKENS', {
        access: response.data.access,
        refresh: response.data.refresh,
      })
      const meResponse = await dispatch('fetchMe')
      return meResponse
    },
    async fetchMe({ commit }) {
      const response = await api.get('/auth/me/')
      commit('SET_USER', response.data)
      return response.data
    },
    async logout({ commit, state }) {
      if (state.refreshToken) {
        try {
          await api.post('/auth/logout/', { refresh: state.refreshToken })
        } catch (e) {
          // ignore logout network/token error
        }
      }
      commit('CLEAR_AUTH')
    },
  },
})
