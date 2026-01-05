<template>
  <div class="forum-container">
    <div class="header">
      <h2>课程讨论区</h2>
      <button v-if="!isSilenced" @click="showPostModal = true" class="btn-primary">发布新帖</button>
    </div>

    <div class="posts-list">
      <div v-for="post in posts" :key="post.id" class="post-card">
        <div class="post-header">
          <span class="author-tag" :class="post.role">{{ getRoleLabel(post.role) }}</span>
          <span class="author-name">{{ post.author_name }}</span>
          <span class="post-time">{{ formatDate(post.created_at) }}</span>
          <span v-if="post.is_pinned" class="pinned-tag">置顶</span>
        </div>

        <h3 class="post-title">{{ post.title }}</h3>
        <p class="post-content">{{ post.content }}</p>

        <div class="post-actions">
          <button @click="toggleLike(post)" :class="{ 'liked': post.is_liked }">
            ❤️ {{ post.like_count }}
          </button>
          <button @click="togglePostReply(post.id)">
            💬 {{ post.reply_count }} 评论
          </button>

          <div v-if="isTeacherOrAdmin" class="admin-actions">
            <button @click="togglePin(post)">{{ post.is_pinned ? '取消置顶' : '置顶' }}</button>
            <button @click="deletePost(post.id)" class="text-red">删除帖子</button>
          </div>
        </div>

        <div class="replies-section">
          <div v-if="activeReplyPostId === post.id" class="reply-input-box">
            <textarea v-model="newReplyContent" placeholder="写下你的评论..."></textarea>
            <div class="reply-actions">
              <button @click="submitReply(post.id)" class="btn-submit">发送</button>
              <button @click="activeReplyPostId = null" class="btn-cancel">取消</button>
            </div>
          </div>

          <div v-if="post.replies && post.replies.length > 0" class="replies-list">
            <div v-for="reply in getRootReplies(post.replies)" :key="reply.id" class="reply-item"
              :class="{ 'hidden-item': reply.is_hidden }">
              <div class="reply-header">
                <span class="reply-author" :class="reply.role">{{ reply.author_name }}</span>
                <span class="reply-role" v-if="reply.role === 'teacher'"> (老师)</span>
                <span class="reply-time">{{ formatDate(reply.created_at) }}</span>
                <span v-if="reply.is_hidden" class="hidden-badge">已隐藏</span>
              </div>

              <div class="reply-content">{{ reply.content }}</div>

              <div class="reply-footer">
                <button @click="openSubReply(post.id, reply)" class="btn-text">回复</button>

                <div v-if="isTeacherOrAdmin" class="reply-manage">
                  <button @click="toggleHideReply(reply)">{{ reply.is_hidden ? '显示' : '隐藏' }}</button>
                  <button @click="deleteReply(reply.id)" class="text-red">删除</button>
                </div>
              </div>

              <div class="sub-replies">
                <div v-for="sub in getSubReplies(post.replies, reply.id)" :key="sub.id" class="sub-reply-item"
                  :class="{ 'hidden-item': sub.is_hidden }">
                  <div class="reply-header">
                    <span class="reply-author">{{ sub.author_name }}</span>
                    <span class="reply-role" v-if="sub.role === 'teacher'"> (老师)</span>
                    <span class="reply-time">{{ formatDate(sub.created_at) }}</span>
                    <span v-if="sub.is_hidden" class="hidden-badge">已隐藏</span>
                  </div>
                  <div class="reply-content">
                    回复 <span class="reply-target">@{{ reply.author_name }}</span>: {{ sub.content }}
                  </div>
                  <div class="reply-footer">
                    <div v-if="isTeacherOrAdmin" class="reply-manage">
                      <button @click="toggleHideReply(sub)">{{ sub.is_hidden ? '显示' : '隐藏' }}</button>
                      <button @click="deleteReply(sub.id)" class="text-red">删除</button>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="replyingToId === reply.id" class="sub-reply-input">
                <input v-model="subReplyContent" :placeholder="'回复 ' + reply.author_name" />
                <button @click="submitSubReply(post.id, reply.id)">回复</button>
                <button @click="replyingToId = null" class="btn-cancel">取消</button>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showPostModal" class="modal-overlay">
      <div class="modal-content">
        <h3>发布新讨论</h3>
        <input v-model="newPost.title" placeholder="标题" class="input-title" />
        <textarea v-model="newPost.content" placeholder="内容详情..." class="input-content"></textarea>
        <div class="modal-actions">
          <button @click="createPost" class="btn-primary">发布</button>
          <button @click="showPostModal = false" class="btn-cancel">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';

