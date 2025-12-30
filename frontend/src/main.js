import { createApp } from 'vue'
import { createPinia } from 'pinia'

// 1. 引入 Element Plus 及其样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 2. 引入所有图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 3. 使用 Element Plus
app.use(ElementPlus)

// 4. 全局注册所有图标 (这样你就可以直接用 <Edit />, <User /> 等)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')