
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.session import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.category_id', ondelete='SET NULL'))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    image_url = Column(Text)
    image_url_2 = Column(Text, nullable=True)
    image_url_3 = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    seller = relationship("User", back_populates="products")
    carts = relationship("Cart", back_populates="product")
    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
