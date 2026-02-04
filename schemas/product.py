from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    """Schema for creating a new product"""
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int = 0
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    image_url_2: Optional[str] = None
    image_url_3: Optional[str] = None


class ProductResponse(BaseModel):
    """Schema for product response"""
    id: int
    seller_id: int
    name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    category_id: Optional[int]
    image_url: Optional[str]
    image_url_2: Optional[str]
    image_url_3: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductWithSeller(ProductResponse):
    """Schema for product with seller information"""
    seller_username: Optional[str] = None
    category_name: Optional[str] = None