<template>
  <div class="teacher-dashboard">
    <el-container>
      <el-aside width="220px" class="aside-menu">
        <div class="logo-area">
          <h2>XIAORUI</h2>
          <p>教师工作台</p>
        </div>
        <el-menu :default-active="activeTab" class="el-menu-vertical" @select="handleMenuSelect">
          <el-menu-item index="monitor">
            <el-icon>
              <DataLine />
            </el-icon>
            <span>学情监控</span>
          </el-menu-item>
          <el-menu-item index="course">
            <el-icon>
              <Reading />
            </el-icon>
            <span>课程发布</span>
          </el-menu-item>
          <el-menu-item index="homework">
            <el-icon>
              <EditPen />
            </el-icon>
            <span>作业管理</span>
          </el-menu-item>
          <el-menu-item index="grading">
            <el-icon>
              <Check />
            </el-icon>
            <span>作业批改</span>
            <el-badge :value="pendingCount" class="badge-item" v-if="pendingCount > 0" />
          </el-menu-item>
          <el-menu-item index="forum">
            <el-icon>
              <ChatDotRound />
            </el-icon>
            <span>讨论区管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="main-content">
        <header class="content-header">
          <h3>{{ pageTitle }}</h3>
          <div class="user-info">
            <span>欢迎您，老师</span>
            <el-button link type="danger" @click="logout">退出</el-button>
          </div>
        </header>

        <div v-if="activeTab === 'monitor'" class="tab-content fade-in">
          <el-row :gutter="20">
            <el-col :span="24">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>班级实时学情</span>
                    <el-button type="primary" size="small" @click="generateReport">生成AI报告</el-button>
                  </div>
                </template>
                <el-table :data="classData" style="width: 100%" stripe>
                  <el-table-column prop="name" label="学生姓名" width="120" />
                  <el-table-column label="综合进度" width="200">
                    <template #default="scope">
                      <el-progress :percentage="scope.row.progress" :color="customColors" />
                    </template>
                  </el-table-column>
                  <el-table-column label="风险状态" width="120">
                    <template #default="scope">
                      <el-tag :type="scope.row.status === 'Risk' ? 'danger' : 'success'">
                        {{ scope.row.status === 'Risk' ? '预警' : '正常' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="薄弱知识点">
                    <template #default="scope">
                      <div class="tags-group">
                        <el-tag v-for="point in scope.row.weak_points_list" :key="point" size="small" type="warning"
                          effect="plain">
                          {{ point }}
                        </el-tag>
                        <span v-if="scope.row.weak_points_list.length === 0" class="text-gray">无明显薄弱点</span>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="150">
                    <template #default="scope">
                      <el-button size="small" @click="remindStudent(scope.row)">提醒</el-button>
                      <el-button size="small" :type="scope.row.is_silenced ? 'info' : 'warning'"
                        @click="toggleSilence(scope.row)">
                        {{ scope.row.is_silenced ? '取消禁言' : '禁言' }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div v-if="activeTab === 'course'" class="tab-content fade-in">
          <el-card class="form-card">
            <template #header>发布新课程</template>
            <el-form :model="courseForm" label-width="100px">
              <el-form-item label="课程名称">
                <el-input v-model="courseForm.title" placeholder="例如：高等数学(上)" />
              </el-form-item>
              <el-form-item label="课程简介">
                <el-input v-model="courseForm.description" type="textarea" rows="3" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="createCourse">立即发布</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>

        <div v-if="activeTab === 'homework'" class="tab-content fade-in">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card class="box-card">
                <template #header>
                  <div class="card-header">
                    <span>1. 创建作业包</span>
                  </div>
                </template>
                <el-form :model="homeworkForm" label-width="80px">
                  <el-form-item label="所属课程">
                    <el-select v-model="homeworkForm.course_id" placeholder="请选择课程" style="width: 100%">
                      <el-option v-for="c in myCourses" :key="c.id" :label="c.title" :value="c.id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="作业标题">
                    <el-input v-model="homeworkForm.title" placeholder="例如：第一章课后练习" />
                  </el-form-item>
                  <el-form-item label="作业说明">
                    <el-input v-model="homeworkForm.description" type="textarea" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="createHomework">创建作业</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-col>

            <el-col :span="12">
              <el-card class="box-card">
                <template #header>
                  <div class="card-header">
                    <span>2. 录入题目</span>
                  </div>
                </template>
                <el-form :model="questionForm" label-width="80px">
                  <el-form-item label="选择课程">
                    <el-select v-model="questionForm.course_id" placeholder="先选课程" @change="fetchHomeworks"
                      style="width: 100%">
                      <el-option v-for="c in myCourses" :key="c.id" :label="c.title" :value="c.id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="选择作业">
                    <el-select v-model="questionForm.homework_id" placeholder="请选择该课程下的作业"
                      :disabled="!questionForm.course_id" style="width: 100%">
                      <el-option v-for="h in availableHomeworks" :key="h.id" :label="h.title" :value="h.id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="题目类型">
                    <el-radio-group v-model="questionForm.type">
                      <el-radio label="choice">单选题</el-radio>
                      <el-radio label="text">主观题</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="题目内容">
                    <el-input v-model="questionForm.content" type="textarea" rows="2" />
                  </el-form-item>
                  <div v-if="questionForm.type === 'choice'">
                    <el-form-item v-for="(opt, idx) in questionForm.options" :key="idx" :label="'选项 ' + 'ABCD'[idx]">
                      <el-input v-model="questionForm.options[idx]" />
                    </el-form-item>
                    <el-form-item label="正确答案">
                      <el-select v-model="questionForm.correct_answer" placeholder="选择正确选项">
                        <el-option v-for="(opt, idx) in questionForm.options" :key="idx" :label="'选项 ' + 'ABCD'[idx]"
                          :value="idx.toString()" />
                      </el-select>
                    </el-form-item>
                  </div>
                  <el-form-item>
                    <el-button type="success" @click="addQuestion"
                      :disabled="!questionForm.homework_id">添加题目</el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div v-if="activeTab === 'grading'" class="tab-content fade-in">
          <el-card>
            <template #header>待批改作业列表</template>
            <el-table :data="pendingSubmissions" style="width: 100%">
              <el-table-column prop="student_name" label="学生" width="120" />
              <el-table-column prop="homework_title" label="作业名称" width="180" />
              <el-table-column prop="question_content" label="题目" show-overflow-tooltip />
              <el-table-column prop="answer_content" label="学生回答" show-overflow-tooltip />
              <el-table-column prop="submitted_at" label="提交时间" width="160" />
              <el-table-column label="操作" width="200">
                <template #default="scope">
                  <el-button size="small" type="primary" @click="openGradeDialog(scope.row)">批改</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <div v-if="activeTab === 'forum'" class="tab-content fade-in">
          <Forum />
        </div>

      </el-main>
    </el-container>

    <el-dialog v-model="gradeDialogVisible" title="作业批改" width="30%">
      <el-form :model="gradeForm">
        <el-form-item label="得分(0-10)">
          <el-input-number v-model="gradeForm.score" :min="0" :max="10" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="gradeForm.comment" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="gradeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitGrade">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataLine, Reading, EditPen, Check, ChatDotRound } from '@element-plus/icons-vue'
import Forum from '../student/Forum.vue'

const router = useRouter()
const activeTab = ref('monitor')
const classData = ref([])
const myCourses = ref([])
const availableHomeworks = ref([])
const pendingSubmissions = ref([])
const gradeDialogVisible = ref(false)
const currentSubmissionId = ref(null)

const courseForm = reactive({ title: '', description: '' })
const homeworkForm = reactive({ course_id: null, title: '', description: '' })
const questionForm = reactive({
  course_id: null,
  homework_id: null,
  type: 'choice',
  content: '',
  options: ['', '', '', ''],
  correct_answer: ''
})
const gradeForm = reactive({ score: 10, comment: '做得不错' })

const pageTitle = computed(() => {
  const map = {
    monitor: '班级学情监控中心',
    course: '课程发布中心',
    homework: '作业与题库管理',
    grading: '作业批改控制台',
    forum: '课程讨论区'
  }
  return map[activeTab.value]
})

const pendingCount = computed(() => pendingSubmissions.value.length)

const customColors = [
  { color: '#f56c6c', percentage: 40 },
  { color: '#e6a23c', percentage: 70 },
  { color: '#5cb87a', percentage: 100 },
]

onMounted(() => {
  fetchMonitorData()
  fetchMyCourses()
  fetchPendingSubmissions()
})

const handleMenuSelect = (index) => {
  activeTab.value = index
  if (index === 'monitor') fetchMonitorData()
  if (index === 'grading') fetchPendingSubmissions()
}

const fetchMonitorData = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:8000/teacher/class-monitor', {
      headers: { Authorization: `Bearer ${token}` }
    })
    classData.value = res.data
  } catch (e) {
    ElMessage.error('获取学情数据失败')
  }
}

