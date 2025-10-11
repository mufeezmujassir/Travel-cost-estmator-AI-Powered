from fastapi import HTTPException, status, Depends
from typing import Optional
import logging

from models.subscription_models import SubscriptionTier
from services.subscription_service import SubscriptionService
from config.tier_config import get_tier_limits, can_access_feature, can_access_vibe
from schemas.user_schema import UserResponse

logger = logging.getLogger(__name__)

class SubscriptionMiddleware:
    """Middleware for checking subscription access and enforcing limits"""
    
    def __init__(self, subscription_service: SubscriptionService):
        self.subscription_service = subscription_service
    
    async def require_subscription(
        self, 
        user: UserResponse, 
        min_tier: SubscriptionTier
    ) -> bool:
        """
        Check if user has at least the minimum required tier.
        Raises 402 Payment Required if not.
        """
        subscription = await self.subscription_service.get_user_subscription(user.id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "subscription_required",
                    "message": "This feature requires a subscription",
                    "required_tier": min_tier.value,
                    "upgrade_url": "/pricing"
                }
            )
        
        # Define tier hierarchy for comparison
        tier_hierarchy = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.TRIP_PASS: 1,
            SubscriptionTier.EXPLORER_ANNUAL: 2,
            SubscriptionTier.TRAVEL_PRO: 3
        }
        
        user_tier_level = tier_hierarchy.get(subscription.tier, 0)
        required_tier_level = tier_hierarchy.get(min_tier, 0)
        
        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "insufficient_tier",
                    "message": f"This feature requires {min_tier.value} or higher",
                    "current_tier": subscription.tier.value,
                    "required_tier": min_tier.value,
                    "upgrade_url": "/pricing"
                }
            )
        
        return True
    
    async def check_trip_generation_limit(
        self, 
        user: UserResponse, 
        destination: str
    ) -> bool:
        """
        Check if user can generate a trip for the destination.
        Raises 402 Payment Required if limit is reached.
        """
        check_result = await self.subscription_service.check_can_generate_trip(
            user.id, 
            destination
        )
        
        if not check_result.can_generate:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "trip_limit_reached",
                    "message": check_result.reason,
                    "requires_upgrade": check_result.requires_upgrade,
                    "suggested_tier": check_result.suggested_tier.value if check_result.suggested_tier else None,
                    "upgrade_url": "/pricing"
                }
            )
        
        return True
    
    async def check_feature_access(
        self, 
        user: UserResponse, 
        feature_name: str
    ) -> bool:
        """
        Check if user's tier has access to a specific feature.
        Raises 402 Payment Required if feature is not available.
        """
        subscription = await self.subscription_service.get_user_subscription(user.id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "subscription_required",
                    "message": f"Feature '{feature_name}' requires a subscription",
                    "upgrade_url": "/pricing"
                }
            )
        
        has_access = can_access_feature(subscription.tier, feature_name)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "feature_not_available",
                    "message": f"Feature '{feature_name}' is not available in your current tier",
                    "current_tier": subscription.tier.value,
                    "upgrade_url": "/pricing"
                }
            )
        
        return True
    
    async def check_vibe_access(
        self, 
        user: UserResponse, 
        vibe: str
    ) -> bool:
        """
        Check if user's tier has access to a specific vibe.
        Raises 402 Payment Required if vibe is not available.
        """
        subscription = await self.subscription_service.get_user_subscription(user.id)
        if not subscription:
            # Default to free tier limitations
            subscription_tier = SubscriptionTier.FREE
        else:
            subscription_tier = subscription.tier
        
        has_access = can_access_vibe(subscription_tier, vibe)
        
        if not has_access:
            limits = get_tier_limits(subscription_tier)
            available_vibes = ", ".join(limits.allowed_vibes)
            
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "vibe_not_available",
                    "message": f"Vibe '{vibe}' is not available in your current tier",
                    "current_tier": subscription_tier.value,
                    "available_vibes": limits.allowed_vibes,
                    "upgrade_url": "/pricing"
                }
            )
        
        return True
    
    async def get_tier_limits_for_user(self, user: UserResponse) -> dict:
        """
        Get tier limits for the current user.
        Returns limits as dict for easy consumption.
        """
        subscription = await self.subscription_service.get_user_subscription(user.id)
        if not subscription:
            tier = SubscriptionTier.FREE
        else:
            tier = subscription.tier
        
        limits = get_tier_limits(tier)
        return limits.dict()
    
    async def track_trip_generation(
        self, 
        user: UserResponse, 
        destination: str
    ) -> bool:
        """
        Track that a trip was generated.
        Should be called after successful trip generation.
        """
        success = await self.subscription_service.record_trip_generation(
            user.id, 
            destination
        )
        
        if not success:
            logger.warning(f"⚠️  Failed to track trip generation for user {user.id}")
        
        return success


# Dependency functions for FastAPI

async def get_subscription_middleware(
    subscription_service: SubscriptionService
) -> SubscriptionMiddleware:
    """Dependency to get subscription middleware instance"""
    return SubscriptionMiddleware(subscription_service)


def require_premium() -> callable:
    """
    Dependency factory that requires user to have a premium subscription.
    Usage: user: UserResponse = Depends(get_current_user), _: bool = Depends(require_premium())
    """
    async def _require_premium(
        user: UserResponse,
        subscription_service: SubscriptionService
    ) -> bool:
        subscription = await subscription_service.get_user_subscription(user.id)
        if not subscription or subscription.tier == SubscriptionTier.FREE:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "premium_required",
                    "message": "This feature requires a premium subscription",
                    "current_tier": subscription.tier.value if subscription else "free",
                    "upgrade_url": "/pricing"
                }
            )
        return True
    
    return _require_premium


def require_feature(feature_name: str) -> callable:
    """
    Dependency factory that requires user to have access to a specific feature.
    Usage: user: UserResponse = Depends(get_current_user), _: bool = Depends(require_feature('price_calendar'))
    """
    async def _require_feature(
        user: UserResponse,
        subscription_service: SubscriptionService
    ) -> bool:
        middleware = SubscriptionMiddleware(subscription_service)
        return await middleware.check_feature_access(user, feature_name)
    
    return _require_feature

