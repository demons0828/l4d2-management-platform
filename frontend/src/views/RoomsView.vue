<template>
  <div class="rooms-view">
    <el-row :gutter="20">
      <el-col :span="24" :md="12">
        <el-card title="我的房间" shadow="hover">
          <div class="room-section">
            <el-button type="primary" @click="showCreateDialog = true" icon="Plus" style="margin-bottom: 20px">
              创建房间
            </el-button>

            <div v-if="myRooms.length === 0" class="no-rooms">
              <p>您还没有创建房间</p>
            </div>

            <div v-else class="room-list">
              <el-card
                v-for="room in myRooms"
                :key="room.id"
                class="room-card"
                shadow="hover"
              >
                <div class="room-header">
                  <h4>{{ room.name }}</h4>
                  <el-tag :type="room.is_active ? 'success' : 'danger'">
                    {{ room.is_active ? '活跃' : '关闭' }}
                  </el-tag>
                </div>
                <div class="room-info">
                  <p><strong>服务器:</strong> {{ room.server_id }}</p>
                  <p><strong>地图:</strong> {{ room.current_map }}</p>
                  <p><strong>模式:</strong> {{ room.game_mode }}</p>
                  <p><strong>玩家:</strong> {{ room.current_players }}/{{ room.max_players }}</p>
                </div>
                <div class="room-actions">
                  <el-button-group>
                    <el-button size="small" @click="joinRoom(room)" type="primary">
                      加入
                    </el-button>
                    <el-button size="small" @click="editRoom(room)" type="warning">
                      编辑
                    </el-button>
                    <el-button size="small" @click="deleteRoom(room)" type="danger">
                      删除
                    </el-button>
                  </el-button-group>
                </div>
              </el-card>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="24" :md="12">
        <el-card title="加入房间" shadow="hover">
          <div class="join-section">
            <el-input
              v-model="joinCode"
              placeholder="输入房间邀请码"
              clearable
              style="margin-bottom: 10px"
            />
            <el-button type="success" @click="joinByCode" :disabled="!joinCode" block>
              加入房间
            </el-button>

            <el-divider>或</el-divider>

            <div class="public-rooms">
              <h5>公开房间</h5>
              <div v-if="publicRooms.length === 0" class="no-rooms">
                <p>暂无公开房间</p>
              </div>
              <div v-else class="room-list">
                <el-card
                  v-for="room in publicRooms"
                  :key="room.id"
                  class="room-card"
                  shadow="hover"
                >
                  <div class="room-header">
                    <h4>{{ room.name }}</h4>
                    <el-tag type="info">公开</el-tag>
                  </div>
                  <div class="room-info">
                    <p><strong>地图:</strong> {{ room.current_map }}</p>
                    <p><strong>模式:</strong> {{ room.game_mode }}</p>
                    <p><strong>玩家:</strong> {{ room.current_players }}/{{ room.max_players }}</p>
                  </div>
                  <div class="room-actions">
                    <el-button @click="joinRoom(room)" type="primary" block>
                      加入房间
                    </el-button>
                  </div>
                </el-card>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建房间对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建房间"
      width="600px"
      @close="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="房间名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入房间名称" />
        </el-form-item>

        <el-form-item label="服务器" prop="serverId">
          <el-select v-model="createForm.serverId" placeholder="选择服务器">
            <el-option
              v-for="server in servers"
              :key="server.id"
              :label="server.name"
              :value="server.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="最大玩家数" prop="maxPlayers">
          <el-input-number
            v-model="createForm.maxPlayers"
            :min="1"
            :max="32"
            controls-position="right"
          />
        </el-form-item>

        <el-form-item label="游戏模式" prop="gameMode">
          <el-select v-model="createForm.gameMode" placeholder="选择游戏模式">
            <el-option label="合作模式" value="coop" />
            <el-option label="对抗模式" value="versus" />
            <el-option label="生存模式" value="survival" />
            <el-option label="清道夫模式" value="scavenge" />
          </el-select>
        </el-form-item>

        <el-form-item label="初始地图" prop="currentMap">
          <el-select v-model="createForm.currentMap" placeholder="选择初始地图">
            <el-option label="酒店" value="c1m1_hotel" />
            <el-option label="小巷" value="c1m2_streets" />
            <el-option label="地铁" value="c1m3_mall" />
            <el-option label="天台" value="c1m4_atrium" />
          </el-select>
        </el-form-item>

        <el-form-item label="房间类型" prop="isPrivate">
          <el-radio-group v-model="createForm.isPrivate">
            <el-radio :label="false">公开房间</el-radio>
            <el-radio :label="true">私密房间</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="createForm.isPrivate" label="密码" prop="password">
          <el-input
            v-model="createForm.password"
            type="password"
            placeholder="设置房间密码"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreateRoom" :loading="createLoading">
            创建
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

