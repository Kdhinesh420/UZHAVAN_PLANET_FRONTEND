from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.Category import Category
from schemas.category import CategoryCreate, Category as CategorySchema
from dependencies import get_db

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategorySchema)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/", response_model=list[CategorySchema])
def read_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

