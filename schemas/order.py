from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    user_id: Optional[int] = None
    total_amount: float
    status: Optional[str] = 'pending'

class OrderCreate(BaseModel):
    user_id: Optional[int] = None
    total_amount: float
    status: Optional[str] = 'pending'
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    order_date: datetime
    items: List[OrderItem] = []
    class Config:
        from_attributes = True
