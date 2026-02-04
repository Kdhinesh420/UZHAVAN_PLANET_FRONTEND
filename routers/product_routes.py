"""
Product routes - CRUD operations for products
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.User import User
from models.Product import Product
from models.Category import Category
from schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductWithSeller
from dependencies import get_db
from auth import get_current_user, get_current_seller

productrouter = APIRouter(prefix="/products", tags=["Products"])


@productrouter.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate, 
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Create a new product (Seller only)
    Protected route - requires seller authentication
    """
    # Verify category exists if provided
    if product.category_id:
        category = db.query(Category).filter(Category.category_id == product.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Create new product
    new_product = Product(
        seller_id=current_user.id,  # Automatically set from authenticated user
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        image_url=product.image_url,
        image_url_2=product.image_url_2,
        image_url_3=product.image_url_3
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@productrouter.get("/", response_model=List[ProductWithSeller])
def get_all_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all products with optional filters
    Public route - no authentication required
    """
    query = db.query(Product)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if in_stock:
        query = query.filter(Product.stock_quantity > 0)
    
    # Get products with pagination
    products = query.offset(skip).limit(limit).all()
    
    # Enrich with seller and category info
    result = []
    for product in products:
        seller = db.query(User).filter(User.id == product.seller_id).first()
        category = db.query(Category).filter(Category.category_id == product.category_id).first() if product.category_id else None
        
        product_dict = {
            "id": product.id,
            "seller_id": product.seller_id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "stock_quantity": product.stock_quantity,
            "category_id": product.category_id,
            "image_url": product.image_url,
            "image_url_2": product.image_url_2,
            "image_url_3": product.image_url_3,
            "created_at": product.created_at,
            "seller_username": seller.username if seller else None,
            "category_name": category.name if category else None
        }
        result.append(product_dict)
    
    return result


@productrouter.get("/my-products", response_model=List[ProductResponse])
def get_my_products(
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Get all products created by the current seller
    Protected route - requires seller authentication
    """
    products = db.query(Product).filter(Product.seller_id == current_user.id).all()
    return products


@productrouter.get("/{product_id}", response_model=ProductWithSeller)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """
    Get a single product by ID
    Public route - no authentication required
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get seller and category info
    seller = db.query(User).filter(User.id == product.seller_id).first()
    category = db.query(Category).filter(Category.category_id == product.category_id).first() if product.category_id else None
    
    return {
        "id": product.id,
        "seller_id": product.seller_id,
        "name": product.name,
        "description": product.description,
        "price": float(product.price),
        "stock_quantity": product.stock_quantity,
        "category_id": product.category_id,
        "image_url": product.image_url,
        "image_url_2": product.image_url_2,
        "image_url_3": product.image_url_3,
        "created_at": product.created_at,
        "seller_username": seller.username if seller else None,
        "category_name": category.name if category else None
    }


@productrouter.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Update a product (Seller can only update their own products)
    Protected route - requires seller authentication
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if the current user owns this product
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products"
        )
    
    # Verify category exists if being updated
    if product_update.category_id:
        category = db.query(Category).filter(Category.category_id == product_update.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Update product fields
    if product_update.name is not None:
        product.name = product_update.name
    if product_update.description is not None:
        product.description = product_update.description
    if product_update.price is not None:
        product.price = product_update.price
    if product_update.stock_quantity is not None:
        product.stock_quantity = product_update.stock_quantity
    if product_update.category_id is not None:
        product.category_id = product_update.category_id
    if product_update.image_url is not None:
        product.image_url = product_update.image_url
    if product_update.image_url_2 is not None:
        product.image_url_2 = product_update.image_url_2
    if product_update.image_url_3 is not None:
        product.image_url_3 = product_update.image_url_3
    
    db.commit()
    db.refresh(product)
    
    return product


@productrouter.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Delete a product (Seller can only delete their own products)
    Protected route - requires seller authentication
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if the current user owns this product
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own products"
        )
    
    db.delete(product)
    db.commit()
    
    return None
