<template>
  <div class="graph-container">
    <el-card shadow="always">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">个性化知识图谱</span>
            <el-select v-model="currentCourseId" placeholder="请选择课程" style="margin-left: 20px; width: 220px"
              @change="fetchGraph" size="default">
              <el-option v-for="item in courseList" :key="item.id" :label="item.title" :value="item.id" />
            </el-select>
          </div>
          <el-button size="small" type="primary" @click="fetchGraph" :loading="loading">刷新状态</el-button>
        </div>
      </template>

      <div v-loading="loading" element-loading-text="正在分析知识掌握情况..." style="min-height: 500px; position: relative;">
        <div v-if="!currentCourseId || (!graphData.nodes || graphData.nodes.length === 0)" class="empty-tip">
          <span v-if="!currentCourseId">请先在左上角选择一门课程</span>
          <span v-else>该课程暂无知识图谱数据</span>
        </div>

        <div v-show="currentCourseId && graphData.nodes && graphData.nodes.length > 0" id="chart-container"
          style="width: 100%; height: 500px;"></div>
      </div>

      <div class="legend-info">
        <div class="legend-item">
          <span class="dot mastered"></span> 已掌握 (Mastered)
        </div>
        <div class="legend-item">
          <span class="dot unmastered"></span> 待学习 (Risk)
        </div>
        <div class="legend-note">
          * 节点大小代表重要性权重，连线代表知识前置依赖关系
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive, nextTick } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const chartInstance = ref(null);
const courseList = ref([]);
const currentCourseId = ref(null);
const loading = ref(false);
const graphData = reactive({ nodes: [], links: [] });
const getAuthHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

const initChart = (data) => {
  const chartDom = document.getElementById('chart-container');
  if (!chartDom) return;

  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
  chartInstance.value = echarts.init(chartDom);

  const option = {
    tooltip: {
      formatter: (params) => {
        if (params.dataType === 'node') {
          const status = params.data.category === 1 ? '已掌握' : '待强化';
          return `<strong>${params.name}</strong><br/>状态: ${status}<br/>权重: ${params.value}`;
        }
        return '';
      }
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: data.nodes,
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
          curveness: 0.2
        },
        emphasis: {
          focus: 'adjacency',
          scale: true
        },
        force: {
          repulsion: 300,
          edgeLength: 100,
          layoutAnimation: true
        }
      }
    ]
  };

  chartInstance.value.setOption(option);
};

const fetchCourses = async () => {
  try {
    const res = await axios.get('http://localhost:8000/student/courses');
    courseList.value = res.data;

    if (courseList.value.length > 0) {
      currentCourseId.value = courseList.value[0].id;
      fetchGraph();
    }
  } catch (error) {
    console.error("课程列表获取失败", error);
  }
};

const fetchGraph = async () => {
  if (!currentCourseId.value) return;

  loading.value = true;
  graphData.nodes = [];

  try {
    const res = await axios.get(
      `http://localhost:8000/student/knowledge-graph/${currentCourseId.value}`,
      getAuthHeaders()
    );
    Object.assign(graphData, res.data);

    nextTick(() => {
      if (graphData.nodes && graphData.nodes.length > 0) {
        initChart(res.data);
      }
    });

  } catch (error) {
    console.error("图谱数据加载失败", error);
    ElMessage.error("获取学习进度失败，请检查登录状态");
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchCourses();
  window.addEventListener('resize', () => chartInstance.value && chartInstance.value.resize());
});
</script>

<style scoped>
.graph-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.empty-tip {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 500px;
  color: #909399;
  font-size: 14px;
  background: #fcfcfc;
}

.legend-info {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 15px;
  display: flex;
  gap: 25px;
  align-items: center;
  font-size: 13px;
  color: #606266;
}

.legend-item {
  display: flex;
  align-items: center;
}

.dot {
  width: 12px;
  height: 12px;
  display: inline-block;
  border-radius: 50%;
  margin-right: 6px;
}

.dot.mastered {
  background-color: #67C23A;
}

.dot.unmastered {
  background-color: #F56C6C;
}

.legend-note {
  margin-left: auto;
  color: #999;
  font-size: 12px;
}
</style>