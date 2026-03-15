from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.OrderItem import OrderItem
from schemas.order import OrderItemCreate, OrderItemUpdate, OrderItem as OrderItemSchema

from dependencies import get_db
from sqlalchemy import text


router = APIRouter(prefix="/order_items", tags=["order_items"])

@router.post("/", response_model=OrderItemSchema)
def create_order_item(order_item: OrderItemCreate, db: Session = Depends(get_db)):
    db_order_item = OrderItem(**order_item.dict())
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

@router.get("/")
def get_order_items(db: Session = Depends(get_db)):
    query = text("""
        SELECT oi.*, p.name as product_name 
        FROM order_items oi 
        JOIN products p ON oi.product_id = p.id
    """)
    result = db.execute(query)
    return [dict(row._mapping) for row in result]

@router.get("/{order_item_id}", response_model=OrderItemSchema)
def get_order_item(order_item_id: int, db: Session = Depends(get_db)):
    db_order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if not db_order_item:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    return db_order_item

@router.put("/{order_item_id}", response_model=OrderItemSchema)
def update_order_item(order_item_id: int, order_item: OrderItemUpdate, db: Session = Depends(get_db)):
    db_order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if not db_order_item:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    
    update_data = order_item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order_item, key, value)
    
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

@router.delete("/{order_item_id}")
def delete_order_item(order_item_id: int, db: Session = Depends(get_db)):
    db_order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if not db_order_item:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    
    db.delete(db_order_item)
    db.commit()
    return {"message": "OrderItem deleted successfully"}
