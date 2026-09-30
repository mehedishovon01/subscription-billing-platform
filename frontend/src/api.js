import axios from 'axios'
import store from './store'
import router from './router'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: attach access token
api.interceptors.request.use(
  (config) => {
    const token = store.state.accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401 & token refresh
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      if (originalRequest.url.includes('/auth/login/') || originalRequest.url.includes('/auth/refresh/')) {
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = store.state.refreshToken
      if (!refreshToken) {
        store.dispatch('logout')
        router.push('/login')
        return Promise.reject(error)
      }

      try {
        const response = await axios.post('/api/v1/auth/refresh/', {
          refresh: refreshToken,
        })
        const newAccessToken = response.data.access
        const newRefreshToken = response.data.refresh || refreshToken

        store.commit('SET_TOKENS', {
          access: newAccessToken,
          refresh: newRefreshToken,
        })

        processQueue(null, newAccessToken)
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
        return api(originalRequest)
      } catch (refreshErr) {
        processQueue(refreshErr, null)
        store.dispatch('logout')
        router.push('/login')
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export async function fetchAllResults(path, params = {}) {
  const results = []
  let page = 1
  let hasNext = true

  while (hasNext) {
    const response = await api.get(path, {
      params: { ...params, page, page_size: 10 },
    })
    const data = response.data

    if (Array.isArray(data)) {
      results.push(...data)
      hasNext = false
    } else {
      results.push(...(data.results || []))
      hasNext = Boolean(data.next)
      page += 1
    }
  }

  return results
}

export default api