import axios from 'axios';

const posts = ref([]);
const showPostModal = ref(false);
const newPost = ref({ title: '', content: '' });
const newReplyContent = ref('');
const subReplyContent = ref('');
const activeReplyPostId = ref(null); 
const replyingToId = ref(null);     
const userRole = localStorage.getItem('user_role') || 'student';
const isSilenced = ref(false);

const isTeacherOrAdmin = computed(() => {
  return ['teacher', 'admin'].includes(userRole);
});

const fetchPosts = async () => {
  try {
    const token = localStorage.getItem('token');
    const res = await axios.get('http://localhost:8000/forum/posts', {
      headers: { Authorization: `Bearer ${token}` }
    });
    posts.value = res.data;
  } catch (error) {
    console.error("加载失败", error);
  }
};

const getRootReplies = (replies) => {
  return replies.filter(r => !r.parent_id);
};

const getSubReplies = (replies, parentId) => {
  return replies.filter(r => r.parent_id === parentId);
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

const getRoleLabel = (role) => {
  const map = { teacher: '教师', admin: '管理员', student: '学生' };
  return map[role] || '用户';
};

const createPost = async () => {
  if (!newPost.value.title || !newPost.value.content) return alert("请填写完整");
  try {
    const token = localStorage.getItem('token');
    await axios.post('http://localhost:8000/forum/posts', newPost.value, {
      headers: { Authorization: `Bearer ${token}` }
    });
    showPostModal.value = false;
    newPost.value = { title: '', content: '' };
    fetchPosts();
  } catch (err) {
    alert(err.response?.data?.detail || "发布失败");
  }
};

const toggleLike = async (post) => {
  try {
    const token = localStorage.getItem('token');
    await axios.post(`http://localhost:8000/forum/posts/${post.id}/like`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPosts();
  } catch (err) {
    console.error(err);
  }
};

const togglePostReply = (postId) => {
  activeReplyPostId.value = activeReplyPostId.value === postId ? null : postId;
  newReplyContent.value = '';
};

const submitReply = async (postId) => {
  if (!newReplyContent.value) return;
  try {
    const token = localStorage.getItem('token');
    await axios.post(`http://localhost:8000/forum/posts/${postId}/reply`, {
      content: newReplyContent.value
    }, { headers: { Authorization: `Bearer ${token}` } });

    newReplyContent.value = '';
    activeReplyPostId.value = null;
    fetchPosts();
  } catch (err) {
    alert(err.response?.data?.detail || "回复失败");
  }
};

const openSubReply = (postId, reply) => {
  replyingToId.value = reply.id;
  subReplyContent.value = '';
};

const submitSubReply = async (postId, parentId) => {
  if (!subReplyContent.value) return;
  try {
    const token = localStorage.getItem('token');
    await axios.post(`http://localhost:8000/forum/posts/${postId}/reply`, {
      content: subReplyContent.value,
      parent_id: parentId
    }, { headers: { Authorization: `Bearer ${token}` } });

    subReplyContent.value = '';
    replyingToId.value = null;
    fetchPosts();
  } catch (err) {
    alert(err.response?.data?.detail || "回复失败");
  }
};

const toggleHideReply = async (reply) => {
  try {
    const token = localStorage.getItem('token');
    await axios.put(`http://localhost:8000/forum/replies/${reply.id}/hide`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPosts();
  } catch (err) {
    alert("操作失败");
  }
};

const deleteReply = async (replyId) => {
  if (!confirm("确定删除这条评论吗？")) return;
  try {
    const token = localStorage.getItem('token');
    await axios.delete(`http://localhost:8000/forum/replies/${replyId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPosts();
  } catch (err) {
    alert("删除失败");
  }
};

const togglePin = async (post) => {
  try {
    const token = localStorage.getItem('token');
    await axios.put(`http://localhost:8000/forum/posts/${post.id}/pin`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPosts();
  } catch (err) {
    alert("操作失败");
  }
};

const deletePost = async (postId) => {
  if (!confirm("确定删除整个帖子吗？")) return;
  try {
    const token = localStorage.getItem('token');
    await axios.delete(`http://localhost:8000/forum/posts/${postId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    fetchPosts();
  } catch (err) {
    alert("删除失败");
  }
};

onMounted(() => {
  fetchPosts();
});
</script>

<style scoped>
.forum-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.post-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.post-header {
  display: flex;
  gap: 10px;
  font-size: 0.9em;
  color: #666;
  margin-bottom: 10px;
}

.author-tag {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8em;
}

.author-tag.teacher {
  background: #e3f2fd;
  color: #1976d2;
}

.author-tag.admin {
  background: #fce4ec;
  color: #c2185b;
}

.author-tag.student {
  background: #f5f5f5;
  color: #616161;
}

.pinned-tag {
  background: #fff3cd;
  color: #856404;
  padding: 0 5px;
  border-radius: 3px;
}

.post-title {
  margin: 0 0 10px 0;
  color: #333;
}

.post-content {
  color: #444;
  line-height: 1.6;
  margin-bottom: 15px;
}

.post-actions {
  display: flex;
  gap: 15px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.post-actions button {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  font-size: 0.9em;
}

.post-actions button.liked {
  color: #e91e63;
}

.admin-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.text-red {
  color: #f44336 !important;
}

.replies-list {
  margin-top: 15px;
}

.reply-item {
  border-bottom: 1px solid #f9f9f9;
  padding: 10px 0;
}

.hidden-item {
  opacity: 0.6;
  background: #fafafa;
}

.hidden-badge {
  background: #eee;
  color: #999;
  font-size: 0.7em;
  padding: 1px 4px;
  margin-left: 5px;
}

.reply-header {
  font-size: 0.85em;
  color: #888;
  margin-bottom: 4px;
}

.reply-author {
  font-weight: bold;
  color: #333;
}

.reply-role {
  color: #1976d2;
  font-size: 0.8em;
}

.reply-content {
  font-size: 0.95em;
  color: #333;
  margin-bottom: 6px;
}

.reply-footer {
  display: flex;
  gap: 10px;
  font-size: 0.8em;
}

.reply-manage {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.btn-text {
  background: none;
  border: none;
  color: #1976d2;
  cursor: pointer;
  padding: 0;
}

.sub-replies {
  margin-left: 20px;
  margin-top: 8px;
  padding-left: 10px;
  border-left: 2px solid #f0f0f0;
}

.sub-reply-item {
  margin-top: 8px;
  padding: 5px;
  background: #fdfdfd;
}

.reply-target {
  color: #1976d2;
  font-weight: 500;
}

.reply-input-box textarea {
  width: 100%;
  height: 60px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.sub-reply-input {
  margin-top: 5px;
  display: flex;
  gap: 5px;
}

.sub-reply-input input {
  flex: 1;
  padding: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.reply-actions {
  margin-top: 5px;
  display: flex;
  gap: 10px;
}

.btn-submit {
  background: #1976d2;
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-cancel {
  background: #ddd;
  color: #333;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
}

.input-title {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
}

.input-content {
  width: 100%;
  height: 100px;
  padding: 8px;
  margin-bottom: 10px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>