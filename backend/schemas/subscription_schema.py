from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from models.subscription_models import SubscriptionTier, SubscriptionStatus, TripPass, UsageStats

class SubscriptionResponse(BaseModel):
    """Response model for subscription details"""
    tier: SubscriptionTier
    status: SubscriptionStatus
    created_at: datetime
    expires_at: Optional[datetime] = None
    active_trip_passes: List[TripPass] = []
    usage_stats: UsageStats
    allowed_vibes: List[str] = Field(default_factory=list, description="List of allowed vibe IDs for this tier")
    is_premium: bool = Field(..., description="Whether user has any premium tier")
    can_generate_trip: bool = Field(..., description="Whether user can generate a trip now")
    stripe_customer_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class CreateTripPassRequest(BaseModel):
    """Request to purchase a trip pass"""
    destination: str = Field(..., description="Destination city for the trip pass", min_length=2)
    success_url: str = Field(..., description="URL to redirect after successful payment")
    cancel_url: str = Field(..., description="URL to redirect if payment is cancelled")

class UpgradeSubscriptionRequest(BaseModel):
    """Request to upgrade subscription tier"""
    target_tier: SubscriptionTier = Field(..., description="Target subscription tier")
    success_url: str = Field(..., description="URL to redirect after successful payment")
    cancel_url: str = Field(..., description="URL to redirect if payment is cancelled")

class CheckTripLimitRequest(BaseModel):
    """Request to check if user can generate trip for destination"""
    destination: str = Field(..., description="Destination city to check")

class CheckTripLimitResponse(BaseModel):
    """Response for trip limit check"""
    can_generate: bool = Field(..., description="Whether user can generate trip")
    reason: Optional[str] = Field(None, description="Reason if cannot generate")
    requires_upgrade: bool = Field(default=False, description="Whether upgrade is needed")
    suggested_tier: Optional[SubscriptionTier] = Field(None, description="Suggested tier to upgrade to")
    has_trip_pass_for_region: bool = Field(default=False, description="Whether user has trip pass for this region")

class TierLimits(BaseModel):
    """Limits for a subscription tier"""
    tier: SubscriptionTier
    trips_per_year: Optional[int] = Field(None, description="Number of trips per year (None = unlimited)")
    allowed_vibes: List[str] = Field(..., description="List of allowed vibe IDs")
    max_flight_options: int = Field(..., description="Maximum flight options to show")
    max_hotel_options: int = Field(..., description="Maximum hotel options to show")
    max_itinerary_days: int = Field(..., description="Maximum days in itinerary")
    has_price_calendar: bool = Field(default=False, description="Access to price calendar")
    has_season_optimization: bool = Field(default=False, description="Access to season optimization")
    has_emotional_intelligence: bool = Field(default=False, description="Access to emotional intelligence analysis")
    has_detailed_breakdown: bool = Field(default=False, description="Access to detailed cost breakdown")
    max_saved_versions: Optional[int] = Field(None, description="Max saved trip versions (None = unlimited)")
    has_pdf_export: bool = Field(default=False, description="Can export to PDF")
    has_trip_comparison: bool = Field(default=False, description="Can compare trips")
    has_multi_city: bool = Field(default=False, description="Multi-city planning")
    has_api_access: bool = Field(default=False, description="API access")

class UsageLimitsResponse(BaseModel):
    """Response with current usage and limits"""
    current_tier: SubscriptionTier
    limits: TierLimits
    usage: UsageStats
    trips_remaining: Optional[int] = Field(None, description="Trips remaining this year (None = unlimited)")
    active_trip_passes: List[Dict[str, Any]] = Field(default_factory=list, description="Active trip passes")
    days_until_reset: Optional[int] = Field(None, description="Days until yearly reset")
    subscription_expires_in_days: Optional[int] = Field(None, description="Days until subscription expires")

class TierInfo(BaseModel):
    """Information about a subscription tier"""
    tier: SubscriptionTier
    name: str
    price: float
    billing_period: str  # "one-time", "annual"
    description: str
    features: List[str]
    limits: TierLimits
    is_recommended: bool = Field(default=False)
    
class TiersResponse(BaseModel):
    """Response with all available tiers"""
    tiers: List[TierInfo]
    current_tier: Optional[SubscriptionTier] = None

