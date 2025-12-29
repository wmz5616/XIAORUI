<template>
  <div class="teacher-dashboard">
    <el-card shadow="hover" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2>🎓 教师教学工作台</h2>
        <div class="quick-actions">
           <el-button type="primary" @click="showCreateCourse = true">+ 新建课程</el-button>
        </div>
      </div>
    </el-card>

    <el-tabs type="border-card" v-model="activeTab">
      
      <el-tab-pane label="班级学情监控" name="monitor">
        <el-table :data="studentData" style="width: 100%" stripe>
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="weakness" label="薄弱点预警" />
          <el-table-column label="掌握度">
            <template #default="scope">
              <el-progress :percentage="scope.row.progress" :status="scope.row.status === 'Risk' ? 'exception' : 'success'" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'Risk' ? 'danger' : 'success'">{{ scope.row.status === 'Risk' ? '需干预' : '正常' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="课程资源管理" name="resource">
        <div class="resource-manage">
          <div style="margin-bottom: 20px;">
            <span>选择课程：</span>
            <el-select v-model="selectedCourseId" placeholder="请选择课程" @change="fetchNodeList">
              <el-option v-for="c in courseList" :key="c.id" :label="c.title" :value="c.id" />
            </el-select>
          </div>

          <el-upload
            class="upload-demo"
            drag
            action="#"
            :http-request="handleUpload"
            :disabled="!selectedCourseId"
            multiple>
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
              <div v-if="!selectedCourseId" style="color: red; margin-top: 5px;">请先选择课程！</div>
            </div>
            <template #tip>
              <div class="el-upload__tip">支持 PDF/Word/MP4 格式，大小不超过 50MB</div>
            </template>
          </el-upload>
        </div>
      </el-tab-pane>

      <el-tab-pane label="知识图谱构建" name="graph">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form label-width="80px" style="margin-top: 20px;">
               <el-form-item label="当前课程">
                  <el-select v-model="selectedCourseId" placeholder="请选择" @change="refreshGraph">
                    <el-option v-for="c in courseList" :key="c.id" :label="c.title" :value="c.id" />
                  </el-select>
               </el-form-item>
               <el-divider>添加节点</el-divider>
               <el-form-item label="名称">
                  <el-input v-model="newNode.label"></el-input>
               </el-form-item>
               <el-button type="success" style="width: 100%" @click="addNode">提交节点</el-button>
               
               <el-divider>建立关联</el-divider>
               <el-form-item label="起点">
                  <el-select v-model="newEdge.source_id">
                    <el-option v-for="n in nodeList" :key="n.id" :label="n.label" :value="n.id" />
                  </el-select>
               </el-form-item>
               <el-form-item label="终点">
                  <el-select v-model="newEdge.target_id">
                    <el-option v-for="n in nodeList" :key="n.id" :label="n.label" :value="n.id" />
                  </el-select>
               </el-form-item>
               <el-button type="warning" style="width: 100%" @click="addEdge">生成连线</el-button>
            </el-form>
          </el-col>
          <el-col :span="16">
            <div id="teacher-chart" style="width: 100%; height: 500px; border: 1px solid #eee;"></div>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showCreateCourse" title="创建新课程" width="30%">
      <el-form>
        <el-form-item label="课程名称">
          <el-input v-model="newCourseForm.title" placeholder="例如：高中物理必修二" />
        </el-form-item>
        <el-form-item label="课程简介">
          <el-input v-model="newCourseForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateCourse = false">取消</el-button>
        <el-button type="primary" @click="createCourse">立即创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const activeTab = ref('monitor')
const studentData = ref([])
const courseList = ref([])
const selectedCourseId = ref(null)
const showCreateCourse = ref(false)
const nodeList = ref([])
const chartInstance = ref(null)

const newCourseForm = reactive({ title: '', description: '' })
const newNode = reactive({ label: '', weight: 0.8 })
const newEdge = reactive({ source_id: null, target_id: null, relation: '前置' })

const getAuthHeader = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })

// 1. 初始化数据
const initData = async () => {
  try {
    const [res1, res2] = await Promise.all([
      axios.get('http://localhost:8000/teacher/class-monitor'),
      axios.get('http://localhost:8000/teacher/my-courses', getAuthHeader())
    ])
    studentData.value = res1.data
    courseList.value = res2.data
    if(courseList.value.length > 0) selectedCourseId.value = courseList.value[0].id
  } catch (err) { console.error(err) }
}

// 2. 创建课程
const createCourse = async () => {
  try {
    await axios.post('http://localhost:8000/teacher/courses', newCourseForm, getAuthHeader())
    ElMessage.success("课程创建成功")
    showCreateCourse.value = false
    initData() // 刷新列表
  } catch (err) { ElMessage.error("创建失败") }
}

// 3. 上传文件
const handleUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  formData.append('course_id', selectedCourseId.value)
  formData.append('title', options.file.name)
  
  try {
    await axios.post('http://localhost:8000/teacher/upload-resource', formData, getAuthHeader())
    ElMessage.success("上传成功！")
  } catch (err) { ElMessage.error("上传失败") }
}

// 4. 图谱相关逻辑
const fetchNodeList = async () => {
  if(!selectedCourseId.value) return
  const res = await axios.get(`http://localhost:8000/teacher/course-nodes/${selectedCourseId.value}`)
  nodeList.value = res.data
}

const addNode = async () => {
  if(!selectedCourseId.value) return ElMessage.warning("请先选择课程")
  await axios.post('http://localhost:8000/teacher/add-node', { ...newNode, course_id: selectedCourseId.value })
  ElMessage.success("节点添加成功")
  refreshGraph()
}

const addEdge = async () => {
  await axios.post('http://localhost:8000/teacher/add-edge', newEdge)
  ElMessage.success("连线成功")
  refreshGraph()
}

const refreshGraph = async () => {
  await fetchNodeList()
  if(!selectedCourseId.value) return
  const res = await axios.get(`http://localhost:8000/ai-engine/knowledge-graph/${selectedCourseId.value}`)
  
  if (chartInstance.value) chartInstance.value.dispose()
  chartInstance.value = echarts.init(document.getElementById('teacher-chart'))
  chartInstance.value.setOption({
    series: [{
      type: 'graph',
      layout: 'force',
      data: res.data.nodes,
      links: res.data.links,
      roam: true,
      label: { show: true, position: 'right' },
      force: { repulsion: 200, edgeLength: 100 }
    }]
  })
}

onMounted(() => {
  initData()
})
</script>

<style scoped>
.teacher-dashboard { max-width: 1200px; margin: 0 auto; padding: 20px; }
.quick-actions { display: flex; gap: 10px; }
.resource-manage { padding: 40px; text-align: center; border: 1px dashed #d9d9d9; border-radius: 6px; }
</style>