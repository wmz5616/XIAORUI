<template>
  <div class="graph-container">
    <el-card shadow="always">
      <template #header>
        <div class="card-header">
          <span>🌌 课程知识图谱 (AI Generated)</span>
          <el-button size="small" type="primary" @click="fetchGraph">刷新图谱</el-button>
        </div>
      </template>
      
      <div id="chart-container" style="width: 100%; height: 500px;"></div>
      
      <div class="legend-info">
        <p><el-tag size="small">节点大小</el-tag> 代表知识点重要性权重</p>
        <p><el-tag size="small" type="warning">连线</el-tag> 代表前置/包含逻辑关系</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const chartInstance = ref(null);

// 初始化图表
const initChart = (graphData) => {
  const chartDom = document.getElementById('chart-container');
  // 防止重复初始化
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
  chartInstance.value = echarts.init(chartDom);

  const option = {
    title: { text: '高中数学必修一', top: 'bottom', left: 'right' },
    tooltip: {},
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        type: 'graph',
        layout: 'force', // 力引导布局
        data: graphData.nodes,
        links: graphData.links,
        categories: graphData.categories,
        roam: true, // 允许缩放和平移
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
          lineStyle: { width: 10 }
        },
        force: {
          repulsion: 300, // 节点排斥力
          edgeLength: 120 // 连线长度
        }
      }
    ]
  };

  chartInstance.value.setOption(option);
};

// 获取数据
const fetchGraph = async () => {
  try {
    // 假设课程ID为 1
    const res = await axios.get('http://localhost:8000/ai-engine/knowledge-graph/1');
    initChart(res.data);
  } catch (error) {
    console.error("获取图谱失败", error);
    alert("无法连接后端或数据库无数据");
  }
};

onMounted(() => {
  fetchGraph();
  // 监听窗口大小变化
  window.addEventListener('resize', () => chartInstance.value && chartInstance.value.resize());
});
</script>

<style scoped>
.graph-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.legend-info { margin-top: 15px; font-size: 12px; color: #666; display: flex; gap: 20px; }
</style>