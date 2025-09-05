<template>
  <div class="servers-view">
    <div class="page-header">
      <h2>服务器管理</h2>
      <div class="header-buttons">
        <el-button type="primary" @click="showCreateDialog = true" icon="Plus">
          添加服务器
        </el-button>
        <el-button type="success" @click="showInstallDialog = true" icon="Download">
          安装服务器
        </el-button>
        <el-button type="info" @click="checkInstallStatus" icon="Info">
          检查安装状态
        </el-button>
      </div>
    </div>

    <!-- 服务器列表 -->
    <el-card shadow="hover">
      <el-table :data="servers" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="服务器名称" width="200" />
        <el-table-column prop="host" label="主机" width="150" />
        <el-table-column prop="port" label="端口" width="100" />
        <el-table-column prop="current_map" label="当前地图" width="150" />
        <el-table-column prop="game_mode" label="游戏模式" width="120" />
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="200">
          <template #default="scope">
            <el-button-group>
              <el-button
                size="small"
                @click="controlServer(scope.row.id, 'start')"
                :disabled="scope.row.status === 'running'"
                type="success"
              >
                启动
              </el-button>
              <el-button
                size="small"
                @click="controlServer(scope.row.id, 'stop')"
                :disabled="scope.row.status === 'stopped'"
                type="danger"
              >
                停止
              </el-button>
              <el-button
                size="small"
                @click="controlServer(scope.row.id, 'restart')"
                type="warning"
              >
                重启
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; text-align: center"
      />
    </el-card>

    <!-- 添加服务器对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="添加服务器"
      width="600px"
      @close="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="服务器名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入服务器名称" />
        </el-form-item>

        <el-form-item label="主机地址" prop="host">
          <el-input v-model="createForm.host" placeholder="localhost" />
        </el-form-item>

        <el-form-item label="端口" prop="port">
          <el-input-number
            v-model="createForm.port"
            :min="1024"
            :max="65535"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="最大玩家数" prop="max_players">
          <el-input-number
            v-model="createForm.max_players"
            :min="1"
            :max="32"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="游戏模式" prop="game_mode">
          <el-select v-model="createForm.game_mode" placeholder="选择游戏模式">
            <el-option label="合作模式" value="coop" />
            <el-option label="对抗模式" value="versus" />
            <el-option label="生存模式" value="survival" />
            <el-option label="清道夫模式" value="scavenge" />
          </el-select>
        </el-form-item>

        <el-form-item label="初始地图" prop="current_map">
          <el-select v-model="createForm.current_map" placeholder="选择初始地图">
            <el-option label="酒店" value="c1m1_hotel" />
            <el-option label="小巷" value="c1m2_streets" />
            <el-option label="地铁" value="c1m3_mall" />
            <el-option label="天台" value="c1m4_atrium" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreateServer" :loading="createLoading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 安装服务器对话框 -->
    <el-dialog
      v-model="showInstallDialog"
      title="安装L4D2服务器"
      width="600px"
    >
      <div class="install-status" v-if="Object.keys(installStatus).length > 0">
        <el-alert
          :title="`SteamCMD: ${installStatus.steamcmd_installed ? '已安装' : '未安装'} | 服务器: ${installStatus.server_installed ? '已安装' : '未安装'}`"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        />
      </div>

      <el-form label-width="120px" @submit.prevent>
        <el-form-item label="安装类型">
          <el-select v-model="installForm.installType" placeholder="选择安装类型">
            <el-option label="完整安装（推荐）" value="full" />
            <el-option label="仅安装SteamCMD" value="steamcmd" />
            <el-option label="仅安装服务器" value="server" />
            <el-option label="仅安装插件" value="plugins" />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="installForm.installType !== 'steamcmd'"
          label="Steam用户名"
        >
          <el-input
            v-model="installForm.steamUsername"
            placeholder="可选，用于下载创意工坊内容"
          />
        </el-form-item>

        <el-form-item
          v-if="installForm.installType !== 'steamcmd'"
          label="Steam密码"
        >
          <el-input
            v-model="installForm.steamPassword"
            type="password"
            placeholder="可选"
            show-password
          />
        </el-form-item>

        <el-alert
          title="注意事项"
          description="如果不提供Steam账号，将使用匿名账户下载，某些内容可能无法下载。建议使用专用Steam账户。"
          type="warning"
          :closable="false"
          style="margin-top: 20px"
        />
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInstallDialog = false">取消</el-button>
          <el-button type="primary" @click="handleInstallServer" :loading="installLoading">
            开始安装
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api/index.js'

