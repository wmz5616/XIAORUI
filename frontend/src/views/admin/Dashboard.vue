<template>
  <div class="admin-dashboard">
    <div class="header">
      <h2 style="color: #303133;">管理员控制台</h2>
      <el-tag type="success" effect="dark">System Online</el-tag>
    </div>

    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="stat-value">{{ stats.user_count }}</div>
          <div class="stat-label">平台总用户</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="stat-value">{{ stats.course_count }}</div>
          <div class="stat-label">课程资源数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="data-card">
          <div class="stat-value" style="color: #67C23A">{{ stats.active_students }}</div>
          <div class="stat-label">今日活跃</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">

        <el-tab-pane label="用户与权限" name="users">
          <el-table :data="userList" stripe style="width: 100%" border>
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="full_name" label="姓名" width="150" />
            <el-table-column prop="role" label="当前角色" width="120">
              <template #default="scope">
                <el-tag :type="getRoleType(scope.row.role)">{{ scope.row.role }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="权限操作">
              <template #default="scope">
                <el-button size="small" type="primary" plain @click="openRoleDialog(scope.row)">修改角色</el-button>
                <el-popconfirm title="确定删除该用户吗？此操作不可逆！" @confirm="handleDeleteUser(scope.row)">
                  <template #reference>
                    <el-button size="small" type="danger">删除账号</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="资源审核" name="resources">
          <el-alert title="请重点审核视频内容合规性" type="warning" show-icon style="margin-bottom: 15px" />
          <el-table :data="resourceList" stripe style="width: 100%">
            <el-table-column prop="title" label="资源名称" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.type === 'video' ? 'warning' : 'info'">
                  {{ scope.row.type === 'video' ? '视频' : '文档' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="teacher" label="上传教师" />
            <el-table-column label="预览" width="100">
              <template #default="scope">
                <el-link type="primary" :href="scope.row.url" target="_blank">查看</el-link>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="scope">
                <el-button size="small" type="danger" @click="handleDeleteResource(scope.row)">违规下架</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="数据分析" name="analysis">
          <div style="display: flex; gap: 20px;">
            <div id="chart-users" style="width: 50%; height: 350px; border: 1px solid #eee; padding: 10px;"></div>
            <div id="chart-active" style="width: 50%; height: 350px; border: 1px solid #eee; padding: 10px;"></div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="系统运维" name="system">
          <el-row :gutter="20">
            <el-col :span="10">
              <el-card header="服务器状态监控">
                <div class="monitor-item">
                  <span>CPU 负载</span>
                  <el-progress :percentage="systemStatus.cpu_usage" :color="getStatusColor(systemStatus.cpu_usage)" />
                </div>
                <div class="monitor-item">
                  <span>内存使用率</span>
                  <el-progress :percentage="systemStatus.memory_usage"
                    :color="getStatusColor(systemStatus.memory_usage)" />
                </div>
                <div class="monitor-item">
                  <span>磁盘空间</span>
                  <el-progress :percentage="systemStatus.disk_usage" status="success" />
                </div>
                <div style="margin-top: 20px; text-align: center;">
                  <el-tag size="large" type="success">System Status: {{ systemStatus.status }}</el-tag>
                </div>
              </el-card>
            </el-col>
            <el-col :span="14">
              <el-card header="系统操作日志">
                <el-table :data="systemLogs" height="250" style="width: 100%">
                  <el-table-column prop="time" label="时间" width="80" />
                  <el-table-column prop="level" label="级别" width="80">
                    <template #default="{ row }">
                      <el-tag size="small"
                        :type="row.level === 'ERROR' ? 'danger' : (row.level === 'WARN' ? 'warning' : 'info')">
                        {{ row.level }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="message" label="日志内容" />
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </el-tab-pane>

        <el-tab-pane label="AI 模型配置" name="ai">
          <div style="max-width: 600px; padding: 20px;">
            <el-form label-position="top" border>
              <el-form-item label="当前模型版本">
                <el-input v-model="aiConfig.model_version" disabled />
              </el-form-item>
              <el-form-item label="个性化推荐阈值 (Threshold)">
                <div style="display: flex; gap: 20px; align-items: center;">
                  <el-slider v-model="aiConfig.recommendation_threshold" :min="0.1" :max="0.9" :step="0.1"
                    style="flex: 1" />
                  <span style="font-weight: bold">{{ aiConfig.recommendation_threshold }}</span>
                </div>
                <div style="font-size: 12px; color: #999">阈值越高，推荐内容越精准但数量越少；阈值越低，推荐内容越广泛。</div>
              </el-form-item>
              <el-button type="primary" @click="updateAiConfig" style="width: 100%">保存算法配置</el-button>
            </el-form>
          </div>
        </el-tab-pane>

      </el-tabs>
    </el-card>

    <el-dialog v-model="showRoleDialog" title="修改用户权限" width="400px">
      <el-form>
        <el-form-item label="当前用户">
          <el-input v-model="editingUser.username" disabled />
        </el-form-item>
        <el-form-item label="分配角色">
          <el-select v-model="editingUser.newRole" style="width: 100%">
            <el-option label="学生 (Student)" value="student" />
            <el-option label="教师 (Teacher)" value="teacher" />
            <el-option label="管理员 (Admin)" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRoleChange">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

const stats = ref({ user_count: 0, course_count: 0, active_students: 0 })
const userList = ref([])
const resourceList = ref([])
const activeTab = ref('users')
const aiConfig = reactive({ recommendation_threshold: 0.6, model_version: '' })

const systemStatus = ref({ cpu_usage: 0, memory_usage: 0, disk_usage: 0, status: 'Loading' })
const systemLogs = ref([])

const showRoleDialog = ref(false)
const editingUser = reactive({ id: null, username: '', newRole: '' })

const init = async () => {
  await fetchStats()
  await fetchUsers()
}

const handleTabClick = (tab) => {
  if (tab.props.name === 'resources') fetchResources()
  if (tab.props.name === 'ai') fetchAiConfig()
  if (tab.props.name === 'analysis') fetchAnalysisData()
  if (tab.props.name === 'system') fetchSystemData()
}

const fetchStats = async () => {
  try {
    const res = await axios.get('http://localhost:8000/admin/stats')
    stats.value = res.data
  } catch (e) { }
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

const fetchAnalysisData = async () => {
  const res = await axios.get('http://localhost:8000/admin/stats/trend')
  const { dates, new_users, daily_active } = res.data

  nextTick(() => {
    const chart1 = echarts.init(document.getElementById('chart-users'))
    chart1.setOption({
      title: { text: '近7日新增用户' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: dates },
      yAxis: { type: 'value' },
      series: [{ data: new_users, type: 'line', smooth: true, areaStyle: {} }]
    })

    const chart2 = echarts.init(document.getElementById('chart-active'))
    chart2.setOption({
      title: { text: '日活跃用户趋势' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: dates },
      yAxis: { type: 'value' },
      series: [{ data: daily_active, type: 'bar', color: '#67C23A' }]
    })
  })
}

const fetchSystemData = async () => {
  const [res1, res2] = await Promise.all([
    axios.get('http://localhost:8000/admin/system/status'),
    axios.get('http://localhost:8000/admin/system/logs')
  ])
  systemStatus.value = res1.data
  systemLogs.value = res2.data
}

const updateAiConfig = async () => {
  await axios.post('http://localhost:8000/admin/ai-config', aiConfig)
  ElMessage.success('配置已更新')
}

const handleDeleteUser = async (row) => {
  await axios.delete(`http://localhost:8000/admin/users/${row.id}`)
  ElMessage.success('用户已删除')
  fetchUsers()
  fetchStats()
}

const handleDeleteResource = (row) => {
  ElMessageBox.confirm(`确定删除资源 "${row.title}" 吗?`, '警告', { type: 'warning' })
    .then(async () => {
      await axios.delete(`http://localhost:8000/admin/resources/${row.id}`)
      ElMessage.success('资源已移除')
      fetchResources()
    })
}

const openRoleDialog = (row) => {
  editingUser.id = row.id
  editingUser.username = row.username
  editingUser.newRole = row.role
  showRoleDialog.value = true
}

const submitRoleChange = async () => {
  try {
    await axios.put(`http://localhost:8000/admin/users/${editingUser.id}/role`, {
      role: editingUser.newRole
    })
    ElMessage.success("权限修改成功")
    showRoleDialog.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error("修改失败")
  }
}

const getRoleType = (role) => {
  if (role === 'admin') return 'danger'
  if (role === 'teacher') return 'warning'
  return 'primary'
}

const getStatusColor = (val) => {
  if (val < 60) return '#67C23A'
  if (val < 80) return '#E6A23C'
  return '#F56C6C'
}

onMounted(init)
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.data-card {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.monitor-item {
  margin-bottom: 20px;
}

.monitor-item span {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #606266;
}
</style>