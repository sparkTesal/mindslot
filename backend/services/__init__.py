# Services package
# Note: content_factory is imported lazily to avoid circular imports with agents

from services.queue_service import QueueService
from services.card_service import CardService
from services.llm_service import LLMService
from services.recommendation_service import RecommendationService, recommendation_service

__all__ = [
    'QueueService',
    'CardService', 
    'LLMService',
    'RecommendationService',
    'recommendation_service',
]

# Lazy import for content_factory
def get_content_factory():
    from services.content_factory import content_factory
    return content_factory