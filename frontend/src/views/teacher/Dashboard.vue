<template>
  <div class="teacher-dashboard">
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <div class="header-flex">
        <div class="welcome-text">
          <h2>教师管理中心</h2>
          <p style="color: #666; font-size: 14px;">欢迎回来，这里是您的数字化教学管理工作台</p>
        </div>
        <el-button type="primary" icon="Plus" @click="showCreateCourse = true">新建课程</el-button>
      </div>
    </el-card>

    <el-tabs type="border-card" v-model="activeTab" class="main-tabs">

      <el-tab-pane label="班级管理" name="monitor">
        <div style="margin-bottom: 15px;">
          <el-button type="success" plain size="small" @click="generateReport">生成AI教学报告</el-button>
        </div>
        <el-table :data="studentData" stripe border style="width: 100%">
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'Risk' ? 'danger' : 'success'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="薄弱点">
            <template #default="{ row }">
              <el-tag v-for="p in row.weak_points_list" :key="p" type="danger" size="small" style="margin-right:5px">{{
                p }}</el-tag>
              <span v-if="!row.weak_points_list?.length" style="color:#ccc;font-size:12px">暂无</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" type="warning" @click="remindStudent(row)">提醒</el-button>
              <el-button size="small" :type="row.is_silenced ? 'info' : 'danger'" @click="toggleSilence(row)">
                {{ row.is_silenced ? '解除' : '禁言' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="资源/题库" name="resource">
        <div class="course-selector-bar">
          <span class="step-label">第一步：选择课程</span>
          <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="fetchNodeList" style="width: 240px">
            <el-option v-for="c in courseList" :key="c.id" :label="c.title" :value="c.id" />
          </el-select>
        </div>

        <el-empty v-if="!selectedCourseId" description="请先在上方选择一个课程" />

        <div v-else>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-card header="录入新题目" shadow="hover">
                <el-form label-position="top">
                  <el-form-item label="题目内容">
                    <el-input v-model="newQuestion.content" type="textarea" :rows="2" placeholder="题目描述"></el-input>
                  </el-form-item>
                  <el-form-item label="类型">
                    <el-radio-group v-model="newQuestion.type">
                      <el-radio value="choice">单选题</el-radio>
                      <el-radio value="text">主观题</el-radio>
                    </el-radio-group>
                  </el-form-item>

                  <div v-if="newQuestion.type === 'choice'" class="choice-box">
                    <el-input v-for="(o, i) in 4" :key="i" v-model="newQuestion.options[i]"
                      :placeholder="'选项 ' + 'ABCD'[i]" style="margin-bottom:5px">
                      <template #prepend>{{ 'ABCD'[i] }}</template>
                    </el-input>
                    <div style="margin-top:10px">正确答案：
                      <el-select v-model="newQuestion.correct_answer" size="small" style="width:100px">
                        <el-option v-for="(o, i) in 4" :key="i" :label="'ABCD'[i]" :value="String(i)" />
                      </el-select>
                    </div>
                  </div>

                  <el-button type="primary" style="width:100%; margin-top:15px" @click="addQuestion">添加题目</el-button>
                </el-form>
              </el-card>
            </el-col>

            <el-col :span="12">
              <el-card header="上传课件" shadow="hover">
                <el-upload drag action="#" :http-request="handleUpload" multiple>
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">拖拽文件或 <em>点击上传</em></div>
                </el-upload>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane label="作业批改" name="grading">
        <el-button icon="Refresh" size="small" @click="fetchSubmissions" style="margin-bottom:15px">刷新</el-button>
        <el-empty v-if="submissions.length === 0" description="暂无待批改作业" />

        <el-card v-for="sub in submissions" :key="sub.id" class="sub-card" shadow="hover">
          <div slot="header" class="sub-header">
            <span><strong>{{ sub.student_name }}</strong> 提交了作业</span>
            <span class="time">{{ sub.submitted_at }}</span>
          </div>
          <div class="sub-body">
            <p><strong>题目：</strong>{{ sub.question_content }}</p>
            <div class="ans-box"><strong>回答：</strong>{{ sub.answer_content }}</div>
            <div class="grade-box">
              <el-input v-model="gradingForm[sub.id].comment" placeholder="评语" size="small" style="margin-bottom:5px" />
              <el-input-number v-model="gradingForm[sub.id].score" :min="0" :max="100" size="small" />
              <el-button type="primary" size="small" @click="submitGrade(sub.id)"
                style="margin-left:10px">提交</el-button>
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="社区治理" name="forum">
        <el-button icon="Refresh" @click="fetchForumPosts" style="margin-bottom:10px">刷新帖子</el-button>
        <el-table :data="forumPosts" border stripe>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="author_name" label="作者" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_pinned" type="danger" effect="dark">置顶</el-tag>
              <el-tag v-else type="info">普通</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" :type="row.is_pinned ? 'warning' : 'primary'" @click="togglePin(row)">
                {{ row.is_pinned ? '取消置顶' : '置顶' }}
              </el-button>
              <el-popconfirm title="确定删除？" @confirm="deletePost(row)">
                <template #reference><el-button size="small" type="danger">删除</el-button></template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="知识图谱管理" name="graph">
        <el-empty description="请在上方选择课程后管理图谱" v-if="!selectedCourseId" />
        <div v-else>
          <el-form :inline="true">
            <el-form-item><el-input v-model="newNode.label" placeholder="节点名称" /></el-form-item>
            <el-form-item><el-button type="primary" @click="addNode">添加节点</el-button></el-form-item>
          </el-form>
        </div>
      </el-tab-pane>

    </el-tabs>

    <el-dialog v-model="showCreateCourse" title="创建课程" width="400px">
      <el-form label-position="top">
        <el-form-item label="名称"><el-input v-model="newCourseForm.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="newCourseForm.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="createCourse" style="width:100%">确定</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UploadFilled, Refresh } from '@element-plus/icons-vue'

const activeTab = ref('resource')
const studentData = ref([])
const courseList = ref([])
const selectedCourseId = ref(null)
const submissions = ref([])
const forumPosts = ref([])
const gradingForm = reactive({})
const showCreateCourse = ref(false)
const newQuestion = reactive({ content: '', type: 'choice', options: ['', '', '', ''], correct_answer: '0' })
const newCourseForm = reactive({ title: '', description: '' })
const newNode = reactive({ label: '', weight: 1.0 })
const getAuth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
const api = 'http://localhost:8000'

const initData = async () => {
  try {
    const [res1, res2] = await Promise.all([
      axios.get(`${api}/teacher/class-monitor`, getAuth()),
      axios.get(`${api}/teacher/my-courses`, getAuth())
    ])
    studentData.value = res1.data
    courseList.value = res2.data
    if (courseList.value.length) selectedCourseId.value = courseList.value[0].id
  } catch (e) { }
}

const generateReport = async () => {
  const res = await axios.post(`${api}/teacher/generate-report`, {}, getAuth())
  ElMessageBox.alert(res.data.report, 'AI分析', { dangerouslyUseHTMLString: true })
}
const toggleSilence = async (row) => {
  await axios.put(`${api}/teacher/students/${row.id}/silence`, {}, getAuth())
  ElMessage.success("操作成功"); initData()
}
const remindStudent = (row) => {
  ElMessageBox.prompt('请输入提醒内容', '发送通知').then(async ({ value }) => {
    await axios.post(`${api}/teacher/remind-student`, { student_id: row.id, message: value }, getAuth())
    ElMessage.success('已发送')
  })
}

const addQuestion = async () => {
  if (!selectedCourseId.value) return ElMessage.warning("请先选择课程")
  try {
    await axios.post(`${api}/teacher/questions`, { course_id: selectedCourseId.value, ...newQuestion }, getAuth())
    ElMessage.success("题目已录入")
    newQuestion.content = ''
  } catch (e) { ElMessage.error("录入失败") }
}
const handleUpload = async (options) => {
  const fd = new FormData()
  fd.append('file', options.file)
  fd.append('course_id', selectedCourseId.value)
  fd.append('title', options.file.name)
  await axios.post(`${api}/teacher/upload-resource`, fd, getAuth())
  ElMessage.success("上传成功")
}

const fetchSubmissions = async () => {
  const res = await axios.get(`${api}/teacher/submissions/pending`, getAuth())
  submissions.value = res.data
  submissions.value.forEach(s => {
    if (!gradingForm[s.id]) gradingForm[s.id] = { score: 80, comment: '不错' }
  })
}
const submitGrade = async (id) => {
  await axios.post(`${api}/teacher/submissions/grade`, { submission_id: id, ...gradingForm[id] }, getAuth())
  ElMessage.success("批改完成"); fetchSubmissions()
}

const fetchForumPosts = async () => {
  const res = await axios.get(`${api}/forum/posts`, getAuth())
  forumPosts.value = res.data
}
const togglePin = async (row) => {
  await axios.put(`${api}/forum/posts/${row.id}/pin`, {}, getAuth())
  ElMessage.success("操作成功"); fetchForumPosts()
}
const deletePost = async (row) => {
  await axios.delete(`${api}/forum/posts/${row.id}`, getAuth())
  ElMessage.success("已删除"); fetchForumPosts()
}

const createCourse = async () => {
  await axios.post(`${api}/teacher/courses`, newCourseForm, getAuth())
  ElMessage.success("创建成功"); showCreateCourse.value = false; initData()
}

const fetchNodeList = () => {}
const addNode = async () => {
  await axios.post(`${api}/teacher/add-node`, { course_id: selectedCourseId.value, ...newNode }, getAuth())
  ElMessage.success("节点已添加")
}

onMounted(() => {
  initData()
  fetchSubmissions()
  fetchForumPosts()
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

.course-selector-bar {
  background: #f0f9eb;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #e1f3d8;
}

.step-label {
  font-weight: bold;
  color: #67C23A;
  margin-right: 15px;
}

.choice-box {
  background: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.sub-card {
  margin-bottom: 15px;
}

.sub-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.sub-body {
  margin-top: 10px;
  font-size: 14px;
}

.ans-box {
  background: #f4f4f5;
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
}

.grade-box {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.time {
  color: #999;
  font-size: 12px;
}
</style>