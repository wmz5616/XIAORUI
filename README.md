小蕊 (Xiaorui) - 智能个性化学习辅助平台

<p align="center">
<img src="frontend/src/assets/logo.svg" width="120" alt="Xiaorui Logo">
</p>

<p align="center">
集成了人工智能技术的现代化在线教育平台




<strong>个性化学习路径 · AI 智能诊断 · 知识图谱可视化</strong>
</p>

📖 项目简介

小蕊 (Xiaorui) 是一个致力于打破传统教育“千人一面”模式，促进教育公平与实现深度个性化教学的现代化智慧教育平台。项目采用当下流行的 前后端分离架构，前端注重交互体验，后端追求高并发性能。

平台不仅仅是一个简单的课程管理系统，更是一个智能的学习伙伴。通过深度接入 豆包 AI (Doubao AI) 大模型，小瑞能够像真人导师一样为学生提供 24/7 的即时辅导。系统利用先进的数据分析算法，自动生成学生的学情诊断报告，并通过 交互式知识图谱 将抽象的知识点关联可视化，帮助学生构建清晰的知识体系。

对于教师和管理员，小瑞提供了基于数据驱动的决策支持工具，让教学管理从“经验主义”走向“数据主义”，极大提升了教学效率和管理水平。

🛠 技术栈

本项目选用了行业内成熟且高效的技术栈，确保了系统的稳定性、可扩展性和开发效率。

后端 (Backend)

开发语言: Python 3.9+ (利用 Type Hints 增强代码健壮性)

核心框架: FastAPI - 基于 Starlette 和 Pydantic 的高性能异步 Web 框架，自动生成 OpenAPI 文档。

数据库: SQLite (默认) / 支持扩展至 PostgreSQL 或 MySQL。使用 SQLAlchemy ORM 进行数据库操作。

AI 服务: 豆包 AI (Doubao AI SDK) - 提供自然语言处理、智能问答及文本生成能力。

认证与安全: OAuth2 with Password (and hashing), JWT (JSON Web Tokens) 令牌机制，CORS 跨域策略配置。

前端 (Frontend)

核心框架: Vue 3 - 使用 Composition API (Script Setup) 编写更加逻辑复用性强的代码。

构建工具: Vite - 极速的冷启动和热更新体验。

路由管理: Vue Router 4 - 实现单页应用 (SPA) 的流畅页面跳转。

数据可视化: D3.js / ECharts (用于构建动态知识图谱和仪表盘图表)。

样式方案: 原生 CSS Variables 配合 Scoped CSS，实现响应式布局。

📦 功能模块详情

👨‍🎓 学生端 (Student) - 沉浸式学习体验

🧠 AI 智能诊断 (AI Diagnosis):

利用 AI 分析学生的测验历史和作业表现，生成多维度的能力评估报告。

自动识别薄弱知识点，并给出针对性的复习建议。

🕸️ 交互式知识图谱 (Knowledge Graph):

以图形化方式展示学科知识点之间的层级与关联。

通过颜色标记掌握程度（如：红色为薄弱，绿色为掌握），点击节点可直接跳转至相关学习资源。

📚 智能自习室 (Study Room):

提供专注模式（Focus Mode），结合番茄工作法帮助学生提升学习效率。

沉浸式 UI 设计，减少干扰。

📝 在线测验与作业 (Quiz & Homework):

支持多种题型（选择、填空、简答）。

提交后即时获得基础反馈，主观题由 AI 辅助批改初步意见。

💬 学习论坛 (Forum):

学生之间的交流社区，支持发帖提问、经验分享。

👩‍🏫 教师端 (Teacher) - 数据驱动教学

📊 教学仪表盘: 全局概览班级学习状态，包括平均分、活跃度、知识点掌握率分布。

📖 课程与作业管理: 便捷发布课程资料（视频、文档）和布置课后作业。

