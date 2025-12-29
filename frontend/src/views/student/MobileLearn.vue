<template>
  <div class="mobile-container">
    <div class="mobile-header">
      <span>📱 小瑞智学 (Mobile)</span>
      <el-avatar :size="28" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
    </div>

    <div class="mobile-content">
      
      <div class="section-title">✨ AI 随身助教</div>
      <el-card class="ai-card" shadow="never">
        <div class="chat-window">
          <div v-if="!aiResponse" class="placeholder">
            <p>遇到难题了？</p>
            <p>输入知识点，我来帮你规划！</p>
          </div>
          <div v-else class="chat-bubble">
            <div class="ai-avatar">🤖</div>
            <div class="ai-text">
              <p><b>诊断结果：</b>{{ aiResponse.logic_reasoning }}</p>
              <div class="step-list">
                <div v-for="(step, i) in aiResponse.recommended_steps" :key="i" class="step-item">
                  {{ i+1 }}. {{ step }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="input-area">
          <el-input v-model="question" placeholder="例如: 三角函数" size="small" style="flex: 1;" />
          <el-button type="primary" size="small" @click="askAI" :loading="loading">发送</el-button>
        </div>
      </el-card>

      <div class="section-title" style="margin-top: 20px;">📚 我的课程</div>
      <div class="course-list">
        <div v-for="c in courses" :key="c.id" class="mobile-course-card">
          <div class="course-info">
            <div class="c-title">{{ c.title }}</div>
            <el-progress :percentage="c.progress" :stroke-width="6" />
          </div>
          <el-button type="text" size="small">继续</el-button>
        </div>
      </div>

    </div>

    <div class="mobile-tabbar">
      <div class="tab-item active">
        <el-icon><Reading /></el-icon>
        <span>学习</span>
      </div>
      <div class="tab-item" @click="$router.push('/student')">
        <el-icon><Monitor /></el-icon>
        <span>回PC版</span>
      </div>
      <div class="tab-item" @click="logout">
        <el-icon><SwitchButton /></el-icon>
        <span>退出</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { Reading, Monitor, SwitchButton } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const question = ref('')
const loading = ref(false)
const aiResponse = ref(null)

const courses = ref([
  { id: 1, title: '高中数学必修一', progress: 85 },
  { id: 2, title: '英语语法专项', progress: 40 },
  { id: 3, title: '物理力学基础', progress: 10 }
])

const askAI = async () => {
  if(!question.value) return
  loading.value = true
  try {
    const res = await axios.post('http://localhost:8000/ai-engine/learning-path', {
      name: "移动端学生",
      grade: 10,
      weak_subjects: [question.value]
    })
    aiResponse.value = res.data
  } catch (error) {
    ElMessage.error("网络请求失败")
  } finally {
    loading.value = false
  }
}

const logout = () => {
  localStorage.clear()
  router.push('/')
}
</script>

<style scoped>
/* 移动端专属样式 */
.mobile-container {
  max-width: 480px; /* 限制最大宽度，模拟手机 */
  margin: 0 auto;
  background-color: #f7f8fa;
  min-height: 100vh;
  position: relative;
  padding-bottom: 60px; /* 留出底部导航位置 */
  box-shadow: 0 0 20px rgba(0,0,0,0.1);
}

.mobile-header {
  background: #409EFF;
  color: white;
  padding: 15px;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mobile-content { padding: 15px; }

.section-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
  font-weight: bold;
}

/* AI 卡片样式 */
.ai-card { border-radius: 12px; border: none; }
.chat-window {
  background: #f0f2f5;
  border-radius: 8px;
  padding: 10px;
  min-height: 120px;
  margin-bottom: 10px;
  font-size: 13px;
}
.placeholder { color: #999; text-align: center; margin-top: 30px; }
.chat-bubble { display: flex; gap: 10px; }
.ai-avatar { font-size: 20px; }
.ai-text { background: white; padding: 8px; border-radius: 0 8px 8px 8px; flex: 1; }
.step-item { margin-top: 5px; color: #409EFF; }

.input-area { display: flex; gap: 8px; }

/* 课程列表样式 */
.mobile-course-card {
  background: white;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.02);
}
.course-info { flex: 1; margin-right: 15px; }
.c-title { font-size: 14px; font-weight: bold; margin-bottom: 5px; }

/* 底部导航 */
.mobile-tabbar {
  position: fixed;
  bottom: 0;
  width: 100%;
  max-width: 480px;
  height: 55px;
  background: white;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
}
.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 10px;
  color: #999;
  cursor: pointer;
}
.tab-item.active { color: #409EFF; }
.tab-item .el-icon { font-size: 20px; margin-bottom: 2px; }
</style>