<template>
  <div class="teacher-dashboard">
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <div class="header-flex">
        <div>
          <h2>教师管理中心</h2>
          <p style="color: #666; font-size: 14px;">欢迎回来，这里是您的数字化教学管理工作台</p>
        </div>
        <el-button type="primary" size="large" @click="showCreateCourse = true">
          <el-icon>
            <Plus />
          </el-icon> 新建课程
        </el-button>
      </div>
    </el-card>

    <el-tabs type="border-card" v-model="activeTab" class="main-tabs">

      <el-tab-pane label="班级管理" name="monitor">
        <div style="margin-bottom: 15px;">
          <el-button type="success" plain @click="generateReport">🤖 生成 AI 教学报告</el-button>
        </div>
        <el-table :data="studentData" stripe border>
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="status" label="学情状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'Risk' ? 'danger' : 'success'">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="管理操作" width="300">
            <template #default="{ row }">
              <el-button size="small" type="warning" @click="remindStudent(row)">提醒</el-button>
              <el-button size="small" :type="row.is_silenced ? 'info' : 'danger'" @click="toggleSilence(row)">
                {{ row.is_silenced ? '解除禁言' : '禁言用户' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="资源/题库" name="resource">
        <div class="course-selector">
          <span>当前操作课程：</span>
          <el-select v-model="selectedCourseId" placeholder="选择课程" @change="fetchNodeList" style="width: 200px">
            <el-option v-for="c in courseList" :key="c.id" :label="c.title" :value="c.id" />
          </el-select>
        </div>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="10">
            <el-card header="课件资源上传">
              <el-upload drag action="#" :http-request="handleUpload" :disabled="!selectedCourseId">
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">拖拽文件或点击上传<br><span style="font-size: 12px; color: #999">(支持 MP4 / PDF /
                    Word)</span></div>
              </el-upload>
            </el-card>
          </el-col>

          <el-col :span="14">
            <el-card header="题库录入">
              <el-form label-width="80px">
                <el-form-item label="题干内容">
                  <el-input v-model="newQuestion.content" type="textarea" :rows="2" placeholder="请输入题目描述"></el-input>
                </el-form-item>
                <el-form-item label="题目类型">
                  <el-radio-group v-model="newQuestion.type">
                    <el-radio label="choice">单选题</el-radio>
                    <el-radio label="text">简答题 (主观)</el-radio>
                  </el-radio-group>
                </el-form-item>

                <div v-if="newQuestion.type === 'choice'"
                  style="background: #f9f9f9; padding: 10px; border-radius: 4px;">
                  <el-form-item label="选项A"><el-input v-model="newQuestion.options[0]" /></el-form-item>
                  <el-form-item label="选项B"><el-input v-model="newQuestion.options[1]" /></el-form-item>
                  <el-form-item label="选项C"><el-input v-model="newQuestion.options[2]" /></el-form-item>
                  <el-form-item label="选项D"><el-input v-model="newQuestion.options[3]" /></el-form-item>
                  <el-form-item label="正确答案">
                    <el-select v-model="newQuestion.correct_answer" placeholder="选择正确项">
                      <el-option label="A" value="0" /><el-option label="B" value="1" />
                      <el-option label="C" value="2" /><el-option label="D" value="3" />
                    </el-select>
                  </el-form-item>
                </div>

                <el-button type="primary" @click="addQuestion" style="width: 100%; margin-top: 15px;">➕
                  录入到题库</el-button>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="作业批改" name="grading">
        <div style="margin-bottom: 15px;">
          <el-button @click="fetchSubmissions" icon="Refresh">刷新待批改列表</el-button>
        </div>

        <el-empty v-if="submissions.length === 0" description="太棒了，所有作业都批改完了！" />

        <div v-else class="submission-list">
          <el-card v-for="sub in submissions" :key="sub.id" class="sub-card" shadow="hover">
            <template #header>
              <div class="sub-header">
                <span>学生：{{ sub.student_name }}</span>
                <span style="color: #999; font-size: 12px;">提交时间: {{ sub.submitted_at }}</span>
              </div>
            </template>
            <p><strong>题目：</strong>{{ sub.question_content }}</p>
            <div class="answer-box">
              <strong>学生作答：</strong> {{ sub.answer_content }}
            </div>
            <div class="grade-action">
              <span style="margin-right: 10px;">评分:</span>
              <el-input-number v-model="gradingForm[sub.id].score" :min="0" :max="100" size="small" />
              <el-input v-model="gradingForm[sub.id].comment" placeholder="写两句评语吧..."
                style="width: 250px; margin: 0 10px;" size="small" />
              <el-button type="primary" size="small" @click="submitGrade(sub.id)">提交</el-button>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="社区治理" name="forum">
        <el-button @click="fetchForumPosts" icon="Refresh" style="margin-bottom: 10px;">刷新帖子</el-button>
        <el-table :data="forumPosts" border>
          <el-table-column prop="title" label="帖子标题" />
          <el-table-column prop="author" label="发布者" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_pinned" type="warning" effect="dark">🔝 置顶</el-tag>
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
              <el-select v-model="newEdge.source_id" placeholder="起点" style="width: 100px"><el-option
                  v-for="n in nodeList" :key="n.id" :label="n.label" :value="n.id" /></el-select>
            </el-form-item>
            <el-form-item>
              <el-select v-model="newEdge.target_id" placeholder="终点" style="width: 100px"><el-option
                  v-for="n in nodeList" :key="n.id" :label="n.label" :value="n.id" /></el-select>
            </el-form-item>
            <el-form-item><el-button type="warning" @click="addEdge">连接</el-button></el-form-item>
          </el-form>
        </div>
        <div id="teacher-chart" style="width: 100%; height: 500px; border: 1px solid #eee; margin-top: 10px;"></div>
      </el-tab-pane>

    </el-tabs>

    <el-dialog v-model="showCreateCourse" title="创建课程" width="400px">
      <el-form>
        <el-form-item label="名称"><el-input v-model="newCourseForm.title" /></el-form-item>
        <el-form-item label="简介"><el-input v-model="newCourseForm.description" type="textarea"
            :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="createCourse">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UploadFilled, Refresh } from '@element-plus/icons-vue'

