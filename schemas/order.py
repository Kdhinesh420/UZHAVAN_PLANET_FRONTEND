from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItemBase(BaseModel):
    """Base schema for order items"""
    product_id: int
    quantity: int
    price: float


class OrderItemCreate(OrderItemBase):
    """Schema for creating order items"""
    pass


class OrderItem(OrderItemBase):
    """Schema for order item response"""
    id: int
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base schema for orders"""
    user_id: Optional[int] = None
    total_amount: float
    status: Optional[str] = 'pending'


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    # Order is created from cart, so no fields needed
    pass


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: int
    user_id: int
    total_amount: float
    status: str
    order_date: datetime
    items: List[dict] = []
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: str  # pending, processing, shipped, delivered, cancelled
