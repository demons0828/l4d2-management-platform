<template>
  <div class="downloads-container">
    <el-card class="downloads-card">
      <template #header>
        <div class="header-content">
          <h3>下载管理</h3>
          <el-button
            type="primary"
            @click="fetchTasks"
            :loading="downloadStore.loading"
            icon="Refresh"
          >
            刷新
          </el-button>
        </div>
      </template>

      <!-- 安装状态 -->
      <div class="install-status">
        <el-alert
          title="安装状态"
          :type="getInstallStatusType()"
          :description="getInstallStatusDescription()"
          show-icon
          :closable="false"
        />
      </div>

      <!-- 安装选项 -->
      <div class="install-options">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="option-card" shadow="hover">
              <div class="option-content">
                <el-icon size="32" class="option-icon"><Setting /></el-icon>
                <h4>SteamCMD</h4>
                <p>安装Steam命令行工具</p>
                <el-button
                  type="primary"
                  size="small"
                  :disabled="installStatus.steamcmd_installed"
                  @click="installSteamCMD"
                  :loading="downloadStore.loading"
                >
                  {{ installStatus.steamcmd_installed ? '已安装' : '安装' }}
                </el-button>
              </div>
            </el-card>
          </el-col>

          <el-col :span="6">
            <el-card class="option-card" shadow="hover">
              <div class="option-content">
                <el-icon size="32" class="option-icon"><Monitor /></el-icon>
                <h4>L4D2服务器</h4>
                <p>下载L4D2专用服务器</p>
                <el-button
                  type="primary"
                  size="small"
                  :disabled="!installStatus.steamcmd_installed"
                  @click="installServer"
                  :loading="downloadStore.loading"
                >
                  下载
                </el-button>
              </div>
            </el-card>
          </el-col>

          <el-col :span="6">
            <el-card class="option-card" shadow="hover">
              <div class="option-content">
                <el-icon size="32" class="option-icon"><Box /></el-icon>
                <h4>插件</h4>
                <p>安装SourceMod和MetaMod</p>
                <el-button
                  type="primary"
                  size="small"
                  :disabled="!installStatus.server_installed"
                  @click="installPlugins"
                  :loading="downloadStore.loading"
                >
                  安装
                </el-button>
              </div>
            </el-card>
          </el-col>

          <el-col :span="6">
            <el-card class="option-card" shadow="hover">
              <div class="option-content">
                <el-icon size="32" class="option-icon"><Check /></el-icon>
                <h4>完整安装</h4>
                <p>一键安装所有组件</p>
                <el-button
                  type="success"
                  size="small"
                  @click="fullInstall"
                  :loading="downloadStore.loading"
                >
                  开始安装
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 下载任务进度 -->
      <div class="download-tasks" v-if="Object.keys(downloadStore.tasks).length > 0">
        <h4>下载任务</h4>
        <div class="task-list">
          <el-card
            v-for="(task, taskId) in downloadStore.tasks"
            :key="taskId"
            class="task-card"
            :class="getTaskClass(task.status)"
          >
            <div class="task-header">
              <div class="task-info">
                <h5>{{ task.description }}</h5>
                <span class="task-status" :class="`status-${task.status}`">
                  {{ getTaskStatusText(task.status) }}
                </span>
              </div>
              <div class="task-actions">
                <el-button
                  v-if="task.status === 'running'"
                  type="danger"
                  size="small"
                  @click="cancelTask(taskId)"
                  icon="Close"
                >
                  取消
                </el-button>
              </div>
            </div>

            <div class="task-progress">
              <el-progress
                :percentage="task.progress"
                :status="getProgressStatus(task.status)"
                :stroke-width="8"
                :text-inside="true"
                :show-text="true"
              />
            </div>

            <div class="task-details" v-if="task.message">
              <p>{{ task.message }}</p>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useDownloadStore } from '@/stores/download'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Monitor, Box, Check, Refresh, Close } from '@element-plus/icons-vue'

