import stripe
import os
from dotenv import load_dotenv
from models.user import users_collection
from bson import ObjectId
from datetime import datetime, timedelta
from fastapi import HTTPException, status

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeService:
    
    @staticmethod
    async def create_checkout_session(user_id: str, email: str):
        """Create Stripe checkout session for premium subscription"""
        try:
            # Get or create Stripe customer
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            
            stripe_customer_id = user.get("stripeCustomerId")
            
            if not stripe_customer_id:
                # Create new Stripe customer
                customer = stripe.Customer.create(
                    email=email,
                    metadata={"user_id": user_id}
                )
                stripe_customer_id = customer.id
                
                # Save customer ID
                users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"stripeCustomerId": stripe_customer_id}}
                )
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': os.getenv("PREMIUM_PRICEID"),
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=os.getenv("FRONTEND_URL", "http://localhost:3000") + "/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=os.getenv("FRONTEND_URL", "http://localhost:3000") + "/cancel",
                metadata={
                    "user_id": user_id
                }
            )
            
            return {
                "sessionId": session.id,
                "url": session.url
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create checkout session: {str(e)}"
            )
    
    @staticmethod
    async def handle_webhook(payload: dict, sig_header: str):
        """Handle Stripe webhook events"""
        try:
            webhook_secret = os.getenv("WEB_HOOK_SECRET")
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            await StripeService._handle_successful_payment(session)
        
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            await StripeService._handle_subscription_updated(subscription)
        
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            await StripeService._handle_subscription_cancelled(subscription)
        
        return {"status": "success"}
    
    @staticmethod
    async def _handle_successful_payment(session):
        """Handle successful payment"""
        user_id = session['metadata'].get('user_id')
        subscription_id = session.get('subscription')
        
        if user_id and subscription_id:
            # Get subscription details
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Calculate subscription end date (1 month from now)
            subscription_end = datetime.utcnow() + timedelta(days=30)
            
            # Update user to premium
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "type": "premium",
                    "subscriptionStatus": "active",
                    "subscriptionId": subscription_id,
                    "subscriptionEndDate": subscription_end
                }}
            )
    
    @staticmethod
    async def _handle_subscription_updated(subscription):
        """Handle subscription update"""
        customer_id = subscription['customer']
        
        # Find user by Stripe customer ID
        user = users_collection.find_one({"stripeCustomerId": customer_id})
        
        if user:
            status = subscription['status']
            
            if status == 'active':
                # Renew subscription
                subscription_end = datetime.utcnow() + timedelta(days=30)
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {
                        "type": "premium",
                        "subscriptionStatus": "active",
                        "subscriptionEndDate": subscription_end
                    }}
                )
            else:
                # Downgrade to basic
                users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {
                        "type": "basic",
                        "subscriptionStatus": "expired",
                        "generationsRemaining": 0
                    }}
                )
    
    @staticmethod
    async def _handle_subscription_cancelled(subscription):
        """Handle subscription cancellation"""
        customer_id = subscription['customer']
        
        # Find user by Stripe customer ID
        user = users_collection.find_one({"stripeCustomerId": customer_id})
        
        if user:
            # Downgrade to basic
            users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "type": "basic",
                    "subscriptionStatus": "cancelled",
                    "generationsRemaining": 0
                }}
            )
    
    @staticmethod
    async def cancel_subscription(user_id: str):
        """Cancel user's subscription"""
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        subscription_id = user.get("subscriptionId")
        
        if not subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )
        
        try:
            # Cancel at period end
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            # Update user status
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"subscriptionStatus": "cancelled"}}
            )
            
            return {"message": "Subscription will be cancelled at the end of the billing period"}
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel subscription: {str(e)}"
            )
    
    @staticmethod
    async def get_subscription_status(user_id: str):
        """Get user's subscription status"""
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "type": user.get("type", "basic"),
            "status": user.get("subscriptionStatus", "expired"),
            "hasUsedFreePlan": user.get("hasUsedFreePlan", False),
            "generationsRemaining": user.get("generationsRemaining", 0),
            "subscriptionEndDate": user.get("subscriptionEndDate")
        }