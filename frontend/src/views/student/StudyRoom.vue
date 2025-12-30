<template>
  <div class="study-room">
    <div class="room-header">
      <el-button link @click="$router.push('/student')">
        <el-icon style="margin-right: 5px">
          <ArrowLeft />
        </el-icon> 退出学习
      </el-button>
      <span class="course-title">{{ courseTitle }}</span>
      <div style="flex: 1"></div>
      <el-tag type="info">沉浸式学习模式</el-tag>
    </div>

    <el-row :gutter="0" class="main-content">
      <el-col :span="18" style="height: 100%; padding: 20px;">
        <div class="player-container">
          <div v-if="currentResource" class="resource-viewer">
            <video v-if="currentResource.type === 'video'" :src="currentResource.url" controls
              class="video-player"></video>

            <div v-else class="doc-viewer">
              <el-icon :size="80" color="#409EFF">
                <Document />
              </el-icon>
              <h3>{{ currentResource.title }}</h3>
              <p>这是一个文档资源，请仔细阅读</p>
              <el-button type="primary" plain tag="a" :href="currentResource.url" target="_blank">
                在新窗口打开
              </el-button>
            </div>
          </div>

          <div v-else class="empty-state">
            <el-empty description="请从右侧目录选择一节课开始学习" />
          </div>
        </div>
      </el-col>

      <el-col :span="6" class="sidebar">
        <div class="sidebar-header">课程目录</div>
        <el-scrollbar class="resource-list-scroll">
          <div v-if="loading" style="padding: 20px; text-align: center; color: #999;">加载中...</div>
          <div v-else-if="resources.length === 0" style="padding: 20px; text-align: center; color: #999;">暂无资源</div>

          <ul class="resource-list">
            <li v-for="(res, index) in resources" :key="res.id"
              :class="{ active: currentResource && currentResource.id === res.id }" @click="playResource(res)">
              <div class="res-idx">{{ index + 1 }}</div>
              <div class="res-info">
                <div class="res-title">{{ res.title }}</div>
                <div class="res-meta">
                  <el-tag size="small" :type="res.type === 'video' ? 'primary' : 'warning'">
                    {{ res.type === 'video' ? '视频' : '文档' }}
                  </el-tag>
                </div>
              </div>
              <el-icon v-if="currentResource && currentResource.id === res.id" color="#409EFF">
                <VideoPlay />
              </el-icon>
            </li>
          </ul>
        </el-scrollbar>

        <div class="sidebar-footer">
          <el-button type="success" size="large" style="width: 100%" @click="$router.push(`/quiz/${courseId}`)">
            参加结业测验
          </el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ArrowLeft, VideoPlay, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const courseId = route.params.id
const courseTitle = route.query.title || '课程学习'

const resources = ref([])
const currentResource = ref(null)
const loading = ref(false)

const fetchResources = async () => {
  loading.value = true
  try {
    const res = await axios.get(`http://localhost:8000/student/course/${courseId}/resources`)
    resources.value = res.data
    if (resources.value.length > 0) {
      currentResource.value = resources.value[0]
    }
  } catch (error) {
    ElMessage.error("资源加载失败")
  } finally {
    loading.value = false
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
.study-room {
  height: 100vh;
  background: #1f1f1f;
  display: flex;
  flex-direction: column;
  color: #fff;
}

.room-header {
  background: #2b2b2b;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.course-title {
  font-size: 16px;
  font-weight: bold;
  margin-left: 15px;
  color: #fff;
}

.main-content {
  flex: 1;
  overflow: hidden;
}

.player-container {
  background: #000;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resource-viewer {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-player {
  width: 100%;
  max-height: 100%;
  outline: none;
}

.doc-viewer {
  text-align: center;
  color: #333;
  background: #fff;
  padding: 40px;
  border-radius: 8px;
  width: 80%;
  height: 80%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.sidebar {
  background: #2b2b2b;
  border-left: 1px solid #333;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 15px 20px;
  font-weight: bold;
  border-bottom: 1px solid #333;
  color: #eee;
}

.resource-list-scroll {
  flex: 1;
}

.resource-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.resource-list li {
  padding: 15px 20px;
  border-bottom: 1px solid #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.resource-list li:hover {
  background: #383838;
}

.resource-list li.active {
  background: #333;
  border-left: 3px solid #409EFF;
}

.res-idx {
  width: 24px;
  height: 24px;
  background: #444;
  border-radius: 50%;
  text-align: center;
  line-height: 24px;
  font-size: 12px;
  margin-right: 12px;
  color: #aaa;
}

.res-info {
  flex: 1;
}

.res-title {
  font-size: 14px;
  margin-bottom: 4px;
  color: #ddd;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #333;
}
</style>