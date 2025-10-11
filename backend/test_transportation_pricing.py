"""
Test Transportation Pricing Agent
Verify that prices match real-world Sri Lankan costs
"""

import asyncio
import sys
from datetime import datetime

from services.config import Settings
from services.grok_service import GrokService
from agents.transportation_pricing_agent import TransportationPricingAgent


async def test_galle_matara_pricing():
    """Test pricing for Galle → Matara route"""
    print("="*70)
    print("TESTING: Transportation Pricing Agent")
    print("="*70)
    
    # Initialize services
    settings = Settings()
    grok_service = GrokService(settings)
    await grok_service.initialize()
    
    # Initialize pricing agent
    pricing_agent = TransportationPricingAgent(grok_service)
    
    # Test parameters
    origin = "Galle"
    destination = "Matara"
    distance_km = 47.0
    travelers = 3
    
    print(f"\n📍 Route: {origin} → {destination}")
    print(f"📏 Distance: {distance_km} km")
    print(f"👥 Travelers: {travelers}")
    print("\n" + "="*70)
    
    # Calculate prices
    result = await pricing_agent.calculate_prices(
        origin=origin,
        destination=destination,
        distance_km=distance_km,
        travelers=travelers
    )
    
    print("\n" + "="*70)
    print("RESULTS:")
    print("="*70)
    
    if result.get("prices"):
        prices = result["prices"]
        
        print(f"\n✅ Country Detected: {result.get('country', 'Unknown')}")
        print(f"✅ Confidence: {result.get('confidence', 0):.0%}")
        
        print("\n📊 PRICING BREAKDOWN:")
        print("-"*70)
        
        # Train
        if "train" in prices:
            train_cost = prices["train"].get("cost", 0)
            train_per_person = train_cost / travelers if travelers > 0 else train_cost
            print(f"\n🚂 TRAIN:")
            print(f"   Total for {travelers} travelers: ${train_cost:.2f}")
            print(f"   Per person: ${train_per_person:.2f}")
            print(f"   Duration: {prices['train'].get('duration', 'N/A')}")
            print(f"   Quality: {prices['train'].get('quality', 'N/A')}")
            
            # Validation
            expected_per_person = 0.40  # LKR 130-150 = ~$0.40-0.45
            if train_per_person < expected_per_person:
                print(f"   ⚠️ WARNING: Price ${train_per_person:.2f}/person too low!")
                print(f"   ⚠️ Expected: ~${expected_per_person:.2f}/person (LKR 130-150)")
            else:
                print(f"   ✓ Price looks reasonable")
        
        # Bus
        if "bus" in prices:
            bus_cost = prices["bus"].get("cost", 0)
            bus_per_person = bus_cost / travelers if travelers > 0 else bus_cost
            print(f"\n🚌 BUS:")
            print(f"   Total for {travelers} travelers: ${bus_cost:.2f}")
            print(f"   Per person: ${bus_per_person:.2f}")
            print(f"   Duration: {prices['bus'].get('duration', 'N/A')}")
            print(f"   Quality: {prices['bus'].get('quality', 'N/A')}")
            
            # Validation
            expected_per_person = 0.55  # LKR 180 = ~$0.55
            if bus_per_person < expected_per_person:
                print(f"   ⚠️ WARNING: Price ${bus_per_person:.2f}/person too low!")
                print(f"   ⚠️ Expected: ~${expected_per_person:.2f}/person (LKR 180)")
            else:
                print(f"   ✓ Price looks reasonable")
        
        # Taxi
        if "taxi" in prices:
            taxi_cost = prices["taxi"].get("cost", 0)
            print(f"\n🚕 TAXI (Private Car):")
            print(f"   Total (shared by all): ${taxi_cost:.2f}")
            print(f"   Duration: {prices['taxi'].get('duration', 'N/A')}")
            print(f"   Quality: {prices['taxi'].get('quality', 'N/A')}")
            
            # Validation
            expected_taxi = 15.0  # LKR 5000 = ~$15
            if taxi_cost < expected_taxi * 0.8:  # Allow 20% variance
                print(f"   ⚠️ WARNING: Price ${taxi_cost:.2f} seems low!")
                print(f"   ⚠️ Expected: ~${expected_taxi:.2f} (LKR 5000)")
            else:
                print(f"   ✓ Price looks reasonable")
        
        # Car Rental
        if "car_rental" in prices:
            car_cost = prices["car_rental"].get("cost", 0)
            print(f"\n🚗 CAR RENTAL:")
            print(f"   Daily rate: ${car_cost:.2f}")
            print(f"   Duration: {prices['car_rental'].get('duration', 'N/A')}")
            print(f"   Quality: {prices['car_rental'].get('quality', 'N/A')}")
            
            # Validation
            expected_car = 25.0  # LKR 8000-10000 = ~$25-30
            if car_cost < expected_car * 0.8:
                print(f"   ⚠️ WARNING: Price ${car_cost:.2f} seems low!")
                print(f"   ⚠️ Expected: ~${expected_car:.2f} (LKR 8000-10000)")
            else:
                print(f"   ✓ Price looks reasonable")
        
        print("\n" + "="*70)
        print("COMPARISON WITH ACTUAL SRI LANKAN PRICES:")
        print("="*70)
        print("\nExpected prices (based on LKR rates):")
        print("  Train:      LKR 130-150/person  = $0.40-0.45/person")
        print("  Bus:        LKR 180/person      = $0.55/person")
        print("  Taxi:       LKR 5000 total      = $15.00 total")
        print("  Car Rental: LKR 8000-10000/day  = $25-30/day")
        
        print("\nFor 3 travelers:")
        print("  Train:      3 × $0.40 = $1.20 total")
        print("  Bus:        3 × $0.55 = $1.65 total")
        print("  Taxi:       $15.00 total (shared)")
        print("  Car Rental: $25-30 total (shared)")
        
    else:
        print("\n❌ No prices returned!")
        print(f"Error: {result.get('reasoning', 'Unknown error')}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_galle_matara_pricing())

