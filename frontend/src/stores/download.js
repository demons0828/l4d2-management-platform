import { defineStore } from 'pinia'
import { downloadAPI } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useDownloadStore = defineStore('download', {
  state: () => ({
    tasks: {},
    currentTask: null,
    loading: false
  }),

  getters: {
    activeTasks: (state) => {
      return Object.values(state.tasks).filter(task => task.status === 'running')
    },

    completedTasks: (state) => {
      return Object.values(state.tasks).filter(task => task.status === 'completed')
    },

    failedTasks: (state) => {
      return Object.values(state.tasks).filter(task => task.status === 'failed')
    }
  },

  actions: {
    async fetchTasks() {
      try {
        const response = await downloadAPI.getTasks()
        this.tasks = response.data
      } catch (error) {
        console.error('获取下载任务失败:', error)
        ElMessage.error('获取下载任务失败')
      }
    },

    async fetchTask(taskId) {
      try {
        const response = await downloadAPI.getTask(taskId)
        this.tasks[taskId] = response.data
        return response.data
      } catch (error) {
        console.error('获取下载任务详情失败:', error)
        throw error
      }
    },

    async installSteamCMD() {
      try {
        this.loading = true
        const response = await downloadAPI.installSteamCMD()

        if (response.data.success) {
          ElMessage.success('SteamCMD安装成功')
          await this.fetchTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('SteamCMD安装失败:', error)
        ElMessage.error('SteamCMD安装失败')
      } finally {
        this.loading = false
      }
    },

    async installServer(credentials = null) {
      try {
        this.loading = true
        const response = await downloadAPI.installServer(credentials || {})

        if (response.data.success) {
          ElMessage.success('L4D2服务器下载已开始')
          if (response.data.task_id) {
            this.currentTask = response.data.task_id
            // 开始轮询任务进度
            this.startPollingTask(response.data.task_id)
          }
          await this.fetchTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('L4D2服务器安装失败:', error)
        ElMessage.error('L4D2服务器安装失败')
      } finally {
        this.loading = false
      }
    },

    async installPlugins(credentials = null) {
      try {
        this.loading = true
        const response = await downloadAPI.installPlugins(credentials || {})

        if (response.data.success) {
          ElMessage.success('插件安装已开始')
          if (response.data.task_id) {
            this.startPollingTask(response.data.task_id)
          }
          await this.fetchTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('插件安装失败:', error)
        ElMessage.error('插件安装失败')
      } finally {
        this.loading = false
      }
    },

    async fullInstall(credentials = null) {
      try {
        this.loading = true
        const response = await downloadAPI.fullInstall(credentials || {})

        if (response.data.success) {
          ElMessage.success('完整安装已开始')
          if (response.data.task_id) {
            this.startPollingTask(response.data.task_id)
          }
          await this.fetchTasks()
        } else {
          ElMessage.error(response.data.message)
        }
      } catch (error) {
        console.error('完整安装失败:', error)
        ElMessage.error('完整安装失败')
      } finally {
        this.loading = false
      }
    },

    async cancelTask(taskId) {
      try {
        await downloadAPI.cancelTask(taskId)
        ElMessage.success('下载任务已取消')
        await this.fetchTasks()
      } catch (error) {
        console.error('取消下载任务失败:', error)
        ElMessage.error('取消下载任务失败')
      }
    },

    startPollingTask(taskId) {
      const pollInterval = setInterval(async () => {
        try {
          const task = await this.fetchTask(taskId)

          if (task.status === 'completed' || task.status === 'failed') {
            clearInterval(pollInterval)
            if (task.status === 'completed') {
              ElMessage.success(`${task.description}完成`)
            } else {
              ElMessage.error(`${task.description}失败: ${task.message}`)
            }
          }
        } catch (error) {
          console.error('轮询任务状态失败:', error)
          clearInterval(pollInterval)
        }
      }, 2000) // 每2秒轮询一次

      // 5分钟后自动停止轮询
      setTimeout(() => {
        clearInterval(pollInterval)
      }, 5 * 60 * 1000)
    }
  }
})
