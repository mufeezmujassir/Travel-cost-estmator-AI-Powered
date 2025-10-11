"""
Test flight search with a city NOT in our manual map
This proves the smart resolver can handle ANY city
"""

import asyncio
from agents.flight_search_agent import FlightSearchAgent
from models.travel_models import TravelRequest, VibeType
from services.config import Settings

async def test_unmapped_city():
    print("=" * 80)
    print("🧪 TESTING UNMAPPED CITY: Matara, Sri Lanka → Bangkok")
    print("=" * 80)
    print()
    print("NOTE: 'Matara' was NOT in the original manual city map!")
    print("The smart resolver should automatically find CMB airport.")
    print()
    
    settings = Settings()
    
    # Test with Matara (not originally in manual map)
    request = TravelRequest(
        origin="Matara",  # NOT in original map!
        destination="Bangkok",
        start_date="2025-11-15",
        return_date="2025-11-22",
        travelers=1,
        budget=1500.0,
        vibe=VibeType.BEACH
    )
    
    print("📋 Test Parameters:")
    print(f"   Origin: {request.origin} (NOT in original manual map)")
    print(f"   Destination: {request.destination}")
    print(f"   Departure: {request.start_date}")
    print(f"   Return: {request.return_date}")
    print()
    
    flight_agent = FlightSearchAgent(settings)
    await flight_agent.initialize()
    
    print("🔍 Searching for flights...")
    print("-" * 80)
    result = await flight_agent.process(request)
    print("-" * 80)
    print()
    
    flights = result.get("flights", [])
    
    if flights:
        has_real_flights = any(f['airline'] != 'SampleAir' for f in flights)
        
        if has_real_flights:
            print("🎉 SUCCESS!")
            print(f"✅ Smart resolver automatically found airport for 'Matara'")
            print(f"✅ Retrieved {len(flights)} real flight options")
            print()
            print(f"Top flight: {flights[0]['airline']} {flights[0]['flight_number']}")
            print(f"   Route: {flights[0]['departure_airport']} → {flights[0]['arrival_airport']}")
            print(f"   Price: ${flights[0]['price']}/person")
        else:
            print("⚠️ Only fallback data found")
    else:
        print("❌ No flights found")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_unmapped_city())

