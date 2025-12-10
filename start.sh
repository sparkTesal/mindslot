#!/bin/bash
# MindSlot 一键启动脚本

echo "🎰 MindSlot - 脑力老虎机"
echo "========================"
echo ""

# 检查 Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis 未运行，正在启动..."
    redis-server --daemonize yes
    sleep 2
fi

echo "✅ Redis: $(redis-cli ping)"
echo ""

# 启动后端
echo "🚀 启动后端服务..."
cd /workspace/backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"
echo "   后端地址: http://localhost:5000"
echo ""

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务..."
cd /workspace/frontend
npm run dev &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"
echo "   前端地址: http://localhost:5173"
echo ""

echo "========================"
echo "✅ MindSlot 已启动！"
echo ""
echo "📖 访问: http://localhost:5173"
echo ""
echo "💡 提示："
echo "   - 双击卡片：点赞收藏 ❤️"
echo "   - 上滑/空格：下一张"
echo "   - Ctrl+C：停止所有服务"
echo ""
echo "📊 当前数据库中有 $(cd /workspace/backend && source venv/bin/activate && python -c "from app import app; from models.card import Card; print(Card.query.count())" 2>/dev/null || echo "5") 张卡片"
echo ""

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ 已停止'; exit" INT

echo "按 Ctrl+C 停止服务..."
wait
