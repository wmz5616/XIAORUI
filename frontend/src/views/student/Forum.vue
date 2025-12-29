<template>
  <div class="forum-container">
    <div class="header-action">
      <h2>💬 学习讨论区</h2>
      <el-button type="primary" size="large" @click="dialogVisible = true">
        + 我要提问
      </el-button>
    </div>

    <el-timeline style="margin-top: 30px;">
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
            <el-tag size="small" :type="post.role === 'teacher' ? 'warning' : ''">
              {{ post.author_name }} ({{ post.role === 'teacher' ? '老师' : '同学' }})
            </el-tag>
          </div>
          <p class="post-content">{{ post.content }}</p>
          <div class="post-footer">
            <el-button type="text" size="small">回复</el-button>
            <el-button type="text" size="small">点赞</el-button>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>

    <el-dialog v-model="dialogVisible" title="发起提问" width="500px">
      <el-form :model="form">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请简要描述你的问题" />
        </el-form-item>
        <el-form-item label="详细内容">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请详细描述..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPost" :loading="loading">发布</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const posts = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const form = reactive({ title: '', content: '' })

// 格式化时间
const formatDate = (isoStr) => {
  const date = new Date(isoStr)
  return date.toLocaleString()
}

// 获取帖子列表
const fetchPosts = async () => {
  try {
    const res = await axios.get('http://localhost:8000/forum/posts')
    posts.value = res.data
  } catch (error) {
    console.error(error)
  }
}

// 提交帖子
const submitPost = async () => {
  if(!form.title || !form.content) return ElMessage.warning("请填写完整")
  
  loading.value = true
  const token = localStorage.getItem('token') // 获取登录 Token
  
  try {
    // 注意：发帖需要鉴权，必须带 Header
    await axios.post('http://localhost:8000/forum/posts', form, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    ElMessage.success("发布成功！")
    dialogVisible.value = false
    form.title = ''
    form.content = ''
    fetchPosts() // 刷新列表
  } catch (error) {
    ElMessage.error("发布失败，请检查是否登录")
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPosts()
})
</script>

<style scoped>
.forum-container { max-width: 900px; margin: 0 auto; padding: 20px; }
.header-action { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 20px; }
.post-title { font-size: 18px; font-weight: bold; margin-right: 10px; }
.post-header { display: flex; align-items: center; margin-bottom: 10px; }
.post-content { color: #555; line-height: 1.6; }
.post-footer { margin-top: 15px; border-top: 1px dashed #eee; padding-top: 10px; text-align: right; }
</style>