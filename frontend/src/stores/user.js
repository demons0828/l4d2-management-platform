import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user
  },

  actions: {
    async login(steamId) {
      try {
        const response = await axios.post(`/api/auth/steam/login?steam_id=${steamId}`)

        if (response.data.success) {
          this.user = {
            steamId: response.data.steam_id,
            username: response.data.username,
            avatarUrl: response.data.avatar_url
          }
          this.token = 'fake-token' // 简化处理，实际项目中应从后端获取真实token
          localStorage.setItem('token', this.token)
          localStorage.setItem('user', JSON.stringify(this.user))
          return { success: true }
        } else {
          return { success: false, message: response.data.message }
        }
      } catch (error) {
        console.error('登录错误:', error)
        return {
          success: false,
          message: error.response?.data?.detail?.[0]?.msg || error.response?.data?.message || '登录失败'
        }
      }
    },

    async loginWithPassword(credentials) {
      try {
        const response = await axios.post('/api/auth/login', credentials)

        if (response.data.success) {
          this.user = response.data.user
          this.token = response.data.token
          localStorage.setItem('token', this.token)
          localStorage.setItem('user', JSON.stringify(this.user))
          return { success: true }
        } else {
          return { success: false, message: response.data.message }
        }
      } catch (error) {
        console.error('账号密码登录错误:', error)
        return {
          success: false,
          message: error.response?.data?.detail || error.response?.data?.message || '登录失败'
        }
      }
    },

    async register(userData) {
      try {
        const response = await axios.post('/api/auth/register', userData)

        if (response.data.success) {
          this.user = response.data.user
          this.token = response.data.token
          localStorage.setItem('token', this.token)
          localStorage.setItem('user', JSON.stringify(this.user))
          return { success: true }
        } else {
          return { success: false, message: response.data.message }
        }
      } catch (error) {
        console.error('注册错误:', error)
        return {
          success: false,
          message: error.response?.data?.detail || error.response?.data?.message || '注册失败'
        }
      }
    },

    async fetchCurrentUser() {
      if (!this.token) return

      try {
        const response = await axios.get('/api/auth/me', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.user = response.data
      } catch (error) {
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    initializeAuth() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')

      if (token && user) {
        this.token = token
        this.user = JSON.parse(user)
        this.fetchCurrentUser()
      }
    }
  }
})
