<template>
    <div class="homework-container">
        <div class="page-header">
            <h2>我的作业</h2>
            <p class="subtitle">查看并完成老师布置的课后作业</p>
        </div>

        <div v-if="loading" class="loading-state">
            <el-icon class="is-loading">
                <Loading />
            </el-icon> 加载中...
        </div>

        <div v-else-if="homeworks.length > 0" class="hw-grid">
            <el-card v-for="item in homeworks" :key="item.course_id" class="hw-card" shadow="hover">
                <template #header>
                    <div class="card-header">
                        <span class="course-name" :title="item.course_title">{{ item.course_title }}</span>
                        <el-tag :type="getStatusType(item.status)" effect="dark" size="small">
                            {{ getStatusText(item.status) }}
                        </el-tag>
                    </div>
                </template>

                <div class="card-body">
                    <div class="teacher-info">
                        <el-icon>
                            <User />
                        </el-icon> 授课教师：{{ item.teacher_name }}
                    </div>

                    <div class="progress-info">
                        <span>完成进度：</span>
                        <span class="nums">{{ item.answered_questions }} / {{ item.total_questions }} 题</span>
                    </div>
                    <el-progress :percentage="calculatePercent(item)"
                        :status="item.status === 'completed' ? 'success' : ''" :stroke-width="10"
                        class="progress-bar" />

                    <div class="actions">
                        <el-button type="primary" round style="width: 100%"
                            @click="goQuiz(item.course_id, item.course_title)" :disabled="item.total_questions === 0">
                            {{ item.status === 'completed' ? '查看成绩 / 重做' : '开始答题' }}
                        </el-button>
                    </div>
                </div>
            </el-card>
        </div>

        <el-empty v-else description="太棒了，目前没有待完成的作业！" />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Loading, User } from '@element-plus/icons-vue'

const router = useRouter()
const homeworks = ref([])
const loading = ref(false)

const fetchHomeworks = async () => {
    loading.value = true
    try {
        const token = localStorage.getItem('token')
        const res = await axios.get('http://localhost:8000/student/homeworks', {
            headers: { Authorization: `Bearer ${token}` }
        })
        homeworks.value = res.data
    } catch (error) {
        console.error("获取作业列表失败", error)
    } finally {
        loading.value = false
    }
}

const getStatusType = (status) => {
    const map = { 'pending': 'info', 'in_progress': 'warning', 'completed': 'success' }
    return map[status] || 'info'
}

const getStatusText = (status) => {
    const map = { 'pending': '未开始', 'in_progress': '进行中', 'completed': '已完成' }
    return map[status] || '未知'
}

const calculatePercent = (item) => {
    if (item.total_questions === 0) return 0
    return Math.floor((item.answered_questions / item.total_questions) * 100)
}

const goQuiz = (courseId, title) => {
    router.push({ path: `/quiz/${courseId}`, query: { title } })
}

onMounted(fetchHomeworks)
</script>

<style scoped>
.homework-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px;
}

.page-header {
    margin-bottom: 30px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

.subtitle {
    color: #888;
    font-size: 14px;
    margin-top: 5px;
}

.loading-state {
    text-align: center;
    padding: 40px;
    color: #999;
}

.hw-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.hw-card {
    border-radius: 8px;
    transition: transform 0.2s;
    border: none;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.hw-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.course-name {
    font-weight: bold;
    font-size: 16px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 65%;
    color: #333;
}

.card-body {
    padding: 10px 0;
}

.teacher-info {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 13px;
    color: #666;
    margin-bottom: 15px;
}

.progress-info {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    color: #666;
    margin-bottom: 8px;
}

.nums {
    font-weight: bold;
    color: #333;
}

.progress-bar {
    margin-bottom: 20px;
}

.actions {
    margin-top: 10px;
}
</style>