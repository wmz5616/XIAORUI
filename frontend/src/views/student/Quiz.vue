<template>
  <div class="quiz-container">
    <el-card class="quiz-box" v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button @click="$router.go(-1)" icon="ArrowLeft" circle />
          <span class="title">作业答题卡</span>
          <el-progress :percentage="progress" type="circle" :width="40" />
        </div>
      </template>

      <div v-if="questions.length > 0">
        <div class="question-area">
          <div class="q-tag">第 {{ currentIndex + 1 }} 题 / 共 {{ questions.length }} 题</div>
          <h3 class="q-content">{{ currentQuestion.content }}</h3>

          <div v-if="currentQuestion.type === 'choice'" class="options-list">
            <div v-for="(opt, idx) in currentQuestion.options" :key="idx" class="option-item"
              :class="{ active: answers[currentIndex] === String(idx) }" @click="selectOption(idx)">
              <span class="opt-label">{{ 'ABCD'[idx] }}</span>
              <span class="opt-text">{{ opt }}</span>
            </div>
          </div>

          <div v-else-if="currentQuestion.type === 'text'" class="text-answer">
            <el-input v-model="answers[currentIndex]" type="textarea" rows="6" placeholder="请输入你的答案..." />
          </div>
        </div>

        <div class="footer-btns">
          <el-button v-if="currentIndex > 0" @click="currentIndex--">上一题</el-button>
          <div class="spacer"></div>
          <el-button v-if="currentIndex < questions.length - 1" type="primary" @click="currentIndex++">下一题</el-button>
          <el-button v-else type="success" @click="submitQuiz" :loading="submitting">提交作业</el-button>
        </div>
      </div>

      <el-empty v-else description="该作业暂时没有题目" />
    </el-card>

    <el-dialog v-model="resultVisible" title="作业结果" width="30%" center :show-close="false">
      <div class="result-content">
        <el-result :icon="resultData.pass ? 'success' : 'warning'" :title="resultData.pass ? '作业已完成' : '待老师批改'"
          :sub-title="resultData.msg">
          <template #extra>
            <div class="score-display" v-if="!resultData.requires_review">
              <span class="big-score">{{ resultData.auto_score }}</span>
              <span class="total-score">/ {{ resultData.total_score }} 分</span>
            </div>
            <el-button type="primary" @click="$router.push('/student/homework-list')">返回列表</el-button>
          </template>
        </el-result>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const homeworkId = route.params.id

const loading = ref(false)
const submitting = ref(false)
const questions = ref([])
const currentIndex = ref(0)
const answers = ref([])
const resultVisible = ref(false)
const resultData = ref({})

const currentQuestion = computed(() => questions.value[currentIndex.value] || {})
const progress = computed(() => questions.value.length ? ((currentIndex.value + 1) / questions.value.length) * 100 : 0)

onMounted(async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get(`http://localhost:8000/quiz/${homeworkId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    questions.value = res.data
    answers.value = new Array(questions.value.length).fill('')
  } catch (e) {
    ElMessage.error('题目加载失败')
  } finally {
    loading.value = false
  }
})

const selectOption = (idx) => {
  answers.value[currentIndex.value] = String(idx)
}

const submitQuiz = async () => {
  const unanswered = answers.value.some(a => a === '')
  if (unanswered && !confirm("还有题目未完成，确定要提交吗？")) return

  submitting.value = true
  try {
    const token = localStorage.getItem('token')
    const payload = questions.value.map((q, idx) => ({
      question_id: q.id,
      answer: answers.value[idx]
    }))

    const res = await axios.post(`http://localhost:8000/quiz/${homeworkId}/submit`, payload, {
      headers: { Authorization: `Bearer ${token}` }
    })

    resultData.value = {
      auto_score: res.data.auto_score,
      total_score: res.data.total_score,
      msg: res.data.msg,
      requires_review: res.data.requires_review,
      pass: !res.data.requires_review
    }
    resultVisible.value = true
  } catch (e) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.quiz-container {
  max-width: 800px;
  margin: 20px auto;
  height: 90vh;
  display: flex;
  flex-direction: column;
}

.quiz-box {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.question-area {
  padding: 20px 0;
  min-height: 300px;
}

.q-tag {
  color: #909399;
  margin-bottom: 10px;
}

.q-content {
  font-size: 20px;
  margin-bottom: 30px;
  line-height: 1.6;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-item:hover {
  background-color: #f5f7fa;
}

.option-item.active {
  background-color: #ecf5ff;
  border-color: #409EFF;
  color: #409EFF;
}

.opt-label {
  font-weight: bold;
  margin-right: 15px;
  width: 20px;
}

.footer-btns {
  margin-top: 30px;
  display: flex;
}

.spacer {
  flex: 1;
}

.score-display {
  text-align: center;
  margin-bottom: 20px;
}

.big-score {
  font-size: 40px;
  color: #409EFF;
  font-weight: bold;
}

.total-score {
  font-size: 16px;
  color: #909399;
}
</style>