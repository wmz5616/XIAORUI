<template>
  <div class="graph-page">
    <div class="graph-header">
      <div class="left">
        <el-button @click="$router.go(-1)" icon="ArrowLeft" circle />
        <span class="title">课程知识结构全景图</span>
      </div>
      <div class="right">
        <el-tag type="info">可缩放/拖拽节点</el-tag>
      </div>
    </div>

    <div class="graph-container" v-loading="loading">
      <div ref="chartRef" class="echarts-full"></div>

      <div class="sidebar" v-if="selectedNode">
        <h4>{{ selectedNode.name }}</h4>
        <p class="node-desc">{{ selectedNode.desc || '暂无描述' }}</p>
        <el-divider />
        <p><strong>权重:</strong> {{ selectedNode.value }}</p>
        <el-button type="primary" size="small" style="width: 100%" @click="closeSidebar">关闭</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const courseId = route.params.courseId
const loading = ref(false)
const chartRef = ref(null)
const selectedNode = ref(null)
let myChart = null

onMounted(async () => {
  loading.value = true
  await initChart()
  loading.value = false
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (myChart) myChart.dispose()
})

const handleResize = () => {
  if (myChart) myChart.resize()
}

const initChart = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get(`http://localhost:8000/ai-engine/knowledge-graph/${courseId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    if (res.data && res.data.nodes) {
      renderGraph(res.data)
    } else {
      ElMessage.warning('该课程暂无知识图谱数据')
    }
  } catch (e) {
    ElMessage.error('图谱加载失败')
  }
}

const renderGraph = (data) => {
  if (!chartRef.value) return
  myChart = echarts.init(chartRef.value)

  const option = {
    title: {
      text: '知识点关联图谱',
      top: 'bottom',
      left: 'right'
    },
    tooltip: {},
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: data.nodes.map(n => ({
          ...n,
          itemStyle: { color: getColor(n.value) } // 根据权重上色
        })),
        links: data.links,
        categories: data.categories,
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 10
          }
        },
        force: {
          repulsion: 400,
          edgeLength: 100
        }
      }
    ]
  }

  myChart.setOption(option)

  myChart.on('click', (params) => {
    if (params.dataType === 'node') {
      selectedNode.value = {
        name: params.name,
        value: params.value,
        desc: params.data.description // 假设后端传了description
      }
    }
  })
}

const getColor = (weight) => {
  if (weight > 1.5) return '#F56C6C' // 核心
  if (weight > 1.0) return '#E6A23C' // 重要
  return '#409EFF' // 基础
}

const closeSidebar = () => {
  selectedNode.value = null
}
</script>

<style scoped>
.graph-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.graph-header {
  height: 60px;
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.title {
  font-size: 18px;
  font-weight: bold;
  margin-left: 15px;
}

.graph-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.echarts-full {
  width: 100%;
  height: 100%;
}

.sidebar {
  position: absolute;
  right: 20px;
  top: 20px;
  width: 250px;
  background: rgba(255, 255, 255, 0.95);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(4px);
}
</style>