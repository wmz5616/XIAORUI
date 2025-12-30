<template>
  <div class="diagnostic-container">
    <el-card class="box-card" v-loading="loading" element-loading-text="AI 正在命题中，请稍候...">
      <template #header>
        <div class="header">
          <span>智能能力诊断</span>
          <el-tag>高中数学</el-tag>
        </div>
      </template>

      <div v-if="status === 'ready'" class="start-screen">
        <h3>准备好了吗？</h3>
        <p>AI 将为您生成 5 道题目，通过测试我们将精准定位您的薄弱点。</p>
        <el-button type="primary" size="large" @click="startTest" round>开始诊断</el-button>
      </div>

      <div v-if="status === 'testing' && questions.length > 0">
        <div v-for="(q, index) in questions" :key="index" class="question-item">
          <div class="q-title">
            <span class="index">{{ index + 1 }}.</span> {{ q.content }}
          </div>
          <el-radio-group v-model="answers[index]" class="options-group">
            <el-radio 
              v-for="(opt, i) in q.options" 
              :key="i" 
              :value="i" 
              border 
              style="margin-bottom: 10px; width: 100%;"
            >
              {{ opt }}
            </el-radio>
          </el-radio-group>
        </div>
        <el-button type="success" size="large" style="width: 100%; margin-top: 20px;" @click="submitTest">
          提交并分析
        </el-button>
      </div>

      <div v-if="status === 'analyzing'" class="result-screen">
        <el-icon class="is-loading" size="50" color="#409EFF"><Loading /></el-icon>
        <p>AI 正在分析您的答题数据...</p>
      </div>

      <div v-if="status === 'finished'" class="result-screen">
        <el-result icon="success" title="诊断完成" sub-title="已为您生成个性化建议">
          <template #extra>
            <div class="report-card">
              <h4>诊断出的薄弱点：</h4>
              <div class="tags">
                <el-tag v-for="p in weakPoints" :key="p" type="danger" effect="dark" size="large">{{ p }}</el-tag>
              </div>
            </div>
            <el-button type="primary" @click="generatePath">基于此生成学习路径</el-button>
          </template>
        </el-result>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const router = useRouter()
const status = ref('ready')
const loading = ref(false)
const questions = ref([])
const answers = ref([])
const weakPoints = ref([])

const getAuthHeaders = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })

const startTest = async () => {
  loading.value = true
  try {
    const res = await axios.post('http://localhost:8000/ai-engine/diagnostic/start', {
      grade: 10,
      subject: "高中数学"
    }, getAuthHeaders())
    
    questions.value = res.data
    answers.value = new Array(questions.value.length).fill(null)
    status.value = 'testing'
  } catch (err) {
    ElMessage.error("AI 服务繁忙，请稍后重试")
  } finally {
    loading.value = false
  }
}

const submitTest = async () => {
  if (answers.value.includes(null)) return ElMessage.warning("请完成所有题目")
  
  status.value = 'analyzing'
  
  const wrongQuestions = questions.value.filter((q, index) => {
    return answers.value[index] !== q.correct_index
  }).map(q => ({
    content: q.content,
    knowledge_point: q.knowledge_point
  }))

  try {
    const res = await axios.post('http://localhost:8000/ai-engine/diagnostic/analyze', {
      wrong_questions: wrongQuestions
    }, getAuthHeaders())
    
    weakPoints.value = res.data.weak_points
    status.value = 'finished'
  } catch (err) {
    ElMessage.error("分析失败")
    status.value = 'testing'
  }
}

const generatePath = () => {
  router.push({
    path: '/student',
    query: { auto_weakness: weakPoints.value.join(',') }
  })
}
</script>

<style scoped>
.diagnostic-container { max-width: 800px; margin: 40px auto; }
.header { display: flex; justify-content: space-between; align-items: center; font-weight: bold; }
.start-screen, .result-screen { text-align: center; padding: 40px 0; }
.question-item { margin-bottom: 30px; text-align: left; }
.q-title { font-weight: bold; margin-bottom: 15px; }
.report-card { background: #fef0f0; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
.tags { display: flex; gap: 10px; justify-content: center; margin-top: 10px; }
</style>