const servers = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const showCreateDialog = ref(false)
const createLoading = ref(false)
const createFormRef = ref()

// 安装相关变量
const showInstallDialog = ref(false)
const installLoading = ref(false)
const installStatus = ref({})
const installForm = reactive({
  steamUsername: '',
  steamPassword: '',
  installType: 'full' // full, steamcmd, server, plugins
})

const createForm = reactive({
  name: '',
  host: 'localhost',
  port: 27015,
  max_players: 8,
  game_mode: 'coop',
  current_map: 'c1m1_hotel'
})

const createRules = {
  name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口号', trigger: 'blur' }],
  max_players: [{ required: true, message: '请输入最大玩家数', trigger: 'blur' }],
  game_mode: [{ required: true, message: '请选择游戏模式', trigger: 'change' }],
  current_map: [{ required: true, message: '请选择初始地图', trigger: 'change' }]
}

const loadServers = async () => {
  loading.value = true
  try {
    const response = await api.get('/servers', {
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      }
    })
    servers.value = response.data
    total.value = response.data.length // 简化处理
  } catch (error) {
    ElMessage.error('加载服务器列表失败')
    console.error('加载服务器失败:', error)
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const statusMap = {
    running: 'success',
    stopped: 'danger',
    starting: 'warning',
    stopping: 'warning',
    error: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    running: '运行中',
    stopped: '已停止',
    starting: '启动中',
    stopping: '停止中',
    error: '错误'
  }
  return statusMap[status] || status
}

const controlServer = async (serverId, action) => {
  try {
    const confirmMessage = {
      start: '确定要启动服务器吗？',
      stop: '确定要停止服务器吗？',
      restart: '确定要重启服务器吗？'
    }

    await ElMessageBox.confirm(confirmMessage[action], '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await api.post(`/servers/${serverId}/control`, {
      action: action
    })

    if (response.data.success) {
      ElMessage.success(response.data.message)
      loadServers()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
      console.error('控制服务器失败:', error)
    }
  }
}

const handleCreateServer = async () => {
  try {
    await createFormRef.value.validate()
    createLoading.value = true

    const response = await api.post('/servers', createForm)

    ElMessage.success('服务器创建成功')
    showCreateDialog.value = false
    loadServers()
  } catch (error) {
    if (error !== 'validation') {
      ElMessage.error('创建服务器失败')
      console.error('创建服务器失败:', error)
    }
  } finally {
    createLoading.value = false
  }
}

const resetCreateForm = () => {
  createFormRef.value?.resetFields()
  Object.assign(createForm, {
    name: '',
    host: 'localhost',
    port: 27015,
    max_players: 8,
    game_mode: 'coop',
    current_map: 'c1m1_hotel'
  })
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadServers()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadServers()
}

// 安装相关方法
const checkInstallStatus = async () => {
  try {
    const response = await api.get('/servers/install/status')
    installStatus.value = response.data

    ElMessage.info(`SteamCMD: ${response.data.steamcmd_installed ? '已安装' : '未安装'}, 服务器: ${response.data.server_installed ? '已安装' : '未安装'}`)
  } catch (error) {
    ElMessage.error('检查安装状态失败')
    console.error('检查安装状态失败:', error)
  }
}

