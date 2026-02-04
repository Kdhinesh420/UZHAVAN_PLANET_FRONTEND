"""
User routes - Authentication, signup, login, profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models.User import User
from schemas.User import UserCreate, UserUpdate, UserResponse, LoginResponse
from dependencies import get_db
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user
)

userrouter = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"]
)


@userrouter.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account (buyer or seller)
    Returns user info and JWT token
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create new user
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,  # Store hashed password
        phone=user.phone,
        address=user.address,
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token
    access_token = create_access_token(data={"user_id": new_user.id, "role": new_user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "phone": new_user.phone,
            "address": new_user.address,
            "role": new_user.role
        }
    }


@userrouter.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login with username and password
    Returns JWT token
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT token
    access_token = create_access_token(data={"user_id": user.id, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "role": user.role
        }
    }


@userrouter.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current logged-in user's profile
    Protected route - requires authentication
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "address": current_user.address,
        "role": current_user.role,
        "created_at": current_user.created_at
    }


@userrouter.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    Protected route - requires authentication
    """
    # Check if new username is taken by another user
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(User).filter(User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Check if new email is taken by another user
    if user_update.email and user_update.email != current_user.email:
        existing_email = db.query(User).filter(User.email == user_update.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
    
    # Update user fields
    if user_update.username:
        current_user.username = user_update.username
    if user_update.email:
        current_user.email = user_update.email
    if user_update.phone:
        current_user.phone = user_update.phone
    if user_update.address:
        current_user.address = user_update.address
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "address": current_user.address,
        "role": current_user.role,
        "created_at": current_user.created_at
    }


@userrouter.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user's account
    Protected route - requires authentication
    """
    db.delete(current_user)
    db.commit()
    return None


@userrouter.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Get user by ID (public info only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "role": user.role,
        "created_at": user.created_at
    }