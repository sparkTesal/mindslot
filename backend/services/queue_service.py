import redis
import os
from typing import List

class QueueService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', None),
            decode_responses=True
        )
    
    def get_queue_key(self, user_id: str) -> str:
        return f"queue:user:{user_id}"
    
    def get_queue_length(self, user_id: str) -> int:
        """获取队列长度"""
        key = self.get_queue_key(user_id)
        return self.redis_client.llen(key)
    
    def push_cards(self, user_id: str, card_ids: List[str]):
        """批量推送卡片 ID 到用户队列"""
        key = self.get_queue_key(user_id)
        if card_ids:
            self.redis_client.rpush(key, *card_ids)
    
    def pop_card(self, user_id: str) -> str:
        """从队列头部取出一张卡片"""
        key = self.get_queue_key(user_id)
        return self.redis_client.lpop(key)
    
    def peek_queue(self, user_id: str, count: int = 10) -> List[str]:
        """查看队列前 N 张卡片（不移除）"""
        key = self.get_queue_key(user_id)
        return self.redis_client.lrange(key, 0, count - 1)
    
    def clear_queue(self, user_id: str):
        """清空用户队列"""
        key = self.get_queue_key(user_id)
        self.redis_client.delete(key)
