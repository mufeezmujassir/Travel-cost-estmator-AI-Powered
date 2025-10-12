from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime
    type: str = "basic"  # "basic" or "premium"
    hasUsedFreePlan: bool = False
    subscriptionStatus: str = "expired"  # "active", "expired", "cancelled"
    subscriptionEndDate: Optional[datetime] = None
    stripeCustomerId: Optional[str] = None
    subscriptionId: Optional[str] = None
    generationsRemaining: int = 1  # For basic users
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class SubscriptionResponse(BaseModel):
    sessionId: str
    url: str

class SubscriptionStatus(BaseModel):
    type: str
    status: str
    hasUsedFreePlan: bool
    generationsRemaining: int
    subscriptionEndDate: Optional[datetime] = None