const fetchMyCourses = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:8000/teacher/my-courses', {
      headers: { Authorization: `Bearer ${token}` }
    })
    myCourses.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const fetchHomeworks = async () => {
  if (!questionForm.course_id) return
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get(`http://localhost:8000/teacher/course/${questionForm.course_id}/homeworks`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    availableHomeworks.value = res.data
    questionForm.homework_id = null
  } catch (e) {
    ElMessage.error('获取作业列表失败')
  }
}

const createCourse = async () => {
  if (!courseForm.title) return ElMessage.warning('请输入课程名称')
  try {
    const token = localStorage.getItem('token')
    await axios.post('http://localhost:8000/teacher/courses', courseForm, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('课程发布成功')
    courseForm.title = ''
    courseForm.description = ''
    fetchMyCourses()
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

const createHomework = async () => {
  if (!homeworkForm.course_id || !homeworkForm.title) return ElMessage.warning('请补全信息')
  try {
    const token = localStorage.getItem('token')
    await axios.post('http://localhost:8000/teacher/homeworks', homeworkForm, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('作业创建成功')
    homeworkForm.title = ''
    homeworkForm.description = ''
    if (questionForm.course_id === homeworkForm.course_id) {
      fetchHomeworks()
    }
  } catch (e) {
    ElMessage.error('创建作业失败')
  }
}

const addQuestion = async () => {
  if (!questionForm.homework_id || !questionForm.content) return ElMessage.warning('请填写完整')
  try {
    const token = localStorage.getItem('token')
    await axios.post('http://localhost:8000/teacher/questions', questionForm, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('题目已录入')
    questionForm.content = ''
    questionForm.options = ['', '', '', '']
  } catch (e) {
    ElMessage.error('录入失败')
  }
}

const fetchPendingSubmissions = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:8000/teacher/submissions/pending', {
      headers: { Authorization: `Bearer ${token}` }
    })
    pendingSubmissions.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const openGradeDialog = (row) => {
  currentSubmissionId.value = row.id
  gradeForm.score = 10
  gradeForm.comment = '回答得很棒，继续加油！'
  gradeDialogVisible.value = true
}

const submitGrade = async () => {
  try {
    const token = localStorage.getItem('token')
    await axios.post('http://localhost:8000/teacher/submissions/grade', {
      submission_id: currentSubmissionId.value,
      score: gradeForm.score,
      comment: gradeForm.comment
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success('批改完成')
    gradeDialogVisible.value = false
    fetchPendingSubmissions()
  } catch (e) {
    ElMessage.error('提交失败')
  }
}

const generateReport = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('http://localhost:8000/teacher/generate-report', {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessageBox.alert(res.data.report, 'AI 分析报告', { dangerouslyUseHTMLString: true })
  } catch (e) {
    ElMessage.error('生成报告失败')
  }
}

const remindStudent = async (student) => {
  try {
    const token = localStorage.getItem('token')
    await axios.post('http://localhost:8000/teacher/remind-student', {
      student_id: student.id,
      message: '检测到你最近学习进度滞后，请及时复习。'
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    ElMessage.success(`已发送提醒给 ${student.name}`)
  } catch (e) {
    ElMessage.error('发送失败')
  }
}

const toggleSilence = async (student) => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.put(`http://localhost:8000/teacher/students/${student.id}/silence`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    student.is_silenced = res.data.is_silenced
    ElMessage.success(student.is_silenced ? '已禁言' : '已解除禁言')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.teacher-dashboard {
  height: 100vh;
  background-color: #f5f7fa;
}

.aside-menu {
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
}

.logo-area {
  height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: #409EFF;
  color: white;
}

.logo-area h2 {
  margin: 0;
  font-size: 20px;
}

.logo-area p {
  margin: 0;
  font-size: 12px;
  opacity: 0.8;
}

.el-menu-vertical {
  border-right: none;
  flex: 1;
}

.main-content {
  padding: 0;
  display: flex;
  flex-direction: column;
}

.content-header {
  height: 60px;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.tab-content {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags-group {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}

.fade-in {
  animation: fadeIn 0.4s ease;
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

.badge-item :deep(.el-badge__content) {
  top: 10px;
  right: 0px;
}
</style>