🧐 学情监控: 深入查看特定学生的详细诊断报告，不仅看分数，更看“哪里不会”。

🛡️ 管理员 (Admin) - 系统运维

👥 用户管理: 审核注册申请，管理师生账号权限。

📈 全局数据看板: 监控平台流量、API 调用情况及系统健康状态。

🛡️ 内容审核: 对论坛帖子和上传资源进行合规性管理。

🚀 快速开始

1. 环境准备

确保您的开发环境满足以下要求：

Python: 3.9 或更高版本

Node.js: 16.0 或更高版本

Git: 版本控制工具

2. 后端设置 (Backend)

建议在一个单独的终端窗口中运行后端服务。

# 1. 进入后端目录
cd backend

# 2. 创建并激活虚拟环境 (推荐)
# Windows:
python -m venv venv
venv\Scripts\activate
# macOS/Linux:
# python3 -m venv venv
# source venv/bin/activate

# 3. 安装依赖包
pip install -r requirements.txt

# 4. 初始化数据库
# 此脚本将创建 SQLite 数据库文件并预填充必要的初始数据(如管理员账号)
python init_data.py

# 5. 启动 FastAPI 服务器
# --reload 参数允许代码修改后自动重启，适合开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


提示: 后端启动成功后，您可以访问 http://localhost:8000/docs 查看交互式的 API 文档 (Swagger UI)，方便进行接口测试。

3. 前端设置 (Frontend)

打开一个新的终端窗口运行前端项目。

# 1. 进入前端目录
cd frontend

# 2. 安装 NPM 依赖
npm install

# 3. 启动 Vite 开发服务器
npm run dev


提示: 前端启动成功后，控制台会输出访问地址，通常为 http://localhost:5173。

📂 项目结构概览

XIAORUI/
├── backend/                   # 后端工程 (FastAPI)
│   ├── app/
│   │   ├── routers/           # API 路由定义 (Student, Teacher, Admin, AI)
│   │   ├── services/          # 核心业务逻辑与 AI 服务集成 (Doubao AI)
│   │   ├── main.py            # FastAPI 应用入口与配置
│   │   └── models.py          # SQLAlchemy 数据库模型定义
│   ├── init_data.py           # 数据库初始化与数据迁移脚本
│   ├── requirements.txt       # Python 依赖清单
│   └── xiaorui_learning.db    # SQLite 数据库文件 (自动生成)
│
├── frontend/                  # 前端工程 (Vue 3 + Vite)
│   ├── src/
│   │   ├── views/             # 页面视图
│   │   │   ├── admin/         # 管理员后台页面
│   │   │   ├── student/       # 学生端功能页 (诊断, 图谱, 测验等)
│   │   │   ├── teacher/       # 教师端功能页
│   │   │   └── Login.vue      # 统一登录页
│   │   ├── components/        # 可复用 UI 组件
│   │   ├── router/            # Vue Router 路由配置
│   │   ├── assets/            # 静态资源 (CSS, Logo, Images)
│   │   └── main.js            # Vue 应用入口
│   ├── vite.config.js         # Vite 构建配置
│   └── package.json           # NPM 依赖与脚本配置
│
└── README.md                  # 项目说明文档


🔧 配置说明

AI 功能配置:
本项目核心的智能辅导功能依赖 豆包 AI (Doubao AI) 接口。

请确保您已申请有效的 API Key。

在 backend/app/services/doubao_ai.py 文件中配置您的 Key，或者（推荐）将其设置为系统环境变量以保证安全。

🤝 贡献指南

我们非常欢迎社区贡献！如果您有好的想法：

Fork 本仓库。

创建您的特性分支 (git checkout -b feature/AmazingFeature)。

提交您的更改 (git commit -m 'Add some AmazingFeature')。

推送到分支 (git push origin feature/AmazingFeature)。

提交 Pull Request。

📄 许可证

本项目采用 MIT License 许可证。
