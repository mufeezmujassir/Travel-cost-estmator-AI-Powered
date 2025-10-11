from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SubscriptionTier(str, Enum):
    """Subscription tier levels"""
    FREE = "free"
    TRIP_PASS = "trip_pass"
    EXPLORER_ANNUAL = "explorer_annual"
    TRAVEL_PRO = "travel_pro"

class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

class TripPass(BaseModel):
    """Trip Pass model for one-time destination passes"""
    destination: str = Field(..., description="Original destination city")
    region: str = Field(..., description="Region/country for matching")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Expiry date (90 days from creation)")
    trips_generated: int = Field(default=0, description="Number of trips generated with this pass")
    is_active: bool = Field(default=True, description="Whether this pass is still active")
    payment_intent_id: Optional[str] = Field(None, description="Stripe payment intent ID")

class UsageStats(BaseModel):
    """User usage statistics"""
    trips_generated_this_year: int = Field(default=0, description="Trips generated in current year")
    trips_generated_lifetime: int = Field(default=0, description="Total trips generated")
    last_trip_date: Optional[datetime] = Field(None, description="Date of last trip generation")
    year_reset_date: datetime = Field(..., description="Date when yearly counter resets")
    last_region_used: Optional[str] = Field(None, description="Last region/destination used")

class Subscription(BaseModel):
    """User subscription model"""
    tier: SubscriptionTier = Field(default=SubscriptionTier.FREE, description="Current subscription tier")
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE, description="Subscription status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Expiry date for annual subscriptions")
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")
    active_trip_passes: List[TripPass] = Field(default_factory=list, description="Active trip passes")
    usage_stats: UsageStats = Field(..., description="Usage statistics")
    subscription_history: List[dict] = Field(default_factory=list, description="Audit trail of subscription changes")
    
    def add_history_entry(self, action: str, details: dict):
        """Add entry to subscription history"""
        self.subscription_history.append({
            "timestamp": datetime.utcnow(),
            "action": action,
            "details": details
        })
    
    def get_active_trip_pass_for_region(self, region: str) -> Optional[TripPass]:
        """Get active trip pass for a specific region"""
        now = datetime.utcnow()
        for trip_pass in self.active_trip_passes:
            if (trip_pass.region == region and 
                trip_pass.is_active and 
                trip_pass.expires_at > now):
                return trip_pass
        return None
    
    def has_valid_trip_pass(self, region: str) -> bool:
        """Check if user has a valid trip pass for region"""
        return self.get_active_trip_pass_for_region(region) is not None
    
    def expire_old_trip_passes(self):
        """Mark expired trip passes as inactive"""
        now = datetime.utcnow()
        for trip_pass in self.active_trip_passes:
            if trip_pass.expires_at <= now and trip_pass.is_active:
                trip_pass.is_active = False

