# MindSlot 开发 TODO 清单

> 根据设计文档整理的待办事项，用于后续迭代开发。

---

## ✅ 已完成 (Phase 1)

### 基础架构
- [x] Flask + SQLite 环境搭建
- [x] 数据模型：Card、User、Interaction 表
- [x] API `/feed/next` 随机返回卡片 JSON
- [x] React 前端解析 JSON 渲染
- [x] Mermaid 图表渲染
- [x] 多主题样式支持 (cyberpunk_terminal, paper_notes, comic_strip, zen_minimalist)
- [x] 代码高亮 (react-syntax-highlighter)
- [x] Markdown 渲染

### 交互
- [x] 上滑/按钮 → 下一张 (SKIP)
- [x] 双击 → 点赞收藏 (LIKE)
- [x] 用户队列逻辑 (内存队列，Redis 可选)
- [x] 已读去重

---

## 🚧 进行中 / 待修复

- [x] Mermaid 渲染在某些主题下样式不协调（需测试验证）

---

## 📋 Phase 2: The Queue & User

### 交互功能
- [ ] **长按 Deep Dive** - 调用 LLM 实时生成该话题的深度解释
  - 前端：检测长按手势 (500ms+)
  - 后端：新增 `/api/card/{id}/deep-dive` 接口
  - LLM：实时生成深度内容

### 推荐优化
- [ ] **秒滑检测** - 识别用户快速跳过行为
  - 前端：记录停留时长 < 2s 的卡片
  - 后端：短期记忆中排除相关话题

### 记录完善
- [ ] 记录 `finish_read` 事件（用户阅读完整张卡片）
- [ ] 记录 `expand` 事件（用户触发 Deep Dive）

---

## 📋 Phase 3: The Brain

### 推荐系统
- [ ] **斯金纳箱混合比例**
  - 60% 核心兴趣 (基于用户 Tags)
  - 30% 随机/通识
  - 10% 惊喜/整活

### 记忆系统
- [ ] **短期记忆 (Session - 30分钟)**
  - 节奏控制：深度内容后插入轻松内容
  - 防撞车：秒滑话题本局不再出现

- [ ] **中期记忆 (Interest Drift - 7~30天)**
  - 识别阶段性痴迷
  - 动态调整 Tag 权重

- [ ] **长期记忆 (Persona - 永久)**
  - 显式画像：用户设定的兴趣标签
  - 隐式向量：历史点赞内容的 Embedding 聚类

### 内容工厂
- [ ] **Director Agent** - 自动生成选题清单
- [ ] **Actor Agent** - 调用 LLM 批量生成卡片
- [ ] **定时任务/Worker** - 自动补充卡片库存
- [ ] **蓝本 + 变体** - 根据用户画像轻量级改写内容

### 高级功能
- [ ] 引入 Vector DB，实现基于语义的推荐
- [ ] 根据用户疲劳度动态调整内容难度
- [ ] PostgreSQL 生产环境迁移
- [ ] Redis 生产环境部署

---

## 💡 优化建议 (非设计文档)

- [ ] 移动端手势优化（真正的滑动手势支持）
- [ ] 加载动画/骨架屏
- [ ] 离线缓存 (PWA)
- [ ] 用户设置页面（选择兴趣标签、主题偏好）

---

*最后更新：2026-01-10*
