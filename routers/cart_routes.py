"""
Cart routes - Shopping cart management
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.User import User
from models.Product import Product
from models.Cart import Cart
from schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse
from dependencies import get_db
from auth import get_current_user, get_current_buyer

cartrouter = APIRouter(prefix="/cart", tags=["Shopping Cart"])


@cartrouter.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    cart_item: CartItemCreate,
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Add a product to cart (Buyer only)
    Protected route - requires buyer authentication
    """
    # Check if product exists and has stock
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.stock_quantity < cart_item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.stock_quantity} items available in stock"
        )
    
    # Check if item already in cart
    existing_cart_item = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == cart_item.product_id
    ).first()
    
    if existing_cart_item:
        # Update quantity if already in cart
        new_quantity = existing_cart_item.quantity + cart_item.quantity
        if product.stock_quantity < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.stock_quantity} items available in stock"
            )
        existing_cart_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_cart_item)
        
        return {
            "cart_id": existing_cart_item.cart_id,
            "user_id": existing_cart_item.user_id,
            "product_id": existing_cart_item.product_id,
            "quantity": existing_cart_item.quantity,
            "product_name": product.name,
            "product_price": float(product.price),
            "product_image": product.image_url,
            "subtotal": float(product.price) * existing_cart_item.quantity
        }
    
    # Create new cart item
    new_cart_item = Cart(
        user_id=current_user.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )
    
    db.add(new_cart_item)
    db.commit()
    db.refresh(new_cart_item)
    
    return {
        "cart_id": new_cart_item.cart_id,
        "user_id": new_cart_item.user_id,
        "product_id": new_cart_item.product_id,
        "quantity": new_cart_item.quantity,
        "product_name": product.name,
        "product_price": float(product.price),
        "product_image": product.image_url,
        "subtotal": float(product.price) * new_cart_item.quantity
    }


@cartrouter.get("/", response_model=dict)
def get_cart(
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Get current user's cart with all items
    Protected route - requires buyer authentication
    """
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    
    if not cart_items:
        return {
            "items": [],
            "total_items": 0,
            "total_amount": 0.0
        }
    
    items = []
    total_amount = 0.0
    
    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        if product:
            subtotal = float(product.price) * cart_item.quantity
            total_amount += subtotal
            
            items.append({
                "cart_id": cart_item.cart_id,
                "user_id": cart_item.user_id,
                "product_id": cart_item.product_id,
                "quantity": cart_item.quantity,
                "product_name": product.name,
                "product_price": float(product.price),
                "product_image": product.image_url,
                "product_stock": product.stock_quantity,
                "subtotal": subtotal
            })
    
    return {
        "items": items,
        "total_items": len(items),
        "total_amount": total_amount
    }


@cartrouter.put("/{cart_id}", response_model=CartItemResponse)
def update_cart_item(
    cart_id: int,
    cart_update: CartItemUpdate,
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Update cart item quantity
    Protected route - requires buyer authentication
    """
    cart_item = db.query(Cart).filter(
        Cart.cart_id == cart_id,
        Cart.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    # Check stock availability
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if product.stock_quantity < cart_update.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.stock_quantity} items available in stock"
        )
    
    cart_item.quantity = cart_update.quantity
    db.commit()
    db.refresh(cart_item)
    
    return {
        "cart_id": cart_item.cart_id,
        "user_id": cart_item.user_id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
        "product_name": product.name,
        "product_price": float(product.price),
        "product_image": product.image_url,
        "subtotal": float(product.price) * cart_item.quantity
    }


@cartrouter.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    cart_id: int,
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Remove item from cart
    Protected route - requires buyer authentication
    """
    cart_item = db.query(Cart).filter(
        Cart.cart_id == cart_id,
        Cart.user_id == current_user.id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    
    db.delete(cart_item)
    db.commit()
    
    return None


@cartrouter.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Clear all items from cart
    Protected route - requires buyer authentication
    """
    db.query(Cart).filter(Cart.user_id == current_user.id).delete()
    db.commit()
    
    return None
