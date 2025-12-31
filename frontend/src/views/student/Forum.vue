<template>
  <div class="forum-container">
    <div class="header-action">
      <div class="header-text">
        <h2>学习讨论区</h2>
        <p class="subtitle">与同学和老师交流，解决学习难题</p>
      </div>
      <el-button type="primary" size="large" class="ask-btn" @click="dialogVisible = true">
        <el-icon style="margin-right: 5px">
          <Edit />
        </el-icon> 我要提问
      </el-button>
    </div>

    <div v-if="loading && posts.length === 0" class="loading-state">
      <el-icon class="is-loading">
        <Loading />
      </el-icon> 加载讨论中...
    </div>

    <div v-else-if="posts.length > 0" class="post-list">
      <div v-for="post in posts" :key="post.id" class="post-item-wrapper">
        <div class="mobile-time" v-if="isMobile">{{ formatDate(post.created_at) }}</div>

        <el-card shadow="hover" class="post-card" :body-style="{ padding: '15px' }">
          <div class="post-header">
            <span class="post-title">{{ post.title }}</span>
            <div class="badges">
              <el-tag size="small" effect="dark" :type="post.role === 'teacher' ? 'warning' : 'primary'">
                {{ post.author_name }}
              </el-tag>
              <span class="role-badge">{{ post.role === 'teacher' ? '教师' : '学生' }}</span>
            </div>
            <span class="pc-time" v-if="!isMobile">{{ formatDate(post.created_at) }}</span>
          </div>

          <p class="post-content">{{ post.content }}</p>

          <div class="post-footer">
            <el-button type="primary" link size="small"><el-icon>
                <ChatDotRound />
              </el-icon> 回复</el-button>
            <el-button type="success" link size="small"><el-icon>
                <Star />
              </el-icon> 点赞</el-button>
          </div>
        </el-card>
      </div>
    </div>

    <el-empty v-else description="还没有人发言，快来抢沙发吧！" />

    <el-dialog v-model="dialogVisible" title="发起提问" width="90%" style="max-width: 500px">
      <el-form :model="form" label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="一句话描述问题" />
        </el-form-item>
        <el-form-item label="详细内容">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请详细描述..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" style="width: 45%">取消</el-button>
        <el-button type="primary" @click="submitPost" :loading="submitting" style="width: 45%">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Edit, Loading, ChatDotRound, Star } from '@element-plus/icons-vue'

const posts = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const submitting = ref(false)
const form = reactive({ title: '', content: '' })
const isMobile = computed(() => window.innerWidth < 768)

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const date = new Date(isoStr)
  return isMobile.value ? date.toLocaleDateString() : date.toLocaleString()
}

const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8000/forum/posts')
    posts.value = res.data
  } catch (error) { ElMessage.error("获取帖子失败") } finally { loading.value = false }
}

const submitPost = async () => {
  if (!form.title || !form.content) return ElMessage.warning("请填写完整")
  submitting.value = true
  try {
    await axios.post('http://localhost:8000/forum/posts', form, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
    ElMessage.success("发布成功"); dialogVisible.value = false; form.title = ''; form.content = ''; fetchPosts()
  } catch (error) { ElMessage.error("发布失败") } finally { submitting.value = false }
}

onMounted(fetchPosts)
</script>

<style scoped>
.forum-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.header-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.subtitle {
  color: #999;
  font-size: 14px;
  margin-top: 5px;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.post-item-wrapper {
  margin-bottom: 20px;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.post-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-right: 10px;
}

.badges {
  display: flex;
  align-items: center;
}

.role-badge {
  font-size: 12px;
  color: #999;
  margin-left: 5px;
}

.pc-time {
  margin-left: auto;
  color: #ccc;
  font-size: 12px;
}

.mobile-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
  margin-left: 2px;
}

.post-content {
  color: #555;
  line-height: 1.6;
  font-size: 14px;
  white-space: pre-wrap;
}

.post-footer {
  margin-top: 10px;
  border-top: 1px solid #f9f9f9;
  padding-top: 8px;
  text-align: right;
}

@media (max-width: 768px) {
  .forum-container {
    padding: 15px;
  }

  .header-action {
    flex-direction: column;
    align-items: flex-start;
  }

  .ask-btn {
    width: 100%;
  }

  .post-title {
    width: 100%;
    margin-bottom: 5px;
    display: block;
  }

  .badges {
    width: 100%;
  }
}
</style>