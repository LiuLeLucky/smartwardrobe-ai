# AI 智能衣柜助手 (Smart Wardrobe AI) 技术设计文档

## 1. 项目愿景
构建一个深度结合计算机视觉 (CV) 与大语言模型 (LLM) 的个人时尚助手，实现衣物自动化管理、智能场景搭配及风格演进学习。

---

## 2. 核心技术栈 (Professional Stack)

### 2.1 后端架构 (The Engine)
| 组件 | 选型 | 说明 |
| :--- | :--- | :--- |
| **主框架** | **FastAPI** | 基于 Python 的高性能异步 Web 框架，支持自动生成 OpenAPI 文档。 |
| **数据校验** | **Pydantic v2** | 利用类型提示 (Type Hints) 实现严格的数据验证。 |
| **异步服务器** | **Uvicorn** | ASGI 兼容服务器，支撑高并发请求。 |
| **配置管理** | **Python-dotenv** | 隔离环境变量（API Keys, DB URL），保障安全性。 |

### 2.2 数据持久化 (Storage)
| 组件 | 选型 | 说明 |
| :--- | :--- | :--- |
| **数据库** | **PostgreSQL** | 生产级关系型数据库（初期可用 SQLite 快速开发）。 |
| **ORM** | **SQLAlchemy 2.0** | 采用 **Async 异步模式** 操作数据库，提升 I/O 效率。 |
| **版本管理** | **Alembic** | 数据库迁移工具，记录表结构变更历史。 |
| **向量检索** | **ChromaDB** | 本地向量数据库，用于存储和检索穿搭风格特征 (Embedding)。 |

### 2.3 AI 逻辑 (The Brain)
| 组件 | 选型 | 说明 |
| :--- | :--- | :--- |
| **编排框架** | **LangChain** | 链接 LLM、Prompt 模板及向量库，构建复杂的搭配链条。 |
| **多模态模型** | **Claude-3.5-Sonnet** | 负责图像识别（识衣）与逻辑推理（搭配生成）。 |
| **视觉处理** | **OpenCV / Pillow** | 基础图像预处理（缩放、裁剪、格式转换）。 |

### 2.4 前端与部署 (Interface & Ops)
| 组件 | 选型 | 说明 |
| :--- | :--- | :--- |
| **快速原型** | **Streamlit** | 全 Python 编写，用于快速验证 AI 核心逻辑界面。 |
| **终端产物** | **Next.js + Tailwind** | 响应式 Web 应用，提供极致的用户交互体验。 |
| **容器化** | **Docker** | 封装环境依赖，确保开发与生产环境的一致性。 |

---

## 3. 数据库模型预留节点 (Schema Design)

### 3.1 Clothing Table (衣物表)
- `id`: UUID (主键)
- `category`: 类别 (如：上装、下装、外套)
- `sub_category`: 细分类别 (如：卫衣、直筒裤)
- `color_code`: 颜色十六进制码 (如：#FFFFFF)
- `material`: 面料 (如：纯棉、亚麻)
- `season`: 适用季节 (List[str])
- `image_url`: 图片存储路径
- `**vector_id**`: (预留) 关联向量库中的特征 ID
- `**raw_ai_metadata**`: (预留) 存储 AI 识别出的原始 JSON 结果

### 3.2 Outfit Table (穿搭方案表)
- `id`: UUID
- `items`: 关联的衣物 ID 列表 (Many-to-Many)
- `scene_tag`: 场景标签 (如：约会、通勤)
- `style_tag`: 风格标签 (如：Miu Miu)
- `ai_score`: A/B/C 评分
- `ai_feedback`: 改进建议文本
- `created_at`: 创建时间

### OutfitItem Table (穿搭-衣物关联表)
- id
- outfit_id (FK)
- clothing_id (FK)
---

## 4. 开发路线图 (Roadmap)

### 第一阶段：MVP 骨架 (核心增删改查)
- [ ] 初始化 **Poetry/Conda** 环境。
- [ ] 配置 **FastAPI + SQLAlchemy 2.0 Async** 异步连接池。
- [ ] 完成 `Clothing` 模型的迁移与基础 CRUD 接口。

### 第二阶段：视觉自动化 (AI 录入)
- [ ] 集成 Claude-3.5 Vision API。
- [ ] 开发识别 Service：上传图片 -> AI 结构化输出 -> 自动填充表单。
router  
  ↓  
service (business logic)  
  ↓  
ai_service (调用 Claude)  
  ↓  
repository (数据库)  
- [ ] 实现图片本地异步存储逻辑。

### 第三阶段：智能搭配 (推荐系统)
- [ ] 编写 **LangChain Prompt**：结合天气、场景与用户现有库存。
- [ ] 实现搭配评分系统 (A/B/C) 及缺失单品建议。
- [ ] 使用 **Streamlit** 搭建简单的可视化操作台。

### 第四阶段：风格演进 (长期计划)
- [ ] 接入 **ChromaDB** 实现相似风格检索。
- [ ] 增加穿搭历史统计：计算“最常穿单品”与“冷宫单品”。
- [ ] 编写 **Docker Compose** 配置文件，实现一键部署。

---

## 5. Claude Code 提问范式 (Standard Prompts)

- **初始化模型**：*"请参考 `TECH_DESIGN.md` 中的 Schema 定义，使用 SQLAlchemy 2.0 的异步语法编写 `app/models/clothing.py`。"*
- **编写接口**：*"请为我创建一个 FastAPI 路由，用于处理衣物上传。要求先进行 Pydantic 校验，然后异步写入数据库。"*
- **调试错误**：*"当前异步 session 报错：[报错内容]。请检查 `app/database/session.py` 中的配置是否符合 FastAPI 的异步依赖注入要求。"*