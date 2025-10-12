import stripe
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from models.subscription_models import SubscriptionTier
from config.tier_config import get_tier_info

logger = logging.getLogger(__name__)

class StripeService:
    """Service for handling Stripe payments and subscriptions"""
    
    def __init__(
        self, 
        secret_key: str, 
        webhook_secret: str,
        mode: str = "test"
    ):
        self.secret_key = secret_key
        self.webhook_secret = webhook_secret
        self.mode = mode
        stripe.api_key = secret_key
        logger.info(f"✅ Stripe initialized in {mode} mode")
    
    def create_customer(
        self, 
        user_id: str, 
        email: str, 
        name: str
    ) -> Optional[str]:
        """
        Create a Stripe customer.
        Returns customer ID or None on error.
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "user_id": user_id
                }
            )
            logger.info(f"✅ Created Stripe customer {customer.id} for user {user_id}")
            return customer.id
        except stripe.StripeError as e:
            logger.error(f"❌ Stripe error creating customer: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating Stripe customer: {e}")
            return None
    
    def create_checkout_session(
        self,
        user_id: str,
        email: str,
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str,
        destination: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe checkout session for one-time payment (Trip Pass).
        Returns session data with URL and session ID.
        """
        try:
            tier_info = get_tier_info(tier)
            
            # Build session parameters
            session_params = {
                "payment_method_types": ["card"],
                "line_items": [{
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(tier_info.price * 100),  # Convert to cents
                        "product_data": {
                            "name": tier_info.name,
                            "description": tier_info.description if destination is None 
                                         else f"{tier_info.description} - {destination}",
                        },
                    },
                    "quantity": 1,
                }],
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {
                    "user_id": user_id,
                    "tier": tier.value,
                }
            }
            
            # Add destination for trip pass
            if destination:
                session_params["metadata"]["destination"] = destination
            
            # Add customer if exists
            if customer_id:
                session_params["customer"] = customer_id
            else:
                session_params["customer_email"] = email
            
            # Create session
            session = stripe.checkout.Session.create(**session_params)
            
            logger.info(f"✅ Created checkout session {session.id} for user {user_id} - Tier: {tier.value}")
            
            return {
                "session_id": session.id,
                "url": session.url,
                "payment_status": session.payment_status
            }
            
        except stripe.StripeError as e:
            logger.error(f"❌ Stripe error creating checkout session: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating checkout session: {e}")
            return None
    
    def create_subscription_checkout(
        self,
        user_id: str,
        email: str,
        tier: SubscriptionTier,
        success_url: str,
        cancel_url: str,
        customer_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe checkout session for recurring subscription (Annual plans).
        Returns session data with URL and session ID.
        """
        try:
            if tier not in [SubscriptionTier.EXPLORER_ANNUAL, SubscriptionTier.TRAVEL_PRO]:
                logger.error(f"❌ Invalid subscription tier: {tier}")
                return None
            
            tier_info = get_tier_info(tier)
            
            # Create a price object for the subscription
            price = stripe.Price.create(
                unit_amount=int(tier_info.price * 100),  # Convert to cents
                currency="usd",
                recurring={"interval": "year"},
                product_data={
                    "name": tier_info.name,
                },
            )
            
            # Build session parameters
            session_params = {
                "payment_method_types": ["card"],
                "line_items": [{
                    "price": price.id,
                    "quantity": 1,
                }],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {
                    "user_id": user_id,
                    "tier": tier.value,
                }
            }
            
            # Add customer if exists
            if customer_id:
                session_params["customer"] = customer_id
            else:
                session_params["customer_email"] = email
            
            # Create session
            session = stripe.checkout.Session.create(**session_params)
            
            logger.info(f"✅ Created subscription checkout session {session.id} for user {user_id} - Tier: {tier.value}")
            
            return {
                "session_id": session.id,
                "url": session.url,
                "payment_status": session.payment_status
            }
            
        except stripe.StripeError as e:
            logger.error(f"❌ Stripe error creating subscription checkout: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating subscription checkout: {e}")
            return None
    
    def construct_webhook_event(
        self, 
        payload: bytes, 
        signature: str
    ) -> Optional[stripe.Event]:
        """
        Construct and verify a webhook event from Stripe.
        Returns event object or None if verification fails.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            logger.info(f"✅ Webhook event verified: {event['type']}")
            return event
        except ValueError as e:
            logger.error(f"❌ Invalid webhook payload: {e}")
            return None
        except stripe.SignatureVerificationError as e:
            logger.error(f"❌ Invalid webhook signature: {e}")
            return None
    
    def cancel_subscription(
        self, 
        subscription_id: str
    ) -> bool:
        """
        Cancel a Stripe subscription.
        Returns True if successful.
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            logger.info(f"✅ Cancelled subscription {subscription_id}")
            return True
        except stripe.StripeError as e:
            logger.error(f"❌ Stripe error cancelling subscription: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error cancelling subscription: {e}")
            return False
    
    def cancel_subscription_immediately(
        self, 
        subscription_id: str
    ) -> bool:
        """
        Cancel a Stripe subscription immediately.
        Returns True if successful.
        """
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            logger.info(f"✅ Immediately cancelled subscription {subscription_id}")
            return True
        except stripe.StripeError as e:
            logger.error(f"❌ Stripe error cancelling subscription immediately: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error cancelling subscription immediately: {e}")
            return False
    
    def get_subscription_details(
        self, 
        subscription_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get subscription details from Stripe.
        Returns subscription data or None on error.
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "customer": subscription.customer
            }
        except stripe.StripeError as e:
            logger.error(f"❌ Stripe error retrieving subscription: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error retrieving subscription: {e}")
            return None
    
    def get_customer(
        self, 
        customer_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get customer details from Stripe.
        Returns customer data or None on error.
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "metadata": customer.metadata
            }
        except stripe.StripeError as e:
            logger.error(f"❌ Stripe error retrieving customer: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error retrieving customer: {e}")
            return None
    
    # Webhook event handlers
    
    async def handle_checkout_completed(
        self, 
        session: Dict[str, Any],
        subscription_service
    ) -> bool:
        """
        Handle successful checkout completion.
        Activates subscription or trip pass based on mode.
        """
        try:
            user_id = session["metadata"].get("user_id")
            tier_str = session["metadata"].get("tier")
            destination = session["metadata"].get("destination")
            
            if not user_id or not tier_str:
                logger.error("❌ Missing user_id or tier in checkout session metadata")
                return False
            
            tier = SubscriptionTier(tier_str)
            
            # Handle based on tier type
            if tier == SubscriptionTier.TRIP_PASS:
                # Activate trip pass
                payment_intent_id = session.get("payment_intent")
                success = await subscription_service.activate_trip_pass(
                    user_id, 
                    destination, 
                    payment_intent_id
                )
                if success:
                    logger.info(f"✅ Activated trip pass for user {user_id} - Destination: {destination}")
                return success
            
            elif tier in [SubscriptionTier.EXPLORER_ANNUAL, SubscriptionTier.TRAVEL_PRO]:
                # For subscription mode, we need to wait for subscription.created event
                logger.info(f"✅ Checkout completed for annual subscription - Waiting for subscription.created event")
                return True
            
            logger.warning(f"⚠️  Unknown tier type in checkout: {tier}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error handling checkout completion: {e}")
            return False
    
    async def handle_subscription_created(
        self, 
        subscription: Dict[str, Any],
        subscription_service
    ) -> bool:
        """
        Handle subscription creation from Stripe.
        """
        try:
            # Get customer to find user_id
            customer_id = subscription.get("customer")
            customer = self.get_customer(customer_id)
            
            if not customer:
                logger.error("❌ Could not retrieve customer for subscription")
                return False
            
            user_id = customer["metadata"].get("user_id")
            if not user_id:
                logger.error("❌ No user_id in customer metadata")
                return False
            
            # Get tier from subscription metadata or price metadata
            tier_str = subscription["metadata"].get("tier")
            if not tier_str:
                logger.error("❌ No tier in subscription metadata")
                return False
            
            tier = SubscriptionTier(tier_str)
            subscription_id = subscription["id"]
            
            # Activate annual subscription
            success = await subscription_service.upgrade_to_annual(
                user_id,
                tier,
                subscription_id
            )
            
            if success:
                logger.info(f"✅ Activated annual subscription for user {user_id} - Tier: {tier.value}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error handling subscription creation: {e}")
            return False
    
    async def handle_subscription_updated(
        self, 
        subscription: Dict[str, Any],
        subscription_service
    ) -> bool:
        """
        Handle subscription update from Stripe (renewal, status change, etc).
        """
        try:
            # This is for future implementation - handle renewals, updates
            logger.info(f"📝 Subscription updated: {subscription['id']} - Status: {subscription['status']}")
            return True
        except Exception as e:
            logger.error(f"❌ Error handling subscription update: {e}")
            return False
    
    async def handle_subscription_deleted(
        self, 
        subscription: Dict[str, Any],
        subscription_service
    ) -> bool:
        """
        Handle subscription cancellation from Stripe.
        """
        try:
            # Get user_id from customer metadata
            customer_id = subscription.get("customer")
            customer = self.get_customer(customer_id)
            
            if not customer:
                logger.error("❌ Could not retrieve customer for cancelled subscription")
                return False
            
            user_id = customer["metadata"].get("user_id")
            if not user_id:
                logger.error("❌ No user_id in customer metadata")
                return False
            
            # Cancel subscription in our system
            success = await subscription_service.cancel_subscription(user_id)
            
            if success:
                logger.info(f"✅ Cancelled subscription for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error handling subscription deletion: {e}")
            return False
    
    async def handle_payment_failed(
        self, 
        invoice: Dict[str, Any],
        subscription_service
    ) -> bool:
        """
        Handle failed payment (future implementation - send email, retry, etc).
        """
        try:
            logger.warning(f"⚠️  Payment failed for invoice: {invoice['id']}")
            # Future: Send email notification, attempt retry, etc.
            return True
        except Exception as e:
            logger.error(f"❌ Error handling payment failure: {e}")
            return False

