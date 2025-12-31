<template>
  <div class="diagnostic-container">
    <div class="header">
      <el-button link @click="$router.push('/student')">
        <el-icon style="margin-right: 5px">
          <ArrowLeft />
        </el-icon> 返回主页
      </el-button>
      <h2 class="page-title">AI智能诊断</h2>
      <div style="width: 60px"></div>
    </div>

    <div v-if="step === 1" class="config-section">
      <el-card shadow="hover" class="config-card">
        <div class="welcome-img">
          <el-icon :size="60" color="#409EFF">
            <DataAnalysis />
          </el-icon>
        </div>
        <h3 style="text-align: center; margin-bottom: 30px;">请选择你要诊断的学科</h3>

        <el-form label-position="top" size="large">
          <el-form-item label="选择学科">
            <el-radio-group v-model="config.subject" class="subject-group">
              <el-radio-button v-for="sub in subjects" :key="sub" :value="sub" :label="sub" />
            </el-radio-group>
          </el-form-item>

          <el-form-item label="选择年级/阶段">
            <el-select v-model="config.grade" placeholder="请选择" style="width: 100%">
              <el-option label="高一 (Grade 10)" :value="10" />
              <el-option label="高二 (Grade 11)" :value="11" />
              <el-option label="高三 (Grade 12)" :value="12" />
              <el-option label="大学入门" :value="13" />
            </el-select>
          </el-form-item>

          <el-button type="primary" class="start-btn" @click="startDiagnostic" :loading="loading">
            生成诊断测试
          </el-button>
        </el-form>
      </el-card>
    </div>

    <div v-if="step === 2" class="quiz-section">
      <el-card shadow="never" class="quiz-card">
        <template #header>
          <div class="quiz-header">
            <span>正在测试：<strong>{{ config.grade }}年级 {{ config.subject }}</strong></span>
            <el-tag type="danger" effect="dark">诊断模式</el-tag>
          </div>
        </template>

        <div v-for="(q, index) in questions" :key="index" class="question-item">
          <div class="q-title">
            <span class="q-idx">{{ index + 1 }}</span>
            {{ q.content }}
          </div>
          <div class="options-list">
            <el-radio-group v-model="answers[index]" class="vertical-radio">
              <el-radio v-for="(opt, oIdx) in q.options" :key="oIdx" :value="oIdx" border>
                {{ opt }}
              </el-radio>
            </el-radio-group>
          </div>
        </div>

        <div class="action-footer">
          <el-button type="success" size="large" @click="submitQuiz" :loading="analyzing"
            style="width: 100%; max-width: 300px;">
            提交并分析薄弱点
          </el-button>
        </div>
      </el-card>
    </div>

    <div v-if="step === 3" class="result-section">
      <el-result icon="success" title="诊断完成" sub-title="AI 引擎已生成您的个性化分析报告">
        <template #extra>
          <el-button type="primary" @click="$router.push('/student')">返回学习</el-button>
          <el-button @click="step = 1">再次诊断</el-button>
        </template>
      </el-result>

      <el-row :gutter="20">
        <el-col :xs="24" :sm="12">
          <el-card header="错题回顾" shadow="hover" class="result-card">
            <el-collapse>
              <el-collapse-item v-for="(wq, idx) in result.wrong_questions" :key="idx"
                :title="'第 ' + (questions.indexOf(wq) + 1) + ' 题'">
                <p><strong>题目：</strong>{{ wq.content }}</p>
                <p style="color: #F56C6C"><strong>你的答案：</strong>{{ wq.options[wq.your_answer] }}</p>
                <p style="color: #67C23A"><strong>正确答案：</strong>{{ wq.options[wq.correct_index] }}</p>
                <p style="margin-top: 5px; font-size: 12px; color: #909399;">考点：{{ wq.knowledge_point }}</p>
              </el-collapse-item>
              <div v-if="result.wrong_questions.length === 0" style="padding: 20px; text-align: center; color: #999;">
                太棒了，全对！
              </div>
            </el-collapse>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12">
          <el-card header="AI薄弱点分析" shadow="hover" class="result-card" style="margin-top: 10px;">
            <div v-if="result.weak_points && result.weak_points.length > 0">
              <el-alert title="建议加入学习计划" type="warning" :closable="false" style="margin-bottom: 15px;" />
              <div v-for="point in result.weak_points" :key="point" class="weak-point-item">
                <el-icon color="#F56C6C">
                  <Warning />
                </el-icon>
                <span>{{ point }}</span>
                <el-button type="primary" link size="small" @click="addToPlan(point)">去学习</el-button>
              </div>
            </div>
            <el-empty v-else description="暂未发现明显薄弱点，继续保持！" />
          </el-card>
        </el-col>
      </el-row>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowLeft, DataAnalysis, Warning } from '@element-plus/icons-vue'

