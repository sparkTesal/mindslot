from models import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class Interaction(db.Model):
    __tablename__ = 'interactions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    card_id = db.Column(UUID(as_uuid=True), db.ForeignKey('cards.id'), nullable=False)
    action = db.Column(db.Enum('LIKE', 'SKIP', 'FINISH_READ', 'EXPAND', name='interaction_action'))
    duration = db.Column(db.Integer)  # 停留毫秒数
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    card = db.relationship('Card', backref='interactions')
