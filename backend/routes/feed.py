"""
Feed 路由 - 卡片流服务

提供卡片获取、队列管理等 API
"""

from flask import Blueprint, jsonify, request, current_app
from models import db
from models.card import Card
from models.interaction import Interaction
from services.queue_service import QueueService
from services.card_service import CardService
from services.recommendation_service import recommendation_service
from services.content_factory import content_factory
import uuid

feed_bp = Blueprint('feed', __name__)
queue_service = QueueService()

# 配置
MIN_CARD_STOCK = 10  # 最低卡片库存
MIN_QUEUE_LENGTH = 5  # 触发补货的队列长度阈值
PREEMPTIVE_GENERATE_THRESHOLD = 3  # 提前触发生成的阈值（未看过的卡片数）


@feed_bp.route('/next', methods=['GET'])
def get_next_card():
    """
    获取下一张卡片
    
    工作流程:
    1. 从用户队列获取卡片ID
    2. 如果队列为空，触发智能补货
    3. 如果卡片库存不足，触发异步生成
    4. 返回卡片内容
    """
    user_id = request.args.get('user_id')
    
    if not user_id:
        user_id = str(uuid.uuid4())
    
    # 验证 UUID 格式
    try:
        uuid.UUID(user_id)
    except ValueError:
        user_id = str(uuid.uuid4())
    
    # 1. 从队列获取卡片ID
    try:
        card_id = queue_service.pop_card(user_id)
    except Exception as e:
        return jsonify({"error": f"Queue error: {str(e)}"}), 500
    
    # 2. 如果队列为空，触发补货
    if not card_id:
        replenish_count = replenish_queue(user_id)
        
        if replenish_count == 0:
            # 数据库也没有可用卡片
            if content_factory.is_llm_available():
                # LLM 可用，触发生成
                trigger_card_generation(user_id)
                return jsonify({
                    "error": "No cards available, generating new content...",
                    "generating": True
                }), 202  # 202 Accepted 表示请求已接受，正在处理
            else:
                # LLM 不可用，返回错误
                return jsonify({
                    "error": "No cards available. LLM not configured - please set OPENAI_API_KEY or DEEPSEEK_API_KEY.",
                    "generating": False,
                    "llm_available": False
                }), 503  # 503 Service Unavailable
        
        card_id = queue_service.pop_card(user_id)
    
    # 3. 如果还是没有，返回错误
    if not card_id:
        return jsonify({"error": "Card not found"}), 404
    
    # 4. 从数据库获取卡片内容
    try:
        card = CardService.get_card_by_id(card_id)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    
    if not card:
        return jsonify({"error": "Card not found in database"}), 404
    
    # 5. 检查队列和库存状态
    queue_length = queue_service.get_queue_length(user_id)
    total_cards = Card.query.count()
    
    # 6. 计算用户还有多少未看过的卡片
    unviewed_cards = CardService.get_unviewed_cards(user_id, limit=100)
    unviewed_count = len(unviewed_cards)
    
    # 7. 提前触发生成：如果未看过的卡片少于阈值，提前生成
    if unviewed_count <= PREEMPTIVE_GENERATE_THRESHOLD and content_factory.is_llm_available():
        if not content_factory._generating:  # 避免重复触发
            print(f"[Feed] Preemptive generation: only {unviewed_count} unviewed cards left")
            trigger_card_generation(user_id, async_mode=True)
    
    # 8. 构建响应
    response_data = card.to_dict()
    response_data['queue_length'] = queue_length
    response_data['unviewed_count'] = unviewed_count
    response_data['needs_replenish'] = queue_length < MIN_QUEUE_LENGTH
    response_data['total_cards_in_pool'] = total_cards
    
    return jsonify(response_data)


def replenish_queue(user_id: str, count: int = 10) -> int:
    """
    智能补货逻辑
    
    使用 RecommendationService 获取个性化推荐的卡片，
    而不是简单的随机获取。
    
    Args:
        user_id: 用户ID
        count: 补货数量
    
    Returns:
        成功推送的卡片数量
    """
    # 使用推荐服务获取卡片
    recommended_cards = recommendation_service.get_recommended_cards(user_id, count)
    
    if not recommended_cards:
        # 如果推荐服务返回空，尝试获取任意未看过的卡片
        cards = CardService.get_unviewed_cards(user_id, limit=count)
        card_ids = [str(card.id) for card in cards]
    else:
        card_ids = [str(card.id) for card in recommended_cards]
    
    # 推送到队列
    if card_ids:
        queue_service.push_cards(user_id, card_ids)
    
    return len(card_ids)


def trigger_card_generation(user_id: str, async_mode: bool = True):
    """
    触发卡片生成
    
    Args:
        user_id: 用户ID（用于获取偏好）
        async_mode: 是否异步生成
    """
    # 获取用户偏好
    user_preferences = recommendation_service.get_user_preferences(user_id)
    
    if async_mode:
        # 异步生成，传入 Flask 应用上下文
        content_factory.generate_cards_async(
            count=10,
            user_preferences=user_preferences,
            app_context=current_app.app_context()
        )
    else:
        # 同步生成（会阻塞请求）
        content_factory.generate_cards_sync(
            count=10,
            user_preferences=user_preferences
        )


@feed_bp.route('/queue/status', methods=['GET'])
def queue_status():
    """查看队列状态"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    length = queue_service.get_queue_length(user_id)
    cards = queue_service.peek_queue(user_id, count=5)
    
    # 获取用户兴趣分析
    interests = recommendation_service.analyze_user_interests(user_id)
    preferred_tags = recommendation_service.get_preferred_tags(user_id)
    
    return jsonify({
        "queue_length": length,
        "preview": cards[:5],
        "user_interests": interests,
        "preferred_tags": preferred_tags
    })


@feed_bp.route('/queue/replenish', methods=['POST'])
def manual_replenish():
    """手动触发补货"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    count = replenish_queue(user_id)
    return jsonify({
        "status": "ok",
        "cards_added": count,
        "new_queue_length": queue_service.get_queue_length(user_id)
    })


@feed_bp.route('/generate', methods=['POST'])
def trigger_generation():
    """
    手动触发卡片生成
    
    请求体:
    {
        "count": 10,
        "domains": "Java, Python, AI",
        "user_id": "xxx" (可选，用于个性化)
    }
    """
    data = request.get_json() or {}
    count = data.get('count', 10)
    domains = data.get('domains')
    user_id = data.get('user_id')
    
    user_preferences = None
    if user_id:
        user_preferences = recommendation_service.get_user_preferences(user_id)
    
    # 异步生成
    content_factory.generate_cards_async(
        count=count,
        domains=domains,
        user_preferences=user_preferences,
        app_context=current_app.app_context()
    )
    
    return jsonify({
        "status": "generating",
        "count": count,
        "message": "Card generation started in background"
    })


@feed_bp.route('/pool/status', methods=['GET'])
def pool_status():
    """获取卡片池状态"""
    status = content_factory.get_card_pool_status()
    return jsonify(status)


@feed_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    获取用户推荐分析
    
    返回用户的兴趣分析、偏好标签等信息
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    interests = recommendation_service.analyze_user_interests(user_id)
    preferred = recommendation_service.get_preferred_tags(user_id)
    disliked = recommendation_service.get_disliked_tags(user_id)
    session_context = recommendation_service.get_session_context(user_id)
    
    return jsonify({
        "interest_weights": interests,
        "preferred_tags": preferred,
        "disliked_tags": disliked,
        "session_context": session_context
    })
