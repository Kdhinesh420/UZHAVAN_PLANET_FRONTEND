from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import SessionLocal, engine,Base
from schemas.User import UserCreate,UserUpdate
from models.User import User

from routers.user_routes import userrouter
from routers.product_routes import productrouter
from routers.cart_routes import cartrouter
from routers.category_routes import router as category_router
from routers.order_routes import router as order_router
from routers.review_routes import router as review_router
from routers.oderitem import router as orderitem_router
from routers.report_routes import router as report_router
from routers.upload_routes import router as upload_router

app = FastAPI(title="UZHAVAN PLANET API", version="1.0.0")

# CORS middleware - allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def greet():
    return {"message":"hello world"}

app.include_router(userrouter)
app.include_router(productrouter)
app.include_router(cartrouter)
app.include_router(category_router)
app.include_router(order_router)
app.include_router(review_router)
app.include_router(orderitem_router)
app.include_router(report_router)
app.include_router(upload_router)

