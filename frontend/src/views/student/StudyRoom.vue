<template>
  <div class="study-room">
    <div class="header-bar">
      <div class="left">
        <el-button @click="$router.push('/student/courses')" icon="ArrowLeft" circle />
        <span class="course-title">{{ courseTitle }} - 学习空间</span>
      </div>
      <div class="right">
        <el-button type="primary" @click="$router.push('/student/homework-list')">
          去写作业 <el-icon class="el-icon--right">
            <EditPen />
          </el-icon>
        </el-button>
      </div>
    </div>

    <div class="main-area" v-loading="loading">
      <el-row :gutter="20" style="height: 100%">
        <el-col :span="16" style="height: 100%">
          <el-card class="resource-card" shadow="never">
            <template #header>
              <div class="card-header">
                <span><el-icon>
                    <VideoPlay />
                  </el-icon> 课程资源</span>
              </div>
            </template>

            <div v-if="currentResource" class="player-area">
              <div class="video-placeholder" v-if="currentResource.type === 'video'">
                <el-icon :size="60">
                  <VideoPlay />
                </el-icon>
                <p>正在播放: {{ currentResource.title }}</p>
                <p class="sub-text">模拟视频播放器</p>
              </div>
              <div class="doc-placeholder" v-else>
                <el-icon :size="60">
                  <Document />
                </el-icon>
                <p>文档预览: {{ currentResource.title }}</p>
                <el-button type="primary" link @click="downloadFile(currentResource.url)">点击下载</el-button>
              </div>
            </div>
            <div v-else class="empty-state">
              <el-empty description="请从下方选择资源开始学习" />
            </div>

            <div class="resource-list">
              <h4>资源列表</h4>
              <el-scrollbar height="200px">
                <div v-for="(res, index) in resources" :key="res.id" class="res-item"
                  :class="{ active: currentResource && currentResource.id === res.id }" @click="playResource(res)">
                  <span class="res-icon">
                    <el-icon v-if="res.type === 'video'">
                      <VideoCamera />
                    </el-icon>
                    <el-icon v-else>
                      <Document />
                    </el-icon>
                  </span>
                  <span class="res-title">{{ res.title }}</span>
                  <el-tag size="small" :type="res.type === 'video' ? 'success' : 'info'">{{ res.type }}</el-tag>
                </div>
              </el-scrollbar>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8" style="height: 100%">
          <el-card class="graph-card" shadow="never">
            <template #header>
              <span><el-icon>
                  <Share />
                </el-icon> 知识图谱</span>
            </template>
            <div ref="graphChart" class="echarts-box"></div>
            <div class="graph-legend">
              <p>Tips: 节点越大代表知识点权重越高</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { ArrowLeft, VideoPlay, VideoCamera, Document, Share, EditPen } from '@element-plus/icons-vue'

const route = useRoute()
const courseId = route.params.id
const courseTitle = ref('加载中...')
const loading = ref(false)
const resources = ref([])
const currentResource = ref(null)
const graphChart = ref(null)

onMounted(async () => {
  loading.value = true
  await fetchCourseInfo()
  await fetchResources()
  await initGraph()
  loading.value = false
})

const fetchCourseInfo = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('http://localhost:8000/student/courses', {
      headers: { Authorization: `Bearer ${token}` }
    })
    const course = res.data.find(c => c.id == courseId)
    if (course) courseTitle.value = course.title
  } catch (e) {
    courseTitle.value = '未知课程'
  }
}

const fetchResources = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get(`http://localhost:8000/student/course/${courseId}/resources`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    resources.value = res.data
    if (resources.value.length > 0) {
      currentResource.value = resources.value[0]
    }
  } catch (e) {
    ElMessage.error('资源加载失败')
  }
}

const initGraph = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get(`http://localhost:8000/ai-engine/knowledge-graph/${courseId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    if (res.data && res.data.nodes.length > 0) {
      renderChart(res.data)
    }
  } catch (e) {
    console.error('图谱加载失败', e)
  }
}

const renderChart = (data) => {
  if (!graphChart.value) return
  const myChart = echarts.init(graphChart.value)

  const option = {
    tooltip: {},
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        type: 'graph',
        layout: 'force',
        symbolSize: 40,
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        edgeSymbol: ['circle', 'arrow'],
        edgeSymbolSize: [4, 10],
        edgeLabel: {
          fontSize: 12
        },
        data: data.nodes,
        links: data.links,
        categories: data.categories,
        lineStyle: {
          opacity: 0.9,
          width: 2,
          curveness: 0.1
        },
        force: {
          repulsion: 300,
          edgeLength: 120
        }
      }
    ]
  }
  myChart.setOption(option)
  window.addEventListener('resize', () => myChart.resize())
}

const playResource = (res) => {
  currentResource.value = res
}

const downloadFile = (url) => {
  window.open(url, '_blank')
}
</script>

<style scoped>
.study-room {
  height: 90vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  padding: 10px 20px;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  background: #fff;
  padding: 0 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
}

.course-title {
  font-size: 18px;
  font-weight: bold;
  margin-left: 15px;
  color: #303133;
}

.main-area {
  flex: 1;
  overflow: hidden;
}

.resource-card,
.graph-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.resource-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.player-area {
  height: 60%;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
}

.video-placeholder,
.doc-placeholder {
  text-align: center;
}

.sub-text {
  font-size: 12px;
  opacity: 0.6;
}

.doc-placeholder {
  background: #f0f2f5;
  color: #606266;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.empty-state {
  height: 60%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f9f9f9;
}

.resource-list {
  flex: 1;
  padding: 15px;
  background: #fff;
  border-top: 1px solid #eee;
}

.resource-list h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.res-item {
  display: flex;
  align-items: center;
  padding: 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
  margin-bottom: 5px;
}

.res-item:hover {
  background: #f5f7fa;
}

.res-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.res-icon {
  margin-right: 10px;
  display: flex;
  align-items: center;
}

.res-title {
  flex: 1;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 10px;
}

.graph-card :deep(.el-card__body) {
  height: calc(100% - 60px);
  padding: 0;
  position: relative;
}

.echarts-box {
  width: 100%;
  height: 100%;
}

.graph-legend {
  position: absolute;
  bottom: 10px;
  left: 10px;
  font-size: 12px;
  color: #909399;
  background: rgba(255, 255, 255, 0.8);
  padding: 5px;
  border-radius: 4px;
}
</style>