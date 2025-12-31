<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="8" style="margin-bottom: 20px;">
        <el-card shadow="hover" class="info-card">
          <div class="avatar-area">
            <el-avatar :size="isMobile ? 80 : 100"
              src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
            <h2 class="name">{{ profile.full_name }}</h2>
            <el-tag size="small" effect="dark">{{ profile.role === 'student' ? '学生' : '教师' }}</el-tag>
          </div>
          <el-divider />
          <div class="stats-row">
            <div class="stat-item">
              <div class="num">{{ profile.learn_time }}</div>
              <div class="label">学习分钟</div>
            </div>
            <div class="stat-item">
              <div class="num">{{ profile.finished_courses }}</div>
              <div class="label">已修课程</div>
            </div>
          </div>
          <el-divider />
          <el-button type="danger" plain style="width: 100%" @click="logout">退出登录</el-button>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="16">
        <el-card shadow="hover" header="能力画像">
          <div id="radar-chart" class="radar-box"></div>
          <div class="chart-tips">
            <p>💡 <strong>数据说明：</strong> 基于您的测验成绩动态计算。</p>
            <p>通过更多课程测验，点亮更多知识点，雷达图将自动扩张。</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const router = useRouter()
const isMobile = computed(() => window.innerWidth < 768)

const profile = ref({
  full_name: '加载中...',
  role: '',
  learn_time: 0,
  finished_courses: 0,
  ability_radar: [50, 50, 50, 50, 50]
})

const logout = () => {
  localStorage.clear()
  router.push('/')
}

const fetchProfile = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) return router.push('/')

    const res = await axios.get('http://localhost:8000/student/profile', {
      headers: { Authorization: `Bearer ${token}` }
    })

    profile.value = res.data

    initRadar(res.data.ability_radar)
  } catch (error) {
    console.error(error)
    ElMessage.error("获取个人信息失败")
  }
}

const initRadar = (data) => {
  const chartDom = document.getElementById('radar-chart')
  if (!chartDom) return

  if (echarts.getInstanceByDom(chartDom)) {
    echarts.dispose(chartDom);
  }

  const myChart = echarts.init(chartDom)

  const option = {
    radar: {
      indicator: [
        { name: '记忆', max: 100 },
        { name: '理解', max: 100 },
        { name: '应用', max: 100 },
        { name: '分析', max: 100 },
        { name: '创造', max: 100 }
      ],
      shape: 'circle',
      radius: isMobile.value ? '60%' : '75%',
      axisName: { color: '#666', fontSize: 12 }
    },
    series: [{
      type: 'radar',
      data: [{
        value: data,
        name: '能力值',
        areaStyle: { color: 'rgba(64, 158, 255, 0.4)' },
        itemStyle: { color: '#409EFF' },
        lineStyle: { width: 2 }
      }]
    }]
  }
  myChart.setOption(option)

  window.addEventListener('resize', () => myChart.resize())
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.avatar-area {
  text-align: center;
  padding: 10px 0;
}

.name {
  margin: 10px 0 5px;
  color: #303133;
  font-size: 20px;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.num {
  font-size: 22px;
  font-weight: bold;
  color: #409EFF;
}

.label {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.radar-box {
  width: 100%;
  height: 400px;
}

.chart-tips {
  margin-top: 10px;
  background: #fdf6ec;
  padding: 10px;
  border-radius: 4px;
  color: #e6a23c;
  font-size: 13px;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 10px;
  }

  .radar-box {
    height: 300px;
  }
}
</style>