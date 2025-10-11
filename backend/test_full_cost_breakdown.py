"""
Full Cost Breakdown Test
Test Galle → Matara with all LLM-powered agents
"""

import asyncio
from datetime import datetime, timedelta
from models.travel_models import TravelRequest, VibeType
from agents.travel_orchestrator import TravelOrchestrator
from services.config import Settings


def print_section(title):
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print('=' * 70)


async def test_full_breakdown():
    print_section("TESTING: Full Cost Breakdown (Galle → Matara)")
    
    # Initialize
    settings = Settings()
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    
    # Create request
    start_date = datetime.now() + timedelta(days=30)
    return_date = start_date + timedelta(days=2)
    
    request = TravelRequest(
        origin="Galle",
        destination="Matara",
        start_date=start_date.strftime("%Y-%m-%d"),
        return_date=return_date.strftime("%Y-%m-%d"),
        travelers=3,
        vibe=VibeType.CULTURAL
    )
    
    print(f"\n📍 Route: {request.origin} → {request.destination}")
    print(f"📅 Dates: {request.start_date} to {request.return_date}")
    print(f"👥 Travelers: {request.travelers}")
    print(f"🎭 Vibe: {request.vibe.value}")
    
    # Process request
    print_section("PROCESSING REQUEST")
    response = await orchestrator.process_travel_request(request)
    
    # Display results
    print_section("TRAVEL TYPE ANALYSIS")
    print(f"Domestic Travel: {response.is_domestic_travel}")
    print(f"Distance: {response.travel_distance_km:.1f} km")
    
    print_section("TRANSPORTATION COSTS")
    if response.transportation:
        # Inter-city options
        inter_city = response.transportation.get("inter_city_options", [])
        print(f"\nInter-City Options: {len(inter_city)}")
        for i, option in enumerate(inter_city[:4], 1):
            cost = option.get('cost', option.get('cost_per_trip', 0))
            print(f"  {i}. {option.get('type', 'Unknown').upper()}")
            print(f"     Cost: ${cost:.2f} (one-way for all travelers)")
            print(f"     Duration: {option.get('duration', 'N/A')}")
        
        # Cost breakdown
        costs = response.transportation.get("cost_breakdown", {})
        print(f"\nTransportation Cost Breakdown:")
        print(f"  Inter-City (round-trip): ${costs.get('inter_city', 0):.2f}")
        print(f"  Local Transport: ${costs.get('local_transport', 0):.2f}")
        print(f"  Airport Transfers: ${costs.get('airport_transfer', 0):.2f}")
        print(f"  TOTAL: ${costs.get('total', 0):.2f}")
    
    print_section("ACCOMMODATION COSTS")
    if response.hotels and len(response.hotels) > 0:
        hotel = response.hotels[0]
        print(f"Hotel: {hotel.name}")
        print(f"Price per night: ${hotel.price_per_night:.2f}")
        
        trip_days = (return_date - start_date).days
        rooms_needed = (request.travelers + 1) // 2  # 2 travelers per room
        total_accommodation = hotel.price_per_night * trip_days * rooms_needed
        
        print(f"Trip duration: {trip_days} nights")
        print(f"Rooms needed: {rooms_needed} ({request.travelers} travelers, 2 per room)")
        print(f"Total accommodation: ${total_accommodation:.2f}")
    
    print_section("FOOD COSTS")
    print(f"Total Food Cost: ${response.cost_breakdown.food:.2f}")
    
    trip_days = (return_date - start_date).days
    daily_per_person = response.cost_breakdown.food / (trip_days * request.travelers)
    print(f"Daily per person: ${daily_per_person:.2f}")
    print(f"({trip_days} days × {request.travelers} travelers)")
    
    print_section("ACTIVITIES COSTS")
    print(f"Total Activities Cost: ${response.cost_breakdown.activities:.2f}")
    activities_daily_per_person = response.cost_breakdown.activities / (trip_days * request.travelers)
    print(f"Daily per person: ${activities_daily_per_person:.2f}")
    print(f"({trip_days} days × {request.travelers} travelers)")
    
    print_section("MISCELLANEOUS COSTS")
    print(f"Total Miscellaneous Cost: ${response.cost_breakdown.miscellaneous:.2f}")
    misc_daily_per_person = response.cost_breakdown.miscellaneous / (trip_days * request.travelers)
    print(f"Daily per person: ${misc_daily_per_person:.2f}")
    print(f"({trip_days} days × {request.travelers} travelers)")
    
    print_section("OVERALL COST BREAKDOWN")
    print(f"Flights:         ${response.cost_breakdown.flights:>8.2f}")
    print(f"Accommodation:   ${response.cost_breakdown.accommodation:>8.2f}")
    print(f"Transportation:  ${response.cost_breakdown.transportation:>8.2f}")
    print(f"Food:            ${response.cost_breakdown.food:>8.2f}")
    print(f"Activities:      ${response.cost_breakdown.activities:>8.2f}")
    print(f"Miscellaneous:   ${response.cost_breakdown.miscellaneous:>8.2f}")
    print(f"{'-' * 40}")
    print(f"TOTAL:           ${response.total_cost:>8.2f}")
    
    print_section("EXPECTED VALUES (Sri Lanka - Cultural)")
    print("\nFor Galle → Matara (3 travelers, 2 days):")
    print("\nExpected:")
    print(f"  Distance:        ~38-47 km")
    print(f"  Inter-City:      $2-4 (train/bus, round-trip for 3)")
    print(f"  Local Transport: $20-30 (2 days)")
    print(f"  Food:            $66-90 ($11-15/day/person)")
    print(f"  Activities:      $60-90 ($10-15/day/person)")
    print(f"  Miscellaneous:   $30-50 ($5-8/day/person)")
    print(f"  Accommodation:   $80-150 (budget hotels, 2 rooms × 2 nights)")
    print(f"  TOTAL:           ~$280-450")
    
    print_section("TEST COMPLETE")
    
    # Verify key values
    print("\nVERIFICATION:")
    
    checks = [
        ("Distance > 0", response.travel_distance_km > 0, response.travel_distance_km),
        ("Is Domestic", response.is_domestic_travel == True, response.is_domestic_travel),
        ("Transportation < $50", response.cost_breakdown.transportation < 50, response.cost_breakdown.transportation),
        ("Food $60-$120", 60 <= response.cost_breakdown.food <= 120, response.cost_breakdown.food),
        ("Activities $50-$120", 50 <= response.cost_breakdown.activities <= 120, response.cost_breakdown.activities),
        ("Miscellaneous $25-$60", 25 <= response.cost_breakdown.miscellaneous <= 60, response.cost_breakdown.miscellaneous),
        ("Total $280-$500", 280 <= response.total_cost <= 500, response.total_cost),
    ]
    
    for check_name, passed, value in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}: {value}")


if __name__ == "__main__":
    asyncio.run(test_full_breakdown())

