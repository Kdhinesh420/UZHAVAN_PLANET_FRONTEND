
import sys
import os
from sqlalchemy.orm import Session
from db.session import SessionLocal, engine
from models.Order import Order
from models.OrderItem import OrderItem
from schemas.order import Order as OrderSchema
from pydantic import TypeAdapter

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def reproduce():
    db = SessionLocal()
    try:
        orders = db.query(Order).all()
        print(f"Found {len(orders)} orders in DB.")
        
        # Simulate Pydantic validation
        adapter = TypeAdapter(list[OrderSchema])
        
        try:
            validated_orders = adapter.validate_python(orders)
            print("Validation SUCCESS")
            for o in validated_orders:
                print(f"Order {o.id} loaded successfully with {len(o.items)} items.")
        except Exception as e:
            print(f"Validation FAILED: {e}")
            # Try validating one by one to find the culprit
            for i, o in enumerate(orders):
                try:
                    OrderSchema.model_validate(o)
                except Exception as inner_e:
                    print(f"Order {o.id} failed validation: {inner_e}")
                    
    except Exception as e:
        print(f"DB Query Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
