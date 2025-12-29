<template>
  <div class="study-room">
    <div class="room-header">
      <el-button link @click="$router.push('/student')">
        <el-icon><ArrowLeft /></el-icon> 返回首页
      </el-button>
      <span class="course-title">{{ courseTitle }}</span>
    </div>

    <el-row :gutter="20" class="main-content">
      <el-col :span="16">
        <el-card shadow="never" class="player-card">
          <div v-if="currentResource" class="player-wrapper">
            <video 
              v-if="currentResource.type === 'video'" 
              :src="currentResource.url" 
              controls 
              autoplay
              class="video-player"
            ></video>
            
            <div v-else class="doc-viewer">
              <el-icon :size="60" color="#409EFF"><Document /></el-icon>
              <h3>{{ currentResource.title }}</h3>
              <p>这是一个文档资源</p>
              <el-button type="primary" tag="a" :href="currentResource.url" target="_blank">
                下载/预览文档
              </el-button>
            </div>
          </div>
          
          <div v-else class="empty-player">
            <el-empty description="请在右侧选择要学习的资源" />
          </div>
          <div style="margin-top: 20px; padding-top: 20px; border-top: 1px dashed #eee; text-align: center;">
  <p style="font-size: 12px; color: #999; margin-bottom: 10px;">已完成所有学习任务？</p>
  <el-button type="success" style="width: 100%" @click="$router.push(`/quiz/${courseId}`)">
    📝 参加课程结业测验
  </el-button>
</div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="never" header="📚 课程目录">
          <el-scrollbar height="500px">
            <div v-if="resources.length === 0" style="color: #999; text-align: center; padding: 20px;">
              老师还没上传资源哦~
            </div>
            <ul class="resource-list">
              <li 
                v-for="(res, index) in resources" 
                :key="res.id"
                :class="{ active: currentResource && currentResource.id === res.id }"
                @click="playResource(res)"
              >
                <div class="res-icon">
                  <el-icon v-if="res.type === 'video'"><VideoPlay /></el-icon>
                  <el-icon v-else><Document /></el-icon>
                </div>
                <div class="res-info">
                  <div class="res-title">第 {{ index + 1 }} 节：{{ res.title }}</div>
                  <div class="res-type">{{ res.type === 'video' ? '视频' : '文档' }}</div>
                </div>
                <el-icon v-if="currentResource && currentResource.id === res.id" color="#67C23A"><Select /></el-icon>
              </li>
            </ul>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ArrowLeft, VideoPlay, Document, Select } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const courseId = route.params.id
const courseTitle = route.query.title || '课程学习'

const resources = ref([])
const currentResource = ref(null)

const fetchResources = async () => {
  try {
    const res = await axios.get(`http://localhost:8000/student/course/${courseId}/resources`)
    resources.value = res.data
    // 如果有资源，默认播放第一个
    if (resources.value.length > 0) {
      currentResource.value = resources.value[0]
    }
  } catch (error) {
    console.error("获取资源失败", error)
  }
}

const playResource = (res) => {
  currentResource.value = res
}

onMounted(() => {
  fetchResources()
})
</script>

<style scoped>
.study-room { height: 100vh; background: #f5f7fa; display: flex; flex-direction: column; }
.room-header { background: white; padding: 0 20px; height: 60px; display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); z-index: 10; }
.course-title { font-size: 18px; font-weight: bold; margin-left: 15px; border-left: 3px solid #409EFF; padding-left: 10px; }
.main-content { padding: 20px; flex: 1; }

.player-card { height: 100%; min-height: 500px; display: flex; flex-direction: column; }
.player-wrapper { width: 100%; height: 100%; }
.video-player { width: 100%; height: 100%; max-height: 550px; background: black; border-radius: 4px; }
.doc-viewer { height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f9f9f9; border: 2px dashed #eee; }
.empty-player { height: 400px; display: flex; align-items: center; justify-content: center; }

.resource-list { list-style: none; padding: 0; margin: 0; }
.resource-list li { padding: 15px; border-bottom: 1px solid #f0f0f0; cursor: pointer; display: flex; align-items: center; transition: all 0.2s; }
.resource-list li:hover { background: #ecf5ff; }
.resource-list li.active { background: #ecf5ff; border-left: 3px solid #409EFF; }
.res-icon { margin-right: 12px; font-size: 20px; color: #909399; }
.res-info { flex: 1; }
.res-title { font-size: 14px; margin-bottom: 4px; }
.res-type { font-size: 12px; color: #999; }
</style>