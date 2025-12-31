<template>
  <div class="study-room">
    <div class="room-header">
      <el-button link @click="$router.push('/student')" style="color: #fff">
        <el-icon style="margin-right: 5px">
          <ArrowLeft />
        </el-icon> 退出学习
      </el-button>
      <span class="course-title">{{ courseTitle }}</span>
      <div style="flex: 1"></div>
      <el-tag type="info" size="small" effect="dark" class="mode-tag">沉浸模式</el-tag>
    </div>

    <el-row :gutter="0" class="main-content">
      <el-col :xs="24" :sm="18" class="player-col">
        <div class="player-wrapper">
          <div v-if="currentResource" class="resource-viewer">
            <video v-if="currentResource.type === 'video'" :src="currentResource.url" controls class="video-player"
              playsinline webkit-playsinline></video>

            <div v-else class="doc-viewer">
              <el-icon :size="60" color="#409EFF">
                <Document />
              </el-icon>
              <h3>{{ currentResource.title }}</h3>
              <p>文档资源请阅读</p>
              <el-button type="primary" plain tag="a" :href="currentResource.url" target="_blank" size="small">
                打开文档
              </el-button>
            </div>
          </div>

          <div v-else class="empty-state">
            <el-empty description="暂无资源或请选择资源" :image-size="100" />
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="6" class="sidebar-col">
        <div class="sidebar-header">课程目录</div>
        <div class="resource-list-container">
          <ul class="resource-list">
            <li v-for="(res, index) in resources" :key="res.id"
              :class="{ active: currentResource && currentResource.id === res.id }" @click="playResource(res)">
              <div class="res-idx">{{ index + 1 }}</div>
              <div class="res-info">
                <div class="res-title">{{ res.title }}</div>
                <div class="res-meta">
                  <el-tag size="small" :type="res.type === 'video' ? 'primary' : 'warning'" effect="plain">
                    {{ res.type === 'video' ? '视频' : '文档' }}
                  </el-tag>
                </div>
              </div>
              <el-icon v-if="currentResource && currentResource.id === res.id" color="#409EFF">
                <VideoPlay />
              </el-icon>
            </li>
          </ul>
          <el-empty v-if="resources.length === 0" description="老师暂未上传资源" :image-size="60" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ArrowLeft, VideoPlay, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const courseId = route.params.id
const courseTitle = route.query.title || '课程学习'

const resources = ref([])
const currentResource = ref(null)

const fetchResources = async () => {
  try {
    const res = await axios.get(`http://localhost:8000/student/course/${courseId}/resources`)
    resources.value = res.data
    if (resources.value.length > 0) {
      currentResource.value = resources.value[0]
    }
  } catch (error) {
    ElMessage.error("资源加载失败")
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
  display: flex;
  flex-direction: column;
  background: #1f1f1f;
  color: #fff;
  overflow: hidden;
}

.room-header {
  height: 50px;
  background: #2b2b2b;
  display: flex;
  align-items: center;
  padding: 0 10px;
  flex-shrink: 0;
  border-bottom: 1px solid #000;
}

.course-title {
  margin-left: 10px;
  font-weight: bold;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 50%;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: row;
  overflow: hidden;
}

.player-col {
  height: 100%;
  padding: 20px;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-wrapper {
  width: 100%;
  height: 100%;
  max-width: 1200px;
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
  background: #000;
}

.doc-viewer {
  background: #fff;
  color: #333;
  padding: 40px;
  border-radius: 8px;
  text-align: center;
  width: 80%;
  max-width: 500px;
}

.sidebar-col {
  background: #2b2b2b;
  border-left: 1px solid #333;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  padding: 15px;
  font-weight: bold;
  border-bottom: 1px solid #333;
  background: #333;
}

.resource-list-container {
  flex: 1;
  overflow-y: auto;
}

.resource-list {
  padding: 0;
  margin: 0;
  list-style: none;
}

.resource-list li {
  padding: 12px 15px;
  border-bottom: 1px solid #383838;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}

.resource-list li:hover {
  background: #333;
}

.resource-list li.active {
  background: #3a3a3a;
  border-left: 3px solid #409EFF;
}

.res-idx {
  width: 20px;
  height: 20px;
  background: #555;
  border-radius: 50%;
  text-align: center;
  line-height: 20px;
  font-size: 12px;
  margin-right: 10px;
  flex-shrink: 0;
}

.res-info {
  flex: 1;
  overflow: hidden;
}

.res-title {
  font-size: 13px;
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .study-room {
    height: auto;
    min-height: 100vh;
    overflow-y: auto;
  }

  .mode-tag {
    display: none;
  }

  .main-content {
    flex-direction: column;
  }

  .player-col {
    height: 40vh;
    padding: 0;
    order: 1;
  }

  .sidebar-col {
    height: 60vh;
    border-left: none;
    border-top: 1px solid #333;
    order: 2;
  }

  .video-player {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}
</style>