from flask import Blueprint, jsonify, request
from models import db
from models.interaction import Interaction
import uuid

interaction_bp = Blueprint('interaction', __name__)

@interaction_bp.route('/record', methods=['POST'])
def record_interaction():
    """记录用户交互行为"""
    data = request.get_json()
    
    required_fields = ['user_id', 'card_id', 'action']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # 验证 action 枚举值
    valid_actions = ['LIKE', 'SKIP', 'FINISH_READ', 'EXPAND']
    if data['action'] not in valid_actions:
        return jsonify({"error": f"Invalid action. Must be one of: {valid_actions}"}), 400
    
    try:
        interaction = Interaction(
            user_id=uuid.UUID(data['user_id']),
            card_id=uuid.UUID(data['card_id']),
            action=data['action'],
            duration=data.get('duration')
        )
        
        db.session.add(interaction)
        db.session.commit()
        
        return jsonify({"status": "ok", "id": str(interaction.id)})
    except ValueError as e:
        return jsonify({"error": f"Invalid UUID format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to record interaction: {str(e)}"}), 500

@interaction_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取用户统计数据"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    try:
        user_uuid = uuid.UUID(user_id)
        
        total = Interaction.query.filter_by(user_id=user_uuid).count()
        likes = Interaction.query.filter_by(user_id=user_uuid, action='LIKE').count()
        skips = Interaction.query.filter_by(user_id=user_uuid, action='SKIP').count()
        finished = Interaction.query.filter_by(user_id=user_uuid, action='FINISH_READ').count()
        
        # 计算平均停留时间
        interactions_with_duration = Interaction.query.filter(
            Interaction.user_id == user_uuid,
            Interaction.duration.isnot(None)
        ).all()
        
        avg_duration = 0
        if interactions_with_duration:
            avg_duration = sum(i.duration for i in interactions_with_duration) / len(interactions_with_duration)
        
        return jsonify({
            "total_interactions": total,
            "total_likes": likes,
            "total_skips": skips,
            "total_finished": finished,
            "avg_duration_ms": int(avg_duration),
            "engagement_rate": round(likes / total * 100, 2) if total > 0 else 0
        })
    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400

@interaction_bp.route('/history', methods=['GET'])
def get_history():
    """获取用户历史记录"""
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 20))
    
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    
    try:
        user_uuid = uuid.UUID(user_id)
        
        interactions = Interaction.query.filter_by(user_id=user_uuid)\
            .order_by(Interaction.created_at.desc())\
            .limit(limit)\
            .all()
        
        history = [{
            "id": str(i.id),
            "card_id": str(i.card_id),
            "action": i.action,
            "duration": i.duration,
            "created_at": i.created_at.isoformat()
        } for i in interactions]
        
        return jsonify({"history": history})
    except ValueError:
        return jsonify({"error": "Invalid user_id format"}), 400
