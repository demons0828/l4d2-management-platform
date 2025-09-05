<template>
  <div id="app">
    <el-container style="height: 100vh">
      <!-- 侧边栏 -->
      <el-aside width="200px" class="sidebar">
        <el-menu
          :default-active="$route.path"
          class="el-menu-vertical-demo l4d2-menu"
          @select="handleSelect"
          background-color="transparent"
          text-color="#F4A460"
          active-text-color="#CD853F"
        >
          <el-menu-item index="/dashboard" class="l4d2-menu-item">
            <el-icon><House /></el-icon>
            <template #title>仪表板</template>
          </el-menu-item>
          <el-menu-item index="/servers" class="l4d2-menu-item">
            <el-icon><Monitor /></el-icon>
            <template #title>服务器管理</template>
          </el-menu-item>
          <el-menu-item index="/mods" class="l4d2-menu-item">
            <el-icon><Box /></el-icon>
            <template #title>Mod管理</template>
          </el-menu-item>
          <el-menu-item index="/rooms" class="l4d2-menu-item">
            <el-icon><User /></el-icon>
            <template #title>房间管理</template>
          </el-menu-item>
          <el-menu-item index="/downloads" class="l4d2-menu-item">
            <el-icon><Download /></el-icon>
            <template #title>下载管理</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-container>
        <!-- 头部 -->
        <el-header class="header">
          <div class="header-left">
            <h3>L4D2 管理平台</h3>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="el-dropdown-link">
                {{ user?.username || '未登录' }}
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>登出</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主要内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  House,
  Monitor,
  Box,
  User,
  Download,
  ArrowDown
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const user = computed(() => userStore.user)

const handleSelect = (key) => {
  router.push(key)
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      // TODO: 实现个人资料页面
      break
    case 'logout':
      userStore.logout()
      ElMessage.success('已登出')
      router.push('/login')
      break
  }
}

onMounted(() => {
  // 检查用户登录状态
  if (!userStore.isLoggedIn) {
    router.push('/login')
  }
})
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.sidebar {
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  border-right: none;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-left h3 {
  margin: 0;
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.5rem;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-right {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  cursor: pointer;
  color: #667eea;
  display: flex;
  align-items: center;
  font-weight: 500;
  transition: color 0.3s ease;
}

.el-dropdown-link:hover {
  color: #764ba2;
}

.main-content {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
  min-height: calc(100vh - 60px);
}

.el-menu-item {
  transition: all 0.3s ease;
  border-radius: 8px;
  margin: 4px 8px;
}

.el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.el-menu-item.is-active {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: linear-gradient(to bottom, #667eea, #764ba2);
  border-radius: 0 4px 4px 0;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(45deg, #667eea, #764ba2);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(45deg, #764ba2, #667eea);
}

/* L4D2 主题菜单样式 */
.l4d2-menu {
  border: none;
  background: rgba(139, 69, 19, 0.1);
  backdrop-filter: blur(10px);
}

.l4d2-menu-item {
  border-radius: 8px;
  margin: 4px 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.l4d2-menu-item:hover {
  background: rgba(205, 133, 63, 0.2);
  transform: translateX(5px);
}

.l4d2-menu-item.is-active {
  background: var(--l4d2-gradient);
  color: white;
  box-shadow: 0 4px 15px rgba(139, 69, 19, 0.3);
}

.l4d2-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 4px;
  background: linear-gradient(to bottom, #CD853F, #D2691E);
  border-radius: 0 4px 4px 0;
}
</style>
