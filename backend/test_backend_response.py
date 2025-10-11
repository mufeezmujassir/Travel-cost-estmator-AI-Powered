"""
Test what the backend is actually returning
"""

import asyncio
from datetime import datetime

from agents.travel_orchestrator import TravelOrchestrator
from models.travel_models import TravelRequest, VibeType
from services.config import Settings


async def test_galle_matara():
    print("="*70)
    print("TESTING BACKEND RESPONSE")
    print("="*70)
    
    # Initialize
    settings = Settings()
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    
    # Create request
    request = TravelRequest(
        origin="Galle",
        destination="Matara",
        start_date="2025-10-22",
        return_date="2025-10-24",
        travelers=3,
        vibe=VibeType.CULTURAL
    )
    
    print(f"\n📍 Request: {request.origin} → {request.destination}")
    print(f"📅 Dates: {request.start_date} to {request.return_date}")
    print(f"👥 Travelers: {request.travelers}")
    
    # Process request
    print("\n" + "="*70)
    print("PROCESSING REQUEST...")
    print("="*70)
    
    response = await orchestrator.process_travel_request(request)
    
    print("\n" + "="*70)
    print("RESPONSE ANALYSIS:")
    print("="*70)
    
    # Check domestic travel detection
    print(f"\n🏠 Is Domestic Travel: {response.is_domestic_travel}")
    print(f"📏 Travel Distance: {response.travel_distance_km} km")
    
    # Check transportation data
    print(f"\n🚗 Transportation Data Available: {response.transportation is not None}")
    
    if response.transportation:
        print("\n📊 TRANSPORTATION BREAKDOWN:")
        print("-"*70)
        
        # Inter-city options
        inter_city = response.transportation.get("inter_city_transportation", [])
        print(f"\nInter-City Options: {len(inter_city)}")
        for i, option in enumerate(inter_city[:4], 1):
            cost = option.get('cost', option.get('cost_per_trip', 0))
            print(f"\n  {i}. {option.get('type', 'Unknown').upper()}")
            print(f"     Cost: ${cost:.2f}")
            print(f"     Duration: {option.get('duration', 'N/A')}")
            print(f"     Distance: {option.get('distance_km', 0)} km")
        
        # Local transportation
        local = response.transportation.get("local_transportation", {})
        if local:
            print(f"\nLocal Transportation:")
            print(f"  Daily Cost: ${local.get('cost_per_day', 0)}")
            print(f"  Options: {local.get('options', [])}")
        
        # Cost breakdown
        costs = response.transportation.get("costs", {})
        if costs:
            print(f"\n💰 COST BREAKDOWN:")
            print(f"  Inter-City: ${costs.get('inter_city_transportation', 0):.2f}")
            print(f"  Local: ${costs.get('local_transportation', 0):.2f}")
            print(f"  Total: ${costs.get('total', 0):.2f}")
            print(f"  Per Person: ${costs.get('cost_per_person', 0):.2f}")
    
    # Check cost breakdown from cost estimation agent
    print(f"\n💵 COST ESTIMATION:")
    print("-"*70)
    print(f"Transportation: ${response.cost_breakdown.transportation:.2f}")
    print(f"Accommodation: ${response.cost_breakdown.accommodation:.2f}")
    print(f"Food: ${response.cost_breakdown.food:.2f}")
    print(f"Activities: ${response.cost_breakdown.activities:.2f}")
    print(f"Miscellaneous: ${response.cost_breakdown.miscellaneous:.2f}")
    print(f"TOTAL: ${response.total_cost:.2f}")
    print(f"Per Person: ${response.total_cost / request.travelers:.2f}")
    
    print("\n" + "="*70)
    print("ISSUES TO FIX:")
    print("="*70)
    
    issues = []
    
    # Check distance
    if response.travel_distance_km == 0:
        issues.append("❌ Distance is 0 km (should be ~47 km)")
    else:
        print(f"✓ Distance: {response.travel_distance_km} km")
    
    # Check inter-city cost
    if response.transportation:
        inter_city_cost = response.transportation.get("costs", {}).get("inter_city_transportation", 0)
        if inter_city_cost > 10:
            issues.append(f"❌ Inter-city cost ${inter_city_cost:.2f} seems high (should be ~$2.58)")
        else:
            print(f"✓ Inter-city cost: ${inter_city_cost:.2f}")
        
        # Check local cost
        local_cost = response.transportation.get("costs", {}).get("local_transportation", 0)
        if local_cost > 50:
            issues.append(f"⚠️ Local cost ${local_cost:.2f} seems high (should be ~$30-40)")
        else:
            print(f"✓ Local cost: ${local_cost:.2f}")
    
    if issues:
        print("\n" + "\n".join(issues))
    else:
        print("\n✅ All checks passed!")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(test_galle_matara())

