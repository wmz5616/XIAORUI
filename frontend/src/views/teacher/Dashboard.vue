<template>
  <div class="teacher-dashboard">
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <div class="header-flex">
        <div class="welcome-text">
          <h2>教师管理中心</h2>
          <p style="color: #666; font-size: 14px;">欢迎回来，这里是您的数字化教学管理工作台</p>
        </div>
        <el-button type="primary" size="default" class="create-btn" @click="showCreateCourse = true">
          <el-icon>
            <Plus />
          </el-icon> 新建课程
        </el-button>
      </div>
    </el-card>

    <el-tabs type="border-card" v-model="activeTab" class="main-tabs">

      <el-tab-pane label="班级管理" name="monitor">
        <div style="margin-bottom: 15px;">
          <el-button type="success" plain size="small" @click="generateReport">生成AI教学报告</el-button>
        </div>
        <div class="table-container">
          <el-table :data="studentData" stripe border style="width: 100%">
            <el-table-column prop="name" label="姓名" width="100" fixed="left" />

            <el-table-column prop="status" label="学情状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Risk' ? 'danger' : 'success'" size="small" effect="dark">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="待攻克薄弱点" min-width="250">
              <template #default="{ row }">
                <div v-if="row.weak_points_list && row.weak_points_list.length > 0" class="weak-tags">
                  <el-tag v-for="(point, index) in row.weak_points_list" :key="index" type="danger" size="small"
                    effect="plain" style="margin-right: 5px; margin-bottom: 5px;">
                    {{ point }}
                  </el-tag>
                </div>
                <span v-else style="color: #909399; font-size: 12px;">
                  <el-icon style="vertical-align: middle">
                    <CircleCheck />
                  </el-icon> 暂无识别
                </span>
              </template>
            </el-table-column>

            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="warning" @click="remindStudent(row)">提醒</el-button>
                <el-button size="small" :type="row.is_silenced ? 'info' : 'danger'" @click="toggleSilence(row)">
                  {{ row.is_silenced ? '解除' : '禁言' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="资源/题库" name="resource">
        <div class="course-selector">
          <span>当前课程：</span>
          <el-select v-model="selectedCourseId" placeholder="选择课程" @change="fetchNodeList" style="width: 160px">
            <el-option v-for="c in courseList" :key="c.id" :label="c.title" :value="c.id" />
          </el-select>
        </div>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :xs="24" :sm="10" style="margin-bottom: 20px;">
            <el-card header="课件资源上传">
              <el-upload drag action="#" :http-request="handleUpload" :disabled="!selectedCourseId">
                <el-icon class="el-icon--upload">
                  <upload-filled />
                </el-icon>
                <div class="el-upload__text">拖拽或点击上传</div>
              </el-upload>
            </el-card>
          </el-col>

          <el-col :xs="24" :sm="14">
            <el-card header="题库录入">
              <el-form label-width="70px" size="small">
                <el-form-item label="题干">
                  <el-input v-model="newQuestion.content" type="textarea" :rows="2"></el-input>
                </el-form-item>
                <el-form-item label="类型">
                  <el-radio-group v-model="newQuestion.type">
                    <el-radio value="choice">单选</el-radio>
                    <el-radio value="text">简答</el-radio>
                  </el-radio-group>
                </el-form-item>

                <div v-if="newQuestion.type === 'choice'" class="choice-area">
                  <el-form-item v-for="(opt, idx) in 4" :key="idx" :label="'选项' + 'ABCD'[idx]">
                    <el-input v-model="newQuestion.options[idx]" />
                  </el-form-item>
                  <el-form-item label="答案">
                    <el-select v-model="newQuestion.correct_answer">
                      <el-option v-for="(opt, idx) in 4" :key="idx" :label="'ABCD'[idx]" :value="String(idx)" />
                    </el-select>
                  </el-form-item>
                </div>

                <el-button type="primary" @click="addQuestion" style="width: 100%; margin-top: 10px;">➕ 录入</el-button>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="批改" name="grading">
        <el-button @click="fetchSubmissions" icon="Refresh" size="small" style="margin-bottom: 10px;">刷新</el-button>
        <el-empty v-if="submissions.length === 0" description="暂无待批改作业" :image-size="80" />
        <div v-else class="submission-list">
          <el-card v-for="sub in submissions" :key="sub.id" class="sub-card" shadow="hover">
            <div class="sub-header">
              <span class="student-name">{{ sub.student_name }}</span>
              <span class="sub-time">{{ sub.submitted_at.split(' ')[0] }}</span>
            </div>
            <p class="question-text">Q: {{ sub.question_content }}</p>
            <div class="answer-box">A: {{ sub.answer_content }}</div>
            <div class="grade-action">
              <el-input-number v-model="gradingForm[sub.id].score" :min="0" :max="100" size="small"
                style="width: 100px" />
              <el-button type="primary" size="small" @click="submitGrade(sub.id)"
                style="margin-left: 10px;">提交</el-button>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="社区治理" name="forum">
        <el-button @click="fetchForumPosts" icon="Refresh" style="margin-bottom: 10px;">刷新帖子</el-button>
        <div class="table-container">
          <el-table :data="forumPosts" border>
            <el-table-column prop="title" label="帖子标题" />
            <el-table-column prop="author" label="发布者" width="120" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_pinned" type="warning" effect="dark">置顶</el-tag>
                <el-tag v-else type="info">普通</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="治理操作" width="220">
              <template #default="{ row }">
                <el-button size="small" :type="row.is_pinned ? 'info' : 'warning'" @click="togglePin(row)">
                  {{ row.is_pinned ? '取消置顶' : '置顶' }}
                </el-button>
                <el-popconfirm title="确定要删除这个帖子吗？" @confirm="deletePost(row)">
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="知识图谱" name="graph">
        <div class="graph-tools">
          <el-form :inline="true" size="small">
            <el-form-item label="操作课程">
              <el-select v-model="selectedCourseId" placeholder="请选择" @change="refreshGraph" style="width: 150px">
                <el-option v-for="c in courseList" :key="c.id" :label="c.title" :value="c.id" />
              </el-select>
            </el-form-item>
            <el-form-item><el-input v-model="newNode.label" placeholder="新节点名称" /></el-form-item>
            <el-form-item><el-button type="success" @click="addNode">添加节点</el-button></el-form-item>
            <el-form-item label="连线">
              <el-select v-model="newEdge.source_id" placeholder="起点" style="width: 100px">
                <el-option v-for="n in nodeList" :key="n.id" :label="n.label" :value="n.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-select v-model="newEdge.target_id" placeholder="终点" style="width: 100px">
                <el-option v-for="n in nodeList" :key="n.id" :label="n.label" :value="n.id" />
              </el-select>
            </el-form-item>
            <el-form-item><el-button type="warning" @click="addEdge">连接</el-button></el-form-item>
          </el-form>
        </div>
        <div id="teacher-chart" style="width: 100%; height: 500px; border: 1px solid #eee; margin-top: 10px;"></div>
      </el-tab-pane>

    </el-tabs>

    <el-dialog v-model="showCreateCourse" title="创建课程" width="90%" style="max-width: 400px;">
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input v-model="newCourseForm.title" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="newCourseForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="createCourse" style="width: 100%">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UploadFilled, Refresh, CircleCheck } from '@element-plus/icons-vue'

const activeTab = ref('monitor')
const studentData = ref([])
const courseList = ref([])
const selectedCourseId = ref(null)
const showCreateCourse = ref(false)
const submissions = ref([])
const gradingForm = reactive({})
const nodeList = ref([])
const chartInstance = ref(null)
const forumPosts = ref([])

const newCourseForm = reactive({ title: '', description: '' })
const newQuestion = reactive({ content: '', type: 'choice', options: ['', '', '', ''], correct_answer: '0' })
const newNode = reactive({ label: '', weight: 0.8 })
const newEdge = reactive({ source_id: null, target_id: null, relation: '前置' })

const getAuthHeader = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })

