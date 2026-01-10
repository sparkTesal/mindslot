# MindSlot 项目结构

```
mindslot/
├── backend/                         # Python 后端
│   ├── agents/                      # LLM Agents
│   │   ├── __init__.py
│   │   ├── director.py             # 选题生成
│   │   ├── actor.py                # 内容生成
│   │   └── validator.py            # 内容验证
│   ├── models/                      # 数据模型
│   │   ├── __init__.py
│   │   ├── card.py                 # 卡片模型
│   │   ├── interaction.py          # 交互记录模型
│   │   └── user.py                 # 用户模型
│   ├── routes/                      # API 路由
│   │   ├── __init__.py
│   │   ├── feed.py                 # 信息流 API
│   │   └── interaction.py          # 交互 API
│   ├── services/                    # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── card_service.py         # 卡片服务
│   │   ├── llm_service.py          # LLM 调用封装
│   │   └── queue_service.py        # Redis 队列服务
│   ├── scripts/                     # 工具脚本
│   │   ├── __init__.py
│   │   ├── init_db.py              # 数据库初始化
│   │   └── factory.py              # 内容生成工厂
│   ├── app.py                       # Flask 应用入口
│   ├── config.py                    # 配置管理
│   ├── requirements.txt             # Python 依赖
│   └── .env.example                 # 环境变量示例
│
├── frontend/                        # React 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── Card/
│   │   │   │   ├── BlockRenderer.tsx    # Block 渲染器
│   │   │   │   └── CardRenderer.tsx     # 卡片渲染器
│   │   │   └── Feed/
│   │   │       └── FeedContainer.tsx    # 信息流容器
│   │   ├── services/
│   │   │   └── api.ts               # API 调用封装
│   │   ├── types/
│   │   │   └── card.ts              # TypeScript 类型定义
│   │   ├── App.tsx                  # 应用主组件
│   │   ├── App.css                  # 全局样式
│   │   ├── main.tsx                 # 应用入口
│   │   └── index.css                # Tailwind 入口
│   ├── index.html                   # HTML 模板
│   ├── package.json                 # Node 依赖
│   ├── vite.config.ts               # Vite 配置
│   ├── tsconfig.json                # TypeScript 配置
│   ├── tailwind.config.js           # Tailwind 配置
│   ├── postcss.config.js            # PostCSS 配置
│   └── .env.example                 # 环境变量示例
│
├── prompts.md                       # LLM 提示词库
├── design.md                        # 设计文档
├── README.md                        # 项目文档
├── QUICKSTART.md                    # 快速启动指南
├── PROJECT_STRUCTURE.md             # 本文件
└── .gitignore                       # Git 忽略配置
```

## 核心文件说明

### 后端核心

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `app.py` | Flask 应用入口，注册路由和中间件 | ⭐⭐⭐⭐⭐ |
| `agents/director.py` | Director Agent，负责生成选题 | ⭐⭐⭐⭐⭐ |
| `agents/actor.py` | Actor Agent，负责生成卡片内容 | ⭐⭐⭐⭐⭐ |
| `routes/feed.py` | 信息流 API，获取卡片和补货逻辑 | ⭐⭐⭐⭐⭐ |
| `services/queue_service.py` | Redis 队列管理 | ⭐⭐⭐⭐ |
| `scripts/factory.py` | 内容生成工厂脚本 | ⭐⭐⭐⭐ |

### 前端核心

| 文件 | 说明 | 重要性 |
|------|------|--------|
| `components/Feed/FeedContainer.tsx` | 信息流容器，管理卡片加载和交互 | ⭐⭐⭐⭐⭐ |
| `components/Card/CardRenderer.tsx` | 卡片渲染器，负责整体布局 | ⭐⭐⭐⭐⭐ |
| `components/Card/BlockRenderer.tsx` | Block 渲染器，支持多种内容类型 | ⭐⭐⭐⭐⭐ |
| `services/api.ts` | API 调用封装，管理用户 ID | ⭐⭐⭐⭐ |
| `App.css` | 样式主题定义 | ⭐⭐⭐ |

## 数据流

### 内容生成流程

```
Director Agent (选题)
    ↓
Actor Agent (逐个生成内容)
    ↓
Validator (验证格式)
    ↓
Card 数据库 (存储)
    ↓
Redis 队列 (分发给用户)
    ↓
Frontend API (获取并渲染)
```

### 用户交互流程

```
用户打开应用
    ↓
FeedContainer.loadNextCard()
    ↓
API: /api/feed/next
    ↓
从 Redis 队列取出 card_id
    ↓
从数据库查询完整内容
    ↓
返回给前端
    ↓
CardRenderer 渲染
    ↓
用户交互 (LIKE/SKIP)
    ↓
记录到 Interaction 表
    ↓
重复循环
```

## 扩展点

### 添加新的 Block 类型

1. 在 `types/card.ts` 中添加新类型
2. 在 `BlockRenderer.tsx` 中添加渲染逻辑
3. 在 `prompts.md` 的 Actor Prompt 中说明新类型

### 添加新的 API 端点

1. 在 `backend/routes/` 创建新的蓝图
2. 在 `app.py` 中注册蓝图
3. 在 `frontend/services/api.ts` 添加调用方法

### 自定义样式主题

在 `frontend/src/App.css` 中添加新的样式类：

```css
.my_theme {
  background: ...;
  color: ...;
}
```

然后在 Actor Prompt 中添加到 `style_preset` 可选值。

## 开发工作流

1. **修改提示词** → `prompts.md`
2. **生成新内容** → `python scripts/factory.py --generate 10`
3. **测试 API** → `curl http://localhost:5000/api/feed/next?user_id=test`
4. **调整样式** → `frontend/src/App.css`
5. **提交代码** → `git commit -m "feat: ..."`

## 性能优化建议

- 后端：使用 Gunicorn + Nginx 部署
- Redis：设置合理的过期时间和内存上限
- 前端：启用 Vite 的代码分割和懒加载
- 数据库：为高频查询字段添加索引

## 监控要点

- LLM API 调用次数和成本
- Redis 队列长度
- 卡片生成成功率
- 用户交互数据（LIKE/SKIP 比例）
- 平均停留时长
