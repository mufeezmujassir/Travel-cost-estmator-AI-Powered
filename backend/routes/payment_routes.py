from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional
import logging

from schemas.user_schema import UserResponse
from schemas.subscription_schema import CreateTripPassRequest, UpgradeSubscriptionRequest
from services.stripe_service import StripeService
from services.subscription_service import SubscriptionService
from services.auth_service import get_current_user
from models.subscription_models import SubscriptionTier
from models.user import users_collection
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payment", tags=["payment"])

# Dependency injection - will be set up in main.py
stripe_service: StripeService = None
subscription_service: SubscriptionService = None

def get_stripe_service() -> StripeService:
    """Dependency to get Stripe service"""
    if stripe_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service not available"
        )
    return stripe_service

def get_subscription_service() -> SubscriptionService:
    """Dependency to get subscription service"""
    if subscription_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Subscription service not available"
        )
    return subscription_service

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateTripPassRequest,
    current_user: UserResponse = Depends(get_current_user),
    stripe_svc: StripeService = Depends(get_stripe_service),
    subscription_svc: SubscriptionService = Depends(get_subscription_service)
):
    """
    Create a Stripe checkout session for purchasing a Trip Pass.
    Returns checkout URL for redirection.
    """
    try:
        # Get user's subscription to check for existing Stripe customer
        subscription = await subscription_svc.get_user_subscription(current_user.id)
        customer_id = subscription.stripe_customer_id if subscription else None
        
        # If no customer exists, create one
        if not customer_id:
            customer_id = stripe_svc.create_customer(
                current_user.id,
                current_user.email,
                current_user.name
            )
            
            # Update user with customer ID
            if customer_id and subscription:
                subscription.stripe_customer_id = customer_id
                users_collection.update_one(
                    {"_id": ObjectId(current_user.id)},
                    {"$set": {"subscription.stripe_customer_id": customer_id}}
                )
        
        # Create checkout session
        session_data = stripe_svc.create_checkout_session(
            user_id=current_user.id,
            email=current_user.email,
            tier=SubscriptionTier.TRIP_PASS,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            destination=request.destination,
            customer_id=customer_id
        )
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create checkout session"
            )
        
        logger.info(f"✅ Created checkout session for user {current_user.id} - Destination: {request.destination}")
        
        return {
            "checkout_url": session_data["url"],
            "session_id": session_data["session_id"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/create-subscription")
async def create_subscription_checkout(
    request: UpgradeSubscriptionRequest,
    current_user: UserResponse = Depends(get_current_user),
    stripe_svc: StripeService = Depends(get_stripe_service),
    subscription_svc: SubscriptionService = Depends(get_subscription_service)
):
    """
    Create a Stripe checkout session for annual subscription.
    Returns checkout URL for redirection.
    """
    try:
        # Validate tier
        if request.target_tier not in [SubscriptionTier.EXPLORER_ANNUAL, SubscriptionTier.TRAVEL_PRO]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subscription tier"
            )
        
        # Get user's subscription to check for existing Stripe customer
        subscription = await subscription_svc.get_user_subscription(current_user.id)
        customer_id = subscription.stripe_customer_id if subscription else None
        
        # If no customer exists, create one
        if not customer_id:
            customer_id = stripe_svc.create_customer(
                current_user.id,
                current_user.email,
                current_user.name
            )
            
            # Update user with customer ID
            if customer_id and subscription:
                subscription.stripe_customer_id = customer_id
                users_collection.update_one(
                    {"_id": ObjectId(current_user.id)},
                    {"$set": {"subscription.stripe_customer_id": customer_id}}
                )
        
        # Create subscription checkout session
        session_data = stripe_svc.create_subscription_checkout(
            user_id=current_user.id,
            email=current_user.email,
            tier=request.target_tier,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            customer_id=customer_id
        )
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create subscription checkout session"
            )
        
        logger.info(f"✅ Created subscription checkout for user {current_user.id} - Tier: {request.target_tier.value}")
        
        return {
            "checkout_url": session_data["url"],
            "session_id": session_data["session_id"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating subscription checkout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription checkout: {str(e)}"
        )

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_svc: StripeService = Depends(get_stripe_service),
    subscription_svc: SubscriptionService = Depends(get_subscription_service)
):
    """
    Handle Stripe webhook events.
    This endpoint is called by Stripe when events occur (payments, subscriptions, etc).
    """
    try:
        # Get webhook payload and signature
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature"
            )
        
        # Verify and construct event
        event = stripe_svc.construct_webhook_event(payload, signature)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook event"
            )
        
        event_type = event["type"]
        logger.info(f"📬 Received Stripe webhook: {event_type}")
        
        # Handle different event types
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            await stripe_svc.handle_checkout_completed(session, subscription_svc)
        
        elif event_type == "customer.subscription.created":
            subscription = event["data"]["object"]
            await stripe_svc.handle_subscription_created(subscription, subscription_svc)
        
        elif event_type == "customer.subscription.updated":
            subscription = event["data"]["object"]
            await stripe_svc.handle_subscription_updated(subscription, subscription_svc)
        
        elif event_type == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            await stripe_svc.handle_subscription_deleted(subscription, subscription_svc)
        
        elif event_type == "invoice.payment_failed":
            invoice = event["data"]["object"]
            await stripe_svc.handle_payment_failed(invoice, subscription_svc)
        
        else:
            logger.info(f"ℹ️  Unhandled webhook event type: {event_type}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )

@router.get("/success")
async def payment_success(
    session_id: Optional[str] = None
):
    """
    Handle successful payment redirect.
    This is where users land after successful Stripe checkout.
    """
    logger.info(f"✅ Payment success redirect - Session: {session_id}")
    
    return {
        "status": "success",
        "message": "Payment completed successfully",
        "session_id": session_id
    }

@router.get("/cancel")
async def payment_cancelled():
    """
    Handle cancelled payment redirect.
    This is where users land if they cancel the Stripe checkout.
    """
    logger.info("❌ Payment cancelled by user")
    
    return {
        "status": "cancelled",
        "message": "Payment was cancelled"
    }

@router.post("/manual-activate-trip-pass")
async def manual_activate_trip_pass(
    request: CreateTripPassRequest,
    current_user: UserResponse = Depends(get_current_user),
    subscription_svc: SubscriptionService = Depends(get_subscription_service)
):
    """
    Manually activate a trip pass after successful payment.
    This is a temporary endpoint for testing when webhooks aren't working.
    """
    try:
        # Activate trip pass manually
        success = await subscription_svc.activate_trip_pass(
            current_user.id,
            request.destination,
            "manual_activation"  # Placeholder payment intent ID
        )
        
        if success:
            logger.info(f"✅ Manually activated trip pass for user {current_user.id} - Destination: {request.destination}")
            return {
                "message": "Trip pass activated successfully",
                "destination": request.destination,
                "status": "active"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to activate trip pass"
            )
            
    except Exception as e:
        logger.error(f"❌ Error manually activating trip pass: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate trip pass: {str(e)}"
        )

