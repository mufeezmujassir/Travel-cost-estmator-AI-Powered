"""
Test cases for intelligent domestic travel detection
"""

import asyncio
from models.travel_models import TravelRequest, VibeType
from agents.travel_orchestrator import TravelOrchestrator
from services.config import Settings
from services.domestic_travel_analyzer import DynamicTransportationAnalyzer, TransportationStrategyCache
from services.distance_calculator import DistanceCalculator
from services.airport_resolver import AirportResolver


async def test_same_airport_domestic():
    """Test Case 1: Same airport (Galle to Colombo) - Should skip flight search"""
    print("\n" + "="*80)
    print("TEST 1: Same Airport Domestic Travel (Galle → Colombo)")
    print("="*80)
    
    request = TravelRequest(
        origin="Galle",
        destination="Colombo",
        start_date="2024-12-01",
        return_date="2024-12-05",
        travelers=2,
        budget=1000,
        vibe=VibeType.BEACH
    )
    
    settings = Settings()
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    
    print(f"\n📋 Request: {request.origin} → {request.destination}")
    print(f"   Travelers: {request.travelers}")
    print(f"   Duration: {request.start_date} to {request.return_date}")
    
    try:
        response = await orchestrator.process_travel_request(request)
        
        print(f"\n✅ Test Result:")
        print(f"   Flights Found: {len(response.flights)}")
        print(f"   Hotels Found: {len(response.hotels)}")
        print(f"   Total Cost: ${response.total_cost:.2f}")
        
        if len(response.flights) == 0:
            print(f"   ✅ PASS: Flight search was skipped (as expected for same airport)")
        else:
            print(f"   ⚠️ UNEXPECTED: Flights were included")
        
        return response
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_short_domestic_sri_lanka():
    """Test Case 2: Short domestic travel within Sri Lanka (Kandy to Galle)"""
    print("\n" + "="*80)
    print("TEST 2: Short Domestic Travel within Sri Lanka (Kandy → Galle)")
    print("="*80)
    
    request = TravelRequest(
        origin="Kandy",
        destination="Galle",
        start_date="2024-12-10",
        return_date="2024-12-15",
        travelers=2,
        budget=800,
        vibe=VibeType.CULTURAL
    )
    
    settings = Settings()
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    
    print(f"\n📋 Request: {request.origin} → {request.destination}")
    
    try:
        response = await orchestrator.process_travel_request(request)
        
        print(f"\n✅ Test Result:")
        print(f"   Flights Found: {len(response.flights)}")
        print(f"   Total Cost: ${response.total_cost:.2f}")
        
        # Both resolve to CMB, so flight search should be skipped
        if len(response.flights) == 0:
            print(f"   ✅ PASS: Flight search was skipped (small country, same airport)")
        else:
            print(f"   ⚠️ Note: Flights were included")
        
        return response
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


async def test_long_domestic_india():
    """Test Case 3: Long domestic travel in India (Delhi to Mumbai) - Should include flights"""
    print("\n" + "="*80)
    print("TEST 3: Long Domestic Travel in India (Delhi → Mumbai)")
    print("="*80)
    
    request = TravelRequest(
        origin="Delhi",
        destination="Mumbai",
        start_date="2025-01-15",
        return_date="2025-01-22",
        travelers=2,
        budget=2000,
        vibe=VibeType.ADVENTURE
    )
    
    settings = Settings()
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    
    print(f"\n📋 Request: {request.origin} → {request.destination}")
    
    try:
        response = await orchestrator.process_travel_request(request)
        
        print(f"\n✅ Test Result:")
        print(f"   Flights Found: {len(response.flights)}")
        print(f"   Total Cost: ${response.total_cost:.2f}")
        
        # Distance ~1400 km, should include flights
        if len(response.flights) > 0:
            print(f"   ✅ PASS: Flights were included (long distance domestic)")
        else:
            print(f"   ⚠️ UNEXPECTED: Flight search was skipped")
        
        return response
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


