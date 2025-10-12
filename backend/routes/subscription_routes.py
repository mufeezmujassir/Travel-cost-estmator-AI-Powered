from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from schemas.user_schema import UserResponse
from schemas.subscription_schema import (
    SubscriptionResponse, CheckTripLimitRequest, CheckTripLimitResponse,
    UsageLimitsResponse, TiersResponse, TierInfo
)
from services.subscription_service import SubscriptionService
from services.auth_service import get_current_user
from config.tier_config import get_all_tiers_info, get_tier_limits
from models.subscription_models import SubscriptionTier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subscription", tags=["subscription"])

# Dependency injection - will be set up in main.py
subscription_service: SubscriptionService = None

def get_subscription_service() -> SubscriptionService:
    """Dependency to get subscription service"""
    if subscription_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Subscription service not available"
        )
    return subscription_service

@router.get("/status", response_model=SubscriptionResponse)
async def get_subscription_status(
    current_user: UserResponse = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Get current user's subscription status and details.
    """
    try:
        logger.info(f"🔍 Getting subscription status for user: {current_user.id}")
        subscription = await service.get_user_subscription(current_user.id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Check if user can generate trip
        can_generate = True
        if subscription.tier == SubscriptionTier.FREE:
            can_generate = subscription.usage_stats.trips_generated_this_year < 1
        elif subscription.tier == SubscriptionTier.EXPLORER_ANNUAL:
            limits = get_tier_limits(subscription.tier)
            can_generate = subscription.usage_stats.trips_generated_this_year < limits.trips_per_year
        
        is_premium = subscription.tier != SubscriptionTier.FREE
        
        # Get tier limits to include allowed vibes
        tier_limits = get_tier_limits(subscription.tier)
        
        response = SubscriptionResponse(
            tier=subscription.tier,
            status=subscription.status,
            created_at=subscription.created_at,
            expires_at=subscription.expires_at,
            active_trip_passes=subscription.active_trip_passes,
            usage_stats=subscription.usage_stats,
            allowed_vibes=tier_limits.allowed_vibes,
            is_premium=is_premium,
            can_generate_trip=can_generate,
            stripe_customer_id=subscription.stripe_customer_id
        )
        
        logger.info(f"✅ Retrieved subscription status for user {current_user.id}")
        logger.info(f"🔍 Response data: {response.dict()}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error getting subscription status: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        logger.error(f"❌ Error details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subscription status: {str(e)}"
        )

@router.get("/tiers", response_model=TiersResponse)
async def get_tiers(
    current_user: UserResponse = None,
    service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Get all available subscription tiers with pricing and features.
    Can be called without authentication for public pricing page.
    """
    try:
        tiers = get_all_tiers_info()
        
        current_tier = None
        if current_user:
            subscription = await service.get_user_subscription(current_user.id)
            if subscription:
                current_tier = subscription.tier
        
        return TiersResponse(
            tiers=tiers,
            current_tier=current_tier
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting tiers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tier information"
        )

@router.post("/check-trip-limit", response_model=CheckTripLimitResponse)
async def check_trip_limit(
    request: CheckTripLimitRequest,
    current_user: UserResponse = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Check if user can generate a trip for the specified destination.
    Returns detailed information about limits and upgrade requirements.
    """
    try:
        result = await service.check_can_generate_trip(
            current_user.id,
            request.destination
        )
        
        logger.info(f"✅ Checked trip limit for user {current_user.id} - Can generate: {result.can_generate}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error checking trip limit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check trip limit"
        )

@router.get("/usage", response_model=UsageLimitsResponse)
async def get_usage_stats(
    current_user: UserResponse = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Get detailed usage statistics for the current user.
    Includes trips remaining, limits, and active trip passes.
    """
    try:
        logger.info(f"🔍 Getting usage stats for user: {current_user.id}")
        usage = await service.get_usage_stats(current_user.id)
        
        if not usage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usage statistics not found"
            )
        
        logger.info(f"✅ Retrieved usage stats for user {current_user.id}")
        return usage
        
    except Exception as e:
        logger.error(f"❌ Error getting usage stats: {e}")
        logger.error(f"❌ Error type: {type(e)}")
        logger.error(f"❌ Error details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve usage statistics: {str(e)}"
        )

@router.post("/cancel")
async def cancel_subscription(
    current_user: UserResponse = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Cancel the user's current subscription.
    For annual plans, cancels at the end of the billing period.
    """
    try:
        success = await service.cancel_subscription(current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to cancel subscription"
            )
        
        logger.info(f"✅ Cancelled subscription for user {current_user.id}")
        return {
            "success": True,
            "message": "Subscription cancelled successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error cancelling subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

@router.post("/manual-track-trip")
async def manual_track_trip(
    request: dict,  # {"destination": "Paris"}
    current_user: UserResponse = Depends(get_current_user),
    service: SubscriptionService = Depends(get_subscription_service)
):
    """
    Manually track a trip generation for testing purposes.
    This endpoint allows you to manually increment trip usage.
    """
    try:
        destination = request.get("destination", "Test Destination")
        
        success = await service.record_trip_generation(current_user.id, destination)
        
        if success:
            logger.info(f"✅ Manually tracked trip for user {current_user.id} to {destination}")
            return {
                "message": f"Trip to {destination} tracked successfully",
                "destination": destination
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to track trip"
            )
            
    except Exception as e:
        logger.error(f"❌ Error manually tracking trip for user {current_user.id}: {type(e)} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track trip: {str(e)}"
        )

# Import at module level after defining router
from config.tier_config import get_tier_limits

