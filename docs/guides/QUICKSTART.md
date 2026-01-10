# MindSlot 快速启动指南

## 第一步：环境准备

### 1. 安装 Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# 或使用 Docker
docker run -d -p 6379:6379 redis:alpine
```

### 2. 安装 Python 依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

如果使用 OpenAI:
```env
OPENAI_API_KEY=sk-your-key-here
```

如果使用 DeepSeek（推荐，更便宜）:
```env
DEEPSEEK_API_KEY=your-deepseek-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

## 第二步：初始化数据库并生成内容

```bash
cd backend

# 1. 初始化数据库表
python scripts/init_db.py

# 2. 生成 10 张测试卡片
python scripts/factory.py --generate 10

# 3. 查看生成的卡片
python scripts/factory.py --list
```

## 第三步：启动后端服务

```bash
cd backend
python app.py
```

后端将运行在 http://localhost:5000

## 第四步：启动前端服务

打开新终端：

```bash
cd frontend
npm install
npm run dev
```

前端将运行在 http://localhost:5173

## 第五步：开始体验！

打开浏览器访问 http://localhost:5173

- **双击卡片**：点赞收藏 ❤️
- **上滑 / 空格键**：下一张
- **方向键 ↑**：下一张

## 常见问题

### Q: Redis 连接失败？

确保 Redis 正在运行：
```bash
redis-cli ping
# 应该返回 PONG
```

### Q: LLM API 调用失败？

1. 检查 `.env` 文件中的 API Key 是否正确
2. 检查网络连接
3. 查看后端日志输出

### Q: 卡片生成失败？

1. 确认 API Key 有余额
2. 检查是否被限速
3. 尝试减少 batch size:
```bash
python scripts/factory.py --generate 5
```

### Q: 前端无法获取卡片？

1. 确认后端服务正在运行
2. 检查浏览器控制台是否有 CORS 错误
3. 确认数据库中有卡片：
```bash
python scripts/factory.py --list
```

## 生产环境部署

参考 README.md 的"部署"章节。

## 下一步

- 调整 `prompts.md` 中的提示词，定制内容风格
- 修改 `frontend/src/App.css` 中的样式主题
- 增加新的 Block 类型（参考 README.md）

祝你玩得开心！🎰🧠
