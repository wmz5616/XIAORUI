<template>
  <div class="common-layout">
    <el-container>
      <el-header v-if="route.path !== '/'" class="header">
        <div class="logo">
          <el-icon :size="24" style="margin-right: 10px; vertical-align: middle;">
            <Monitor />
          </el-icon>
          <span>XIAORUI 智适应学习平台</span>
        </div>
        <div class="user-info">
          <el-avatar :size="32" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
            style="cursor: pointer;" @click="$router.push('/student/profile')" />
          <span style="margin: 0 10px; font-weight: bold;">{{ username }}</span>
          <el-button link type="danger" @click="logout">退出</el-button>
        </div>
      </el-header>

      <el-main :style="{ padding: route.path === '/' ? '0' : '20px' }">
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Monitor } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const username = ref('')

// 监听路由变化，更新用户名
watchEffect(() => {
  username.value = localStorage.getItem('username') || '访客'
})

const logout = () => {
  localStorage.clear()
  router.push('/')
}
</script>

<style>
body {
  margin: 0;
  background-color: #f5f7fa;
  font-family: sans-serif;
}

.header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  display: flex;
  align-items: center;
}
</style>