const myRooms = ref([])
const publicRooms = ref([])
const servers = ref([])
const joinCode = ref('')
const showCreateDialog = ref(false)
const createLoading = ref(false)
const createFormRef = ref()

const createForm = reactive({
  name: '',
  serverId: null,
  maxPlayers: 8,
  gameMode: 'coop',
  currentMap: 'c1m1_hotel',
  isPrivate: false,
  password: ''
})

const createRules = {
  name: [{ required: true, message: '请输入房间名称', trigger: 'blur' }],
  serverId: [{ required: true, message: '请选择服务器', trigger: 'change' }],
  maxPlayers: [{ required: true, message: '请输入最大玩家数', trigger: 'blur' }],
  gameMode: [{ required: true, message: '请选择游戏模式', trigger: 'change' }],
  currentMap: [{ required: true, message: '请选择初始地图', trigger: 'change' }]
}

const loadRooms = async () => {
  try {
    const [myRoomsResponse, publicRoomsResponse] = await Promise.all([
      api.get('/rooms'),
      api.get('/rooms') // 这里应该有过滤公开房间的API
    ])

    myRooms.value = myRoomsResponse.data.filter(room => room.creator_id === 1) // 临时过滤
    publicRooms.value = publicRoomsResponse.data.filter(room => !room.is_private)
  } catch (error) {
    ElMessage.error('加载房间列表失败')
    console.error('加载房间失败:', error)
  }
}

const loadServers = async () => {
  try {
    const response = await api.get('/servers')
    servers.value = response.data
  } catch (error) {
    console.error('加载服务器失败:', error)
  }
}

const handleCreateRoom = async () => {
  try {
    await createFormRef.value.validate()
    createLoading.value = true

    const response = await api.post('/rooms', createForm)

    ElMessage.success('房间创建成功')
    showCreateDialog.value = false
    loadRooms()
  } catch (error) {
    if (error !== 'validation') {
      ElMessage.error('创建房间失败')
      console.error('创建房间失败:', error)
    }
  } finally {
    createLoading.value = false
  }
}

const joinRoom = async (room) => {
  try {
    if (room.is_private) {
      // 处理私密房间
      const password = await ElMessageBox.prompt('请输入房间密码', '加入房间', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.+/,
        inputErrorMessage: '密码不能为空'
      })

      await api.post(`/rooms/${room.id}/join`, { password: password.value })
    } else {
      await api.post(`/rooms/${room.id}/join`)
    }

    ElMessage.success('成功加入房间')
    loadRooms()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('加入房间失败')
      console.error('加入房间失败:', error)
    }
  }
}

const joinByCode = async () => {
  // 这里应该实现通过邀请码加入房间的逻辑
  ElMessage.info('邀请码功能开发中')
}

const editRoom = (room) => {
  // 这里应该实现编辑房间的逻辑
  ElMessage.info('编辑功能开发中')
}

const deleteRoom = async (room) => {
  try {
    await ElMessageBox.confirm('确定要删除这个房间吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await api.delete(`/rooms/${room.id}`)
    ElMessage.success('房间删除成功')
    loadRooms()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除房间失败')
      console.error('删除房间失败:', error)
    }
  }
}

const resetCreateForm = () => {
  createFormRef.value?.resetFields()
  Object.assign(createForm, {
    name: '',
    serverId: null,
    maxPlayers: 8,
    gameMode: 'coop',
    currentMap: 'c1m1_hotel',
    isPrivate: false,
    password: ''
  })
}

onMounted(() => {
  loadRooms()
  loadServers()
})
</script>

<style scoped>
.rooms-view {
  padding: 20px;
}

.room-section, .join-section {
  height: 100%;
}

.no-rooms {
  text-align: center;
  color: #909399;
  padding: 40px 20px;
}

.room-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.room-card {
  margin-bottom: 0;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.room-header h4 {
  margin: 0;
}

.room-info p {
  margin: 5px 0;
  color: #606266;
  font-size: 14px;
}

.room-actions {
  margin-top: 15px;
}

.public-rooms h5 {
  margin: 20px 0 15px 0;
  color: #303133;
}

.dialog-footer {
  text-align: right;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .rooms-view {
    padding: 10px;
  }

  .room-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>
