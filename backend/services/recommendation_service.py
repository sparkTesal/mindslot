"""
RecommendationService - 推荐服务

基于用户行为数据实现个性化推荐，包括：
1. 用户兴趣分析 - 基于 LIKE/SKIP 计算标签权重
2. 斯金纳箱混合 - 60% 兴趣 / 30% 通识 / 10% 惊喜
3. 短期记忆 - 避免连续推送相似内容
4. 秒滑检测 - 识别不感兴趣的话题
"""

from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import random
import uuid

from models import db
from models.card import Card
from models.interaction import Interaction


class RecommendationService:
    """推荐服务 - 基于用户行为的智能推荐"""
    
    # 斯金纳箱配比
    INTEREST_RATIO = 0.6    # 60% 核心兴趣
    GENERAL_RATIO = 0.3     # 30% 通识/随机
    SURPRISE_RATIO = 0.1    # 10% 惊喜/整活
    
    # 秒滑阈值（毫秒）
    QUICK_SKIP_THRESHOLD = 2000  # 停留少于 2 秒视为秒滑
    
    # 短期记忆窗口
    SESSION_WINDOW_MINUTES = 30
    
    # 通识标签
    GENERAL_TAGS = ['History', 'Science', 'Philosophy', 'Economics', 'Psychology']
    
    # 惊喜/整活标签
    SURPRISE_TAGS = ['Memes', 'Dark_Humor', 'Controversy', 'Mind_Blown', 'Random']
    
    def __init__(self):
        pass
    
    def analyze_user_interests(self, user_id: str) -> Dict[str, float]:
        """
        分析用户兴趣，返回标签权重
        
        算法:
        - LIKE: 标签权重 +2
        - SKIP (停留 > 2s): 标签权重 +0 (中性)
        - SKIP (停留 < 2s，秒滑): 标签权重 -1
        
        Returns:
            {tag: weight} 标签权重字典，已归一化
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return {}
        
        # 获取所有交互记录
        interactions = Interaction.query.filter_by(user_id=user_uuid).all()
        
        if not interactions:
            return {}
        
        tag_weights = defaultdict(float)
        tag_counts = defaultdict(int)
        
        for interaction in interactions:
            # 获取卡片的标签
            card = Card.query.get(interaction.card_id)
            if not card:
                continue
            
            for tag in card.tags:
                tag_counts[tag] += 1
                
                if interaction.action == 'LIKE':
                    tag_weights[tag] += 2.0
                elif interaction.action == 'SKIP':
                    duration = interaction.duration or 0
                    if duration < self.QUICK_SKIP_THRESHOLD:
                        # 秒滑 = 不感兴趣
                        tag_weights[tag] -= 1.0
                    # 正常跳过不影响权重
        
        # 归一化权重
        if not tag_weights:
            return {}
        
        min_weight = min(tag_weights.values())
        max_weight = max(tag_weights.values())
        weight_range = max_weight - min_weight
        
        if weight_range > 0:
            normalized = {
                tag: (weight - min_weight) / weight_range
                for tag, weight in tag_weights.items()
            }
        else:
            # 所有权重相同
            normalized = {tag: 0.5 for tag in tag_weights.keys()}
        
        return normalized
    
    def get_preferred_tags(self, user_id: str, top_n: int = 5) -> List[str]:
        """获取用户最感兴趣的 N 个标签"""
        interests = self.analyze_user_interests(user_id)
        
        if not interests:
            return []
        
        # 按权重排序
        sorted_tags = sorted(interests.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in sorted_tags[:top_n]]
    
    def get_disliked_tags(self, user_id: str, threshold: float = 0.2) -> List[str]:
        """获取用户不感兴趣的标签（权重低于阈值）"""
        interests = self.analyze_user_interests(user_id)
        
        return [tag for tag, weight in interests.items() if weight < threshold]
    
    def get_session_context(self, user_id: str) -> Dict:
        """
        获取短期记忆/会话上下文
        
        Returns:
            {
                'recent_tags': [最近30分钟看过的标签],
                'recent_card_ids': [最近看过的卡片ID],
                'last_complexity': 最后一张卡片的复杂度,
                'quick_skipped_tags': [被秒滑的标签]
            }
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return {'recent_tags': [], 'recent_card_ids': [], 'quick_skipped_tags': []}
        
        # 最近 30 分钟的交互
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.SESSION_WINDOW_MINUTES)
        
        recent_interactions = Interaction.query.filter(
            Interaction.user_id == user_uuid,
            Interaction.created_at >= cutoff_time
        ).order_by(Interaction.created_at.desc()).all()
        
        recent_tags = []
        recent_card_ids = []
        quick_skipped_tags = []
        last_complexity = 3  # 默认中等
        
        for interaction in recent_interactions:
            card = Card.query.get(interaction.card_id)
            if not card:
                continue
            
            recent_card_ids.append(str(card.id))
            recent_tags.extend(card.tags)
            
            if interaction.action == 'SKIP':
                duration = interaction.duration or 0
                if duration < self.QUICK_SKIP_THRESHOLD:
                    quick_skipped_tags.extend(card.tags)
            
            if not last_complexity and card.complexity:
                last_complexity = card.complexity
        
        return {
            'recent_tags': list(set(recent_tags)),
            'recent_card_ids': recent_card_ids,
            'last_complexity': last_complexity,
            'quick_skipped_tags': list(set(quick_skipped_tags))
        }
    
    def get_recommended_cards(self, user_id: str, count: int = 10) -> List[Card]:
        """
        获取推荐卡片列表（核心推荐算法）
        
        实现斯金纳箱混合比例：
        - 60% 核心兴趣
        - 30% 通识/随机
        - 10% 惊喜/整活
        
        Args:
            user_id: 用户ID
            count: 需要的卡片数量
        
        Returns:
            推荐的卡片列表
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            # 无效用户ID，返回随机卡片
            return self._get_random_cards(count, [])
        
        # 1. 获取用户已看过的卡片
        viewed_card_ids = db.session.query(Interaction.card_id).filter(
            Interaction.user_id == user_uuid
        ).all()
        viewed_ids = [cid[0] for cid in viewed_card_ids]
        
        # 2. 获取用户兴趣和会话上下文
        preferred_tags = self.get_preferred_tags(user_id)
        session_context = self.get_session_context(user_id)
        disliked_tags = session_context.get('quick_skipped_tags', [])
        
        # 3. 计算各类卡片数量
        interest_count = int(count * self.INTEREST_RATIO)
        general_count = int(count * self.GENERAL_RATIO)
        surprise_count = count - interest_count - general_count
        
        recommended = []
        
        # 4. 获取兴趣卡片
        if preferred_tags:
            interest_cards = self._get_cards_by_tags(
                preferred_tags, 
                interest_count, 
                exclude_ids=viewed_ids,
                exclude_tags=disliked_tags
            )
            recommended.extend(interest_cards)
        
        # 5. 获取通识卡片
        general_cards = self._get_cards_by_tags(
            self.GENERAL_TAGS,
            general_count,
            exclude_ids=viewed_ids + [c.id for c in recommended],
            exclude_tags=disliked_tags
        )
        recommended.extend(general_cards)
        
        # 6. 获取惊喜卡片
        surprise_cards = self._get_cards_by_tags(
            self.SURPRISE_TAGS,
            surprise_count,
            exclude_ids=viewed_ids + [c.id for c in recommended],
            exclude_tags=[]  # 惊喜卡片不排除
        )
        recommended.extend(surprise_cards)
        
        # 7. 如果不够数量，用随机卡片补充
        if len(recommended) < count:
            remaining = count - len(recommended)
            random_cards = self._get_random_cards(
                remaining,
                exclude_ids=viewed_ids + [c.id for c in recommended]
            )
            recommended.extend(random_cards)
        
        # 8. 打乱顺序（斯金纳箱的随机性）
        random.shuffle(recommended)
        
        return recommended
    
    def _get_cards_by_tags(self, tags: List[str], count: int, 
                           exclude_ids: List = None,
                           exclude_tags: List[str] = None) -> List[Card]:
        """根据标签获取卡片"""
        if not tags:
            return []
        
        exclude_ids = exclude_ids or []
        exclude_tags = exclude_tags or []
        
        # SQLite 的 JSON 查询比较受限，使用 Python 过滤
        all_cards = Card.query.all()
        
        matching_cards = []
        for card in all_cards:
            if card.id in exclude_ids:
                continue
            
            # 检查是否包含排除标签
            if any(tag in card.tags for tag in exclude_tags):
                continue
            
            # 检查是否包含目标标签
            if any(tag in card.tags for tag in tags):
                matching_cards.append(card)
        
        # 随机选择
        random.shuffle(matching_cards)
        return matching_cards[:count]
    
    def _get_random_cards(self, count: int, exclude_ids: List = None) -> List[Card]:
        """获取随机卡片"""
        exclude_ids = exclude_ids or []
        
        query = Card.query
        if exclude_ids:
            query = query.filter(Card.id.notin_(exclude_ids))
        
        cards = query.order_by(db.func.random()).limit(count).all()
        return cards
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """
        获取用户偏好摘要（用于传递给 ContentFactory）
        """
        preferred_tags = self.get_preferred_tags(user_id)
        disliked_tags = self.get_disliked_tags(user_id)
        interests = self.analyze_user_interests(user_id)
        
        return {
            'preferred_tags': preferred_tags,
            'disliked_tags': disliked_tags,
            'interest_weights': interests,
            'has_history': len(interests) > 0
        }


# 全局单例
recommendation_service = RecommendationService()
