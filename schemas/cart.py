from pydantic import BaseModel
from typing import Optional

class CartBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CartCreate(CartBase):
    pass

class CartUpdate(BaseModel):
    quantity: int

class Cart(CartBase):
    cart_id: int
    
    class Config:
        from_attributes = True
