from pydantic import BaseModel, EmailStr, Field
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
    subscription_tier: Optional[str] = Field(default="free", description="User's subscription tier")
    subscription_status: Optional[str] = Field(default="active", description="User's subscription status")
    subscription_expiry: Optional[datetime] = Field(None, description="When subscription expires")
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        return self.subscription_tier and self.subscription_tier != "free"
    
    @property
    def can_generate_trip(self) -> bool:
        """Check if user can generate trips (basic check, detailed check in service)"""
        return self.subscription_status == "active"
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None