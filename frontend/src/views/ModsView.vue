<template>
  <div class="mods-view">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card title="创意工坊物品管理" shadow="hover">
          <div class="search-section">
            <el-input
              v-model="searchQuery"
              placeholder="搜索创意工坊物品..."
              @input="handleSearch"
              clearable
              style="width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="showAddDialog = true" icon="Plus">
              添加物品
            </el-button>
          </div>

          <el-table :data="workshopItems" style="width: 100%" v-loading="loading">
            <el-table-column prop="title" label="物品名称" min-width="200" />
            <el-table-column prop="item_type" label="类型" width="100" />
            <el-table-column prop="author" label="作者" width="150" />
            <el-table-column label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.is_installed ? 'success' : 'warning'">
                  {{ scope.row.is_installed ? '已安装' : '未安装' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="150">
              <template #default="scope">
                <el-button-group>
                  <el-button
                    size="small"
                    @click="downloadItem(scope.row)"
                    :disabled="scope.row.is_installed"
                    type="primary"
                  >
                    下载
                  </el-button>
                  <el-button
                    size="small"
                    @click="uninstallItem(scope.row)"
                    :disabled="!scope.row.is_installed"
                    type="danger"
                  >
                    卸载
                  </el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加物品对话框 -->
    <el-dialog
      v-model="showAddDialog"
      title="添加创意工坊物品"
      width="500px"
      @close="resetAddForm"
    >
      <el-form
        ref="addFormRef"
        :model="addForm"
        :rules="addRules"
        label-width="100px"
      >
        <el-form-item label="物品ID" prop="workshopId">
          <el-input
            v-model="addForm.workshopId"
            placeholder="请输入创意工坊物品ID"
          />
        </el-form-item>
        <el-form-item label="物品名称" prop="title">
          <el-input
            v-model="addForm.title"
            placeholder="请输入物品名称"
          />
        </el-form-item>
        <el-form-item label="类型" prop="itemType">
          <el-select v-model="addForm.itemType" placeholder="选择物品类型">
            <el-option label="地图" value="map" />
            <el-option label="Mod" value="mod" />
            <el-option label="插件" value="plugin" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="handleAddItem" :loading="addLoading">
            添加
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import api from '@/api/index.js'

const workshopItems = ref([])
const loading = ref(false)
const searchQuery = ref('')
const showAddDialog = ref(false)
const addLoading = ref(false)
const addFormRef = ref()

const addForm = reactive({
  workshopId: '',
  title: '',
  itemType: ''
})

const addRules = {
  workshopId: [{ required: true, message: '请输入物品ID', trigger: 'blur' }],
  title: [{ required: true, message: '请输入物品名称', trigger: 'blur' }],
  itemType: [{ required: true, message: '请选择物品类型', trigger: 'change' }]
}

const loadWorkshopItems = async () => {
  loading.value = true
  try {
    const response = await api.get('/mods/workshop')
    workshopItems.value = response.data
  } catch (error) {
    ElMessage.error('加载创意工坊物品失败')
    console.error('加载物品失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 实现搜索功能
  console.log('搜索:', searchQuery.value)
}

const downloadItem = async (item) => {
  try {
    const response = await api.post('/mods/workshop/download', {
      workshop_ids: [item.workshop_id]
    })

    if (response.data.success) {
      ElMessage.success('开始下载物品')
      loadWorkshopItems()
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    ElMessage.error('下载失败')
    console.error('下载失败:', error)
  }
}

const uninstallItem = async (item) => {
  try {
    await api.delete(`/mods/workshop/${item.workshop_id}`)
    ElMessage.success('物品已卸载')
    loadWorkshopItems()
  } catch (error) {
    ElMessage.error('卸载失败')
    console.error('卸载失败:', error)
  }
}

const handleAddItem = async () => {
  try {
    await addFormRef.value.validate()
    addLoading.value = true

    // 这里应该调用后端API添加物品
    // 暂时只是显示成功消息
    ElMessage.success('物品添加成功')
    showAddDialog.value = false
    loadWorkshopItems()
  } catch (error) {
    if (error !== 'validation') {
      ElMessage.error('添加物品失败')
      console.error('添加物品失败:', error)
    }
  } finally {
    addLoading.value = false
  }
}

const resetAddForm = () => {
  addFormRef.value?.resetFields()
  Object.assign(addForm, {
    workshopId: '',
    title: '',
    itemType: ''
  })
}

onMounted(() => {
  loadWorkshopItems()
})
</script>

<style scoped>
.mods-view {
  padding: 20px;
}

.search-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dialog-footer {
  text-align: right;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .mods-view {
    padding: 10px;
  }

  .search-section {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
}
</style>
