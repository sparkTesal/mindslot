from models import db
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
from datetime import datetime

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = db.Column(db.String(255), nullable=False, index=True)
    tags = db.Column(JSON, nullable=False)  # ["Java", "JVM"]
    complexity = db.Column(db.Integer, nullable=False)  # 1-5
    payload = db.Column(JSON, nullable=False)  # 完整的卡片内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'topic': self.topic,
            'tags': self.tags,
            'complexity': self.complexity,
            'payload': self.payload,
            'created_at': self.created_at.isoformat()
        }
