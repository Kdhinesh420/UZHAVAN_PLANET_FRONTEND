
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, nullable=False)  #  MUST
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    role = Column(String(50), default='customer')
    created_at = Column(DateTime, default=datetime.utcnow)

    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    products = relationship("Product", back_populates="seller")
    reports = relationship("Report", back_populates="user")
