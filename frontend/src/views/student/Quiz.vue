<template>
  <div class="quiz-container">
    <el-card class="quiz-card" v-loading="loading">
      <template #header>
        <div class="header">
          <span>课程结业测验</span>
          <el-tag v-if="!result">考试中</el-tag>
          <el-tag type="warning" v-else-if="result.requires_review">待批改</el-tag>
          <el-tag type="success" v-else-if="isPassed">已通过</el-tag>
          <el-tag type="danger" v-else>未通过</el-tag>
        </div>
      </template>

      <div v-if="questions.length > 0 && !result" class="question-list">
        <div v-for="(q, index) in questions" :key="q.id" class="question-item">
          <div class="q-title">
            <span class="index">{{ index + 1 }}.</span>
            <el-tag size="small" :type="q.type === 'choice' ? 'info' : 'warning'" style="margin-right: 5px;">
              {{ q.type === 'choice' ? '单选' : '简答' }}
            </el-tag>
            {{ q.content }}
          </div>

          <div v-if="q.type === 'choice'">
            <el-radio-group v-model="userAnswers[index]" class="options-group">
              <el-radio v-for="(opt, optIndex) in q.options" :key="optIndex" :value="String(optIndex)" border
                style="margin-bottom: 10px; width: 100%;">
                {{ opt }}
              </el-radio>
            </el-radio-group>
          </div>

          <div v-else>
            <el-input v-model="userAnswers[index]" type="textarea" :rows="3" placeholder="请输入你的答案..." />
          </div>
        </div>

        <el-button type="primary" size="large" style="width: 100%; margin-top: 20px;" @click="submitQuiz"
          :loading="submitting">
          提交试卷
        </el-button>
      </div>

      <div v-else-if="result" class="result-area">
        <div v-if="result.requires_review">
          <div class="score-circle pending">
            <span style="font-size: 16px;">待批改</span>
          </div>
          <h2 style="margin: 20px 0;">主观题已提交</h2>
          <p class="feedback">{{ result.msg }}</p>
          <p class="sub-info">客观题系统评分：{{ result.auto_score }} 分</p>
        </div>

        <div v-else>
          <div class="score-circle" :class="{ pass: isPassed, fail: !isPassed }">
            {{ result.auto_score }} <span style="font-size: 14px">分</span>
          </div>
          <h2 style="margin: 20px 0;">{{ isPassed ? '恭喜！测验通过' : '很遗憾，请继续加油' }}</h2>
          <p class="feedback">{{ result.msg }}</p>
        </div>

        <div class="actions">
          <el-button @click="$router.push('/student')">返回首页</el-button>
          <el-button v-if="!result.requires_review && isPassed" type="primary"
            @click="$router.push('/student/profile')">查看能力提升</el-button>
        </div>

        <div v-if="!result.requires_review && !isPassed" style="margin-top: 20px;">
          <el-button text @click="retry">再做一次</el-button>
        </div>
      </div>

      <el-empty v-else description="暂无题目，老师可能还在出卷中..." />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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

const isPassed = computed(() => {
  if (!result.value || result.value.requires_review) return false
  return result.value.auto_score >= 60
})

const fetchQuestions = async () => {
  loading.value = true
  try {
    const res = await axios.get(`http://localhost:8000/quiz/${courseId}`)
    questions.value = res.data
    userAnswers.value = new Array(questions.value.length).fill('')
    result.value = null
  } catch (error) {
    ElMessage.error("获取题目失败")
  } finally {
    loading.value = false
  }
}

const retry = () => {
  result.value = null
  userAnswers.value = new Array(questions.value.length).fill('')
}

const submitQuiz = async () => {
  const hasEmpty = userAnswers.value.some(ans => ans === null || ans === '')
  if (hasEmpty) {
    return ElMessage.warning("还有题目未完成，请检查")
  }

  submitting.value = true
  try {
    const token = localStorage.getItem('token')
    const payload = questions.value.map((q, index) => ({
      question_id: q.id,
      answer: userAnswers.value[index]
    }))

    const res = await axios.post(
      `http://localhost:8000/quiz/${courseId}/submit`,
      payload,
      { headers: { Authorization: `Bearer ${token}` } }
    )

    result.value = res.data

    if (result.value.requires_review) {
      ElMessage.info("提交成功，请等待老师批改主观题")
    } else if (isPassed.value) {
      ElMessage.success("恭喜！通过测试")
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
  display: flex;
  align-items: center;
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
  width: 100%;
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

.score-circle.pending {
  border-color: #E6A23C;
  color: #E6A23C;
  background: #fdf6ec;
  font-size: 20px;
}

.feedback {
  color: #909399;
  margin-bottom: 10px;
  font-size: 16px;
}

.sub-info {
  color: #666;
  font-size: 14px;
  margin-bottom: 30px;
}

.actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
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