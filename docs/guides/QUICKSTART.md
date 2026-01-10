# MindSlot 快速启动指南

## 一键启动（推荐）

### Windows

双击运行 `start.bat`，脚本会自动：
1. 检查并激活 conda 环境
2. 安装依赖（首次运行）
3. 启动后端和前端服务
4. 自动打开浏览器

### Linux/macOS

```bash
chmod +x start.sh
./start.sh
```

---

## 手动启动

### 第一步：环境准备

#### 1. 创建 Conda 环境（推荐）

```bash
conda create -n mindslot python=3.11 -y
conda activate mindslot
```

#### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

#### 4. 配置 LLM API Key（可选，用于无限内容生成）

**Windows (PowerShell):**
```powershell
# 使用 DeepSeek（推荐，更便宜）
$env:DEEPSEEK_API_KEY = "your-deepseek-key"

# 或使用 OpenAI
$env:OPENAI_API_KEY = "sk-your-key-here"
```

**Windows (CMD):**
```cmd
set DEEPSEEK_API_KEY=your-deepseek-key
:: 或
set OPENAI_API_KEY=sk-your-key-here
```

**Linux/macOS:**
```bash
export DEEPSEEK_API_KEY=your-deepseek-key
# 或
export OPENAI_API_KEY=sk-your-key-here
```

> 💡 不配置 API Key 也可以使用，但看完预置卡片后无法生成新内容。

---

### 第二步：启动服务

#### 启动后端

```bash
cd backend
conda activate mindslot
python app.py
```

后端将运行在 http://localhost:5000

#### 启动前端（新终端）

```bash
cd frontend
npm run dev
```

前端将运行在 http://localhost:5173

---

### 第三步：开始体验！

打开浏览器访问 http://localhost:5173

**操作方式：**
- 🖱️ **双击卡片**：点赞收藏 ❤️
- ⬆️ **点击按钮**：下一张
- ⌨️ **空格键/↑**：下一张

---

## 生成更多卡片

### 方式一：通过脚本生成（需要 API Key）

```bash
cd backend
conda activate mindslot
python scripts/factory.py --generate 10
```

### 方式二：自动生成

配置好 API Key 后，当卡片用完时系统会自动触发 LLM 生成新内容。

### 查看当前卡片

```bash
python scripts/factory.py --list
```

---

## 常见问题

### Q: Redis 连接失败？

**不影响使用！** 系统会自动使用内存队列。如果需要 Redis：

```bash
# Windows (使用 Docker)
docker run -d -p 6379:6379 redis:alpine

# 或者直接跳过，内存队列完全够用
```

### Q: 卡片用完了怎么办？

1. 如果配置了 LLM API Key：系统会自动生成新卡片
2. 如果没有配置：运行 `python scripts/factory.py --generate 10`

### Q: LLM API 调用失败？

1. 检查 API Key 是否正确设置
2. 检查网络连接
3. 确认 API Key 有余额
4. 查看后端日志输出

### Q: 前端无法获取卡片？

1. 确认后端服务正在运行
2. 检查浏览器控制台是否有错误
3. 尝试刷新页面

---

## API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/feed/next?user_id=xxx` | 获取下一张卡片 |
| `POST /api/interaction/record` | 记录用户交互 |
| `GET /api/feed/recommendations?user_id=xxx` | 获取推荐分析 |
| `POST /api/feed/generate` | 手动触发卡片生成 |
| `GET /api/feed/pool/status` | 获取卡片池状态 |
| `GET /health` | 健康检查 |

---

## 下一步

- 📝 调整 `docs/development/prompts.md` 中的提示词，定制内容风格
- 🎨 修改 `frontend/src/App.css` 中的样式主题
- 📊 查看 `docs/development/TODO.md` 了解开发进度

祝你玩得开心！🎰🧠