const activeTab = ref('monitor')
const studentData = ref([])
const courseList = ref([])
const selectedCourseId = ref(null)
const showCreateCourse = ref(false)
const nodeList = ref([])
const chartInstance = ref(null)

const newCourseForm = reactive({ title: '', description: '' })
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
  } catch (e) { console.error(e) }
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

const newQuestion = reactive({ content: '', type: 'choice', options: ['', '', '', ''], correct_answer: '0' })
const addQuestion = async () => {
  if (!selectedCourseId.value) return ElMessage.warning("请先选择课程")
  try {
    await axios.post('http://localhost:8000/teacher/questions', {
      course_id: selectedCourseId.value, ...newQuestion
    }, getAuthHeader())
    ElMessage.success("录入成功")
    newQuestion.content = ''
  } catch (e) { ElMessage.error("录入失败") }
}

const handleUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  formData.append('course_id', selectedCourseId.value)
  formData.append('title', options.file.name)
  await axios.post('http://localhost:8000/teacher/upload-resource', formData, getAuthHeader())
  ElMessage.success("上传成功")
}

const submissions = ref([])
const gradingForm = reactive({})

const fetchSubmissions = async () => {
  try {
    const res = await axios.get('http://localhost:8000/teacher/submissions/pending', getAuthHeader())
    submissions.value = res.data
    submissions.value.forEach(s => {
      if (!gradingForm[s.id]) gradingForm[s.id] = { score: 80, comment: '不错，继续加油' }
    })
  } catch (e) { console.error(e) }
}

const submitGrade = async (id) => {
  try {
    await axios.post('http://localhost:8000/teacher/submissions/grade', {
      submission_id: id, ...gradingForm[id]
    }, getAuthHeader())
    ElMessage.success("评分提交成功")
    fetchSubmissions()
  } catch (e) { ElMessage.error("提交失败") }
}

const forumPosts = ref([])
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

const createCourse = async () => {
  await axios.post('http://localhost:8000/teacher/courses', newCourseForm, getAuthHeader())
  ElMessage.success("创建成功")
  showCreateCourse.value = false
  initData()
}

const newNode = reactive({ label: '', weight: 0.8 })
const newEdge = reactive({ source_id: null, target_id: null, relation: '前置' })
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
  padding: 20px;
}

.header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-selector {
  margin-bottom: 20px;
  font-weight: bold;
}

.sub-card {
  margin-bottom: 15px;
}

.sub-header {
  display: flex;
  justify-content: space-between;
}

.answer-box {
  background: #f9f9f9;
  padding: 15px;
  margin: 10px 0;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
  font-family: monospace;
}

.grade-action {
  display: flex;
  align-items: center;
  margin-top: 15px;
  justify-content: flex-end;
}

.graph-tools {
  margin-bottom: 10px;
  background: #fafafa;
  padding: 10px;
  border-radius: 4px;
}
</style>