<template>
  <div class="dashboard-container">
    <div class="top-actions">
      <el-button type="success" @click="$router.push('/student/graph')">
        <el-icon style="margin-right: 5px">
          <DataLine />
        </el-icon> 查看知识图谱
      </el-button>
      
      <el-button type="warning" @click="$router.push('/student/diagnostic')">
        <el-icon style="margin-right: 5px">
          <FirstAidKit />
        </el-icon> 智能诊断测试
      </el-button>

      <el-button type="primary" plain @click="$router.push('/forum')">
        <el-icon style="margin-right: 5px">
          <ChatDotRound />
        </el-icon> 进入讨论区
      </el-button>
    </div>

    <el-card class="box-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span> AI学习助手</span>
        </div>
      </template>

      <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <el-input 
          v-model="weakPoint" 
          placeholder="请输入你的薄弱知识点（如：三角函数），AI 将为你规划路径" 
          style="max-width: 500px;" 
          clearable
          @keyup.enter="getAIPath" 
        />
        <el-button type="primary" @click="getAIPath" :loading="aiLoading">
          <el-icon style="margin-right: 5px">
            <MagicStick />
          </el-icon> 生成个性化路径
        </el-button>
      </div>

      <div v-if="aiResult" class="ai-result-area">
        <el-alert 
          title="AI 诊断分析" 
          type="success" 
          :description="aiResult.logic_reasoning" 
          show-icon 
          :closable="false"
          style="margin-bottom: 20px;" 
        />
        <el-timeline>
          <el-timeline-item 
            v-for="(step, index) in aiResult.recommended_steps" 
            :key="index" 
            type="primary"
            :hollow="true" 
            :timestamp="'步骤 ' + (index + 1)"
          >
            {{ step }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>

    <h3 style="margin-top: 30px; display: flex; align-items: center;">
      推荐课程
      <el-tag type="info" size="small" style="margin-left: 10px">实时更新</el-tag>
    </h3>

    <div v-if="loading" style="text-align: center; padding: 40px; color: #909399;">
      <el-icon class="is-loading" style="font-size: 24px; vertical-align: middle; margin-right: 8px;">
        <Loading />
      </el-icon>
      <span>加载课程库中...</span>
    </div>

    <el-row :gutter="20" v-else>
      <el-col :span="8" v-for="course in courses" :key="course.id">
        <el-card shadow="hover" class="course-card" @click="startLearning(course)">
          <div class="card-content">
            <div class="cover-placeholder">{{ course.title[0] }}</div>
            <div class="info">
              <span class="course-title">{{ course.title }}</span>
              <p class="desc">{{ course.description || '暂无介绍' }}</p>
              <el-button type="primary" link>开始学习</el-button>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="24" v-if="courses.length === 0">
        <el-empty description="老师暂时还没有发布课程哦~" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { DataLine, ChatDotRound, MagicStick, Loading, FirstAidKit } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const weakPoint = ref('')
const aiResult = ref(null)
const aiLoading = ref(false)
const courses = ref([])
const loading = ref(false)

const getAIPath = async () => {
  if (!weakPoint.value) return ElMessage.warning('请先输入薄弱知识点')

  aiLoading.value = true
  aiResult.value = null
  
  const currentUsername = localStorage.getItem('username') || "同学"

  try {
    const res = await axios.post('http://localhost:8000/ai-engine/learning-path', {
      name: currentUsername,
      grade: 10,
      weak_subjects: [weakPoint.value]
    }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    
    aiResult.value = res.data
    ElMessage.success('AI 路径规划完成！')
  } catch (error) {
    console.error(error)
    ElMessage.error(error.response?.data?.error || 'AI 服务连接异常')
  } finally {
    aiLoading.value = false
  }
}

const fetchCourses = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8000/student/courses')
    courses.value = res.data
  } catch (error) {
    console.error("获取课程失败:", error)
  } finally {
    loading.value = false
  }
}

const startLearning = (course) => {
  router.push({
    path: `/learn/${course.id}`,
    query: { title: course.title }
  })
}

onMounted(() => {
  fetchCourses()
  if (route.query.auto_weakness) {
    weakPoint.value = route.query.auto_weakness
    setTimeout(() => {
      getAIPath()
    }, 500)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.top-actions {
  margin-bottom: 20px;
  text-align: right;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
  display: flex; 
  justify-content: flex-end;
  gap: 10px;
}

.course-card {
  cursor: pointer;
  transition: transform 0.2s;
  margin-bottom: 20px;
}

.course-card:hover {
  transform: translateY(-5px);
}

.card-content {
  display: flex;
  align-items: center;
}

.cover-placeholder {
  width: 60px;
  height: 60px;
  background: #409EFF;
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.info {
  flex: 1;
  overflow: hidden;
}

.course-title {
  font-weight: bold;
  font-size: 16px;
  display: block;
  margin-bottom: 5px;
  color: #303133;
}

.desc {
  font-size: 13px;
  color: #909399;
  margin: 0 0 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>