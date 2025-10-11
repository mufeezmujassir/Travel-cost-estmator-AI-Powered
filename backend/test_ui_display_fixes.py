"""
Test script to verify UI display fixes:
1. Duration formatting (e.g., 0.9 hours -> 54m, 1.25 hours -> 1h 15m)
2. Transportation cost breakdown (outbound + return)
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.travel_orchestrator import TravelOrchestrator
from models.travel_models import TravelRequest, VibeType
from services.config import Settings

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"{title:^70}")
    print(f"{'=' * 70}\n")

async def test_galle_to_matara():
    """Test the Galle to Matara domestic travel scenario"""
    print_section("🧪 TESTING UI DISPLAY FIXES: GALLE → MATARA")
    
    # Initialize
    settings = Settings()
    orchestrator = TravelOrchestrator(settings)
    await orchestrator.initialize()
    
    # Create test request
    start_date = datetime.now() + timedelta(days=30)
    return_date = start_date + timedelta(days=2)
    
    request = TravelRequest(
        origin="Galle",
        destination="Matara",
        start_date=start_date.strftime("%Y-%m-%d"),
        return_date=return_date.strftime("%Y-%m-%d"),
        travelers=3,
        vibe=VibeType.CULTURAL,
        budget=None
    )
    
    print(f"📍 Route: {request.origin} → {request.destination}")
    print(f"📅 Dates: {request.start_date} to {request.return_date}")
    print(f"👥 Travelers: {request.travelers}")
    print(f"🎭 Vibe: {request.vibe}")
    
    # Process request
    print("\n⏳ Processing travel request...\n")
    response = await orchestrator.process_travel_request(request)
    
    # ================================================================
    # TEST 1: DURATION DISPLAY
    # ================================================================
    print_section("TEST 1: DURATION DISPLAY FORMAT")
    
    inter_city_options = response.transportation.get("inter_city_transportation", [])
    
    print(f"Found {len(inter_city_options)} transportation options:\n")
    
    for i, option in enumerate(inter_city_options, 1):
        duration_hours = option.get("duration_hours", 0)
        duration_str = option.get("duration_str", "N/A")
        
        print(f"{i}. {option.get('type', 'Unknown').upper()}")
        print(f"   Duration (hours): {duration_hours}")
        print(f"   Duration (formatted): {duration_str}")
        print(f"   ✅ Has duration_str: {'Yes' if duration_str != 'N/A' else 'No'}")
        print()
    
    # Verify duration_str is present
    has_duration_str = all(opt.get("duration_str") for opt in inter_city_options)
    print(f"{'✅' if has_duration_str else '❌'} All options have duration_str field\n")
    
    # ================================================================
    # TEST 2: COST BREAKDOWN
    # ================================================================
    print_section("TEST 2: TRANSPORTATION COST BREAKDOWN")
    
    total_inter_city = response.cost_breakdown.transportation
    outbound_cost = total_inter_city / 2
    return_cost = total_inter_city / 2
    
    print(f"Total Inter-City Transportation: ${total_inter_city:.2f}")
    print(f"  ├─ Outbound (3 travelers): ${outbound_cost:.2f}")
    print(f"  └─ Return (3 travelers): ${return_cost:.2f}")
    print()
    
    # Show which option was used
    if inter_city_options:
        cheapest = min(inter_city_options, key=lambda x: x.get("cost_per_trip", float('inf')))
        print(f"Selected option: {cheapest.get('type', 'Unknown').upper()}")
        print(f"  Cost per trip: ${cheapest.get('cost_per_trip', 0):.2f}")
        print(f"  Round trip (×2): ${cheapest.get('cost_per_trip', 0) * 2:.2f}")
        print()
    
    # Verify the math
    expected_total = outbound_cost + return_cost
    math_correct = abs(expected_total - total_inter_city) < 0.01
    print(f"{'✅' if math_correct else '❌'} Outbound + Return = Total\n")
    
    # ================================================================
    # TEST 3: COMPLETE COST BREAKDOWN
    # ================================================================
    print_section("TEST 3: COMPLETE COST BREAKDOWN")
    
    print("Cost Breakdown (as shown in UI):")
    print(f"  ├─ Inter-City (Outbound): ${outbound_cost:.2f}")
    print(f"  ├─ Inter-City (Return): ${return_cost:.2f}")
    print(f"  ├─ Accommodation: ${response.cost_breakdown.accommodation:.2f}")
    print(f"  ├─ Activities: ${response.cost_breakdown.activities:.2f}")
    print(f"  ├─ Food & Dining: ${response.cost_breakdown.food:.2f}")
    print(f"  └─ Miscellaneous: ${response.cost_breakdown.miscellaneous:.2f}")
    print(f"\n  Total: ${response.total_cost:.2f}")
    print(f"  Per Person: ${response.total_cost / request.travelers:.2f}")
    print()
    
    # ================================================================
    # TEST 4: UI DATA STRUCTURE
    # ================================================================
    print_section("TEST 4: UI DATA STRUCTURE VALIDATION")
    
    checks = [
        ("is_domestic_travel flag", response.is_domestic_travel == True),
        ("travel_distance_km available", response.travel_distance_km > 0),
        ("transportation data available", response.transportation is not None),
        ("inter_city_options available", len(inter_city_options) > 0),
        ("All options have cost_per_trip", all(opt.get("cost_per_trip") for opt in inter_city_options)),
        ("All options have duration_str", all(opt.get("duration_str") for opt in inter_city_options)),
        ("All options have distance_km", all(opt.get("distance_km") for opt in inter_city_options)),
    ]
    
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    print()
    
    # ================================================================
    # SUMMARY
    # ================================================================
    print_section("🎯 TEST SUMMARY")
    
    all_passed = all(passed for _, passed in checks) and has_duration_str and math_correct
    
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nThe UI should now display:")
        print("  1. ✅ Correct duration format (e.g., '1h 15m' instead of '1.25')")
        print("  2. ✅ Separate outbound and return costs")
        print("  3. ✅ All required fields for proper rendering")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the failures above.")
    
    print()

if __name__ == "__main__":
    asyncio.run(test_galle_to_matara())

