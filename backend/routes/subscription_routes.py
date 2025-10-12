from fastapi import APIRouter, Depends, HTTPException, status, Request
from schemas.user_schema import UserResponse, SubscriptionResponse, SubscriptionStatus
from services.auth_service import get_current_user
from services.stripe_service import StripeService
import stripe

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.post("/create-checkout-session", response_model=SubscriptionResponse)
async def create_checkout_session(current_user: UserResponse = Depends(get_current_user)):
    """Create Stripe checkout session for premium subscription"""
    return await StripeService.create_checkout_session(current_user.id, current_user.email)

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    return await StripeService.handle_webhook(payload, sig_header)

@router.post("/cancel")
async def cancel_subscription(current_user: UserResponse = Depends(get_current_user)):
    """Cancel user's subscription"""
    return await StripeService.cancel_subscription(current_user.id)

@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(current_user: UserResponse = Depends(get_current_user)):
    """Get user's subscription status"""
    return await StripeService.get_subscription_status(current_user.id)