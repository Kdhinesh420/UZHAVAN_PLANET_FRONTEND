from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime

class Feedback(Base):
    __tablename__ = 'feedbacks'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    username = Column(String(100))
    email = Column(String(100))
    rating = Column(Integer) # 1-5 based on emojis
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User')
