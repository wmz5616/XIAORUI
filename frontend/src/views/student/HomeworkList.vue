<template>
    <div class="homework-container">
        <div class="header-area">
            <h2>我的作业</h2>
            <p>查看待完成的作业和过往成绩</p>
        </div>

        <el-card shadow="hover" class="list-card">
            <el-table :data="homeworks" style="width: 100%" stripe v-loading="loading">
                <el-table-column prop="title" label="作业标题" min-width="150" />
                <el-table-column prop="course_title" label="所属课程" width="150" />
                <el-table-column prop="teacher_name" label="任课教师" width="120" />

                <el-table-column label="状态" width="120">
                    <template #default="scope">
                        <el-tag :type="getStatusType(scope.row.status)">
                            {{ getStatusText(scope.row.status) }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column label="得分" width="100">
                    <template #default="scope">
                        <span v-if="scope.row.score !== null" class="score-text">{{ scope.row.score }} 分</span>
                        <span v-else class="text-gray">-</span>
                    </template>
                </el-table-column>

                <el-table-column label="老师评语" min-width="200">
                    <template #default="scope">
                        <div v-if="scope.row.comment" class="teacher-comment">
                            <el-icon>
                                <ChatLineSquare />
                            </el-icon>
                            {{ scope.row.comment }}
                        </div>
                        <span v-else class="text-gray">暂无评语</span>
                    </template>
                </el-table-column>

                <el-table-column label="操作" width="150" fixed="right">
                    <template #default="scope">
                        <el-button v-if="scope.row.status === 'pending' || scope.row.status === 'in_progress'"
                            type="primary" size="small" @click="goToQuiz(scope.row.homework_id)">
                            开始答题
                        </el-button>
                        <el-button v-else type="success" plain size="small" @click="goToQuiz(scope.row.homework_id)">
                            查看详情
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ChatLineSquare } from '@element-plus/icons-vue'

const router = useRouter()
const homeworks = ref([])
const loading = ref(false)

const getStatusType = (status) => {
    const map = {
        pending: 'info',
        in_progress: 'warning',
        submitted: 'primary',
        completed: 'success'
    }
    return map[status] || 'info'
}

const getStatusText = (status) => {
    const map = {
        pending: '未开始',
        in_progress: '进行中',
        submitted: '待批改',
        completed: '已完成'
    }
    return map[status] || '未知'
}

onMounted(async () => {
    loading.value = true
    try {
        const token = localStorage.getItem('token')
        const res = await axios.get('http://localhost:8000/student/homeworks', {
            headers: { Authorization: `Bearer ${token}` }
        })
        homeworks.value = res.data
    } catch (e) {
        ElMessage.error('获取作业列表失败')
    } finally {
        loading.value = false
    }
})

const goToQuiz = (id) => {
    router.push(`/quiz/${id}`)
}
</script>

<style scoped>
.homework-container {
    max-width: 1200px;
    margin: 20px auto;
    padding: 20px;
}

.header-area {
    margin-bottom: 20px;
    text-align: center;
}

.score-text {
    font-weight: bold;
    color: #67C23A;
    font-size: 16px;
}

.text-gray {
    color: #909399;
    font-size: 12px;
}

.teacher-comment {
    background: #fdf6ec;
    color: #e6a23c;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 5px;
}
</style>