from models.subscription_models import SubscriptionTier
from schemas.subscription_schema import TierLimits, TierInfo
from typing import Dict, List

# Tier Limits Configuration
TIER_LIMITS: Dict[SubscriptionTier, TierLimits] = {
    SubscriptionTier.FREE: TierLimits(
        tier=SubscriptionTier.FREE,
        trips_per_year=1,
        allowed_vibes=["cultural", "beach", "nature"],  # Only 3 vibes
        max_flight_options=2,
        max_hotel_options=2,
        max_itinerary_days=3,
        has_price_calendar=False,
        has_season_optimization=False,
        has_emotional_intelligence=False,
        has_detailed_breakdown=False,
        max_saved_versions=0,  # Cannot save
        has_pdf_export=False,
        has_trip_comparison=False,
        has_multi_city=False,
        has_api_access=False
    ),
    SubscriptionTier.TRIP_PASS: TierLimits(
        tier=SubscriptionTier.TRIP_PASS,
        trips_per_year=None,  # Unlimited for one region (90 days)
        allowed_vibes=["romantic", "adventure", "beach", "nature", "cultural", "culinary", "wellness"],  # All 7
        max_flight_options=5,
        max_hotel_options=5,
        max_itinerary_days=30,
        has_price_calendar=True,
        has_season_optimization=True,
        has_emotional_intelligence=True,
        has_detailed_breakdown=True,
        max_saved_versions=3,
        has_pdf_export=True,
        has_trip_comparison=False,
        has_multi_city=False,
        has_api_access=False
    ),
    SubscriptionTier.EXPLORER_ANNUAL: TierLimits(
        tier=SubscriptionTier.EXPLORER_ANNUAL,
        trips_per_year=3,
        allowed_vibes=["romantic", "adventure", "beach", "nature", "cultural", "culinary", "wellness"],  # All 7
        max_flight_options=5,
        max_hotel_options=5,
        max_itinerary_days=30,
        has_price_calendar=True,
        has_season_optimization=True,
        has_emotional_intelligence=True,
        has_detailed_breakdown=True,
        max_saved_versions=None,  # Unlimited
        has_pdf_export=True,
        has_trip_comparison=True,
        has_multi_city=False,
        has_api_access=False
    ),
    SubscriptionTier.TRAVEL_PRO: TierLimits(
        tier=SubscriptionTier.TRAVEL_PRO,
        trips_per_year=None,  # Unlimited
        allowed_vibes=["romantic", "adventure", "beach", "nature", "cultural", "culinary", "wellness"],  # All 7
        max_flight_options=10,
        max_hotel_options=10,
        max_itinerary_days=60,
        has_price_calendar=True,
        has_season_optimization=True,
        has_emotional_intelligence=True,
        has_detailed_breakdown=True,
        max_saved_versions=None,  # Unlimited
        has_pdf_export=True,
        has_trip_comparison=True,
        has_multi_city=True,
        has_api_access=True
    )
}

