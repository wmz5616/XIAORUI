<template>
  <div class="dashboard-container">
    <div class="top-actions">
      <el-button type="success" @click="$router.push('/student/graph')">
        🌌 查看知识图谱 (3D)
      </el-button>
      <el-button type="primary" plain @click="$router.push('/forum')">
        💬 进入讨论区
      </el-button>
    </div>

    <el-card class="box-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>🤖 AI 学习助手 (豆包驱动)</span>
        </div>
      </template>

      <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <el-input v-model="weakPoint" placeholder="请输入你的薄弱知识点，例如：三角函数、牛顿第二定律" style="max-width: 500px;" clearable
          @keyup.enter="getAIPath" />
        <el-button type="primary" @click="getAIPath" :loading="aiLoading">
          生成个性化路径
        </el-button>
      </div>

      <div v-if="aiResult" class="ai-result-area">
        <el-alert title="AI 诊断分析" type="success" :description="aiResult.logic_reasoning" show-icon :closable="false"
          style="margin-bottom: 20px;" />
        <el-timeline>
          <el-timeline-item v-for="(step, index) in aiResult.recommended_steps" :key="index" type="primary"
            :hollow="true" :timestamp="'步骤 ' + (index + 1)">
            {{ step }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>

    <h3 style="margin-top: 30px; display: flex; align-items: center;">
      📚 推荐课程
      <el-tag type="info" size="small" style="margin-left: 10px">实时更新</el-tag>
    </h3>

    <el-row :gutter="20">
      <el-col :span="8" v-for="course in courses" :key="course.id">
        <el-card shadow="hover" class="course-card" @click="startLearning(course)">
          <img :src="`https://picsum.photos/seed/${course.id}/300/150`" class="course-cover" />
          <div style="padding: 14px">
            <span class="course-title">{{ course.title }}</span>
            <div class="bottom">
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
import { useRouter } from 'vue-router'

const router = useRouter()

// --- 数据状态 ---
const weakPoint = ref('')
const aiResult = ref(null)
const aiLoading = ref(false)
const courses = ref([]) // 存储从后端获取的课程列表

// 1. 获取 AI 路径
const getAIPath = async () => {
  if (!weakPoint.value) return ElMessage.warning('请先输入薄弱知识点')

  aiLoading.value = true
  aiResult.value = null

  try {
    // 调用后端 AI 引擎接口
    const res = await axios.post('http://localhost:8000/ai-engine/learning-path', {
      name: "当前学生",
      grade: 10,
      weak_subjects: [weakPoint.value]
    })
    aiResult.value = res.data
    ElMessage.success('AI 路径规划完成！')
  } catch (error) {
    console.error(error)
    ElMessage.error('AI 服务响应超时，请检查后端终端是否卡死')
  } finally {
    aiLoading.value = false
  }
}

// 2. 获取课程列表 (初始化时调用)
const fetchCourses = async () => {
  try {
    const res = await axios.get('http://localhost:8000/student/courses')
    courses.value = res.data
  } catch (error) {
    console.error("获取课程失败:", error)
    // 不弹窗报错，避免打扰用户，控制台记录即可
  }
}

// 3. 跳转到学习教室
const startLearning = (course) => {
  // 跳转路由：/learn/1?title=课程名
  router.push({
    path: `/learn/${course.id}`,
    query: { title: course.title }
  })
}

// 页面加载时执行
onMounted(() => {
  fetchCourses()
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
}

/* 课程卡片样式 */
.course-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 20px;
  border: none;
}

.course-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.course-cover {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
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
  margin: 0;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 移动端适配微调 */
@media (max-width: 768px) {
  .el-col {
    width: 100% !important;
  }
}
</style>