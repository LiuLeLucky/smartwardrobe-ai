# 🧥 SmartWardrobe AI — 智能衣橱助手

> 用 AI 帮你管理衣橱、生成搭配、记录穿搭历史。  
> 从一个想法到完整的全栈 Web 应用。

---

## 📅 研发时间线

| 阶段 | 时间 | 内容 |
|------|------|------|
| 项目立项 & 架构设计 | 2026 年 3 月 | 功能规划、技术选型、数据库设计 |
| Phase 1：后端骨架 | 2026 年 3 月 | Auth、JWT、衣物 CRUD API |
| Phase 2：Vision AI | 2026 年 3 月 | 图片上传、GLM-4V-Plus 自动识别衣物 |
| Phase 3：AI 搭配生成 | 2026 年 3 月 | 智谱 GLM 生成多套搭配、A/B/C 评分、改进建议 |
| Streamlit 原型 UI | 2026 年 4 月 | 完整可用的原型界面，验证所有后端功能 |
| Next.js 正式前端 | 2026 年 4 月 | Warm Natural 风格、响应式设计、全功能页面 |
| 部署准备 | 2026 年 4 月 | GitHub 仓库、Render/Vercel 部署配置 |

---

## ✨ 已实现功能

### 👗 衣橱管理
- 添加、编辑、删除衣物
- 上传衣物照片，**AI 自动识别**类别、颜色、材质、适合季节
- 按季节、颜色、名称筛选衣物
- 支持手动录入或纯图片上传（AI 填充信息）

### 🤖 AI 搭配生成
- 选择场合（约会 / 工作 / 休闲 / 运动 / 聚会）和风格（简约 / 复古 / 街头 / 职业）
- **一次生成 3 套**不同搭配方案，按评分排序
- 每套搭配包含：
  - AI 中文搭配说明（颜色和谐、场合适配、穿搭技巧、配件建议）
  - A / B / C 评分（完美 / 良好 / 勉强）
  - B/C 级专属改进建议
- 预览后自主选择保存或丢弃

### 👔 手动创建搭配
- 从衣橱中手动勾选单品组合成搭配
- 保存到"我的搭配"

### 📒 穿搭记录
- AI 搭配和手动搭配分类展示
- 支持删除历史记录
- 最近 30 条未保存记录自动清理

### 🔐 用户系统
- 邮箱注册 / 登录
- JWT Token 鉴权
- 数据完全隔离（每个用户只能看到自己的数据）

---

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 数据库 ORM | SQLAlchemy 2.0 Async |
| 数据库 | SQLite（开发）→ PostgreSQL（生产） |
| AI 搭配生成 | 智谱 GLM-4（ZhipuAI SDK） |
| Vision AI | 智谱 GLM-4V-Plus（图片识别） |
| 身份验证 | JWT + bcrypt |
| 原型前端 | Streamlit |
| 正式前端 | Next.js 16 + Tailwind CSS v4 |
| 状态管理 | Zustand |
| HTTP 客户端 | Axios |
| 部署（前端） | Vercel |
| 部署（后端） | Render |

---

## 🚀 快速开始（本地开发）

### 前置条件
- Python 3.10+
- Node.js 18+
- 智谱 AI API Key（[申请地址](https://bigmodel.cn)）

### 后端启动

```bash
# 1. 克隆项目
git clone https://github.com/LiuLeLucky/smartwardrobe-ai.git
cd smartwardrobe-ai

# 2. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 ZHIPU_API_KEY

# 5. 启动后端
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

后端运行于：`http://127.0.0.1:8001`  
API 文档：`http://127.0.0.1:8001/docs`

### 前端启动

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 配置环境变量
cp .env.example .env.local
# 编辑 .env.local，确认 NEXT_PUBLIC_API_URL=http://127.0.0.1:8001

# 3. 启动前端
npm run dev
```

前端运行于：`http://localhost:3000`

### Streamlit 原型（可选）

```bash
streamlit run app/ui.py
```

原型运行于：`http://localhost:8501`

---

## 📁 项目结构

```
smartwardrobe-ai/
│
├── app/                        # FastAPI 后端
│   ├── main.py                 # 应用入口、CORS、路由注册
│   ├── config.py               # 环境变量配置
│   ├── api/                    # 路由层
│   │   ├── auth.py             # 注册、登录
│   │   ├── clothing.py         # 衣物 CRUD + 图片上传
│   │   ├── outfits.py          # 搭配生成、保存、删除
│   │   └── deps.py             # JWT 鉴权依赖
│   ├── core/
│   │   ├── security.py         # bcrypt + JWT
│   │   └── exceptions.py       # 自定义异常
│   ├── database/               # 数据库连接
│   ├── models/                 # SQLAlchemy 数据模型
│   ├── schemas/                # Pydantic 请求/响应模型
│   └── services/               # 业务逻辑层
│       ├── ai_service.py       # GLM 搭配生成 + Vision 识别
│       ├── clothing_service.py
│       ├── outfit_service.py
│       └── user_service.py
│
├── frontend/                   # Next.js 前端
│   ├── app/
│   │   ├── login/              # 登录/注册页
│   │   ├── wardrobe/           # 我的衣橱
│   │   ├── generate/           # 生成搭配
│   │   ├── create-outfit/      # 手动创建搭配
│   │   └── outfits/            # 我的穿搭
│   ├── components/
│   │   ├── Navbar.tsx
│   │   └── ClothingCard.tsx
│   └── lib/
│       ├── api.ts              # Axios API 客户端
│       ├── store.ts            # Zustand 状态管理
│       └── types.ts            # TypeScript 类型定义
│
├── docs/                       # 项目文档
├── uploads/                    # 用户上传图片（本地）
├── test_e2e.py                 # 端到端测试脚本
├── .env.example                # 环境变量模板
└── requirements.txt
```

---

## 🗺 后续规划

- [ ] 穿着频率统计可视化（每件衣物穿了多少次）
- [ ] 每日搭配推荐（打开 App 自动推荐今日穿搭）
- [ ] 英文界面切换（国际化支持）
- [ ] 手机号 / 微信登录
- [ ] Alembic 数据库迁移（切换 PostgreSQL）
- [ ] ChromaDB 向量数据库（相似搭配推荐）
- [ ] Docker 容器化部署

---

## 📄 环境变量说明

```env
# 数据库
DATABASE_URL=sqlite:///./smartwardrobe.db

# JWT 密钥（生产环境请使用随机长字符串）
SECRET_KEY=your-secret-key-here

# AI 提供商（zhipu / mock）
AI_PROVIDER=zhipu

# 智谱 AI Key（https://bigmodel.cn）
ZHIPU_API_KEY=

# 图片上传目录
UPLOAD_DIR=uploads
```

---

## 🙏 致谢

本项目使用 [Claude](https://claude.ai) 辅助开发，AI 搭配能力由 [智谱 AI](https://bigmodel.cn) GLM 系列模型提供。