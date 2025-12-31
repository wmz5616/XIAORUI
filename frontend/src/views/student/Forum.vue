<template>
  <div class="forum-container">
    <div class="header-action">
      <div class="header-text">
        <h2>学习讨论区</h2>
        <p class="subtitle">与同学和老师交流，解决学习难题</p>
      </div>
      <el-button type="primary" size="large" icon="Edit" @click="dialogVisible = true">我要提问</el-button>
    </div>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading">
        <Loading />
      </el-icon> 加载中...
    </div>

    <div v-else-if="posts.length > 0" class="post-list">
      <div v-for="post in posts" :key="post.id" class="post-wrapper">
        <el-card shadow="hover" :class="{ 'pinned-card': post.is_pinned }">
          <div class="post-header">
            <el-tag v-if="post.is_pinned" type="danger" effect="dark" size="small" class="pin-tag">置顶</el-tag>
            <span class="post-title">{{ post.title }}</span>
            <div class="meta-info">
              <el-tag size="small" :type="post.role === 'teacher' ? 'warning' : 'info'" effect="plain">
                {{ post.author_name }} ({{ post.role === 'teacher' ? '教师' : '学生' }})
              </el-tag>
              <span class="time">{{ formatDate(post.created_at) }}</span>
            </div>
          </div>

          <p class="post-content">{{ post.content }}</p>

          <div class="post-footer">
            <div class="left-actions">
              <el-button :type="post.is_liked ? 'danger' : 'default'" link size="small" @click="toggleLike(post)">
                <el-icon>
                  <StarFilled v-if="post.is_liked" />
                  <Star v-else />
                </el-icon>
                {{ post.is_liked ? '已赞' : '点赞' }} ({{ post.like_count }})
              </el-button>

              <el-button type="primary" link size="small" @click="toggleReplyBox(post.id)">
                <el-icon>
                  <ChatDotRound />
                </el-icon>
                {{ activeReplyId === post.id ? '收起回复' : `回复 (${post.reply_count})` }}
              </el-button>
            </div>

            <div class="right-actions" v-if="userRole === 'teacher' || userRole === 'admin'">
              <el-button :type="post.is_pinned ? 'warning' : 'info'" link size="small" @click="togglePin(post)">
                {{ post.is_pinned ? '取消置顶' : '置顶' }}
              </el-button>
              <el-popconfirm title="确定删除此贴？" @confirm="deletePost(post.id)">
                <template #reference>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>

          <div v-if="activeReplyId === post.id" class="reply-section">
            <el-divider content-position="left">评论区</el-divider>

            <div v-if="post.replies && post.replies.length > 0" class="reply-list">
              <div v-for="reply in post.replies" :key="reply.id" class="reply-item">
                <div class="reply-user">
                  <span :class="{ 'teacher-name': reply.role === 'teacher' }">{{ reply.author_name }}:</span>
                </div>
                <div class="reply-content">{{ reply.content }}</div>
                <div class="reply-time">{{ formatDate(reply.created_at) }}</div>
              </div>
            </div>
            <div v-else class="empty-reply">暂无评论，快来抢沙发</div>

            <div class="reply-input">
              <el-input v-model="replyContent" placeholder="写下你的看法..." class="input-box"
                @keyup.enter="submitReply(post.id)">
                <template #append>
                  <el-button @click="submitReply(post.id)" :loading="replying">发送</el-button>
                </template>
              </el-input>
            </div>
          </div>

        </el-card>
      </div>
    </div>
    <el-empty v-else description="暂无讨论，快来提问吧！" />

    <el-dialog v-model="dialogVisible" title="发起提问" width="90%" style="max-width: 500px">
      <el-form :model="form">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="简要描述问题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="form.content" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPost" :loading="submitting">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Edit, Loading, ChatDotRound, Star, StarFilled } from '@element-plus/icons-vue'
import { jwtDecode } from "jwt-decode";

