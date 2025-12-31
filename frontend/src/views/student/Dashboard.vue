<template>
  <div class="student-dashboard">
    <div class="welcome-header">
      <div class="text-content">
        <h1>欢迎回来，{{ user.full_name || user.username }}</h1>
        <p>今天也是充满进步的一天，准备好开始学习了吗？</p>
      </div>
      <div class="stats-overview">
        <div class="stat-item">
          <span class="num">{{ user.learn_time || 0 }}</span>
          <span class="label">学习时长(分)</span>
        </div>
        <div class="stat-item">
          <span class="num">{{ user.learn_days || 1 }}</span>
          <span class="label">坚持天数</span>
        </div>
      </div>
    </div>

    <h3 class="section-title">学习中心</h3>
    <div class="feature-grid">
      <div class="feature-card course-card" @click="goToCourses">
        <div class="icon-wrapper">
          <el-icon :size="32">
            <Reading />
          </el-icon>
        </div>
        <div class="card-info">
          <h3>我的课程</h3>
          <p>进入学习室，观看视频与文档</p>
        </div>
      </div>

      <div class="feature-card homework-card" @click="$router.push('/student/homework-list')">
        <div class="icon-wrapper">
          <el-icon :size="32">
            <EditPen />
          </el-icon>
        </div>
        <div class="card-info">
          <h3>我的作业</h3>
          <p>查看待办作业与批改结果</p>
        </div>
      </div>

      <div class="feature-card forum-card" @click="$router.push('/student/forum')">
        <div class="icon-wrapper">
          <el-icon :size="32">
            <ChatLineRound />
          </el-icon>
        </div>
        <div class="card-info">
          <h3>讨论区</h3>
          <p>与同学老师交流，解决难题</p>
        </div>
      </div>

      <div class="feature-card ai-card" @click="$router.push('/student/ai-diagnosis')">
        <div class="icon-wrapper">
          <el-icon :size="32">
            <DataAnalysis />
          </el-icon>
        </div>
        <div class="card-info">
          <h3>AI 智能诊断</h3>
          <p>分析薄弱点，生成个性化建议</p>
        </div>
      </div>

      <div class="feature-card profile-card" @click="$router.push('/student/profile')">
        <div class="icon-wrapper">
          <el-icon :size="32">
            <User />
          </el-icon>
        </div>
        <div class="card-info">
          <h3>个人中心</h3>
          <p>查看学习数据与能力雷达</p>
        </div>
      </div>
    </div>

    <h3 class="section-title" style="margin-top: 40px;">最新消息</h3>
    <div v-if="notifications.length > 0" class="notification-list">
      <div v-for="n in notifications.slice(0, 3)" :key="n.id" class="notif-item" :class="{ unread: !n.is_read }">
        <el-tag size="small" :type="n.is_read ? 'info' : 'danger'" style="margin-right: 10px;">
          {{ n.is_read ? '已读' : '新消息' }}
        </el-tag>
        <span class="notif-content">{{ n.content }}</span>
        <span class="notif-time">{{ n.created_at }}</span>
      </div>
    </div>
    <el-empty v-else description="暂无新消息" :image-size="60" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Reading, ChatLineRound, User, EditPen, DataAnalysis } from '@element-plus/icons-vue'

const router = useRouter()
const user = ref({})
const notifications = ref([])

const fetchData = async () => {
  try {
    const token = localStorage.getItem('token')
    const headers = { Authorization: `Bearer ${token}` }

    const resUser = await axios.get('http://localhost:8000/student/profile', { headers })
    user.value = resUser.data

    const resNotif = await axios.get('http://localhost:8000/student/notifications', { headers })
    notifications.value = resNotif.data
  } catch (error) {
    console.error("Dashboard data error", error)
  }
}

const goToCourses = () => {
  router.push('/student/courses')
}

onMounted(fetchData)
</script>

<style scoped>
.student-dashboard {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px 40px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
}

.welcome-header h1 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.welcome-header p {
  margin: 0;
  opacity: 0.9;
}

.stats-overview {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-item .num {
  font-size: 28px;
  font-weight: bold;
}

.stat-item .label {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
}

.section-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
  border-left: 4px solid #764ba2;
  padding-left: 10px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.feature-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #eee;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
}

.icon-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  color: white;
  flex-shrink: 0;
}

.course-card .icon-wrapper {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.homework-card .icon-wrapper {
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
}

.forum-card .icon-wrapper {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
}

.ai-card .icon-wrapper {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.profile-card .icon-wrapper {
  background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%);
}

.card-info h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.card-info p {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.notification-list {
  background: white;
  border-radius: 8px;
  padding: 10px;
  border: 1px solid #eee;
}

.notif-item {
  padding: 12px;
  border-bottom: 1px solid #f5f5f5;
  display: flex;
  align-items: center;
  font-size: 14px;
}

.notif-item:last-child {
  border-bottom: none;
}

.notif-content {
  flex: 1;
  color: #555;
}

.notif-time {
  color: #aaa;
  font-size: 12px;
  margin-left: 10px;
}

.unread .notif-content {
  font-weight: bold;
  color: #333;
}
</style>