const router = useRouter()
const step = ref(1)
const loading = ref(false)
const analyzing = ref(false)

const config = reactive({ subject: '数学', grade: 10 })
const subjects = ['数学', '物理', 'Python', '英语', '化学', '历史']
const questions = ref([])
const answers = ref({})
const result = reactive({ wrong_questions: [], weak_points: [] })

const startDiagnostic = async () => {
  loading.value = true
  try {
    const res = await axios.post('http://localhost:8000/ai-engine/diagnostic/start', config, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    questions.value = res.data
    answers.value = {}
    step.value = 2
  } catch (error) {
    ElMessage.error("试卷生成失败，AI 服务可能繁忙")
  } finally {
    loading.value = false
  }
}

const submitQuiz = async () => {
  if (Object.keys(answers.value).length < questions.value.length) {
    return ElMessage.warning("请先完成所有题目")
  }

  analyzing.value = true
  const wrongList = []

  questions.value.forEach((q, index) => {
    const myAns = answers.value[index]
    if (String(myAns) !== String(q.correct_index)) {
      wrongList.push({
        ...q,
        your_answer: myAns
      })
    }
  })

  result.wrong_questions = wrongList

  try {
    const res = await axios.post('http://localhost:8000/ai-engine/diagnostic/analyze', {
      wrong_questions: wrongList
    }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })

    result.weak_points = res.data.weak_points
    step.value = 3
  } catch (error) {
    ElMessage.error("分析失败")
  } finally {
    analyzing.value = false
  }
}

const addToPlan = (point) => {
  router.push({ path: '/student', query: { auto_weakness: point } })
}
</script>

<style scoped>
.diagnostic-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.config-card {
  max-width: 500px;
  margin: 40px auto;
  padding: 20px;
}

.welcome-img {
  text-align: center;
  margin-bottom: 20px;
}

.subject-group {
  display: flex;
  flex-wrap: wrap;
}

.start-btn {
  width: 100%;
  margin-top: 20px;
  font-weight: bold;
  font-size: 16px;
  padding: 20px;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-item {
  margin-bottom: 30px;
}

.q-title {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 15px;
  display: flex;
}

.q-idx {
  background: #409EFF;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  text-align: center;
  line-height: 24px;
  margin-right: 10px;
  font-size: 14px;
  flex-shrink: 0;
}

.vertical-radio {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.options-list .el-radio {
  margin-right: 0;
  width: 100%;
}

.action-footer {
  text-align: center;
  margin-top: 40px;
}

.result-card {
  margin-bottom: 20px;
}

.weak-point-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fef0f0;
  color: #f56c6c;
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 10px;
}

@media (max-width: 768px) {
  .diagnostic-container {
    padding: 10px;
  }

  .subject-group .el-radio-button {
    flex: 1;
    min-width: 30%;
  }

  :deep(.el-radio-button__inner) {
    width: 100%;
  }

  .config-card {
    margin: 10px auto;
  }
}
</style>