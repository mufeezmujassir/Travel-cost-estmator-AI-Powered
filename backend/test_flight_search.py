"""
Test script to verify flight search functionality
Tests: Galle to Tokyo flight search with real data
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.flight_search_agent import FlightSearchAgent
from models.travel_models import TravelRequest, VibeType
from services.config import Settings

async def test_flight_search():
    """Test flight search from Galle to Tokyo"""
    
    print("=" * 80)
    print("✈️ TESTING FLIGHT SEARCH AGENT")
    print("=" * 80)
    print()
    
    # Load settings
    settings = Settings()
    
    # Create test request
    request = TravelRequest(
        origin="Galle",
        destination="Tokyo",
        start_date="2025-10-22",
        return_date="2025-10-27",
        travelers=2,
        budget=3000.0,
        vibe=VibeType.CULTURAL
    )
    
    print("📋 Test Parameters:")
    print(f"   Origin: {request.origin}")
    print(f"   Destination: {request.destination}")
    print(f"   Departure: {request.start_date}")
    print(f"   Return: {request.return_date}")
    print(f"   Travelers: {request.travelers}")
    print()
    
    # Initialize flight agent
    print("🔧 Initializing Flight Search Agent...")
    flight_agent = FlightSearchAgent(settings)
    await flight_agent.initialize()
    print("✅ Agent initialized")
    print()
    
    # Run flight search
    print("🔍 Searching for flights...")
    print("-" * 80)
    result = await flight_agent.process(request)
    print("-" * 80)
    print()
    
    # Display results
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    flights = result.get("flights", [])
    
    print(f"✅ SEARCH COMPLETE!")
    print(f"   Flights found: {len(flights)}")
    print()
    
    if flights:
        print("✈️ FLIGHT OPTIONS:")
        print("=" * 80)
        for i, flight in enumerate(flights, 1):
            print(f"\n{i}. {flight['airline']} {flight['flight_number']}")
            print(f"   📍 Route: {flight['departure_airport']} → {flight['arrival_airport']}")
            print(f"   🕐 Departure: {flight['departure_time']}")
            print(f"   🕐 Arrival: {flight['arrival_time']}")
            print(f"   ⏱️ Duration: {flight['duration']}")
            print(f"   💰 Price: ${flight['price']}/person")
            print(f"   🎫 Class: {flight.get('class_type', 'Economy')}")
            print(f"   🔄 Stops: {flight.get('stops', 0)}")
            
            # Check if it's sample data
            if flight['airline'] == 'SampleAir':
                print(f"   ⚠️ WARNING: This is FALLBACK data - real flights not found!")
            else:
                print(f"   ✅ Real flight data from SERP API")
            
            if flight.get('aircraft'):
                print(f"   ✈️ Aircraft: {flight['aircraft']}")
            
            print("-" * 80)
    else:
        print("⚠️ No flights found")
    
    print()
    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print()
    
    # Verdict
    has_real_flights = any(f['airline'] != 'SampleAir' for f in flights)
    if has_real_flights:
        print("🎉 SUCCESS: Real flight data retrieved!")
    else:
        print("❌ FAILURE: Only fallback data found - check SERP API configuration")

if __name__ == "__main__":
    asyncio.run(test_flight_search())