# Tier Pricing and Information
TIER_INFO: Dict[SubscriptionTier, TierInfo] = {
    SubscriptionTier.FREE: TierInfo(
        tier=SubscriptionTier.FREE,
        name="Free Explorer",
        price=0.0,
        billing_period="forever",
        description="Try out our AI travel planner with basic features",
        features=[
            "1 complete trip estimate per year",
            "Access to 3 travel vibes",
            "View up to 2 flight options",
            "View up to 2 hotel options",
            "Basic 3-day itinerary",
            "Basic cost breakdown",
            "Email support"
        ],
        limits=TIER_LIMITS[SubscriptionTier.FREE],
        is_recommended=False
    ),
    SubscriptionTier.TRIP_PASS: TierInfo(
        tier=SubscriptionTier.TRIP_PASS,
        name="Trip Pass",
        price=15.0,
        billing_period="one-time",
        description="Perfect for planning your annual trip - valid for 90 days",
        features=[
            "Unlimited estimates for ONE destination",
            "Valid for 90 days",
            "All 7 travel vibes available",
            "Up to 5 flight options",
            "Up to 5 hotel options",
            "Full 30-day itinerary",
            "Price trend calendar",
            "Season optimization",
            "Emotional intelligence analysis",
            "Detailed cost breakdown",
            "Save & compare 3 versions",
            "PDF export",
            "Priority email support"
        ],
        limits=TIER_LIMITS[SubscriptionTier.TRIP_PASS],
        is_recommended=True  # Most popular option
    ),
    SubscriptionTier.EXPLORER_ANNUAL: TierInfo(
        tier=SubscriptionTier.EXPLORER_ANNUAL,
        name="Explorer Annual",
        price=59.0,
        billing_period="annual",
        description="For travelers who take multiple trips per year",
        features=[
            "3 complete trip estimates per year",
            "All 7 travel vibes available",
            "Up to 5 flight options",
            "Up to 5 hotel options",
            "Full 30-day itinerary",
            "Price trend calendar",
            "Season optimization",
            "Emotional intelligence analysis",
            "Detailed cost breakdown",
            "Unlimited saved versions",
            "Trip comparison tool",
            "PDF export",
            "Priority email support",
            "Early access to new features"
        ],
        limits=TIER_LIMITS[SubscriptionTier.EXPLORER_ANNUAL],
        is_recommended=False
    ),
    SubscriptionTier.TRAVEL_PRO: TierInfo(
        tier=SubscriptionTier.TRAVEL_PRO,
        name="Travel Pro",
        price=149.0,
        billing_period="annual",
        description="For frequent travelers, bloggers, and travel professionals",
        features=[
            "UNLIMITED trip estimates",
            "All 7 travel vibes available",
            "Up to 10 flight options",
            "Up to 10 hotel options",
            "Extended 60-day itinerary",
            "Price trend calendar + historical data",
            "Season optimization",
            "Emotional intelligence analysis",
            "Detailed cost breakdown",
            "Unlimited saved versions",
            "Trip comparison tool",
            "Multi-city trip planning",
            "White-label PDF export",
            "API access (100 requests/month)",
            "Group trip coordination (up to 10 travelers)",
            "24-hour priority support",
            "Early access & beta testing"
        ],
        limits=TIER_LIMITS[SubscriptionTier.TRAVEL_PRO],
        is_recommended=False
    )
}

def get_tier_limits(tier: SubscriptionTier) -> TierLimits:
    """Get limits for a specific tier"""
    return TIER_LIMITS.get(tier, TIER_LIMITS[SubscriptionTier.FREE])

def get_tier_info(tier: SubscriptionTier) -> TierInfo:
    """Get information for a specific tier"""
    return TIER_INFO.get(tier, TIER_INFO[SubscriptionTier.FREE])

def can_access_vibe(tier: SubscriptionTier, vibe: str) -> bool:
    """Check if tier can access a specific vibe"""
    limits = get_tier_limits(tier)
    return vibe in limits.allowed_vibes

def can_access_feature(tier: SubscriptionTier, feature: str) -> bool:
    """Check if tier can access a specific feature"""
    limits = get_tier_limits(tier)
    feature_map = {
        "price_calendar": limits.has_price_calendar,
        "season_optimization": limits.has_season_optimization,
        "emotional_intelligence": limits.has_emotional_intelligence,
        "detailed_breakdown": limits.has_detailed_breakdown,
        "pdf_export": limits.has_pdf_export,
        "trip_comparison": limits.has_trip_comparison,
        "multi_city": limits.has_multi_city,
        "api_access": limits.has_api_access
    }
    return feature_map.get(feature, False)

def get_all_tiers_info() -> List[TierInfo]:
    """Get information for all tiers"""
    return [
        TIER_INFO[SubscriptionTier.FREE],
        TIER_INFO[SubscriptionTier.TRIP_PASS],
        TIER_INFO[SubscriptionTier.EXPLORER_ANNUAL],
        TIER_INFO[SubscriptionTier.TRAVEL_PRO]
    ]

def is_premium_tier(tier: SubscriptionTier) -> bool:
    """Check if tier is premium (not free)"""
    return tier != SubscriptionTier.FREE

def get_upgrade_path(current_tier: SubscriptionTier) -> List[SubscriptionTier]:
    """Get available upgrade options for current tier"""
    tier_hierarchy = [
        SubscriptionTier.FREE,
        SubscriptionTier.TRIP_PASS,
        SubscriptionTier.EXPLORER_ANNUAL,
        SubscriptionTier.TRAVEL_PRO
    ]
    
    try:
        current_index = tier_hierarchy.index(current_tier)
        return tier_hierarchy[current_index + 1:]
    except (ValueError, IndexError):
        return []

