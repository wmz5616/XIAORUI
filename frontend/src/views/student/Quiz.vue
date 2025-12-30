<template>
  <div class="quiz-container">
    <el-card class="quiz-card" v-loading="loading">
      <template #header>
        <div class="header">
          <span>📝 课程结业测验</span>
          <el-tag v-if="!result">考试中</el-tag>
          <el-tag type="success" v-else-if="result.passed">已通过</el-tag>
          <el-tag type="danger" v-else>未通过</el-tag>
        </div>
      </template>

      <div v-if="questions.length > 0 && !result" class="question-list">
        <div v-for="(q, index) in questions" :key="q.id" class="question-item">
          <div class="q-title">
            <span class="index">{{ index + 1 }}.</span> {{ q.content }}
          </div>
          <el-radio-group v-model="userAnswers[index]" class="options-group">
            <el-radio v-for="(opt, optIndex) in q.options" :key="optIndex" :value="optIndex" border
              style="margin-bottom: 10px; width: 100%;">
              {{ opt }}
            </el-radio>
          </el-radio-group>
        </div>

        <el-button type="primary" size="large" style="width: 100%; margin-top: 20px;" @click="submitQuiz"
          :loading="submitting">
          提交试卷
        </el-button>
      </div>

      <div v-else-if="result" class="result-area">
        <div class="score-circle" :class="{ pass: result.passed, fail: !result.passed }">
          {{ result.score }} <span style="font-size: 14px">分</span>
        </div>
        <h2 style="margin: 20px 0;">{{ result.passed ? '🎉 恭喜！测验通过' : '💪 很遗憾，请继续加油' }}</h2>
        <p class="feedback">{{ result.mastery_update }}</p>

        <div class="actions">
          <el-button @click="$router.push('/student')">返回首页</el-button>
          <el-button v-if="result.passed" type="primary" @click="$router.push('/student/profile')">查看能力提升</el-button>
        </div>

        <div v-if="!result.passed" style="margin-top: 20px;">
          <el-button text @click="retry">再做一次</el-button>
        </div>
      </div>

      <el-empty v-else description="暂无题目，老师可能还在出卷中..." />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const courseId = route.params.id || 1
const questions = ref([])
const userAnswers = ref([])
const result = ref(null)
const loading = ref(false)
const submitting = ref(false)

const fetchQuestions = async () => {
  loading.value = true
  try {
    const res = await axios.get(`http://localhost:8000/quiz/${courseId}`)
    questions.value = res.data
    // 重置答案
    userAnswers.value = new Array(questions.value.length).fill(null)
    result.value = null
  } catch (error) {
    ElMessage.error("获取题目失败")
  } finally {
    loading.value = false
  }
}

const retry = () => {
  result.value = null
  userAnswers.value = new Array(questions.value.length).fill(null)
}

const submitQuiz = async () => {
  if (userAnswers.value.includes(null)) {
    return ElMessage.warning("还有题目未完成，请检查")
  }

  submitting.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post(
      `http://localhost:8000/quiz/${courseId}/submit`,
      userAnswers.value,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    result.value = res.data
    if (result.value.passed) {
      ElMessage.success("恭喜！知识点掌握状态已更新数据库")
    }
  } catch (error) {
    ElMessage.error("提交失败")
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchQuestions()
})
</script>

<style scoped>
.quiz-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 18px;
}

.question-item {
  margin-bottom: 30px;
  border-bottom: 1px dashed #eee;
  padding-bottom: 20px;
}

.q-title {
  font-size: 16px;
  margin-bottom: 15px;
  font-weight: bold;
  color: #333;
}

.index {
  color: #409EFF;
  margin-right: 5px;
  font-weight: 900;
}

.options-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.result-area {
  text-align: center;
  padding: 40px 0;
  animation: fadeIn 0.5s ease;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  font-size: 36px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.score-circle.pass {
  border-color: #67C23A;
  color: #67C23A;
  background: #f0f9eb;
}

.score-circle.fail {
  border-color: #F56C6C;
  color: #F56C6C;
  background: #fef0f0;
}

.feedback {
  color: #909399;
  margin-bottom: 30px;
  font-size: 16px;
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
</style>