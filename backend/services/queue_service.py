import os
from typing import List, Optional
from collections import defaultdict

class QueueService:
    """
    队列服务 - 支持 Redis 和内存队列两种模式
    在没有 Redis 的情况下自动使用内存队列（适用于开发/MVP）
    """
    
    def __init__(self):
        self.redis_client = None
        self.use_memory = True
        self._memory_queues: dict[str, list] = defaultdict(list)
        
        # 尝试连接 Redis
        try:
            import redis
            client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD', None),
                decode_responses=True
            )
            # 测试连接
            client.ping()
            self.redis_client = client
            self.use_memory = False
            print("[QueueService] Using Redis backend")
        except Exception as e:
            print(f"[QueueService] Redis not available ({e}), using in-memory queue")
    
    def get_queue_key(self, user_id: str) -> str:
        return f"queue:user:{user_id}"
    
    def get_queue_length(self, user_id: str) -> int:
        """获取队列长度"""
        if self.use_memory:
            return len(self._memory_queues[user_id])
        key = self.get_queue_key(user_id)
        return self.redis_client.llen(key)
    
    def push_cards(self, user_id: str, card_ids: List[str]):
        """批量推送卡片 ID 到用户队列"""
        if not card_ids:
            return
        if self.use_memory:
            self._memory_queues[user_id].extend(card_ids)
        else:
            key = self.get_queue_key(user_id)
            self.redis_client.rpush(key, *card_ids)
    
    def pop_card(self, user_id: str) -> Optional[str]:
        """从队列头部取出一张卡片"""
        if self.use_memory:
            queue = self._memory_queues[user_id]
            return queue.pop(0) if queue else None
        key = self.get_queue_key(user_id)
        return self.redis_client.lpop(key)
    
    def peek_queue(self, user_id: str, count: int = 10) -> List[str]:
        """查看队列前 N 张卡片（不移除）"""
        if self.use_memory:
            return self._memory_queues[user_id][:count]
        key = self.get_queue_key(user_id)
        return self.redis_client.lrange(key, 0, count - 1)
    
    def clear_queue(self, user_id: str):
        """清空用户队列"""
        if self.use_memory:
            self._memory_queues[user_id] = []
        else:
            key = self.get_queue_key(user_id)
            self.redis_client.delete(key)
