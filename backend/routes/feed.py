from flask import Blueprint, jsonify, request
from models import db
from models.card import Card
from models.interaction import Interaction
from services.queue_service import QueueService
from services.card_service import CardService
import uuid

feed_bp = Blueprint('feed', __name__)
queue_service = QueueService()

@feed_bp.route('/next', methods=['GET'])
def get_next_card():
    """获取下一张卡片"""
    user_id = request.args.get('user_id', str(uuid.uuid4()))  # MVP: 自动生成匿名用户
    
    # 1. 从 Redis 队列获取
    card_id = queue_service.pop_card(user_id)
    
    # 2. 如果队列为空，触发补货
    if not card_id:
        replenish_count = replenish_queue(user_id)
        if replenish_count == 0:
            return jsonify({"error": "No cards available"}), 404
        card_id = queue_service.pop_card(user_id)
    
    # 3. 如果还是没有，返回错误
    if not card_id:
        return jsonify({"error": "Card not found"}), 404
    
    # 4. 从数据库获取卡片内容
    card = CardService.get_card_by_id(card_id)
    if not card:
        return jsonify({"error": "Card not found in database"}), 404
    
    # 5. 检查队列长度，如果低于阈值，记录需要补货
    queue_length = queue_service.get_queue_length(user_id)
    response_data = card.to_dict()
    response_data['queue_length'] = queue_length
    response_data['needs_replenish'] = queue_length < 5
    
    return jsonify(response_data)

def replenish_queue(user_id: str, count: int = 10):
    """
    补货逻辑：从卡片池随机获取未看过的卡片
    返回：成功推送的卡片数量
    """
    # 获取未看过的卡片
    cards = CardService.get_unviewed_cards(user_id, limit=count)
    
    # 推送到 Redis 队列
    card_ids = [str(card.id) for card in cards]
    queue_service.push_cards(user_id, card_ids)
    
    return len(card_ids)

@feed_bp.route('/queue/status', methods=['GET'])
def queue_status():
    """查看队列状态"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    length = queue_service.get_queue_length(user_id)
    cards = queue_service.peek_queue(user_id, count=5)
    
    return jsonify({
        "queue_length": length,
        "preview": cards[:5]
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
