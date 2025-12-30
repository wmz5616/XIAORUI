<template>
  <div class="forum-container">
    <div class="header-action">
      <div>
        <h2>💬 学习讨论区</h2>
        <p class="subtitle">与同学和老师交流，解决学习难题</p>
      </div>
      <el-button type="primary" size="large" @click="dialogVisible = true">
        <el-icon style="margin-right: 5px"><Edit /></el-icon> 我要提问
      </el-button>
    </div>

    <div v-if="loading && posts.length === 0" style="padding: 40px; text-align: center; color: #909399;">
      <el-icon class="is-loading" style="font-size: 24px; vertical-align: middle; margin-right: 8px;">
        <Loading />
      </el-icon>
      <span>加载讨论中...</span>
    </div>

    <el-timeline style="margin-top: 30px;" v-else-if="posts.length > 0">
      <el-timeline-item 
        v-for="post in posts" 
        :key="post.id" 
        :timestamp="formatDate(post.created_at)" 
        placement="top"
        :color="post.role === 'teacher' ? '#E6A23C' : '#409EFF'"
      >
        <el-card shadow="hover" class="post-card">
          <div class="post-header">
            <span class="post-title">{{ post.title }}</span>
            <el-tag size="small" effect="dark" :type="post.role === 'teacher' ? 'warning' : 'primary'">
              {{ post.author_name }}
            </el-tag>
            <span class="role-badge">{{ post.role === 'teacher' ? '教师' : '学生' }}</span>
          </div>
          <p class="post-content">{{ post.content }}</p>
          <div class="post-footer">
            <el-button type="primary" link size="small">
              <el-icon style="margin-right: 3px"><ChatDotRound /></el-icon> 回复
            </el-button>
            <el-button type="success" link size="small">
              <el-icon style="margin-right: 3px"><Star /></el-icon> 点赞
            </el-button>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-else description="还没有人发言，快来抢沙发吧！" />

    <el-dialog v-model="dialogVisible" title="发起提问" width="500px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="例如：请问 Python 中的 List 和 Tuple 有什么区别？" />
        </el-form-item>
        <el-form-item label="详细内容">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请详细描述你的疑问..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPost" :loading="submitting">发布</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
// 显式导入所有用到的图标
import { Edit, Loading, ChatDotRound, Star } from '@element-plus/icons-vue'

const posts = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const submitting = ref(false)
const form = reactive({ title: '', content: '' })

const formatDate = (isoStr) => {
  if (!isoStr) return ''
  const date = new Date(isoStr)
  return date.toLocaleString()
}

const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8000/forum/posts')
    posts.value = res.data
  } catch (error) {
    ElMessage.error("获取帖子失败")
  } finally {
    loading.value = false
  }
}

const submitPost = async () => {
  if(!form.title || !form.content) return ElMessage.warning("请填写标题和内容")
  
  submitting.value = true
  const token = localStorage.getItem('token')
  
  try {
    await axios.post('http://localhost:8000/forum/posts', form, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    ElMessage.success("发布成功！")
    dialogVisible.value = false
    form.title = ''
    form.content = ''
    fetchPosts() 
  } catch (error) {
    if (error.response && error.response.status === 401) {
      ElMessage.error("登录已过期，请重新登录")
    } else {
      ElMessage.error("发布失败")
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.forum-container { max-width: 900px; margin: 0 auto; padding: 20px; }
.header-action { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f0f0f0; padding-bottom: 20px; margin-bottom: 20px; }
.subtitle { color: #999; margin: 5px 0 0; font-size: 14px; }
.post-card { border-radius: 8px; }
.post-title { font-size: 16px; font-weight: bold; margin-right: 10px; color: #333; }
.post-header { display: flex; align-items: center; margin-bottom: 12px; }
.role-badge { font-size: 12px; color: #999; margin-left: 5px; }
.post-content { color: #555; line-height: 1.6; white-space: pre-wrap; }
.post-footer { margin-top: 15px; border-top: 1px solid #f9f9f9; padding-top: 10px; text-align: right; }
</style>