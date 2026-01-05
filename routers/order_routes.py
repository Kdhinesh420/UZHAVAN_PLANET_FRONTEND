from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from db.session import SessionLocal
from models.Order import Order
from models.OrderItem import OrderItem
from schemas.order import OrderCreate, Order as OrderSchema
from schemas.order import OrderCreate, Order as OrderSchema

router = APIRouter(prefix="/orders", tags=["orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.get("/", response_model=list[OrderSchema])
def read_orders(db: Session = Depends(get_db)):
    return db.query(Order).options(joinedload(Order.items)).all()

@router.get("get/{user_id}")
def get_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(Order).options(joinedload(Order.items)).filter(Order.user_id == user_id).all()

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
