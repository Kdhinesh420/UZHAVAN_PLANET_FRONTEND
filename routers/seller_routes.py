"""
Seller routes - Dashboard analytics and seller-specific operations
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from dependencies import get_db
from models.User import User
from models.Product import Product
from models.Order import Order
from models.OrderItem import OrderItem
from auth import get_current_seller
from schemas.product import ProductResponse

router = APIRouter(prefix="/seller", tags=["Seller Dashboard"])

@router.get("/dashboard")
def get_seller_dashboard_stats(
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Get seller dashboard statistics
    """
    # 1. Total Products
    total_products = db.query(Product).filter(Product.seller_id == current_user.id).count()
    
    # 2. Total Orders & Revenue
    # We need to join OrderItems with Products to filter by seller
    query = db.query(
        func.count(func.distinct(OrderItem.order_id)).label("total_orders"),
        func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue")
    ).join(Product, OrderItem.product_id == Product.id)\
     .filter(Product.seller_id == current_user.id)
    
    result = query.first()
    total_orders = result.total_orders if result.total_orders else 0
    total_revenue = float(result.total_revenue) if result.total_revenue else 0.0
    
    # 3. Pending Orders
    pending_query = db.query(func.count(func.distinct(OrderItem.order_id)))\
        .join(Product, OrderItem.product_id == Product.id)\
        .join(Order, OrderItem.order_id == Order.id)\
        .filter(Product.seller_id == current_user.id)\
        .filter(Order.status == "pending")
        
    pending_orders = pending_query.scalar() or 0
    
    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders
    }

@router.get("/products", response_model=List[ProductResponse])
def get_seller_products(
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Get all products created by the current seller
    """
    products = db.query(Product).filter(Product.seller_id == current_user.id).all()
    return products

@router.get("/orders")
def get_seller_orders(
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Get all orders containing seller's products
    """
    # Using raw SQL for complex join and improved performance/clarity like in order_routes
    query = text("""
        SELECT 
            o.id as order_id,
            o.order_date,
            o.total_amount,
            o.status,
            u.username,
            u.phone,
            u.address,
            oi.product_id,
            oi.quantity,
            oi.price as item_price,
            p.name as product_name,
            p.image_url
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE p.seller_id = :seller_id
        ORDER BY o.order_date DESC
    """)
    
    results = db.execute(query, {"seller_id": current_user.id}).fetchall()
    
    # Group items by order to avoid duplicates in list
    orders_map = {}
    for row in results:
        if row.order_id not in orders_map:
            orders_map[row.order_id] = {
                "id": row.order_id,
                "created_at": row.order_date,
                "total": float(row.total_amount),
                "status": row.status,
                "customer_name": row.username,
                "customer_phone": row.phone,
                "customer_address": row.address,
                # For dashboard list, we might want to show first product name or summary
                "product_name": row.product_name, # Shows one product name. If multiple, it shows last one processed for this order? 
                # Better: List items or "Product A + 2 more"
                # For simple MVP, showing one product is fine or list of items.
                "items": []
            }
        
        # We append items but also keep `product_name` at top level for table display
        orders_map[row.order_id]["items"].append({
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity": row.quantity,
            "price": float(row.item_price),
            "image_url": row.image_url
        })
        
        # Update top level product name to include count if multiple
        if len(orders_map[row.order_id]["items"]) > 1:
             first_prod = orders_map[row.order_id]["items"][0]["product_name"]
             count = len(orders_map[row.order_id]["items"]) - 1
             orders_map[row.order_id]["product_name"] = f"{first_prod} + {count} more"

    return list(orders_map.values())

@router.put("/products/{product_id}/stock")
def update_product_stock(
    product_id: int,
    stock: int,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Update product stock quantity
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
        
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products"
        )
        
    product.stock_quantity = stock
    db.commit()
    
    return {"message": "Stock updated successfully", "new_stock": stock}