const posts = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const replying = ref(false)
const activeReplyId = ref(null)
const replyContent = ref("")
const form = reactive({ title: '', content: '' })
const userRole = ref('student')

const getAuth = () => ({ headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })

const checkRole = () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const decoded = jwtDecode(token)
      userRole.value = decoded.role
    } catch (e) {
      console.error("Token decode failed")
    }
  }
}

const formatDate = (str) => new Date(str).toLocaleString()

const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8000/forum/posts', getAuth())
    posts.value = res.data
  } catch (e) { ElMessage.error("获取列表失败") }
  finally { loading.value = false }
}

const submitPost = async () => {
  if (!form.title || !form.content) return ElMessage.warning("请填写完整")
  submitting.value = true
  try {
    await axios.post('http://localhost:8000/forum/posts', form, getAuth())
    ElMessage.success("发布成功")
    dialogVisible.value = false
    form.title = ''; form.content = ''
    fetchPosts()
  } catch (e) { ElMessage.error("发布失败") }
  finally { submitting.value = false }
}

const toggleLike = async (post) => {
  try {
    const res = await axios.post(`http://localhost:8000/forum/posts/${post.id}/like`, {}, getAuth())
    post.is_liked = res.data.is_liked
    post.like_count += res.data.is_liked ? 1 : -1
    ElMessage.success(res.data.msg)
  } catch (e) { ElMessage.error("操作失败") }
}

const toggleReplyBox = (pid) => {
  if (activeReplyId.value === pid) {
    activeReplyId.value = null
  } else {
    activeReplyId.value = pid
    replyContent.value = ""
  }
}

const submitReply = async (postId) => {
  if (!replyContent.value.trim()) return ElMessage.warning("内容不能为空")
  replying.value = true
  try {
    await axios.post(`http://localhost:8000/forum/posts/${postId}/reply`, { content: replyContent.value }, getAuth())
    ElMessage.success("回复成功")
    replyContent.value = ""
    fetchPosts()
  } catch (e) { ElMessage.error("回复失败") }
  finally { replying.value = false }
}

const deletePost = async (id) => {
  try {
    await axios.delete(`http://localhost:8000/forum/posts/${id}`, getAuth())
    ElMessage.success("已删除")
    fetchPosts()
  } catch (e) { ElMessage.error("删除失败") }
}

const togglePin = async (post) => {
  try {
    await axios.put(`http://localhost:8000/forum/posts/${post.id}/pin`, {}, getAuth())
    ElMessage.success("操作成功")
    fetchPosts()
  } catch (e) { ElMessage.error("操作失败") }
}

onMounted(() => {
  checkRole()
  fetchPosts()
})
</script>

<style scoped>
.forum-container {
  max-width: 900px;
  margin: 20px auto;
  padding: 0 15px;
}

.header-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f2f5;
  padding-bottom: 15px;
}

.post-wrapper {
  margin-bottom: 20px;
}

.pinned-card {
  border: 1px solid #ffcc99;
  background: #fffaf5;
}

.pin-tag {
  margin-right: 8px;
  vertical-align: text-bottom;
}

.post-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-right: 10px;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-info {
  margin-left: auto;
  font-size: 12px;
  color: #999;
}

.post-content {
  font-size: 14px;
  color: #555;
  line-height: 1.6;
  margin-bottom: 15px;
  white-space: pre-wrap;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #f0f0f0;
  padding-top: 10px;
}

.reply-section {
  background: #fafafa;
  padding: 15px;
  margin-top: 15px;
  border-radius: 4px;
}

.reply-item {
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
  font-size: 13px;
}

.reply-user {
  font-weight: bold;
  margin-bottom: 4px;
}

.teacher-name {
  color: #E6A23C;
}

.reply-time {
  color: #aaa;
  font-size: 12px;
  margin-top: 2px;
  text-align: right;
}

.reply-input {
  margin-top: 15px;
}

.empty-reply {
  text-align: center;
  color: #999;
  padding: 10px;
  font-size: 12px;
}
</style>