from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.User import User
from schemas.User import UserCreate, UserUpdate
from schemas.product import ProductCreate
from models.Product import Product
from models.Category import Category
from dependencies import get_db

productrouter = APIRouter(prefix="/products", tags=["Products"])


@productrouter.post("/addproduct")
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    if product.category_id:
        category = db.query(Category).filter(Category.category_id == product.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
            
    new_product = Product(
        name=product.name,
        description=product.description,
        price = product.price,
        category_id=product.category_id
       )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@productrouter.get("/allproducts")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products    

@productrouter.put("/{prod_id}")
def update_product(prod_id: int, product_update: ProductCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == prod_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product.name = product_update.name
    product.description = product_update.description
    product.price = product_update.price
    db.commit()
    db.refresh(product)
    return {"message": "Update Done", "product": product}



# use query parameter to delete user
@productrouter.delete("/")
def delete_product(prod_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == prod_id).first()
    if product:
        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    return {"message": "Product not found"}

@productrouter.get("/get/{prod_id}")
def get_product(prod_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == prod_id).first()
    if product:
        return product
    return {"message": "Product not found"}
