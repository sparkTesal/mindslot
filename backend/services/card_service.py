from models import db
from models.card import Card
from models.interaction import Interaction
from typing import List
import uuid

class CardService:
    @staticmethod
    def get_unviewed_cards(user_id: str, limit: int = 10) -> List[Card]:
        """获取用户未查看过的卡片"""
        # 1. 获取用户已看过的卡片 ID
        viewed_card_ids = db.session.query(Interaction.card_id).filter(
            Interaction.user_id == uuid.UUID(user_id)
        ).all()
        viewed_ids = [cid[0] for cid in viewed_card_ids]
        
        # 2. 随机获取未看过的卡片
        query = Card.query
        if viewed_ids:
            query = query.filter(Card.id.notin_(viewed_ids))
        
        cards = query.order_by(db.func.random()).limit(limit).all()
        return cards
    
    @staticmethod
    def create_card(topic: str, tags: List[str], complexity: int, payload: dict) -> Card:
        """创建新卡片"""
        card = Card(
            topic=topic,
            tags=tags,
            complexity=complexity,
            payload=payload
        )
        db.session.add(card)
        db.session.commit()
        return card
    
    @staticmethod
    def get_card_by_id(card_id: str) -> Card:
        """根据 ID 获取卡片"""
        return Card.query.get(uuid.UUID(card_id))
    
    @staticmethod
    def get_all_cards(limit: int = 100) -> List[Card]:
        """获取所有卡片"""
        return Card.query.order_by(Card.created_at.desc()).limit(limit).all()
