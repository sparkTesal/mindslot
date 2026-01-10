"""
ContentFactoryService - 内容工厂服务

负责协调 Director 和 Actor Agent，自动生成卡片内容。
当卡片库存不足时自动触发生成流程。
"""

import threading
import time
from typing import List, Optional
from models import db


class ContentFactoryService:
    """
    内容工厂服务 - 异步生成卡片内容
    
    工作流程:
    1. Director Agent 生成选题清单
    2. Actor Agent 根据选题生成卡片内容
    3. 验证并存入数据库
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.director = None
        self.actor = None
        self._generating = False
        self._generation_lock = threading.Lock()
        self._llm_available = False
        
        # 尝试初始化 Agent（延迟导入避免循环依赖）
        try:
            from agents.director import DirectorAgent
            from agents.actor import ActorAgent
            
            self.director = DirectorAgent()
            self.actor = ActorAgent()
            
            # 检查 LLM 是否真正可用
            if self.director.llm.is_available():
                self._llm_available = True
                print("[ContentFactory] Initialized with LLM support")
            else:
                print("[ContentFactory] Initialized but LLM not available (no API key)")
        except Exception as e:
            print(f"[ContentFactory] Initialized without LLM support: {e}")
        
        self._initialized = True
    
    def is_llm_available(self) -> bool:
        """检查 LLM 是否可用"""
        return self._llm_available
    
    def get_card_pool_status(self) -> dict:
        """获取卡片池状态"""
        from models.card import Card
        from models.interaction import Interaction
        
        total_cards = Card.query.count()
        
        # 统计各标签的卡片数量
        all_cards = Card.query.all()
        tag_counts = {}
        for card in all_cards:
            for tag in card.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            "total_cards": total_cards,
            "tag_distribution": tag_counts,
            "is_generating": self._generating,
            "llm_available": self._llm_available
        }
    
    def generate_cards_sync(self, count: int = 10, domains: str = None, 
                            user_preferences: dict = None) -> List[dict]:
        """
        同步生成卡片（阻塞调用）
        
        Args:
            count: 要生成的卡片数量
            domains: 领域范围，如 "Java, Python, AI, History"
            user_preferences: 用户偏好，用于个性化生成
        
        Returns:
            生成成功的卡片列表
        """
        # 检查 LLM 是否可用
        if not self._llm_available:
            print("[ContentFactory] Cannot generate cards: LLM not available")
            return []
        
        with self._generation_lock:
            if self._generating:
                print("[ContentFactory] Generation already in progress, skipping")
                return []
            self._generating = True
        
        try:
            from services.card_service import CardService
            
            print(f"[ContentFactory] Starting generation of {count} cards...")
            
            # 1. 根据用户偏好调整 domains
            if user_preferences and user_preferences.get('preferred_tags'):
                preferred = user_preferences['preferred_tags'][:3]
                domains = ", ".join(preferred) + ", History, Science, Memes"
            elif not domains:
                domains = "Java, Python, AI, History, Science, Philosophy, Memes"
            
            # 2. Director 生成选题
            print(f"[ContentFactory] Director generating topics for: {domains}")
            topics = self.director.generate_topics(count=count, domains=domains)
            
            if not topics:
                print("[ContentFactory] Director failed to generate topics")
                return []
            
            print(f"[ContentFactory] Director generated {len(topics)} topics")
            
            # 3. Actor 逐个生成卡片
            generated_cards = []
            for i, topic_data in enumerate(topics):
                try:
                    print(f"[ContentFactory] Actor generating card {i+1}/{len(topics)}: {topic_data.get('topic', 'Unknown')}")
                    
                    payload = self.actor.generate_card(topic_data)
                    
                    if payload and self._validate_payload(payload):
                        # 4. 存入数据库
                        card = CardService.create_card(
                            topic=topic_data.get('topic', 'Unknown'),
                            tags=topic_data.get('tags', []),
                            complexity=topic_data.get('complexity', 3),
                            payload=payload
                        )
                        generated_cards.append(card.to_dict())
                        print(f"[ContentFactory] Card saved: {card.id}")
                    else:
                        print(f"[ContentFactory] Invalid payload for topic: {topic_data.get('topic')}")
                        
                except Exception as e:
                    print(f"[ContentFactory] Error generating card: {e}")
                    continue
            
            print(f"[ContentFactory] Generation complete: {len(generated_cards)}/{len(topics)} cards created")
            return generated_cards
            
        finally:
            self._generating = False
    
    def generate_cards_async(self, count: int = 10, domains: str = None,
                             user_preferences: dict = None, app_context=None):
        """
        异步生成卡片（非阻塞）
        
        Args:
            count: 要生成的卡片数量
            domains: 领域范围
            user_preferences: 用户偏好
            app_context: Flask 应用上下文（必须传入）
        """
        def _generate():
            if app_context:
                with app_context:
                    self.generate_cards_sync(count, domains, user_preferences)
            else:
                self.generate_cards_sync(count, domains, user_preferences)
        
        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()
        print(f"[ContentFactory] Async generation started in background")
    
    def _validate_payload(self, payload: dict) -> bool:
        """验证卡片 payload 是否符合规范"""
        required_fields = ['title', 'blocks']
        
        if not all(field in payload for field in required_fields):
            return False
        
        if not isinstance(payload.get('blocks'), list):
            return False
        
        if len(payload['blocks']) == 0:
            return False
        
        # 验证 blocks 结构
        valid_types = {'chat_bubble', 'mermaid', 'markdown', 'code_snippet', 'quote'}
        for block in payload['blocks']:
            if not isinstance(block, dict):
                return False
            if block.get('type') not in valid_types:
                return False
            if 'content' not in block:
                return False
        
        return True
    
    def ensure_minimum_stock(self, min_count: int = 20, user_preferences: dict = None,
                             app_context=None) -> bool:
        """
        确保卡片池有最低库存
        
        Args:
            min_count: 最低库存数量
            user_preferences: 用户偏好
            app_context: Flask 应用上下文
        
        Returns:
            是否触发了生成
        """
        from models.card import Card
        
        current_count = Card.query.count()
        
        if current_count < min_count:
            needed = min_count - current_count + 10  # 多生成一些
            print(f"[ContentFactory] Stock low ({current_count}/{min_count}), generating {needed} cards")
            self.generate_cards_async(
                count=needed,
                user_preferences=user_preferences,
                app_context=app_context
            )
            return True
        
        return False


# 全局单例
content_factory = ContentFactoryService()
