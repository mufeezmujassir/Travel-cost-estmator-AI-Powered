"""
Test script to verify hotel search functionality
Tests: Galle to Tokyo hotel search
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.hotel_search_agent import HotelSearchAgent
from models.travel_models import TravelRequest, VibeType
from services.config import Settings

async def test_hotel_search():
    """Test hotel search from Galle to Tokyo"""
    
    print("=" * 80)
    print("🏨 TESTING HOTEL SEARCH AGENT")
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
    print(f"   Check-in: {request.start_date}")
    print(f"   Check-out: {request.return_date}")
    print(f"   Travelers: {request.travelers}")
    print(f"   Vibe: {request.vibe.value}")
    print()
    
    # Initialize hotel agent
    print("🔧 Initializing Hotel Search Agent...")
    hotel_agent = HotelSearchAgent(settings)
    await hotel_agent.initialize()
    print("✅ Agent initialized")
    print()
    
    # Run hotel search
    print("🔍 Searching for hotels in Tokyo...")
    print("-" * 80)
    result = await hotel_agent.process(request)
    print("-" * 80)
    print()
    
    # Display results
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    hotels = result.get("hotels", [])
    total_found = result.get("total_options_found", 0)
    
    print(f"✅ SEARCH COMPLETE!")
    print(f"   Total hotels found: {total_found}")
    print(f"   Hotels shown: {len(hotels)}")
    print()
    
    if hotels:
        print("🏨 TOP HOTELS:")
        print("=" * 80)
        for i, hotel in enumerate(hotels, 1):
            print(f"\n{i}. {hotel['name']}")
            print(f"   📍 Location: {hotel['location']}")
            print(f"   💰 Price: ${hotel['price_per_night']}/night")
            print(f"   ⭐ Rating: {hotel['rating']}/5.0")
            
            # Price confidence indicator
            confidence = hotel.get('price_confidence', 'high')
            confidence_emoji = "✅" if confidence == "high" else "⚠️"
            print(f"   {confidence_emoji} Price confidence: {confidence}")
            
            # Data source
            source = hotel.get('data_source', 'unknown')
            print(f"   📊 Data source: {source}")
            
            # Amenities
            amenities = hotel.get('amenities', [])
            if amenities:
                amenities_str = ', '.join(amenities[:5])
                if len(amenities) > 5:
                    amenities_str += f" (+{len(amenities)-5} more)"
                print(f"   🏊 Amenities: {amenities_str}")
            
            # Description
            desc = hotel.get('description', '')
            if desc:
                desc_short = desc[:100] + "..." if len(desc) > 100 else desc
                print(f"   📝 {desc_short}")
            
            print("-" * 80)
    else:
        print("⚠️ No hotels found")
    
    # Vibe analysis
    vibe_analysis = result.get("vibe_analysis", {})
    if vibe_analysis:
        print("\n🎭 VIBE ANALYSIS:")
        print(f"   Selected vibe: {vibe_analysis.get('vibe', 'N/A')}")
        criteria = vibe_analysis.get('hotel_criteria', {})
        if criteria:
            print(f"   Preferred amenities: {', '.join(criteria.get('amenities', []))}")
            print(f"   Preferred location: {criteria.get('location', 'N/A')}")
            print(f"   Atmosphere: {criteria.get('atmosphere', 'N/A')}")
    
    print()
    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_hotel_search())

