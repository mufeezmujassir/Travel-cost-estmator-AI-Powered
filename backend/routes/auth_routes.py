from fastapi import APIRouter, Depends, HTTPException, status
from schemas.user_schema import UserCreate, UserLogin, UserUpdate, UserResponse, Token
from services.auth_service import AuthService, get_current_user
from utils.security import create_access_token
from datetime import timedelta
import os

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    return await AuthService.register_user(user)

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user = await AuthService.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    return await AuthService.update_user(current_user.id, update_data)

@router.delete("/profile")
async def delete_profile(current_user: UserResponse = Depends(get_current_user)):
    return await AuthService.delete_user(current_user.id)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str):
    user = await AuthService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user