async def test_international_travel():
    """Test Case 4: International travel (Tokyo to New York) - Should include flights"""
    print("\n" + "="*80)
    print("TEST 4: International Travel (Tokyo → New York)")
    print("="*80)
    
    request = TravelRequest(
        origin="Tokyo",
        destination="New York",
        start_date="2025-02-01",
        return_date="2025-02-10",
        travelers=2,
        budget=5000,
        vibe=VibeType.ADVENTURE
    )
    
    settings = Settings()
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    
    print(f"\n📋 Request: {request.origin} → {request.destination}")
    
    try:
        response = await orchestrator.process_travel_request(request)
        
        print(f"\n✅ Test Result:")
        print(f"   Flights Found: {len(response.flights)}")
        print(f"   Total Cost: ${response.total_cost:.2f}")
        
        # International travel, should always include flights
        if len(response.flights) > 0:
            print(f"   ✅ PASS: Flights were included (international travel)")
        else:
            print(f"   ⚠️ UNEXPECTED: Flight search was skipped")
        
        return response
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


async def test_country_strategy():
    """Test Case 5: Test dynamic country transportation strategy"""
    print("\n" + "="*80)
    print("TEST 5: Dynamic Country Transportation Strategy")
    print("="*80)
    
    settings = Settings()
    cache = TransportationStrategyCache()
    
    # Test different countries
    countries = ["Sri Lanka", "India", "United States", "Japan", "China"]
    
    for country in countries:
        print(f"\n🌍 Testing strategy for: {country}")
        try:
            strategy = await cache.get_strategy(country, settings)
            print(f"   Size Category: {strategy.get('country_size_category')}")
            print(f"   Max Ground Distance: {strategy.get('max_ground_distance_km')} km")
            print(f"   Preferred Transport: {', '.join(strategy.get('preferred_transport', []))}")
            print(f"   Infrastructure Score: {strategy.get('infrastructure_score')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_distance_calculation():
    """Test Case 6: Test distance calculation between cities"""
    print("\n" + "="*80)
    print("TEST 6: Distance Calculation")
    print("="*80)
    
    calculator = DistanceCalculator()
    
    test_routes = [
        ("Galle", "Colombo"),
        ("Delhi", "Mumbai"),
        ("Tokyo", "Osaka"),
        ("New York", "Los Angeles")
    ]
    
    for origin, destination in test_routes:
        print(f"\n📏 Calculating: {origin} → {destination}")
        try:
            distance = await calculator.calculate_distance(origin, destination)
            if distance:
                print(f"   Distance: {distance:.1f} km")
            else:
                print(f"   ⚠️ Could not calculate distance")
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_airport_resolver():
    """Test Case 7: Test airport and country detection"""
    print("\n" + "="*80)
    print("TEST 7: Airport and Country Detection")
    print("="*80)
    
    settings = Settings()
    resolver = AirportResolver(settings.serp_api_key)
    
    test_cities = [
        "Galle", "Colombo", "Kandy",
        "Delhi", "Mumbai",
        "Tokyo", "New York"
    ]
    
    for city in test_cities:
        print(f"\n🏙️ Testing: {city}")
        try:
            airport = await resolver.get_airport_code(city)
            country = await resolver.get_country_for_city(city)
            print(f"   Airport: {airport}")
            print(f"   Country: {country}")
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def run_all_tests():
    """Run all test cases"""
    print("\n" + "🧪" * 40)
    print("INTELLIGENT DOMESTIC TRAVEL DETECTION - TEST SUITE")
    print("🧪" * 40)
    
    # Run individual tests
    await test_same_airport_domestic()
    await test_short_domestic_sri_lanka()
    await test_long_domestic_india()
    await test_international_travel()
    await test_country_strategy()
    await test_distance_calculation()
    await test_airport_resolver()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(run_all_tests())

