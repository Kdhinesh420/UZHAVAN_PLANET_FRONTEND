"""
Order routes - Order management for buyers and sellers
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.User import User
from models.Order import Order
from models.OrderItem import OrderItem
from models.Product import Product
from models.Cart import Cart
from schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from dependencies import get_db
from auth import get_current_user, get_current_buyer, get_current_seller

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Create a new order from cart items (Buyer only)
    Protected route - requires buyer authentication
    """
    # Get cart items
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Validate stock and calculate total
    total_amount = 0.0
    order_items_data = []
    
    for cart_item in cart_items:
        product = db.query(Product).filter(Product.id == cart_item.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {cart_item.product_id} not found"
            )
        
        if product.stock_quantity < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}. Only {product.stock_quantity} available"
            )
        
        item_total = float(product.price) * cart_item.quantity
        total_amount += item_total
        
        order_items_data.append({
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
            "price": float(product.price)
        })
    
    # Create order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending"
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Create order items and reduce stock
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            price=item_data["price"]
        )
        db.add(order_item)
        
        # Reduce product stock
        product = db.query(Product).filter(Product.id == item_data["product_id"]).first()
        product.stock_quantity -= item_data["quantity"]
    
    # Clear cart
    db.query(Cart).filter(Cart.user_id == current_user.id).delete()
    
    db.commit()
    db.refresh(new_order)
    
    return {
        "id": new_order.id,
        "user_id": new_order.user_id,
        "total_amount": float(new_order.total_amount),
        "status": new_order.status,
        "order_date": new_order.order_date,
        "items": []
    }


@router.get("/my-orders", response_model=List[dict])
def get_my_orders(
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Get buyer's order history
    Protected route - requires buyer authentication
    """
    query = text("""
        SELECT 
            o.id as order_id,
            o.order_date,
            o.total_amount,
            o.status,
            oi.product_id,
            oi.quantity,
            oi.price as item_price,
            p.name as product_name,
            p.image_url
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        WHERE o.user_id = :user_id
        ORDER BY o.order_date DESC
    """)
    
    results = db.execute(query, {"user_id": current_user.id}).fetchall()
    
    # Group items by order
    orders_map = {}
    for row in results:
        if row.order_id not in orders_map:
            orders_map[row.order_id] = {
                "order_id": row.order_id,
                "order_date": row.order_date,
                "total_amount": float(row.total_amount),
                "status": row.status,
                "items": []
            }
        orders_map[row.order_id]["items"].append({
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity": row.quantity,
            "price": float(row.item_price),
            "image_url": row.image_url
        })
    
    return list(orders_map.values())


@router.get("/seller/orders", response_model=List[dict])
def get_seller_orders(
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Get all orders containing seller's products
    Protected route - requires seller authentication
    """
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
    
    # Group items by order
    orders_map = {}
    for row in results:
        if row.order_id not in orders_map:
            orders_map[row.order_id] = {
                "order_id": row.order_id,
                "order_date": row.order_date,
                "total_amount": float(row.total_amount),
                "status": row.status,
                "customer_name": row.username,
                "customer_phone": row.phone,
                "customer_address": row.address,
                "items": []
            }
        orders_map[row.order_id]["items"].append({
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity": row.quantity,
            "price": float(row.item_price),
            "image_url": row.image_url
        })
    
    return list(orders_map.values())


@router.get("/{order_id}", response_model=dict)
def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order details by ID
    Protected route - user can only view their own orders or orders with their products
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check authorization
    if current_user.role == "buyer" and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )
    
    # Get order items
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    items = []
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        # If seller, only show items for their products
        if current_user.role == "seller" and product.seller_id != current_user.id:
            continue
        
        items.append({
            "product_id": item.product_id,
            "product_name": product.name if product else "Unknown",
            "quantity": item.quantity,
            "price": float(item.price),
            "image_url": product.image_url if product else None
        })
    
    if current_user.role == "seller" and not items:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This order does not contain your products"
        )
    
    return {
        "order_id": order.id,
        "order_date": order.order_date,
        "total_amount": float(order.total_amount),
        "status": order.status,
        "items": items
    }


@router.put("/{order_id}/status", response_model=dict)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_seller),
    db: Session = Depends(get_db)
):
    """
    Update order status (Seller only)
    Protected route - requires seller authentication
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify seller has products in this order
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    has_seller_products = False
    
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product and product.seller_id == current_user.id:
            has_seller_products = True
            break
    
    if not has_seller_products:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update orders containing your products"
        )
    
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    
    return {
        "order_id": order.id,
        "status": order.status,
        "message": f"Order status updated to {status_update.status}"
    }


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_buyer),
    db: Session = Depends(get_db)
):
    """
    Cancel an order (Buyer only, only if status is 'pending')
    Protected route - requires buyer authentication
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending orders"
        )
    
    # Restore stock
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity
    
    # Update status to cancelled
    order.status = "cancelled"
    db.commit()
    
    return None
