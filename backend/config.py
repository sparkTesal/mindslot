import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mindslot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # LLM 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    
    # 后台工厂配置
    FACTORY_INTERVAL = int(os.getenv('FACTORY_INTERVAL', 3600))  # 每小时
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 20))
    
    # 队列配置
    QUEUE_MIN_LENGTH = 5  # 触发补货的阈值
    QUEUE_REPLENISH_SIZE = 10  # 每次补货数量
