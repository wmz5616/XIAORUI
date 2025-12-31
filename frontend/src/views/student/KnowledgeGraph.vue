<template>
  <div class="graph-container">
    <el-card shadow="always" :body-style="{ padding: isMobile ? '10px' : '20px' }">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">个性化知识图谱</span>
            <el-select v-model="currentCourseId" placeholder="请选择课程" class="course-select" @change="fetchGraph"
              size="default">
              <el-option v-for="item in courseList" :key="item.id" :label="item.title" :value="item.id" />
            </el-select>
          </div>
          <el-button class="refresh-btn" size="small" type="primary" @click="fetchGraph" :loading="loading"
            :icon="Refresh">
            {{ isMobile ? '' : '刷新状态' }}
          </el-button>
        </div>
      </template>

      <div v-loading="loading" element-loading-text="正在分析..." class="chart-wrapper">
        <div v-if="!currentCourseId || (!graphData.nodes || graphData.nodes.length === 0)" class="empty-tip">
          <span v-if="!currentCourseId">请选择课程</span>
          <span v-else>暂无数据</span>
        </div>

        <div v-show="currentCourseId && graphData.nodes && graphData.nodes.length > 0" id="chart-container"
          class="echart-box"></div>
      </div>

      <div class="legend-info">
        <div class="legend-item">
          <span class="dot mastered"></span> 已掌握
        </div>
        <div class="legend-item">
          <span class="dot unmastered"></span> 待学习
        </div>
        <div class="legend-note">
          * 节点越大越重要
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive, nextTick, computed } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { Refresh } from '@element-plus/icons-vue';

const chartInstance = ref(null);
const courseList = ref([]);
const currentCourseId = ref(null);
const loading = ref(false);
const graphData = reactive({ nodes: [], links: [] });
const isMobile = computed(() => window.innerWidth < 768);

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
      trigger: 'item',
      confine: true,
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
        zoom: isMobile.value ? 0.6 : 1,
        label: {
          show: true,
          position: 'right',
          fontSize: isMobile.value ? 10 : 12,
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
          repulsion: isMobile.value ? 150 : 300,
          edgeLength: isMobile.value ? 50 : 100,
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
  } catch (error) { console.error(error); }
};

const fetchGraph = async () => {
  if (!currentCourseId.value) return;
  loading.value = true;
  graphData.nodes = [];
  try {
    const res = await axios.get(`http://localhost:8000/student/knowledge-graph/${currentCourseId.value}`, getAuthHeaders());
    Object.assign(graphData, res.data);
    nextTick(() => { if (graphData.nodes && graphData.nodes.length > 0) initChart(res.data); });
  } catch (error) { ElMessage.error("获取失败"); } finally { loading.value = false; }
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
  flex-wrap: wrap;
  gap: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  white-space: nowrap;
}

.course-select {
  margin-left: 20px;
  width: 220px;
}

.chart-wrapper {
  min-height: 500px;
  position: relative;
}

.echart-box {
  width: 100%;
  height: 500px;
}

.empty-tip {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #909399;
  font-size: 14px;
  background: #fcfcfc;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.legend-info {
  margin-top: 15px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
  font-size: 13px;
  color: #606266;
}

.legend-item {
  display: flex;
  align-items: center;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 5px;
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

@media (max-width: 768px) {
  .graph-container {
    padding: 10px;
  }

  .course-select {
    margin-left: 10px;
    flex: 1;
    width: auto;
  }

  .refresh-btn {
    padding: 8px;
  }

  .chart-wrapper,
  .echart-box {
    min-height: 350px;
    height: 350px;
  }

  .legend-note {
    width: 100%;
    margin-left: 0;
    margin-top: 5px;
  }
}
</style>