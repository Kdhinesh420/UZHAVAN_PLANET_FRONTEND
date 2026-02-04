from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    order_id = Column(String(50), nullable=True) # Can be #ORD-123 or just 123
    issue_type = Column(String(50), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default='open') # open, resolved, closed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='reports')
