<template>
  <div class="quiz-container">
    <el-card class="quiz-card">
      <template #header>
        <div class="header">
          <span>📝 课程结业测验</span>
          <el-tag>考试中</el-tag>
        </div>
      </template>

      <div v-if="questions.length > 0 && !result" class="question-list">
        <div v-for="(q, index) in questions" :key="q.id" class="question-item">
          <div class="q-title">
            <span class="index">{{ index + 1 }}.</span> {{ q.content }}
          </div>
          <el-radio-group v-model="userAnswers[index]" class="options-group">
            <el-radio 
              v-for="(opt, optIndex) in q.options" 
              :key="optIndex" 
              :value="optIndex" 
              border 
              style="margin-bottom: 10px; width: 100%;"
            >
              {{ opt }}
            </el-radio>
          </el-radio-group>
        </div>
        
        <el-button type="primary" size="large" style="width: 100%; margin-top: 20px;" @click="submitQuiz">
          交卷
        </el-button>
      </div>

      <div v-else-if="result" class="result-area">
        <div class="score-circle" :class="{ pass: result.passed, fail: !result.passed }">
          {{ result.score }} <span style="font-size: 14px">分</span>
        </div>
        <h2 style="margin: 20px 0;">{{ result.passed ? '恭喜！测验通过' : '很遗憾，未通过' }}</h2>
        <p class="feedback">{{ result.mastery_update }}</p>
        
        <div class="actions">
          <el-button @click="$router.push('/student')">返回首页</el-button>
          <el-button type="primary" @click="$router.push('/student/graph')">查看更新后的图谱</el-button>
        </div>
      </div>

      <el-empty v-else description="加载题目中..." />
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

const fetchQuestions = async () => {
  try {
    const res = await axios.get(`http://localhost:8000/quiz/${courseId}`)
    questions.value = res.data
    // 初始化答案数组
    userAnswers.value = new Array(questions.value.length).fill(null)
  } catch (error) {
    ElMessage.error("获取题目失败")
  }
}

const submitQuiz = async () => {
  // 检查是否做完
  if (userAnswers.value.includes(null)) {
    return ElMessage.warning("请先完成所有题目")
  }

  try {
    const token = localStorage.getItem('token')
    const res = await axios.post(
      `http://localhost:8000/quiz/${courseId}/submit`, 
      userAnswers.value,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    result.value = res.data
    if(result.value.passed) {
      ElMessage.success("恭喜！知识掌握度已更新")
    } else {
      ElMessage.warning("请继续加油")
    }
  } catch (error) {
    ElMessage.error("提交失败")
  }
}

onMounted(() => {
  fetchQuestions()
})
</script>

<style scoped>
.quiz-container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
.header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; font-size: 18px; }
.question-item { margin-bottom: 30px; }
.q-title { font-size: 16px; margin-bottom: 15px; font-weight: bold; }
.index { color: #409EFF; margin-right: 5px; }
.options-group { display: flex; flex-direction: column; align-items: flex-start; }

.result-area { text-align: center; padding: 40px 0; }
.score-circle { 
  width: 120px; height: 120px; border-radius: 50%; 
  border: 4px solid #ddd; 
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto; font-size: 36px; font-weight: bold;
}
.score-circle.pass { border-color: #67C23A; color: #67C23A; background: #f0f9eb; }
.score-circle.fail { border-color: #F56C6C; color: #F56C6C; background: #fef0f0; }
.feedback { color: #909399; margin-bottom: 30px; }
</style>