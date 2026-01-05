小瑞 (Xiaorui) - 智能个性化学习辅助平台

<p align="center">
<img src="frontend/src/assets/logo.svg" width="120" alt="Xiaorui Logo">
</p>

<p align="center">
集成了人工智能技术的现代化在线教育平台




<strong>个性化学习路径 · AI 智能诊断 · 知识图谱可视化</strong>
</p>

📖 项目简介

小瑞 (Xiaorui) 是一个致力于教育公平与个性化教学的现代化平台。项目采用前后端分离架构，旨在为学生提供定制化的学习体验，同时赋予教师和管理员高效的管理工具。

核心特色包括接入 豆包 AI (Doubao AI) 进行智能辅导、自动化的学情诊断以及基于知识图谱的可视化学习导航。

🛠 技术栈

后端 (Backend)

开发语言: Python 3.9+

核心框架: FastAPI - 高性能异步 Web 框架

数据库: SQLite (轻量级，开箱即用)

AI 服务: 豆包 AI (Doubao AI SDK)

认证机制: JWT (JSON Web Tokens)

前端 (Frontend)

核心框架: Vue 3 (Composition API)

构建工具: Vite

路由管理: Vue Router

可视化: 知识图谱渲染 (基于 D3.js 或相关库实现)

📦 功能模块

角色

功能亮点

👨‍🎓 学生

AI 诊断 (学习强弱项分析)、知识图谱 (可视化导航)、自习室 (沉浸式学习)、智能测验

👩‍🏫 教师

教学管理 (课程/作业发布)、学情监控 (查看学生诊断报告与数据)

🛡️ 管理员

系统管理 (用户/内容审核)、数据看板 (平台运行数据监控)

🚀 快速开始

1. 环境准备

确保您的环境满足以下要求：

Python: 3.9+

Node.js: 16.0+

Git

2. 后端设置 (Backend)

建议在一个单独的终端窗口中运行后端。

# 1. 进入后端目录
cd backend

# 2. 创建并激活虚拟环境
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS/Linux:
# python3 -m venv venv
# source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库 (首次运行必须)
python init_data.py

# 5. 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


后端启动成功后，API 文档地址: http://localhost:8000/docs

3. 前端设置 (Frontend)

打开一个新的终端窗口运行前端。

# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev


前端启动成功后，访问地址通常为: http://localhost:5173

📂 项目结构概览

XIAORUI/
├── backend/                   # 后端工程 (FastAPI)
│   ├── app/
│   │   ├── routers/           # API 路由定义 (Student, Teacher, Admin, AI)
│   │   ├── services/          # 业务逻辑与 AI 服务集成
│   │   ├── main.py            # 程序入口
│   │   └── models.py          # 数据库模型
│   ├── init_data.py           # 数据库初始化脚本
│   └── requirements.txt       # Python 依赖
│
├── frontend/                  # 前端工程 (Vue 3 + Vite)
│   ├── src/
│   │   ├── views/             # 页面视图 (按角色分文件夹)
│   │   ├── components/        # 公共组件
│   │   └── router/            # 路由配置
│   ├── vite.config.js         # Vite 构建配置
│   └── package.json           # npm 依赖
│
└── README.md


🔧 配置说明

AI 功能配置:
本项目依赖 豆包 AI 提供智能服务。请确保在后端代码或环境变量中配置了有效的 API Key。

配置文件位置: backend/app/services/doubao_ai.py (或相应的配置加载文件)

🤝 贡献指南

Fork 本仓库

创建特性分支 (git checkout -b feature/AmazingFeature)

提交更改 (git commit -m 'Add some AmazingFeature')

推送到分支 (git push origin feature/AmazingFeature)

提交 Pull Request

📄 许可证

MIT License