const initData = async () => {
  try {
    const [res1, res2] = await Promise.all([
      axios.get('http://localhost:8000/teacher/class-monitor', getAuthHeader()),
      axios.get('http://localhost:8000/teacher/my-courses', getAuthHeader())
    ])
    studentData.value = res1.data
    courseList.value = res2.data
    if (courseList.value.length && !selectedCourseId.value) selectedCourseId.value = courseList.value[0].id
  } catch (e) { }
}

const generateReport = async () => {
  try {
    ElMessage.info("正在分析班级数据，请稍候...")
    const res = await axios.post('http://localhost:8000/teacher/generate-report', {}, getAuthHeader())
    ElMessageBox.alert(res.data.report, 'AI教学报告', {
      dangerouslyUseHTMLString: true,
      customStyle: { maxWidth: '600px' }
    })
  } catch (e) {
    ElMessage.error("报告生成失败")
  }
}

const toggleSilence = async (row) => {
  try {
    const res = await axios.put(`http://localhost:8000/teacher/students/${row.id}/silence`, {}, getAuthHeader())
    ElMessage.success(res.data.msg)
    initData()
  } catch (e) { ElMessage.error("操作失败") }
}

const remindStudent = (row) => {
  ElMessageBox.prompt('请输入提醒内容', '发送通知', {
    confirmButtonText: '发送',
    inputValue: '请注意跟上学习进度。'
  }).then(async ({ value }) => {
    await axios.post('http://localhost:8000/teacher/remind-student', { student_id: row.id, message: value }, getAuthHeader())
    ElMessage.success('已发送')
  })
}

