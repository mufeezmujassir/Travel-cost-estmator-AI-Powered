from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import logging

from models.user import users_collection
from models.subscription_models import (
    SubscriptionTier, SubscriptionStatus, Subscription, TripPass, UsageStats
)
from schemas.subscription_schema import (
    SubscriptionResponse, CheckTripLimitResponse, UsageLimitsResponse
)
from config.tier_config import get_tier_limits, get_tier_info, is_premium_tier
from services.region_resolver import RegionResolver

logger = logging.getLogger(__name__)

class SubscriptionService:
    """Service for managing user subscriptions and usage tracking"""
    
    def __init__(self, region_resolver: RegionResolver):
        self.region_resolver = region_resolver
    
    async def get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user's subscription details"""
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None
            
            # Build subscription object from user document
            subscription_data = user.get("subscription", {})
            
            # Default values if not present
            if not subscription_data:
                subscription_data = self._create_default_subscription()
            
            # Ensure usage_stats exists
            if "usage_stats" not in subscription_data:
                subscription_data["usage_stats"] = self._create_default_usage_stats()
            
            logger.info(f"🔍 Creating subscription object with data: {subscription_data}")
            subscription = Subscription(**subscription_data)
            
            # Expire old trip passes
            subscription.expire_old_trip_passes()
            
            # Check and update expired subscription
            if subscription.expires_at and subscription.expires_at < datetime.utcnow():
                if subscription.status == SubscriptionStatus.ACTIVE:
                    subscription.status = SubscriptionStatus.EXPIRED
                    # Downgrade to free tier
                    subscription.tier = SubscriptionTier.FREE
                    await self._save_subscription(user_id, subscription.dict())
            
            return subscription
            
        except Exception as e:
            logger.error(f"❌ Error getting subscription for user {user_id}: {e}")
            return None
    
    async def check_can_generate_trip(
        self, 
        user_id: str, 
        destination: str
    ) -> CheckTripLimitResponse:
        """
        Check if user can generate a trip for the given destination.
        Returns detailed response with reason if cannot generate.
        """
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                return CheckTripLimitResponse(
                    can_generate=False,
                    reason="User subscription not found",
                    requires_upgrade=False
                )
            
            tier = subscription.tier
            limits = get_tier_limits(tier)
            usage = subscription.usage_stats
            
            # Get region for destination
            region = await self.region_resolver.get_region_for_destination(destination)
            if not region:
                # If we can't resolve region, allow generation (fail open)
                logger.warning(f"⚠️  Could not resolve region for {destination}, allowing generation")
                return CheckTripLimitResponse(
                    can_generate=True,
                    reason=None,
                    requires_upgrade=False
                )
            
            # Check for FREE tier
            if tier == SubscriptionTier.FREE:
                if usage.trips_generated_this_year >= 1:
                    return CheckTripLimitResponse(
                        can_generate=False,
                        reason="You've used your 1 free trip for this year. Upgrade to continue planning!",
                        requires_upgrade=True,
                        suggested_tier=SubscriptionTier.TRIP_PASS
                    )
                return CheckTripLimitResponse(can_generate=True)
            
            # Check for TRIP_PASS tier
            if tier == SubscriptionTier.TRIP_PASS:
                # Check if user has a valid trip pass for this region
                trip_pass = subscription.get_active_trip_pass_for_region(region)
                if trip_pass:
                    return CheckTripLimitResponse(
                        can_generate=True,
                        has_trip_pass_for_region=True
                    )
                else:
                    return CheckTripLimitResponse(
                        can_generate=False,
                        reason=f"Your Trip Pass is for a different region. Purchase a new Trip Pass for {region}.",
                        requires_upgrade=True,
                        suggested_tier=SubscriptionTier.TRIP_PASS
                    )
            
            # Check for EXPLORER_ANNUAL tier
            if tier == SubscriptionTier.EXPLORER_ANNUAL:
                if limits.trips_per_year and usage.trips_generated_this_year >= limits.trips_per_year:
                    return CheckTripLimitResponse(
                        can_generate=False,
                        reason=f"You've used all {limits.trips_per_year} trips for this year. Upgrade to Travel Pro for unlimited trips!",
                        requires_upgrade=True,
                        suggested_tier=SubscriptionTier.TRAVEL_PRO
                    )
                return CheckTripLimitResponse(can_generate=True)
            
            # TRAVEL_PRO tier - unlimited
            if tier == SubscriptionTier.TRAVEL_PRO:
                return CheckTripLimitResponse(can_generate=True)
            
            # Default: allow generation
            return CheckTripLimitResponse(can_generate=True)
            
        except Exception as e:
            logger.error(f"❌ Error checking trip limit for user {user_id}: {e}")
            # Fail open - allow generation on error
            return CheckTripLimitResponse(
                can_generate=True,
                reason="Error checking limits, proceeding with generation"
            )
    
    async def record_trip_generation(
        self, 
        user_id: str, 
        destination: str
    ) -> bool:
        """
        Record that a trip was generated for tracking purposes.
        Updates usage statistics and trip pass usage.
        """
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                logger.error(f"❌ Cannot record trip - subscription not found for user {user_id}")
                return False
            
            # Get region
            region = await self.region_resolver.get_region_for_destination(destination)
            if not region:
                region = destination  # Fallback to destination itself
            
            # Update usage stats
            subscription.usage_stats.trips_generated_this_year += 1
            subscription.usage_stats.trips_generated_lifetime += 1
            subscription.usage_stats.last_trip_date = datetime.utcnow()
            subscription.usage_stats.last_region_used = region
            
            # If trip pass tier, increment trip pass usage
            if subscription.tier == SubscriptionTier.TRIP_PASS:
                trip_pass = subscription.get_active_trip_pass_for_region(region)
                if trip_pass:
                    trip_pass.trips_generated += 1
            
            # Add history entry
            subscription.add_history_entry("trip_generated", {
                "destination": destination,
                "region": region,
                "tier": subscription.tier.value
            })
            
            # Save to database
            await self._save_subscription(user_id, subscription.dict())
            
            logger.info(f"✅ Recorded trip generation for user {user_id} to {destination} ({region})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recording trip generation for user {user_id}: {e}")
            return False
    
    async def activate_trip_pass(
        self, 
        user_id: str, 
        destination: str, 
        payment_intent_id: str
    ) -> bool:
        """
        Activate a trip pass for a user after successful payment.
        Trip pass is valid for 90 days from activation.
        """
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                logger.error(f"❌ Cannot activate trip pass - subscription not found for user {user_id}")
                return False
            
            # Get region for destination
            region = await self.region_resolver.get_region_for_destination(destination)
            if not region:
                region = destination  # Fallback
            
            # Create trip pass
            trip_pass = TripPass(
                destination=destination,
                region=region,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=90),
                trips_generated=0,
                is_active=True,
                payment_intent_id=payment_intent_id
            )
            
            # Add to active trip passes
            subscription.active_trip_passes.append(trip_pass)
            
            # Update tier to trip pass
            subscription.tier = SubscriptionTier.TRIP_PASS
            subscription.status = SubscriptionStatus.ACTIVE
            
            # Add history entry
            subscription.add_history_entry("trip_pass_activated", {
                "destination": destination,
                "region": region,
                "expires_at": trip_pass.expires_at.isoformat(),
                "payment_intent_id": payment_intent_id
            })
            
            # Save to database
            await self._save_subscription(user_id, subscription.dict())
            
            logger.info(f"✅ Activated trip pass for user {user_id} - Region: {region}, Expires: {trip_pass.expires_at}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error activating trip pass for user {user_id}: {e}")
            return False
    
    async def upgrade_to_annual(
        self, 
        user_id: str, 
        tier: SubscriptionTier, 
        stripe_subscription_id: str
    ) -> bool:
        """
        Upgrade user to an annual subscription tier.
        """
        try:
            if tier not in [SubscriptionTier.EXPLORER_ANNUAL, SubscriptionTier.TRAVEL_PRO]:
                logger.error(f"❌ Invalid annual tier: {tier}")
                return False
            
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                logger.error(f"❌ Cannot upgrade - subscription not found for user {user_id}")
                return False
            
            # Update subscription
            subscription.tier = tier
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.expires_at = datetime.utcnow() + timedelta(days=365)
            subscription.stripe_subscription_id = stripe_subscription_id
            
            # Reset yearly counter if upgrading from lower tier
            subscription.usage_stats.trips_generated_this_year = 0
            subscription.usage_stats.year_reset_date = datetime.utcnow() + timedelta(days=365)
            
            # Add history entry
            subscription.add_history_entry("upgraded_to_annual", {
                "tier": tier.value,
                "expires_at": subscription.expires_at.isoformat(),
                "stripe_subscription_id": stripe_subscription_id
            })
            
            # Save to database
            await self._save_subscription(user_id, subscription.dict())
            
            logger.info(f"✅ Upgraded user {user_id} to {tier.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error upgrading user {user_id} to annual: {e}")
            return False
    
    async def cancel_subscription(self, user_id: str) -> bool:
        """Cancel user's subscription"""
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                return False
            
            subscription.status = SubscriptionStatus.CANCELLED
            
            # Add history entry
            subscription.add_history_entry("subscription_cancelled", {
                "previous_tier": subscription.tier.value,
                "cancelled_at": datetime.utcnow().isoformat()
            })
            
            await self._save_subscription(user_id, subscription.dict())
            
            logger.info(f"✅ Cancelled subscription for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cancelling subscription for user {user_id}: {e}")
            return False
    
    async def get_usage_stats(self, user_id: str) -> Optional[UsageLimitsResponse]:
        """Get detailed usage statistics for user"""
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                return None
            
            limits = get_tier_limits(subscription.tier)
            usage = subscription.usage_stats
            
            # Calculate trips remaining
            trips_remaining = None
            if limits.trips_per_year is not None:
                trips_remaining = max(0, limits.trips_per_year - usage.trips_generated_this_year)
            
            # Calculate days until reset
            days_until_reset = None
            if usage.year_reset_date:
                delta = usage.year_reset_date - datetime.utcnow()
                days_until_reset = max(0, delta.days)
            
            # Calculate days until subscription expires
            subscription_expires_in_days = None
            if subscription.expires_at:
                delta = subscription.expires_at - datetime.utcnow()
                subscription_expires_in_days = max(0, delta.days)
            
            # Get active trip passes info
            active_passes = []
            for trip_pass in subscription.active_trip_passes:
                if trip_pass.is_active and trip_pass.expires_at > datetime.utcnow():
                    active_passes.append({
                        "destination": trip_pass.destination,
                        "region": trip_pass.region,
                        "expires_at": trip_pass.expires_at.isoformat(),
                        "trips_generated": trip_pass.trips_generated,
                        "days_remaining": (trip_pass.expires_at - datetime.utcnow()).days
                    })
            
            return UsageLimitsResponse(
                current_tier=subscription.tier,
                limits=limits,
                usage=usage,
                trips_remaining=trips_remaining,
                active_trip_passes=active_passes,
                days_until_reset=days_until_reset,
                subscription_expires_in_days=subscription_expires_in_days
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting usage stats for user {user_id}: {e}")
            return None
    
    async def reset_annual_limits(self, user_id: str) -> bool:
        """Reset yearly trip counter (called by scheduled job)"""
        try:
            subscription = await self.get_user_subscription(user_id)
            if not subscription:
                return False
            
            # Check if reset date has passed
            if subscription.usage_stats.year_reset_date <= datetime.utcnow():
                subscription.usage_stats.trips_generated_this_year = 0
                subscription.usage_stats.year_reset_date = datetime.utcnow() + timedelta(days=365)
                
                subscription.add_history_entry("annual_limit_reset", {
                    "reset_date": datetime.utcnow().isoformat()
                })
                
                await self._save_subscription(user_id, subscription.dict())
                logger.info(f"✅ Reset annual limits for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error resetting annual limits for user {user_id}: {e}")
            return False
    
    async def initialize_user_subscription(self, user_id: str) -> bool:
        """Initialize subscription for a new user"""
        try:
            subscription = self._create_default_subscription()
            await self._save_subscription(user_id, subscription)
            logger.info(f"✅ Initialized subscription for new user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing subscription for user {user_id}: {e}")
            return False
    
    # Helper methods
    
    def _create_default_subscription(self) -> Dict[str, Any]:
        """Create default subscription data for new users"""
        usage_stats = self._create_default_usage_stats()
        return {
            "tier": SubscriptionTier.FREE.value,
            "status": SubscriptionStatus.ACTIVE.value,
            "created_at": datetime.utcnow(),
            "expires_at": None,
            "stripe_subscription_id": None,
            "stripe_customer_id": None,
            "active_trip_passes": [],
            "usage_stats": usage_stats,
            "subscription_history": [{
                "timestamp": datetime.utcnow(),
                "action": "account_created",
                "details": {"tier": "free"}
            }]
        }
    
    def _create_default_usage_stats(self) -> Dict[str, Any]:
        """Create default usage stats"""
        return {
            "trips_generated_this_year": 0,
            "trips_generated_lifetime": 0,
            "last_trip_date": None,
            "year_reset_date": datetime.utcnow() + timedelta(days=365),
            "last_region_used": None
        }
    
    async def _save_subscription(self, user_id: str, subscription: Dict[str, Any]) -> bool:
        """Save subscription to database"""
        try:
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"subscription": subscription}}
            )
            return result.modified_count > 0 or result.matched_count > 0
        except Exception as e:
            logger.error(f"❌ Error saving subscription for user {user_id}: {e}")
            return False

