<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="system-title">XIAORUI智学平台</h2>

      <el-tabs v-model="activeTab" stretch>

        <el-tab-pane label="登录" name="login">
          <el-form label-position="top" size="large">
            <el-form-item label="学号/用户名">
              <el-input v-model="loginForm.username" placeholder="请输入学号/用户名" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock"
                show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-button type="primary" class="full-btn" :loading="loading" @click="handleLogin">
              立即登录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="新用户注册" name="register">
          <el-form label-position="top" size="large">
            <el-form-item label="学号/用户名">
              <el-input v-model="regForm.username" placeholder="请输入学号/用户名" :prefix-icon="User" />
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="regForm.full_name" placeholder="请输入姓名" :prefix-icon="Postcard" />
            </el-form-item>
            <el-form-item label="设置密码">
              <el-input v-model="regForm.password" type="password" placeholder="设置登录密码" :prefix-icon="Lock"
                show-password />
            </el-form-item>
            <el-form-item label="身份选择">
              <el-radio-group v-model="regForm.role" style="width: 100%">
                <el-radio value="student" size="large" border style="flex: 1; margin-right: 10px;">我是学生</el-radio>
                <el-radio value="teacher" size="large" border style="flex: 1;">我是老师</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-button type="success" class="full-btn" :loading="loading" @click="handleRegister">
              立即注册
            </el-button>
          </el-form>
        </el-tab-pane>

      </el-tabs>

    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { User, Lock, Postcard } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('login')

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', password: '', full_name: '', role: 'student' })

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) return ElMessage.warning("请输入账号密码")

  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('username', loginForm.username)
    params.append('password', loginForm.password)

    const res = await axios.post('http://localhost:8000/token', params)

    const { access_token, role, user_id } = res.data
    localStorage.setItem('token', access_token)
    localStorage.setItem('role', role)
    localStorage.setItem('user_id', user_id)
    localStorage.setItem('username', loginForm.username)

    ElMessage.success(`登录成功，欢迎 ${role}`)

    if (role === 'student') router.push('/student')
    else if (role === 'teacher') router.push('/teacher')
    else if (role === 'admin') router.push('/admin')

  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "登录失败")
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!regForm.username || !regForm.password || !regForm.full_name) {
    return ElMessage.warning("请补全注册信息")
  }

  loading.value = true
  try {
    await axios.post('http://localhost:8000/register', regForm)

    ElMessage.success("注册成功！请登录")
    loginForm.username = regForm.username
    loginForm.password = ''
    activeTab.value = 'login'

  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "注册失败")
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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 20px;
}

.login-card {
  width: 420px;
  max-width: 100%;
  padding: 20px 30px;
  border-radius: 12px;
}

@media (max-width: 480px) {
  .login-card {
    padding: 15px;
    width: 95%;
  }

  .system-title {
    font-size: 1.2rem;
  }
}

.system-title {
  color: #409EFF;
  text-align: center;
  margin-bottom: 25px;
  font-weight: 600;
}

.full-btn {
  width: 100%;
  font-weight: bold;
  font-size: 16px;
  margin-top: 10px;
}

.tips {
  margin-top: 20px;
  font-size: 12px;
  color: #999;
  text-align: center;
  background: #f4f4f5;
  padding: 8px;
  border-radius: 4px;
}
</style>