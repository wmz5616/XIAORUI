小蕊 (Xiaorui) - 智能个性化学习辅助平台

<p align="center">
<img src="frontend/src/assets/logo.svg" width="100" alt="Xiaorui Logo">
</p>

📖 项目简介

小蕊 (Xiaorui) 是一个集成了人工智能技术的现代化在线教育平台。项目采用前后端分离架构，旨在为学生提供个性化的学习路径规划、AI 智能诊断和知识图谱可视化，同时为教师和管理员提供高效的教学管理工具。

核心特色包括接入 豆包 AI (Doubao AI) 进行智能辅导、自动化测验评估以及互动的学习社区。

🛠 技术栈

后端 (Backend)

开发语言: Python 3.9+

核心框架: FastAPI - 高性能异步 Web 框架

数据库: SQLite (轻量级，易于部署)

AI 服务: 豆包 AI (Doubao AI SDK)

认证机制: JWT (JSON Web Tokens)

ORM: SQLAlchemy

前端 (Frontend)

核心框架: Vue 3 (Composition API)

构建工具: Vite

路由管理: Vue Router

UI 样式: CSS Variables, Scoped CSS

可视化: 知识图谱渲染 (基于 KnowledgeGraph.vue)

📦 功能模块

👨‍🎓 学生端 (Student)

仪表盘: 概览学习进度和待办事项。

AI 诊断 (AiDiagnosis): 利用 AI 分析学习强弱项。

知识图谱 (KnowledgeGraph): 可视化展示知识点关联。

诊断测试 (DiagnosticTest): 入学或阶段性能力测试。

作业与测验: 在线完成作业 (HomeworkList) 和 测验 (Quiz)。

自习室 (StudyRoom): 沉浸式学习环境。

论坛 (Forum): 学生交流社区。

👩‍🏫 教师端 (Teacher)

教学管理: 管理课程、发布作业。

学生监控: 查看学生学习数据和诊断报告。

🛡️ 管理员 (Admin)

系统管理: 用户管理、内容审核。

数据看板: 平台整体运行数据监控。

🤖 AI 引擎 (AI Engine)

基于 doubao_ai.py 服务，提供智能问答、作业批改辅助及个性化建议。

🚀 快速开始

1. 环境准备

请确保您的本地环境已安装：

Python 3.9 或更高版本

Node.js 16.0 或更高版本

Git

2. 后端设置 (Backend)

进入后端目录并设置虚拟环境：

cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt


初始化数据:
首次运行前，请初始化数据库：

python init_data.py


启动服务器:

# 开发模式启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


后端 API 文档地址: http://localhost:8000/docs

3. 前端设置 (Frontend)

打开一个新的终端窗口，进入前端目录：

cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev


前端访问地址: http://localhost:5173 (具体端口视 Vite 输出而定)

📂 项目结构概览

XIAORUI/
├── backend/                   # 后端代码目录
│   ├── app/
│   │   ├── routers/           # 路由模块 (API Endpoints)
│   │   │   ├── admin.py       # 管理员接口
│   │   │   ├── ai_engine.py   # AI交互接口
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── forum.py       # 论坛接口
│   │   │   ├── quiz.py        # 测验接口
│   │   │   ├── student.py     # 学生业务接口
│   │   │   └── teacher.py     # 教师业务接口
│   │   ├── services/          # 业务逻辑服务
│   │   │   └── doubao_ai.py   # 豆包AI集成
│   │   ├── main.py            # FastAPI 入口文件
│   │   └── models.py          # 数据库模型
│   ├── init_data.py           # 数据初始化脚本
│   ├── requirements.txt       # Python 依赖列表
│   └── xiaorui_full_system.db # SQLite 数据库文件
│
├── frontend/                  # 前端代码目录
│   ├── public/                # 静态资源
│   ├── src/
│   │   ├── assets/            # CSS, Logo 等资源
│   │   ├── router/            # Vue 路由配置
│   │   ├── views/             # 页面视图组件
│   │   │   ├── admin/         # 管理员页面
│   │   │   ├── student/       # 学生页面 (诊断, 图谱, 测验等)
│   │   │   ├── teacher/       # 教师页面
│   │   │   └── Login.vue      # 登录页
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # Vue 入口文件
│   ├── package.json           # npm 配置
│   └── vite.config.js         # Vite 配置
└── README.md


🔧 配置说明

如果涉及 AI 功能调用，请确保在后端配置了正确的 API Key。通常需要在环境变量或配置文件中设置豆包 AI 的凭证。

🤝 贡献指南

Fork 本仓库

创建您的特性分支 (git checkout -b feature/AmazingFeature)

提交您的更改 (git commit -m 'Add some AmazingFeature')

推送到分支 (`git push origin feature/AmazingFeature
