<template>
  <div class="dashboard-layout">
    <div class="nav-header">
      <div class="logo-area">
        <img src="@/assets/logo.svg" alt="logo" class="logo-icon" />
        <span class="app-name">XIAORUI 智教</span>
      </div>
      <el-menu mode="horizontal" :default-active="activeIndex" class="top-menu" :ellipsis="false" router>
        <el-menu-item index="/student">工作台</el-menu-item>
        <el-menu-item index="/student/courses">课程中心</el-menu-item>
        <el-menu-item index="/student/homework-list">我的作业</el-menu-item>
        <el-menu-item index="/student/ai-diagnosis">AI 诊断</el-menu-item>
        <el-menu-item index="/student/forum">学习论坛</el-menu-item>
      </el-menu>
      <div class="user-area">
        <el-dropdown>
          <span class="el-dropdown-link">
            {{ userInfo.full_name || userInfo.username }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/student/profile')">个人资料</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="main-content">
      <div class="student-dashboard">
        <el-row :gutter="20">
          <el-col :span="16">
            <div class="welcome-card fade-in">
              <div class="welcome-text">
                <h2>早安，{{ userInfo.full_name || userInfo.username }}同学</h2>
                <p>今天也要充满活力地学习哦！你已经坚持学习了 {{ userInfo.learn_days }} 天。</p>
              </div>
              <img src="@/assets/logo.svg" class="welcome-img" alt="logo" />
            </div>

            <el-row :gutter="20" style="margin-top: 20px">
              <el-col :span="12">
                <el-card shadow="hover" class="stat-card">
                  <template #header>
                    <div class="card-header">
                      <span>学习时长</span>
                      <el-tag type="success">本周</el-tag>
                    </div>
                  </template>
                  <div class="stat-value">
                    {{ userInfo.learn_time }} <span class="unit">分钟</span>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card shadow="hover" class="stat-card">
                  <template #header>
                    <div class="card-header">
                      <span>已做作业</span>
                      <el-tag type="warning">累计</el-tag>
                    </div>
                  </template>
                  <div class="stat-value">
                    {{ userInfo.notes_count }} <span class="unit">次</span>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-card shadow="hover" style="margin-top: 20px" class="chart-card">
              <template #header>
                <span>能力雷达模型</span>
              </template>
              <div ref="radarChart" style="width: 100%; height: 300px"></div>
            </el-card>
          </el-col>

          <el-col :span="8">
            <el-card shadow="hover" class="notice-card">
              <template #header>
                <div class="card-header">
                  <span>最新消息</span>
                  <el-button link type="primary" @click="fetchNotifications">刷新</el-button>
                </div>
              </template>
              <div class="notice-list" v-loading="loadingNotify">
                <div v-for="notice in notifications" :key="notice.id" class="notice-item"
                  :class="{ unread: !notice.is_read }" @click="markRead(notice)">
                  <div class="notice-icon">
                    <el-icon>
                      <Bell />
                    </el-icon>
                  </div>
                  <div class="notice-content">
                    <p class="n-text">{{ notice.content }}</p>
                    <span class="n-time">{{ notice.created_at }}</span>
                  </div>
                  <div class="notice-dot" v-if="!notice.is_read"></div>
                </div>
                <el-empty v-if="notifications.length === 0" description="暂无新消息" />
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { Bell, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const activeIndex = ref('/student')
const userInfo = reactive({
  username: '',
  full_name: '',
  learn_time: 0,
  learn_days: 0,
  notes_count: 0
})
const notifications = ref([])
const loadingNotify = ref(false)
const radarChart = ref(null)

onMounted(() => {
  fetchProfile()
  fetchNotifications()
})

const fetchProfile = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:8000/student/profile', {
      headers: { Authorization: `Bearer ${token}` }
    })
    Object.assign(userInfo, res.data)
    initChart(res.data.radar_data)
  } catch (e) {
    console.error(e)
  }
}

const fetchNotifications = async () => {
  loadingNotify.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:8000/student/notifications', {
      headers: { Authorization: `Bearer ${token}` }
    })
    notifications.value = res.data
  } catch (e) {
    ElMessage.error('消息获取失败')
  } finally {
    loadingNotify.value = false
  }
}

const markRead = async (notice) => {
  if (notice.is_read) return
  try {
    const token = localStorage.getItem('token')
    await axios.put(`http://localhost:8000/student/notifications/${notice.id}/read`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    notice.is_read = true
  } catch (e) {
    console.error(e)
  }
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}

const initChart = (data) => {
  if (!radarChart.value) return
  const myChart = echarts.init(radarChart.value)
  const option = {
    radar: {
      indicator: [
        { name: '逻辑', max: 100 },
        { name: '记忆', max: 100 },
        { name: '专注', max: 100 },
        { name: '计算', max: 100 },
        { name: '阅读', max: 100 },
        { name: '创造', max: 100 }
      ]
    },
    series: [
      {
        name: '能力值',
        type: 'radar',
        data: [
          {
            value: data || [60, 60, 60, 60, 60, 60],
            name: '当前能力'
          }
        ]
      }
    ]
  }
  myChart.setOption(option)
  window.addEventListener('resize', () => myChart.resize())
}
</script>

<style scoped>
.dashboard-layout {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.nav-header {
  height: 60px;
  background: #fff;
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo-area {
  display: flex;
  align-items: center;
  width: 200px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}

.app-name {
  font-weight: bold;
  font-size: 18px;
  color: #409EFF;
}

.top-menu {
  flex: 1;
  border-bottom: none;
}

.user-area {
  margin-left: 20px;
  cursor: pointer;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  color: #606266;
}

.main-content {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

/* 原有的 Dashboard 样式保持不变，略作调整 */
.welcome-card {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  border-radius: 12px;
  padding: 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #2c3e50;
  margin-bottom: 20px;
}

.welcome-text h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.welcome-img {
  height: 100px;
  opacity: 0.8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
  padding: 20px 0;
}

.unit {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.notice-card {
  height: 100%;
  min-height: 500px;
}

.notice-list {
  max-height: 450px;
  overflow-y: auto;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background 0.3s;
  position: relative;
}

.notice-item:hover {
  background-color: #f5f7fa;
}

.notice-item.unread {
  background-color: #ecf5ff;
}

.notice-icon {
  margin-right: 12px;
  color: #409eff;
  margin-top: 2px;
}

.notice-content {
  flex: 1;
}

.n-text {
  font-size: 14px;
  color: #303133;
  margin-bottom: 5px;
  line-height: 1.4;
}

.n-time {
  font-size: 12px;
  color: #909399;
}

.notice-dot {
  width: 8px;
  height: 8px;
  background-color: #f56c6c;
  border-radius: 50%;
  position: absolute;
  top: 15px;
  right: 15px;
}

.fade-in {
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>