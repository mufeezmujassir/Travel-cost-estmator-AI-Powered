"""
Test Suitability Scoring System
Verify scoring logic and API integration
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.suitability_scorer import SuitabilityScorer
from services.weather_service import WeatherService
from services.region_mapper import RegionMapper

async def test_region_mapper():
    """Test region mapping functionality"""
    print("=" * 60)
    print("🗺️  TESTING REGION MAPPER")
    print("=" * 60)
    
    mapper = RegionMapper()
    
    test_destinations = [
        "Tokyo",
        "Bangkok", 
        "Paris",
        "New York",
        "Sydney",
        "Rio de Janeiro"
    ]
    
    for dest in test_destinations:
        print(f"\n📍 Testing: {dest}")
        try:
            info = await mapper.get_destination_info(dest)
            print(f"   Region: {info['region']}")
            print(f"   Climate: {info['climate_zone']}")
            print(f"   Hemisphere: {info['hemisphere']}")
            if info['coordinates']:
                print(f"   Coordinates: {info['coordinates'][0]:.2f}, {info['coordinates'][1]:.2f}")
            
            # Test events lookup
            events = mapper.get_events_for_destination(info, 3)  # March
            print(f"   March events: {len(events)} found")
            if events:
                print(f"   Sample: {events[0]['description']}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_weather_service():
    """Test weather service functionality"""
    print("\n" + "=" * 60)
    print("🌤️  TESTING WEATHER SERVICE")
    print("=" * 60)
    
    weather_service = WeatherService()
    
    # Test coordinates for different regions
    test_locations = [
        ("Tokyo", 35.6762, 139.6503),
        ("Bangkok", 13.7563, 100.5018),
        ("Paris", 48.8566, 2.3522),
        ("New York", 40.7128, -74.0060)
    ]
    
    for name, lat, lon in test_locations:
        print(f"\n🌡️  Testing: {name} ({lat}, {lon})")
        try:
            # Test March climate
            climate = await weather_service.get_climate_normals(lat, lon, 3)
            print(f"   March avg temp: {climate['avg_temperature']:.1f}°C")
            print(f"   March avg precip: {climate['avg_precipitation']:.1f}mm")
            print(f"   March avg humidity: {climate['avg_humidity']:.0f}%")
            
            # Test comfort scoring for different vibes
            for vibe in ["beach", "adventure", "romantic"]:
                comfort = weather_service.score_weather_comfort(climate, vibe)
                print(f"   {vibe} comfort: {comfort['overall_score']:.1f}/100")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_suitability_scorer():
    """Test complete suitability scoring"""
    print("\n" + "=" * 60)
    print("🎯 TESTING SUITABILITY SCORER")
    print("=" * 60)
    
    scorer = SuitabilityScorer()  # No SERP service for testing
    
    test_cases = [
        {
            "vibe": "beach",
            "destination": "Bangkok",
            "start_date": "2025-03-15",
            "duration": 7,
            "description": "Beach vibe in Bangkok during March (dry season)"
        },
        {
            "vibe": "adventure", 
            "destination": "Tokyo",
            "start_date": "2025-06-15",
            "duration": 5,
            "description": "Adventure vibe in Tokyo during June (rainy season)"
        },
        {
            "vibe": "romantic",
            "destination": "Paris",
            "start_date": "2025-04-15", 
            "duration": 4,
            "description": "Romantic vibe in Paris during April (spring)"
        },
        {
            "vibe": "cultural",
            "destination": "New York",
            "start_date": "2025-12-15",
            "duration": 6,
            "description": "Cultural vibe in NYC during December (winter/holidays)"
        }
    ]
    
    for case in test_cases:
        print(f"\n🎯 Testing: {case['description']}")
        try:
            result = await scorer.calculate_suitability_score(
                vibe=case["vibe"],
                destination=case["destination"],
                start_date=case["start_date"],
                duration_days=case["duration"]
            )
            
            print(f"   Overall Score: {result['score']}/100")
            print(f"   Label: {result['label']}")
            print(f"   Reason: {result['reason']}")
            
            details = result['details']
            print(f"   Weather: {details['weather_score']}/100 - {details['weather_summary']}")
            print(f"   Crowd: {details['crowd_score']}/100 - {details['crowd_summary']}")
            print(f"   Events: {details['events_summary']}")
            
            breakdown = details['breakdown']
            print(f"   Breakdown: W:{breakdown['weather']:.1f} C:{breakdown['crowd']:.1f} E:{breakdown['events']:.1f} S:{breakdown['seasonality']:.1f}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 60)
    print("⚠️  TESTING EDGE CASES")
    print("=" * 60)
    
    scorer = SuitabilityScorer()
    
    edge_cases = [
        {
            "vibe": "invalid_vibe",
            "destination": "NonexistentCity12345",
            "start_date": "2025-03-15",
            "duration": 5,
            "description": "Invalid vibe and non-existent city"
        },
        {
            "vibe": "beach",
            "destination": "Antarctica",
            "start_date": "2025-03-15", 
            "duration": 5,
            "description": "Extreme location (Antarctica)"
        },
        {
            "vibe": "adventure",
            "destination": "Tokyo",
            "start_date": "invalid-date",
            "duration": 5,
            "description": "Invalid date format"
        }
    ]
    
    for case in edge_cases:
        print(f"\n⚠️  Testing: {case['description']}")
        try:
            result = await scorer.calculate_suitability_score(
                vibe=case["vibe"],
                destination=case["destination"],
                start_date=case["start_date"],
                duration_days=case["duration"]
            )
            
            print(f"   Result: {result['score']}/100 - {result['label']}")
            print(f"   Reason: {result['reason']}")
            
        except Exception as e:
            print(f"   ❌ Expected error: {e}")

async def main():
    """Run all tests"""
    print("🧪 SUITABILITY SCORING SYSTEM TESTS")
    print("=" * 80)
    
    try:
        await test_region_mapper()
        await test_weather_service()
        await test_suitability_scorer()
        await test_edge_cases()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
