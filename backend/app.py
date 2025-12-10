#!/usr/bin/env python
"""
MindSlot Backend API
"""
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from models.card import Card
from models.interaction import Interaction
from models.user import User
from routes.feed import feed_bp
from routes.interaction import interaction_bp

# 创建 Flask 应用
app = Flask(__name__)
app.config.from_object(Config)

# 启用 CORS
CORS(app)

# 初始化数据库
db.init_app(app)

# 注册路由
app.register_blueprint(feed_bp, url_prefix='/api/feed')
app.register_blueprint(interaction_bp, url_prefix='/api/interaction')

# 健康检查
@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "service": "MindSlot Backend",
        "version": "0.1.0"
    })

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to MindSlot API",
        "endpoints": {
            "feed": "/api/feed/next",
            "interaction": "/api/interaction/record",
            "health": "/health"
        }
    })

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # 开发环境下自动创建表
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")
    
    print("🚀 MindSlot Backend starting...")
    print("📍 API available at: http://localhost:5000")
    print("📖 Health check: http://localhost:5000/health")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
