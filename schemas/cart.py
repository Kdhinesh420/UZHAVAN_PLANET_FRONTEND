from pydantic import BaseModel
from typing import Optional


class CartItemCreate(BaseModel):
    """Schema for adding item to cart"""
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    """Schema for updating cart item"""
    quantity: int


class CartItemResponse(BaseModel):
    """Schema for cart item response"""
    cart_id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: str
    product_price: float
    product_image: Optional[str]
    subtotal: float
    
    class Config:
        from_attributes = True
