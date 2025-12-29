<template>
  <div class="admin-dashboard">
    <h2 style="margin-bottom: 20px; color: #303133;">🛡️ 管理员控制台</h2>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="stat-value">{{ stats.user_count }}</div>
          <div class="stat-label">平台总用户数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="stat-value">{{ stats.course_count }}</div>
          <div class="stat-label">课程资源总数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="stat-value" style="color: #67C23A">{{ stats.active_students }}</div>
          <div class="stat-label">活跃学习者</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        
        <el-tab-pane label="用户与权限管理" name="users">
          <el-table :data="userList" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="full_name" label="姓名" width="120" />
            <el-table-column prop="role" label="角色">
              <template #default="scope">
                <el-tag :type="getRoleType(scope.row.role)">{{ scope.row.role }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作">
              <template #default="scope">
                <el-button size="small" type="danger" @click="handleDeleteUser(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="课程资源审核" name="resources">
          <el-table :data="resourceList" stripe style="width: 100%">
            <el-table-column prop="title" label="资源名称" />
            <el-table-column prop="type" label="类型" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.type === 'video' ? 'warning' : 'info'">
                  {{ scope.row.type === 'video' ? '视频' : '文档' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="course" label="所属课程" />
            <el-table-column prop="teacher" label="上传教师" />
            <el-table-column label="内容预览" width="120">
              <template #default="scope">
                <el-link type="primary" :href="scope.row.url" target="_blank">点击查看</el-link>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="scope">
                <el-button size="small" type="danger" @click="handleDeleteResource(scope.row)">违规删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="AI 算法配置" name="ai">
          <div style="max-width: 500px; padding: 20px;">
            <el-form label-position="top">
              <el-form-item label="模型版本">
                <el-input v-model="aiConfig.model_version" disabled />
              </el-form-item>
              <el-form-item label="推荐阈值">
                <div style="display: flex; gap: 20px;">
                  <el-slider v-model="aiConfig.recommendation_threshold" :min="0.1" :max="0.9" :step="0.1" style="flex: 1" />
                  <span>{{ aiConfig.recommendation_threshold }}</span>
                </div>
              </el-form-item>
              <el-button type="primary" @click="updateAiConfig">保存配置</el-button>
            </el-form>
          </div>
        </el-tab-pane>

      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const stats = ref({ user_count: 0, course_count: 0, active_students: 0 })
const userList = ref([])
const resourceList = ref([]) // 资源列表
const activeTab = ref('users')
const aiConfig = reactive({ recommendation_threshold: 0.6, model_version: '' })

// 初始化加载
const init = async () => {
  await fetchStats()
  await fetchUsers()
}

// 切换 Tab 时加载对应数据
const handleTabClick = (tab) => {
  if (tab.props.name === 'resources') fetchResources()
  if (tab.props.name === 'ai') fetchAiConfig()
}

// --- API 调用 ---
const fetchStats = async () => {
  try {
    const res = await axios.get('http://localhost:8000/admin/stats')
    stats.value = res.data
  } catch (e) {}
}

const fetchUsers = async () => {
  const res = await axios.get('http://localhost:8000/admin/users')
  userList.value = res.data
}

const fetchResources = async () => {
  const res = await axios.get('http://localhost:8000/admin/resources')
  resourceList.value = res.data
}

const fetchAiConfig = async () => {
  const res = await axios.get('http://localhost:8000/admin/ai-config')
  aiConfig.recommendation_threshold = res.data.recommendation_threshold
  aiConfig.model_version = res.data.model_version
}

const updateAiConfig = async () => {
  await axios.post('http://localhost:8000/admin/ai-config', aiConfig)
  ElMessage.success('更新成功')
}

// --- 删除操作 ---
const handleDeleteUser = (row) => {
  ElMessageBox.confirm('确定删除该用户?', '警告', { type: 'warning' })
    .then(async () => {
      await axios.delete(`http://localhost:8000/admin/users/${row.id}`)
      ElMessage.success('用户已删除')
      fetchUsers()
      fetchStats()
    })
}

const handleDeleteResource = (row) => {
  ElMessageBox.confirm(`确定删除资源 "${row.title}" 吗?`, '资源审核', { type: 'warning' })
    .then(async () => {
      await axios.delete(`http://localhost:8000/admin/resources/${row.id}`)
      ElMessage.success('资源已移除')
      fetchResources()
    })
}

const getRoleType = (role) => {
  if (role === 'admin') return 'danger'
  if (role === 'teacher') return 'warning'
  return 'primary'
}

onMounted(init)
</script>

<style scoped>
.admin-dashboard { max-width: 1200px; margin: 0 auto; padding: 20px; }
.data-card { text-align: center; padding: 20px 0; }
.stat-value { font-size: 32px; font-weight: bold; color: #409EFF; margin-bottom: 10px; }
.stat-label { color: #909399; font-size: 14px; }
</style>