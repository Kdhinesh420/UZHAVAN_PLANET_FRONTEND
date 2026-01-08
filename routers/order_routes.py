from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from models.Order import Order
from models.OrderItem import OrderItem
from schemas.order import OrderCreate, Order as OrderSchema
from dependencies import get_db
router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderSchema)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(user_id=order.user_id, total_amount=order.total_amount, status=order.status)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    for item in order.items:
        db_item = OrderItem(order_id=db_order.id, product_id=item.product_id, quantity=item.quantity, price=item.price)
        db.add(db_item)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/all", tags=["orders"])
def read_all_orders_admin(db: Session = Depends(get_db)):
    """
    Admin/Seller view: See ALL orders with User details and Items.
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
        ORDER BY o.order_date DESC
    """)
    results = db.execute(query).fetchall()
    
    # Grouping logic to nest items under orders
    orders_map = {}
    for row in results:
        if row.order_id not in orders_map:
            orders_map[row.order_id] = {
                "order_id": row.order_id,
                "order_date": row.order_date,
                "total_amount": row.total_amount,
                "status": row.status,
                "username": row.username,
                "phone": row.phone,
                "address": row.address,
                "items": []
            }
        orders_map[row.order_id]["items"].append({
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity": row.quantity,
            "price": row.item_price,
            "image_url": row.image_url
        })
    
    return list(orders_map.values())

@router.get("/my_orders/{user_id}", tags=["orders"])
def get_my_orders(user_id: int, db: Session = Depends(get_db)):
    """
    Buyer view: See only their own orders.
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
    results = db.execute(query, {"user_id": user_id}).fetchall()
    
    orders_map = {}
    for row in results:
        if row.order_id not in orders_map:
            orders_map[row.order_id] = {
                "order_id": row.order_id,
                "order_date": row.order_date,
                "total_amount": row.total_amount,
                "status": row.status,
                "items": []
            }
        orders_map[row.order_id]["items"].append({
            "product_id": row.product_id,
            "product_name": row.product_name,
            "quantity": row.quantity,
            "price": row.item_price,
            "image_url": row.image_url
        })
        
    return list(orders_map.values())

@router.delete("delete/{user_id}")
def delete_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    db.query(Order).filter(Order.user_id == user_id).delete()    
    db.commit()
    return {"message": "Orders deleted"}    

@router.put("update/{user_id}/{order_id}")
def update_orders_by_user(user_id: int, order_id: int, db: Session = Depends(get_db)):
    db.query(Order).filter(Order.user_id == user_id, Order.id == order_id).update({"status": "completed"})
    db.commit()   
    return {"message": "Orders updated"}    