const addQuestion = async () => {
  if (!selectedCourseId.value) return ElMessage.warning("请先选择课程")
  await axios.post('http://localhost:8000/teacher/questions', { course_id: selectedCourseId.value, ...newQuestion }, getAuthHeader())
  ElMessage.success("录入成功"); newQuestion.content = ''
}

const handleUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file); formData.append('course_id', selectedCourseId.value); formData.append('title', options.file.name)
  await axios.post('http://localhost:8000/teacher/upload-resource', formData, getAuthHeader())
  ElMessage.success("上传成功")
}

const fetchSubmissions = async () => {
  try {
    const res = await axios.get('http://localhost:8000/teacher/submissions/pending', getAuthHeader())
    submissions.value = res.data
    submissions.value.forEach(s => { if (!gradingForm[s.id]) gradingForm[s.id] = { score: 80, comment: '' } })
  } catch (e) { console.error(e) }
}

const submitGrade = async (id) => {
  await axios.post('http://localhost:8000/teacher/submissions/grade', { submission_id: id, ...gradingForm[id] }, getAuthHeader())
  ElMessage.success("评分成功"); fetchSubmissions()
}

const createCourse = async () => {
  await axios.post('http://localhost:8000/teacher/courses', newCourseForm, getAuthHeader())
  ElMessage.success("创建成功"); showCreateCourse.value = false; initData()
}

const fetchForumPosts = async () => {
  const res = await axios.get('http://localhost:8000/teacher/forum/posts', getAuthHeader())
  forumPosts.value = res.data
}
const togglePin = async (row) => {
  await axios.put(`http://localhost:8000/teacher/forum/posts/${row.id}/pin`, {}, getAuthHeader())
  ElMessage.success("操作成功")
  fetchForumPosts()
}
const deletePost = async (row) => {
  await axios.delete(`http://localhost:8000/teacher/forum/posts/${row.id}`, getAuthHeader())
  ElMessage.success("已删除")
  fetchForumPosts()
}

const fetchNodeList = async () => {
  if (!selectedCourseId.value) return
  const res = await axios.get(`http://localhost:8000/teacher/course-nodes/${selectedCourseId.value}`, getAuthHeader())
  nodeList.value = res.data
  refreshGraph()
}
const addNode = async () => {
  await axios.post('http://localhost:8000/teacher/add-node', { ...newNode, course_id: selectedCourseId.value }, getAuthHeader())
  ElMessage.success("添加成功"); refreshGraph()
}
const addEdge = async () => {
  await axios.post('http://localhost:8000/teacher/add-edge', newEdge, getAuthHeader())
  ElMessage.success("连接成功"); refreshGraph()
}
const refreshGraph = async () => {
  if (!selectedCourseId.value) return
  const res = await axios.get(`http://localhost:8000/ai-engine/knowledge-graph/${selectedCourseId.value}`, getAuthHeader())
  const chartDom = document.getElementById('teacher-chart')
  if (chartDom) {
    if (chartInstance.value) chartInstance.value.dispose()
    chartInstance.value = echarts.init(chartDom)
    chartInstance.value.setOption({
      series: [{ type: 'graph', layout: 'force', data: res.data.nodes, links: res.data.links, roam: true, label: { show: true }, force: { repulsion: 200 } }]
    })
  }
}

onMounted(() => {
  initData()
  fetchSubmissions()
  fetchForumPosts()
  window.addEventListener('resize', () => chartInstance.value && chartInstance.value.resize())
})
</script>

<style scoped>
.teacher-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.table-container {
  overflow-x: auto;
}

.choice-area {
  background: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.sub-card {
  margin-bottom: 15px;
}

.sub-header {
  display: flex;
  justify-content: space-between;
  font-weight: bold;
  margin-bottom: 5px;
}

.sub-time {
  font-weight: normal;
  color: #999;
  font-size: 12px;
}

.answer-box {
  background: #f0f9eb;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
  font-size: 14px;
}

.grade-action {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.graph-tools {
  margin-bottom: 10px;
  background: #fafafa;
  padding: 10px;
  border-radius: 4px;
}

.weak-tags {
  display: flex;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .header-flex {
    flex-direction: column;
    align-items: flex-start;
  }

  .create-btn {
    margin-top: 10px;
    width: 100%;
  }

  .course-selector {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .course-selector .el-select {
    width: 100% !important;
  }
}
</style>