<template>
    <div class="courses-container">
        <div class="page-header">
            <h2>我的课程中心</h2>
            <p>探索知识的海洋，构建完整的知识体系</p>
        </div>

        <div class="course-grid" v-loading="loading">
            <el-card v-for="course in courses" :key="course.id" class="course-card" shadow="hover">
                <div class="course-cover">
                    <el-icon :size="50" color="#fff">
                        <Reading />
                    </el-icon>
                </div>
                <div class="course-info">
                    <h3 class="c-title" :title="course.title">{{ course.title }}</h3>
                    <p class="c-desc">{{ course.description || '暂无简介' }}</p>
                    <div class="c-meta">
                        <el-tag size="small" effect="plain">讲师ID: {{ course.teacher_id }}</el-tag>
                    </div>
                </div>
                <div class="course-actions">
                    <el-button type="primary" class="action-btn" @click="goStudy(course.id)">
                        开始学习
                    </el-button>
                    <el-button class="action-btn" @click="goGraph(course.id)">
                        <el-icon>
                            <Share />
                        </el-icon> 知识结构
                    </el-button>
                </div>
            </el-card>

            <el-empty v-if="!loading && courses.length === 0" description="暂无课程" class="empty-box" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Reading, Share } from '@element-plus/icons-vue'

const router = useRouter()
const courses = ref([])
const loading = ref(false)

onMounted(async () => {
    loading.value = true
    try {
        const token = localStorage.getItem('token')
        const res = await axios.get('http://localhost:8000/student/courses', {
            headers: { Authorization: `Bearer ${token}` }
        })
        courses.value = res.data
    } catch (e) {
        ElMessage.error('课程列表加载失败')
    } finally {
        loading.value = false
    }
})

const goStudy = (id) => {
    router.push(`/study/${id}`)
}

const goGraph = (id) => {
    router.push(`/student/knowledge-graph/${id}`)
}
</script>

<style scoped>
.courses-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.page-header {
    text-align: center;
    margin-bottom: 40px;
}

.page-header h2 {
    font-size: 28px;
    color: #303133;
    margin-bottom: 10px;
}

.page-header p {
    color: #909399;
}

.course-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

.course-card {
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.3s;
    display: flex;
    flex-direction: column;
}

.course-card:hover {
    transform: translateY(-5px);
}

.course-cover {
    height: 120px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    justify-content: center;
    align-items: center;
}

.course-info {
    padding: 15px;
    flex: 1;
}

.c-title {
    margin: 0 0 10px 0;
    font-size: 18px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.c-desc {
    font-size: 13px;
    color: #606266;
    margin-bottom: 15px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    height: 36px;
}

.course-actions {
    padding: 15px;
    border-top: 1px solid #ebeef5;
    display: flex;
    gap: 10px;
}

.action-btn {
    flex: 1;
}

.empty-box {
    grid-column: 1 / -1;
}
</style>