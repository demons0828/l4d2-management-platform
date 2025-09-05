import api from './index.js'

export const authAPI = {
  steamLogin: (steamId) => api.post(`/auth/steam/login?steam_id=${steamId}`),
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout')
}

export const downloadAPI = {
  getTasks: () => api.get('/servers/downloads'),
  getTask: (taskId) => api.get(`/servers/downloads/${taskId}`),
  cancelTask: (taskId) => api.delete(`/servers/downloads/${taskId}`),
  installSteamCMD: () => api.post('/servers/install/steamcmd'),
  installServer: (credentials) => api.post('/servers/install/server', credentials),
  installPlugins: (credentials) => api.post('/servers/install/plugins', credentials),
  fullInstall: (credentials) => api.post('/servers/install/full', credentials)
}
