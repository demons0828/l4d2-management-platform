<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <!-- 服务器状态卡片 -->
      <el-col :span="24" :md="12" :lg="6">
        <el-card class="stat-card l4d2-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon server-icon l4d2-icon">
              <el-icon size="32"><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ serverStats.total }}</h3>
              <p>服务器总数</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 运行中服务器 -->
      <el-col :span="24" :md="12" :lg="6">
        <el-card class="stat-card l4d2-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon running-icon l4d2-icon">
              <el-icon size="32"><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ serverStats.running }}</h3>
              <p>运行中</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 房间数量 -->
      <el-col :span="24" :md="12" :lg="6">
        <el-card class="stat-card l4d2-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon room-icon l4d2-icon">
              <el-icon size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ roomStats.total }}</h3>
              <p>活跃房间</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 下载任务 -->
      <el-col :span="24" :md="12" :lg="6">
        <el-card class="stat-card l4d2-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon download-icon l4d2-icon">
              <el-icon size="32"><Download /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ downloadStats.active }}</h3>
              <p>下载任务</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24" :md="12">
        <el-card title="快速操作" shadow="hover">
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/servers')" icon="Monitor">
              管理服务器
            </el-button>
            <el-button type="success" @click="$router.push('/mods')" icon="Box">
              Mod管理
            </el-button>
            <el-button type="info" @click="$router.push('/rooms')" icon="User">
              房间管理
            </el-button>
            <el-button type="warning" @click="$router.push('/downloads')" icon="Download">
              下载管理
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="24" :md="12">
        <el-card title="系统状态" shadow="hover">
          <div class="system-status">
            <div class="status-item">
              <span>后端服务:</span>
              <el-tag type="success">正常</el-tag>
            </div>
            <div class="status-item">
              <span>数据库:</span>
              <el-tag type="success">正常</el-tag>
            </div>
            <div class="status-item">
              <span>Steam API:</span>
              <el-tag :type="steamApiStatus ? 'success' : 'warning'">
                {{ steamApiStatus ? '正常' : '未配置' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card title="最近活动" style="margin-top: 20px" shadow="hover">
      <el-timeline>
        <el-timeline-item
          v-for="activity in recentActivities"
          :key="activity.id"
          :timestamp="activity.timestamp"
        >
          {{ activity.description }}
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Monitor, VideoPlay, User, Download } from '@element-plus/icons-vue'
import api from '@/api/index.js'

const serverStats = ref({
  total: 0,
  running: 0
})

const roomStats = ref({
  total: 0
})

const downloadStats = ref({
  active: 0
})

const steamApiStatus = ref(false)

const recentActivities = ref([
  {
    id: 1,
    description: '系统启动',
    timestamp: '2024-01-01 00:00:00'
  }
])

const loadDashboardData = async () => {
  try {
    // 加载服务器统计
    const serversResponse = await api.get('/servers')
    const servers = serversResponse.data
    serverStats.value.total = servers.length
    serverStats.value.running = servers.filter(s => s.status === 'running').length

    // 加载房间统计
    const roomsResponse = await api.get('/rooms')
    roomStats.value.total = roomsResponse.data.length

    // 加载下载统计
    const downloadsResponse = await api.get('/downloads')
    downloadStats.value.active = downloadsResponse.data.filter(d => d.status === 'downloading').length

  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card {
  height: 120px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
  position: relative;
  z-index: 1;
}

.stat-icon {
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-icon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover .stat-icon::before {
  opacity: 1;
}

.server-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.running-icon {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  color: white;
  box-shadow: 0 8px 20px rgba(103, 194, 58, 0.3);
}

.room-icon {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
  color: white;
  box-shadow: 0 8px 20px rgba(230, 162, 60, 0.3);
}

.download-icon {
  background: linear-gradient(135deg, #f56c6c, #f78989);
  color: white;
  box-shadow: 0 8px 20px rgba(245, 108, 108, 0.3);
}

.stat-info h3 {
  margin: 0 0 5px 0;
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-info p {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
  font-weight: 500;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.quick-actions .el-button {
  height: 45px;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: none;
}

.quick-actions .el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.quick-actions .el-button:hover::before {
  left: 100%;
}

.quick-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.status-item:last-child {
  border-bottom: none;
}

/* 时间线样式优化 */
.el-timeline-item {
  animation: slideInLeft 0.5s ease-out;
  animation-fill-mode: both;
}

.el-timeline-item:nth-child(1) { animation-delay: 0.1s; }
.el-timeline-item:nth-child(2) { animation-delay: 0.2s; }
.el-timeline-item:nth-child(3) { animation-delay: 0.3s; }

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }

  .stat-card {
    height: 100px;
    margin-bottom: 15px;
  }

  .stat-content {
    flex-direction: column;
    text-align: center;
    padding: 15px;
  }

  .stat-icon {
    margin-right: 0;
    margin-bottom: 10px;
    width: 50px;
    height: 50px;
  }

  .stat-info h3 {
    font-size: 20px;
  }

  .quick-actions {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .quick-actions .el-button {
    height: 50px;
    font-size: 16px;
  }
}

/* 脉冲动画效果 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
  }
}

.stat-card:hover .server-icon {
  animation: pulse 2s infinite;
}

/* L4D2 卡片样式 */
.l4d2-card {
  background: var(--l4d2-bg-gradient);
  border: 2px solid var(--l4d2-accent);
  position: relative;
  overflow: hidden;
}

.l4d2-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--l4d2-gradient);
}

.l4d2-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(139, 69, 19, 0.3);
}

.l4d2-icon::before {
  background: linear-gradient(45deg, rgba(205, 133, 63, 0.2), rgba(210, 105, 30, 0.2));
}
</style>
