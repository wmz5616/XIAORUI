<template>
  <div class="common-layout">
    <el-container>
      <el-header v-if="route.path !== '/'" class="header">
        <div class="logo">
          <el-icon :size="24" class="logo-icon">
            <Monitor />
          </el-icon>
          <span class="logo-text">XIAORUI智学平台</span>
        </div>
        <div class="user-info">
          <span class="user-name">{{ username }}</span>
          <el-avatar :size="30" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
            style="cursor: pointer;" @click="$router.push('/student/profile')" />
          <el-button link type="danger" size="small" @click="logout" style="margin-left: 5px;">退出</el-button>
        </div>
      </el-header>

      <el-main :class="{ 'no-padding': isMobile }" :style="{ padding: route.path === '/' ? '0' : '' }">
        <router-view></router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watchEffect, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Monitor } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const username = ref('')
const isMobile = computed(() => window.innerWidth < 768)

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
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  height: 60px;
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  display: flex;
  align-items: center;
}

.logo-icon {
  margin-right: 8px;
  vertical-align: middle;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-name {
  margin: 0 10px;
  font-weight: bold;
  font-size: 14px;
}

@media (max-width: 768px) {
  .header {
    padding: 0 10px;
    height: 50px;
  }

  .logo-text {
    display: none;
  }

  .logo-icon {
    margin-right: 0;
  }

  .user-name {
    display: none;
  }

  .el-main {
    padding: 10px !important;
  }

  .el-main.no-padding {
    padding: 10px !important;
  }
}

@media (min-width: 769px) {
  .logo-text {
    display: inline;
  }

  .el-main {
    padding: 20px;
  }
}
</style>