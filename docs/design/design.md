# MindSlot MVP Design Document (v0.1)

**项目名称：** MindSlot (脑力老虎机)

**核心目标：** 构建一个基于 LLM 生成、异步预加载、高信噪比的沉浸式信息流应用。

**开发原则：** 轻量级启动，重架构逻辑，优先跑通"生产-消费"闭环。

## 1. 系统架构概览 (System Architecture)

系统采用 "前店后厂" (Storefront-Factory) 模式，将耗时的 LLM 生成与实时的用户交互完全解耦。

```mermaid
graph TD
    User[用户 (Mobile Web)] <--> |实时交互 JSON| API_Gateway[Python Backend API]
    
    subgraph "前台 (Storefront)"
        API_Gateway <--> |读/写| Redis_Queue[Redis User Buffer Queue]
        API_Gateway <--> |记录行为| DB_Interaction[交互日志表]
    end
    
    subgraph "后台工厂 (Content Factory)"
        Scheduler[定时任务/Worker] --> |1. 制定选题| Director_Agent[LLM Director]
        Director_Agent --> |2. 下发蓝本指令| Actor_Agent[LLM Actor]
        Actor_Agent --> |3. 生成结构化内容| Parser[JSON Parser & Validator]
        Parser --> |4. 入库| DB_Card_Pool[卡片公共池 (Postgres/SQLite)]
        
        Distributor[分发器 Worker] --> |5. 捞取 & 填充| DB_Card_Pool
        Distributor --> |6. Push| Redis_Queue
    end
```

## 2. 技术栈选型 (Tech Stack)

- **Frontend:** React 18 (Vite), TailwindCSS, Framer Motion (动画), Mermaid.js (图表渲染), React-Markdown
- **Backend:** Python (Flask 或 FastAPI). MVP 建议 Flask 配合 Celery/APScheduler 做异步任务
- **Database:**
  - SQLite (Dev) / PostgreSQL (Prod): 存储卡片内容、用户元数据
  - Redis: 存储用户的待消费队列 (List)、Session 上下文
- **LLM:** DeepSeek-Chat (性价比高，中文强) 或 GPT-4o (逻辑强)

## 3. 数据模型设计 (Data Models)

### 3.1 Card (卡片表)

存储生产好的静态内容（蓝本）。

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | 主键 |
| topic | String | 主题 (e.g., "Java GC", "Rome Fall") |
| tags | JSON | 标签 (e.g., ["History", "DarkHumor", "Tech"]) |
| complexity | Int | 1-5 (1=小白, 5=硬核) |
| payload | JSON | 核心内容，包含渲染所需的所有数据 (见 4.1) |
| created_at | DateTime | 创建时间 |

### 3.2 UserQueue (Redis List)

- **Key:** `queue:user:{user_id}`
- **Value:** List of card_id
- **Logic:** 保持长度在 10-20 之间。低于阈值触发后台补货。

### 3.3 Interaction (交互表)

用于后续训练推荐算法。

| Field | Type | Description |
|-------|------|-------------|
| user_id | UUID | 用户ID |
| card_id | UUID | 卡片ID |
| action | Enum | LIKE, SKIP, finish_read, expand |
| duration | Int | 停留毫秒数 |

## 4. 核心协议：卡片数据结构 (Card Protocol)

前端不展示纯文本，而是渲染结构化 JSON。

### 4.1 JSON Payload 示例

```json
{
  "card_id": "c-1024",
  "style_preset": "cyberpunk_terminal",
  "title": "为什么 synchronized 以前很慢？",
  "hook_text": "别被老黄历骗了，现在的锁比你想象的聪明。",
  "blocks": [
    {
      "type": "chat_bubble",
      "role": "roast_master",
      "content": "还在背八股文说 synchronized 是重量级锁？JDK 6 的偏向锁都要笑死在常量池里了。"
    },
    {
      "type": "mermaid",
      "content": "graph TD; A[无锁] -->|线程A访问| B[偏向锁]; B -->|线程B竞争| C[轻量级锁(CAS)]; C -->|自旋失败| D[重量级锁(OS Mutex)];"
    },
    {
      "type": "markdown",
      "content": "**关键点：** 只有在`D`阶段，线程才会真正挂起进入内核态。前面的阶段都是用户态的自嗨，极快。"
    },
    {
      "type": "code_snippet",
      "lang": "java",
      "content": "Object header = new Object(); // Mark Word 就在这里"
    }
  ]
}
```

## 5. 后台工厂逻辑 (Content Factory Pipeline)

### 5.1 Step 1: Director Agent (选题与编排)

- **Prompt 目标:** 生成选题清单，确保多样性
- **输入:** 预设的领域列表 (Java, AI, History, Meme)
- **输出 JSON:**

```json
[
  {"topic": "Java Virtual Threads", "tone": "Excited", "format": "code_comparison"},
  {"topic": "The absurdity of microservices", "tone": "Sarcastic", "format": "rant"}
]
```

### 5.2 Step 2: Actor Agent (内容生成)

- **Prompt 目标:** 根据 Director 的指令，生成符合 Card Protocol 的 JSON
- **关键指令:**
  - "You are NOT a helpful assistant. You are a chaotic senior engineer."
  - "Use Mermaid diagrams for logic."
  - "Keep text blocks under 50 words."

## 6. 推荐与分发逻辑 (MVP Version)

### 6.1 补货策略 (Replenishment)

当用户请求 `/feed/next` 且 Redis 队列长度 < 5 时，触发异步补货任务：

1. **Search:** 从 Card 数据库中随机捞取 10 张卡片
2. **Filter:** 排除用户 Interaction 表中已看过的 card_id
3. **Push:** 塞入 Redis 队列

MVP 阶段暂不实现复杂的 Vector Embedding 匹配，优先保证队列有货且不重复。

### 6.2 斯金纳箱微调

在补货时，按以下比例混合卡片类型：

- 60% 核心兴趣 (基于用户选定的 Tags, 如 Java)
- 30% 随机/通识 (History, Science)
- 10% 惊喜/整活 (High Entropy, Jokes)

## 7. 前端交互设计 (UI/UX)

### 7.1 布局

- **全屏沉浸式：** 类似 TikTok/Instagram Reels
- **无无限滚动：** 采用 Snap Scrolling (一次一张)，强制用户做决策 (看完/滑走)

### 7.2 交互手势

- **上滑 (Swipe Up):** 下一张 (Next)
- **长按 (Long Press):** 触发 "Deep Dive" 模式 (调用 LLM 实时生成该话题的深度解释，这是唯一的实时生成场景)
- **双击 (Double Tap):** 收藏/点赞 (记录到 Long-term Memory)

## 8. 开发路线图 (Roadmap)

### Phase 1: The Pipeline (本周目标)

1. 搭建 Flask + SQLite 环境
2. 写一个 Python 脚本 (Factory)，调用 LLM 生成 20 个 JSON 卡片存入数据库
3. 写一个 API `/feed/next` 能从数据库随机返回一个 JSON
4. 前端 React 能解析这个 JSON 并渲染出 Mermaid 图和文字

### Phase 2: The Queue & User (下周目标)

1. 引入 Redis，实现 User Queue 逻辑
2. 实现"已读去重"
3. 增加"长按 Deep Dive"功能

### Phase 3: The Brain (未来迭代)

1. 引入 Vector DB，实现基于语义的推荐
2. 完善 LLM Director 的策略，根据用户疲劳度动态调整内容难度
