"""
Test complete travel request flow with correct pricing
Simulates: User submits Galle → Paris request → System returns full travel plan
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.travel_orchestrator import TravelOrchestrator
from models.travel_models import TravelRequest, VibeType
from services.config import Settings


async def test_full_travel_flow():
    """Test complete travel request flow"""
    
    print("="*80)
    print("🌍 FULL TRAVEL REQUEST FLOW TEST")
    print("="*80)
    print()
    
    settings = Settings()
    
    # User's travel request
    request = TravelRequest(
        origin="Galle",
        destination="Paris",
        start_date="2025-10-22",
        return_date="2025-10-27",
        travelers=4,
        budget=10000.0,
        vibe=VibeType.CULTURAL,
        include_price_trends=False  # Skip for faster test
    )
    
    print("📋 User Request:")
    print(f"   From: {request.origin}")
    print(f"   To: {request.destination}")
    print(f"   Dates: {request.start_date} to {request.return_date}")
    print(f"   Travelers: {request.travelers}")
    print(f"   Budget: ${request.budget:,.2f}")
    print(f"   Vibe: {request.vibe.value}")
    print()
    
    print("-"*80)
    print("🚀 Processing Travel Request...")
    print("-"*80)
    print()
    
    # Initialize orchestrator
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    
    # Process request
    response = await orchestrator.process_travel_request(request)
    
    print()
    print("="*80)
    print("📊 TRAVEL PLAN GENERATED")
    print("="*80)
    print()
    
    # Display results
    print("✈️ FLIGHTS:")
    print(f"   Found: {len(response.flights)} options")
    if response.flights:
        best_flight = response.flights[0]
        price_per_person = best_flight.price / request.travelers
        print(f"   Best Option: {best_flight.airline}")
        print(f"   Price: ${best_flight.price:,.2f} total (${price_per_person:,.2f}/person)")
        print(f"   Route: {best_flight.departure_airport} → {best_flight.arrival_airport}")
        print(f"   Stops: {best_flight.stops}")
    print()
    
    print("🏨 HOTELS:")
    print(f"   Found: {len(response.hotels)} options")
    if response.hotels:
        recommended = response.hotels[0]
        print(f"   Recommended: {recommended.name}")
        print(f"   Price: ${recommended.price_per_night:,.2f}/night")
        print(f"   Rating: {recommended.rating}/5.0")
        print(f"   Confidence: {recommended.price_confidence}")
    print()
    
    print("💰 COST BREAKDOWN:")
    cost = response.cost_breakdown
    print(f"   Flights:        ${cost.flights:>10,.2f}")
    print(f"   Accommodation:  ${cost.accommodation:>10,.2f}")
    print(f"   Transportation: ${cost.transportation:>10,.2f}")
    print(f"   Activities:     ${cost.activities:>10,.2f}")
    print(f"   Food & Dining:  ${cost.food:>10,.2f}")
    print(f"   Miscellaneous:  ${cost.miscellaneous:>10,.2f}")
    print(f"   " + "-"*36)
    print(f"   TOTAL:          ${response.total_cost:>10,.2f}")
    print(f"   Per Person:     ${response.total_cost/request.travelers:>10,.2f}")
    print()
    
    print("🎯 BUDGET ANALYSIS:")
    if response.total_cost <= request.budget:
        surplus = request.budget - response.total_cost
        print(f"   ✅ WITHIN BUDGET!")
        print(f"   Budget: ${request.budget:,.2f}")
        print(f"   Estimated: ${response.total_cost:,.2f}")
        print(f"   Remaining: ${surplus:,.2f}")
    else:
        deficit = response.total_cost - request.budget
        print(f"   ⚠️ OVER BUDGET")
        print(f"   Budget: ${request.budget:,.2f}")
        print(f"   Estimated: ${response.total_cost:,.2f}")
        print(f"   Over by: ${deficit:,.2f}")
    print()
    
    print("📍 TRAVEL TYPE:")
    if hasattr(response, 'is_domestic_travel'):
        if response.is_domestic_travel:
            print(f"   Domestic travel within same country")
            if hasattr(response, 'travel_distance_km'):
                print(f"   Distance: {response.travel_distance_km:.1f} km")
        else:
            print(f"   International travel")
    print()
    
    print("="*80)
    print("✅ PRICING VERIFICATION")
    print("="*80)
    print()
    
    # Verify pricing is realistic
    if response.flights:
        best_flight = response.flights[0]
        price_per_person = best_flight.price / request.travelers
        
        print("✈️ Flight Price Check:")
        print(f"   Total: ${best_flight.price:,.2f}")
        print(f"   Per Person: ${price_per_person:,.2f}")
        
        # Realistic range for CMB-CDG: $600-1500/person
        if 600 <= price_per_person <= 1500:
            print(f"   ✅ REALISTIC - Within expected range ($600-$1500/person)")
        elif price_per_person < 600:
            print(f"   ⚠️ Suspiciously low - May be error or budget airline")
        else:
            print(f"   ⚠️ High price - Business/First class or peak season")
    print()
    
    if response.hotels:
        recommended = response.hotels[0]
        
        print("🏨 Hotel Price Check:")
        print(f"   Price: ${recommended.price_per_night:,.2f}/night")
        print(f"   Confidence: {recommended.price_confidence}")
        
        # Realistic range for Paris hotels: $100-500/night
        if 100 <= recommended.price_per_night <= 500:
            print(f"   ✅ REALISTIC - Within expected range ($100-$500/night)")
        elif recommended.price_per_night < 100:
            print(f"   ⚠️ Budget option - Hostel or budget hotel")
        else:
            print(f"   ⚠️ Luxury option - High-end hotel")
        
        if recommended.price_confidence == "high":
            print(f"   ✅ HIGH CONFIDENCE - Real SERP API data")
        else:
            print(f"   ⚠️ ESTIMATED - Fallback pricing")
    print()
    
    print("💰 Total Cost Check:")
    cost_per_person = response.total_cost / request.travelers
    print(f"   Total: ${response.total_cost:,.2f}")
    print(f"   Per Person: ${cost_per_person:,.2f}")
    
    # Realistic range for 5-day Paris trip: $1800-3500/person
    if 1800 <= cost_per_person <= 3500:
        print(f"   ✅ REALISTIC - Within expected range ($1800-$3500/person)")
    elif cost_per_person < 1800:
        print(f"   ⚠️ Budget trip - Very economical")
    else:
        print(f"   ⚠️ Luxury trip - High-end experience")
    print()
    
    print("="*80)
    print("🎉 TEST COMPLETE")
    print("="*80)
    print()
    
    # Final verdict
    has_flights = len(response.flights) > 0
    has_hotels = len(response.hotels) > 0
    has_realistic_prices = (
        response.flights and 
        600 <= (response.flights[0].price / request.travelers) <= 1500 and
        response.hotels and
        100 <= response.hotels[0].price_per_night <= 500 and
        response.hotels[0].price_confidence == "high"
    )
    
    if has_flights and has_hotels and has_realistic_prices:
        print("✅ SUCCESS: Complete travel plan with realistic pricing!")
    elif has_flights and has_hotels:
        print("⚠️ PARTIAL: Travel plan generated but check price ranges")
    else:
        print("❌ FAILURE: Missing critical components")
    print()


if __name__ == "__main__":
    asyncio.run(test_full_travel_flow())