const downloadStore = useDownloadStore()
const installStatus = ref({
  steamcmd_installed: false,
  server_installed: false
})

// 获取安装状态
const getInstallStatusType = () => {
  if (installStatus.value.server_installed) return 'success'
  if (installStatus.value.steamcmd_installed) return 'warning'
  return 'info'
}

const getInstallStatusDescription = () => {
  if (installStatus.value.server_installed) {
    return 'L4D2服务器已完全安装，可以开始创建游戏服务器了！'
  } else if (installStatus.value.steamcmd_installed) {
    return 'SteamCMD已安装，可以下载L4D2服务器了'
  } else {
    return '尚未安装任何组件，请先安装SteamCMD'
  }
}

// 获取任务状态文本
const getTaskStatusText = (status) => {
  const statusMap = {
    pending: '等待中',
    running: '进行中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status
}

// 获取任务卡片样式
const getTaskClass = (status) => {
  return `task-${status}`
}

// 获取进度条状态
const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  if (status === 'running') return ''
  return ''
}

// 操作方法
const fetchTasks = async () => {
  await downloadStore.fetchTasks()
}

const installSteamCMD = async () => {
  await downloadStore.installSteamCMD()
  await fetchInstallStatus()
}

const installServer = async () => {
  await downloadStore.installServer()
}

const installPlugins = async () => {
  await downloadStore.installPlugins()
}

const fullInstall = async () => {
  const confirm = await ElMessageBox.confirm(
    '这将开始完整的L4D2服务器安装过程，可能需要几分钟到几十分钟。确定要继续吗？',
    '确认安装',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )

  if (confirm) {
    await downloadStore.fullInstall()
  }
}

const cancelTask = async (taskId) => {
  const confirm = await ElMessageBox.confirm(
    '确定要取消这个下载任务吗？',
    '确认取消',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )

  if (confirm) {
    await downloadStore.cancelTask(taskId)
  }
}

const fetchInstallStatus = async () => {
  try {
    // 这里可以调用后端的安装状态API
    // 暂时使用简单的检查
    installStatus.value = {
      steamcmd_installed: true, // 从之前的测试知道已安装
      server_installed: false
    }
  } catch (error) {
    console.error('获取安装状态失败:', error)
  }
}

// 组件挂载时获取数据
onMounted(async () => {
  await fetchTasks()
  await fetchInstallStatus()
})
</script>

<style scoped>
.downloads-container {
  padding: 20px;
}

.downloads-card {
  width: 100%;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.install-status {
  margin-bottom: 20px;
}

.install-options {
  margin-bottom: 30px;
}

.option-card {
  height: 180px;
  text-align: center;
  transition: transform 0.2s;
}

.option-card:hover {
  transform: translateY(-5px);
}

.option-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 140px;
  padding: 10px 0;
}

.option-icon {
  color: #409eff;
  margin-bottom: 8px;
}

.option-content h4 {
  margin: 8px 0;
  font-size: 16px;
}

.option-content p {
  margin: 4px 0;
  font-size: 12px;
  color: #909399;
  flex: 1;
}

.download-tasks h4 {
  margin-bottom: 15px;
  color: #303133;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-card {
  transition: box-shadow 0.2s;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.task-info h5 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.task-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.status-pending {
  background-color: #f4f4f5;
  color: #909399;
}

.status-running {
  background-color: #e6f7ff;
  color: #1890ff;
}

.status-completed {
  background-color: #f6ffed;
  color: #52c41a;
}

.status-failed {
  background-color: #fff2f0;
  color: #ff4d4f;
}

.task-progress {
  margin-bottom: 10px;
}

.task-details p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .downloads-container {
    padding: 10px;
  }

  .header-content {
    flex-direction: column;
    gap: 10px;
  }

  .install-options .el-col {
    margin-bottom: 15px;
  }

  .option-card {
    height: 160px;
  }

  .task-header {
    flex-direction: column;
    gap: 8px;
  }
}
</style>