const handleInstallServer = async () => {
  installLoading.value = true
  try {
    let endpoint = '/servers/install/'
    let params = {}

    // 根据安装类型选择不同的端点
    switch (installForm.installType) {
      case 'steamcmd':
        endpoint += 'steamcmd'
        break
      case 'server':
        endpoint += 'server'
        if (installForm.steamUsername && installForm.steamPassword) {
          params = {
            steam_username: installForm.steamUsername,
            steam_password: installForm.steamPassword
          }
        }
        break
      case 'plugins':
        endpoint += 'plugins'
        if (installForm.steamUsername && installForm.steamPassword) {
          params = {
            steam_username: installForm.steamUsername,
            steam_password: installForm.steamPassword
          }
        }
        break
      case 'full':
        endpoint += 'full'
        if (installForm.steamUsername && installForm.steamPassword) {
          params = {
            steam_username: installForm.steamUsername,
            steam_password: installForm.steamPassword
          }
        }
        break
    }

    const response = await api.post(endpoint, null, { params })

    if (response.data.success) {
      ElMessage.success(response.data.message)
      showInstallDialog.value = false
      checkInstallStatus()
    } else {
      ElMessage.error(response.data.message || '安装失败')
    }
  } catch (error) {
    ElMessage.error('安装过程中出现错误')
    console.error('安装失败:', error)
  } finally {
    installLoading.value = false
  }
}

onMounted(() => {
  loadServers()
  checkInstallStatus()
})
</script>

<style scoped>
.servers-view {
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

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.7));
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.page-header h2 {
  margin: 0;
  color: #2c3e50;
  font-weight: 700;
  font-size: 1.8rem;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-buttons {
  display: flex;
  gap: 12px;
}

.header-buttons .el-button {
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: none;
}

.header-buttons .el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.header-buttons .el-button:hover::before {
  left: 100%;
}

.header-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.dialog-footer {
  text-align: right;
}

/* 表格样式优化 */
.el-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.el-table th {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-weight: 600;
  border: none;
}

.el-table td {
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  transition: background-color 0.3s ease;
}

.el-table tr:hover td {
  background-color: rgba(102, 126, 234, 0.05);
}

.el-button-group .el-button {
  border-radius: 8px !important;
  margin: 0 2px;
  transition: all 0.3s ease;
}

.el-button-group .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 对话框样式优化 */
.el-dialog {
  border-radius: 16px;
  overflow: hidden;
}

.el-dialog__header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  margin: 0;
  padding: 20px;
}

.el-dialog__title {
  font-weight: 600;
}

.el-dialog__body {
  padding: 24px;
}

.el-form-item__label {
  font-weight: 600;
  color: #2c3e50;
}

/* 分页样式优化 */
.el-pagination {
  margin-top: 30px;
  justify-content: center;
}

.el-pagination .el-pager li {
  transition: all 0.3s ease;
}

.el-pagination .el-pager li:hover {
  transform: scale(1.1);
}

.el-pagination .el-pager li.is-active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-color: #667eea;
}

/* 表单样式优化 */
.el-input__wrapper {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.el-input__wrapper:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.el-select .el-input__wrapper {
  border-radius: 8px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .servers-view {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
    padding: 15px;
  }

  .page-header h2 {
    text-align: center;
    font-size: 1.5rem;
  }

  .header-buttons {
    flex-direction: column;
    width: 100%;
    gap: 8px;
  }

  .header-buttons .el-button {
    width: 100%;
    height: 45px;
  }

  .el-table {
    font-size: 14px;
  }

  .el-button-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .el-button-group .el-button {
    width: 100%;
    margin: 0;
  }
}

/* 加载状态动画 */
@keyframes shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

.el-table__row {
  animation: slideInUp 0.5s ease-out;
  animation-fill-mode: both;
}

.el-table__row:nth-child(1) { animation-delay: 0.1s; }
.el-table__row:nth-child(2) { animation-delay: 0.2s; }
.el-table__row:nth-child(3) { animation-delay: 0.3s; }

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
