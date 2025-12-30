<template>
  <div class="profile-container">
    <el-row :gutter="20">

      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <div class="avatar-area">
            <el-avatar :size="100" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
            <h2 class="name">{{ profile.full_name }}</h2>
            <el-tag>{{ profile.role === 'student' ? '学生' : '教师' }}</el-tag>
          </div>
          <el-divider />
          <div class="stats-row">
            <div class="stat-item">
              <div class="num">{{ profile.learn_time }}</div>
              <div class="label">学习分钟</div>
            </div>
            <div class="stat-item">
              <div class="num">{{ profile.finished_courses }}</div>
              <div class="label">已掌握课程</div>
            </div>
          </div>
          <el-divider />
          <el-button type="danger" plain style="width: 100%" @click="logout">退出登录</el-button>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card shadow="hover" header="个人能力画像">
          <div id="radar-chart" style="width: 100%; height: 400px;"></div>
          <div class="chart-tips">
            <p>💡 <strong>数据说明：</strong> 能力值基于你通过的<strong>测验数量</strong>动态计算。</p>
            <p>通过更多课程测验，点亮更多知识点，雷达图将自动扩张。</p>
          </div>
        </el-card>
      </el-col>

    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'

const router = useRouter()
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
    const res = await axios.get('http://localhost:8000/student/profile', {
      headers: { Authorization: `Bearer ${token}` }
    })
    profile.value = res.data
    initRadar(res.data.ability_radar)
  } catch (error) {
    console.error(error)
  }
}

const initRadar = (data) => {
  const chartDom = document.getElementById('radar-chart')
  if (echarts.getInstanceByDom(chartDom)) {
    echarts.dispose(chartDom);
  }
  const myChart = echarts.init(chartDom)

  const option = {
    radar: {
      indicator: [
        { name: '记忆力', max: 100 },
        { name: '理解力', max: 100 },
        { name: '应用力', max: 100 },
        { name: '分析力', max: 100 },
        { name: '创造力', max: 100 }
      ],
      shape: 'circle',
      splitNumber: 5,
      axisName: { color: '#428BD4', fontSize: 14 }
    },
    series: [
      {
        name: '能力维度',
        type: 'radar',
        data: [
          {
            value: data,
            name: '当前能力',
            areaStyle: { color: 'rgba(64, 158, 255, 0.4)' },
            itemStyle: { color: '#409EFF' },
            lineStyle: { width: 2 }
          }
        ]
      }
    ]
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
  padding: 20px 0;
}

.name {
  margin: 10px 0 5px;
  color: #303133;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.num {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.label {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.chart-tips {
  margin-top: 20px;
  background: #fdf6ec;
  padding: 15px;
  border-radius: 4px;
  color: #e6a23c;
  font-size: 14px;
}
</style>