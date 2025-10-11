"""
Migration script to add subscription fields to existing users.
Run this script once before deploying the subscription system.

Usage:
    python backend/scripts/migrate_users_to_subscription.py
"""

import sys
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.subscription_models import SubscriptionTier, SubscriptionStatus

# Load environment variables
load_dotenv()

def migrate_users():
    """Add subscription fields to all existing users"""
    
    # Connect to MongoDB
    mongodb_uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("DATABASE_NAME", "travel_agent_db")
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment variables")
        return False
    
    try:
        client = MongoClient(mongodb_uri)
        db = client[database_name]
        users_collection = db["users"]
        
        print(f"🔌 Connected to MongoDB: {database_name}")
        
        # Get all users
        users = list(users_collection.find({}))
        print(f"📊 Found {len(users)} users in database")
        
        if len(users) == 0:
            print("✅ No users to migrate")
            return True
        
        # Default subscription structure
        default_subscription = {
            "tier": SubscriptionTier.FREE.value,
            "status": SubscriptionStatus.ACTIVE.value,
            "created_at": datetime.utcnow(),
            "expires_at": None,
            "stripe_subscription_id": None,
            "stripe_customer_id": None,
            "active_trip_passes": [],
            "usage_stats": {
                "trips_generated_this_year": 0,
                "trips_generated_lifetime": 0,
                "last_trip_date": None,
                "year_reset_date": datetime.utcnow() + timedelta(days=365),
                "last_region_used": None
            },
            "subscription_history": [{
                "timestamp": datetime.utcnow(),
                "action": "migrated_to_subscription_system",
                "details": {"tier": "free", "migrated_from": "legacy"}
            }]
        }
        
        # Migrate each user
        migrated_count = 0
        skipped_count = 0
        
        for user in users:
            user_id = user["_id"]
            email = user.get("email", "unknown")
            
            # Check if user already has subscription field
            if "subscription" in user:
                print(f"⏭️  Skipping {email} - already has subscription")
                skipped_count += 1
                continue
            
            # Add subscription field
            result = users_collection.update_one(
                {"_id": user_id},
                {"$set": {"subscription": default_subscription}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Migrated {email}")
                migrated_count += 1
            else:
                print(f"⚠️  Failed to migrate {email}")
        
        print("\n" + "="*50)
        print(f"📊 Migration Summary:")
        print(f"   Total users: {len(users)}")
        print(f"   Migrated: {migrated_count}")
        print(f"   Skipped: {skipped_count}")
        print("="*50)
        
        # Create indexes for subscription queries
        print("\n🔧 Creating indexes...")
        users_collection.create_index("subscription.tier")
        users_collection.create_index("subscription.status")
        users_collection.create_index("subscription.expires_at")
        print("✅ Indexes created")
        
        client.close()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting user subscription migration...")
    print("="*50)
    
    success = migrate_users()
    
    if success:
        print("\n✅ All done! You can now deploy the subscription system.")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)

