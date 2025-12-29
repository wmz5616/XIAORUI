import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 【关键步骤】导入路由配置
import router from './router' 

const app = createApp(App)

// 【关键步骤】使用路由插件
app.use(router)
app.use(ElementPlus)

app.mount('#app')