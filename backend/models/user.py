from models import db
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    preferences = db.Column(JSON, default=dict)  # 用户偏好设置
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat()
        }
