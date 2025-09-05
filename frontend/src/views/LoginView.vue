<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="login-header">
          <h2>L4D2 管理平台</h2>
          <p>请选择登录方式</p>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <!-- Steam登录 -->
        <el-tab-pane label="Steam登录" name="steam">
          <el-form
            ref="steamFormRef"
            :model="steamForm"
            :rules="steamRules"
            label-width="80px"
            @submit.prevent="handleSteamLogin"
          >
            <el-form-item label="Steam ID" prop="steamId">
              <el-input
                v-model="steamForm.steamId"
                placeholder="请输入您的Steam ID"
                :prefix-icon="User"
                clearable
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                @click="handleSteamLogin"
                style="width: 100%"
              >
                Steam登录
              </el-button>
            </el-form-item>
          </el-form>

          <div class="login-footer">
            <p>如何获取Steam ID？</p>
            <ol>
              <li>访问 <a href="https://steamid.io/" target="_blank">steamid.io</a></li>
              <li>输入您的Steam个人资料URL</li>
              <li>复制Steam64 ID</li>
            </ol>
          </div>
        </el-tab-pane>

        <!-- 账号密码登录 -->
        <el-tab-pane label="账号登录" name="password">
          <el-tabs v-model="passwordTab" type="card">
            <!-- 登录 -->
            <el-tab-pane label="登录" name="login">
              <el-form
                ref="loginFormRef"
                :model="loginForm"
                :rules="loginRules"
                label-width="80px"
                @submit.prevent="handlePasswordLogin"
              >
                <el-form-item label="邮箱" prop="email">
                  <el-input
                    v-model="loginForm.email"
                    placeholder="请输入邮箱"
                    :prefix-icon="Message"
                    clearable
                  />
                </el-form-item>

                <el-form-item label="密码" prop="password">
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    placeholder="请输入密码"
                    :prefix-icon="Lock"
                    clearable
                    show-password
                  />
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    :loading="loading"
                    @click="handlePasswordLogin"
                    style="width: 100%"
                  >
                    登录
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <!-- 注册 -->
            <el-tab-pane label="注册" name="register">
              <el-form
                ref="registerFormRef"
                :model="registerForm"
                :rules="registerRules"
                label-width="80px"
                @submit.prevent="handleRegister"
              >
                <el-form-item label="用户名" prop="username">
                  <el-input
                    v-model="registerForm.username"
                    placeholder="请输入用户名"
                    :prefix-icon="User"
                    clearable
                  />
                </el-form-item>

                <el-form-item label="邮箱" prop="email">
                  <el-input
                    v-model="registerForm.email"
                    placeholder="请输入邮箱"
                    :prefix-icon="Message"
                    clearable
                  />
                </el-form-item>

                <el-form-item label="密码" prop="password">
                  <el-input
                    v-model="registerForm.password"
                    type="password"
                    placeholder="请输入密码"
                    :prefix-icon="Lock"
                    clearable
                    show-password
                  />
                </el-form-item>

                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input
                    v-model="registerForm.confirmPassword"
                    type="password"
                    placeholder="请再次输入密码"
                    :prefix-icon="Lock"
                    clearable
                    show-password
                  />
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    :loading="loading"
                    @click="handleRegister"
                    style="width: 100%"
                  >
                    注册
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { User, Message, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

// 标签页状态
const activeTab = ref('steam')
const passwordTab = ref('login')

// 表单引用
const steamFormRef = ref()
const loginFormRef = ref()
const registerFormRef = ref()
const loading = ref(false)

// Steam登录表单
const steamForm = reactive({
  steamId: ''
})

// 账号密码登录表单
const loginForm = reactive({
  email: '',
  password: ''
})

// 注册表单
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// Steam登录验证规则
const steamRules = {
  steamId: [
    { required: true, message: '请输入Steam ID', trigger: 'blur' },
    {
      pattern: /^\d{17}$/,
      message: 'Steam ID格式不正确（应为17位数字）',
      trigger: 'blur'
    }
  ]
}

// 账号密码登录验证规则
const loginRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

// 注册验证规则
const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度在2到20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 处理标签页切换
const handleTabClick = (tab) => {
  // 切换到账号密码登录时，默认显示登录标签
  if (tab.props.name === 'password') {
    passwordTab.value = 'login'
  }
}

// Steam登录处理
const handleSteamLogin = async () => {
  try {
    await steamFormRef.value.validate()
    loading.value = true

    const result = await userStore.login(steamForm.steamId)

    if (result.success) {
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('Steam登录验证失败:', error)
  } finally {
    loading.value = false
  }
}

// 账号密码登录处理
const handlePasswordLogin = async () => {
  try {
    await loginFormRef.value.validate()
    loading.value = true

    const result = await userStore.loginWithPassword({
      email: loginForm.email,
      password: loginForm.password
    })

    if (result.success) {
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('账号密码登录验证失败:', error)
  } finally {
    loading.value = false
  }
}

// 注册处理
const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    loading.value = true

    const result = await userStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password
    })

    if (result.success) {
      ElMessage.success('注册成功')
      // 注册成功后自动切换到登录标签
      passwordTab.value = 'login'
      // 清空登录表单并填入注册的邮箱
      loginForm.email = registerForm.email
      loginForm.password = ''
      // 清空注册表单
      Object.keys(registerForm).forEach(key => {
        registerForm[key] = ''
      })
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('注册验证失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 10px;
}

.login-header {
  text-align: center;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.login-header p {
  margin: 0;
  color: #606266;
}

.login-footer {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.login-footer p {
  margin: 0 0 10px 0;
  font-weight: bold;
  color: #303133;
}

.login-footer ol {
  margin: 0;
  padding-left: 20px;
}

.login-footer li {
  margin-bottom: 5px;
  color: #606266;
  font-size: 14px;
}

.login-footer a {
  color: #409eff;
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}

/* 标签页样式 */
:deep(.el-tabs__header) {
  margin: 0 0 20px 0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
}

/* 内层标签页样式 */
:deep(.el-tabs--card > .el-tabs__header) {
  border-bottom: none;
  margin-bottom: 15px;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__nav) {
  border: none;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item) {
  border: 1px solid #dcdfe6;
  margin-right: 10px;
  border-radius: 4px 4px 0 0;
  background-color: #f5f7fa;
}

:deep(.el-tabs--card > .el-tabs__header .el-tabs__item.is-active) {
  background-color: #fff;
  border-bottom-color: #fff;
}

:deep(.el-tabs--card > .el-tabs__content) {
  padding: 0;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .login-container {
    padding: 10px;
  }

  .login-card {
    max-width: 100%;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    padding: 0 15px;
  }
}
</style>
