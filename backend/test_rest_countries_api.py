"""
Test script to check REST Countries API connectivity
"""

import asyncio
import httpx
from services.domestic_travel_analyzer import DynamicTransportationAnalyzer
from services.config import Settings


async def test_rest_countries_api():
    """Test REST Countries API connectivity"""
    print("🌍 Testing REST Countries API...")
    print("="*60)
    
    # Test countries
    test_countries = [
        "Sri Lanka",
        "India", 
        "United States",
        "Japan",
        "China",
        "Germany",
        "Brazil",
        "Australia"
    ]
    
    # Initialize the analyzer
    settings = Settings()
    analyzer = DynamicTransportationAnalyzer(settings)
    
    # Test each country
    for country in test_countries:
        print(f"\n🏙️ Testing: {country}")
        try:
            # Test direct API call
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://restcountries.com/v3.1/name/{country}",
                    params={"fullText": "false"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        country_data = data[0]
                        area = country_data.get("area", 0)
                        population = country_data.get("population", 0)
                        region = country_data.get("region", "Unknown")
                        
                        print(f"   ✅ API Response: {response.status_code}")
                        print(f"   📊 Area: {area:,} km²")
                        print(f"   👥 Population: {population:,}")
                        print(f"   🌍 Region: {region}")
                        
                        # Test our analyzer
                        strategy = await analyzer.get_country_transportation_strategy(country)
                        print(f"   🚗 Max Ground Distance: {strategy['max_ground_distance_km']:.0f} km")
                        print(f"   🛤️ Preferred Transport: {', '.join(strategy['preferred_transport'])}")
                    else:
                        print(f"   ❌ No data returned")
                else:
                    print(f"   ❌ API Error: {response.status_code}")
                    print(f"   📄 Response: {response.text[:200]}")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_direct_api_calls():
    """Test direct API calls to see what's happening"""
    print("\n🔧 Testing Direct API Calls...")
    print("="*60)
    
    test_cases = [
        "Sri Lanka",
        "sri lanka", 
        "LKA",  # ISO code
        "india",
        "united states"
    ]
    
    for query in test_cases:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Try different endpoints
                endpoints = [
                    f"https://restcountries.com/v3.1/name/{query}",
                    f"https://restcountries.com/v3.1/name/{query}?fullText=true",
                    f"https://restcountries.com/v3.1/alpha/{query.upper()}" if len(query) == 3 else None
                ]
                
                for i, endpoint in enumerate(endpoints):
                    if endpoint:
                        print(f"   📡 Endpoint {i+1}: {endpoint}")
                        try:
                            response = await client.get(endpoint)
                            print(f"      Status: {response.status_code}")
                            
                            if response.status_code == 200:
                                data = response.json()
                                if data and len(data) > 0:
                                    country = data[0]
                                    name = country.get("name", {}).get("common", "Unknown")
                                    area = country.get("area", 0)
                                    print(f"      ✅ Found: {name} ({area:,} km²)")
                                    break
                                else:
                                    print(f"      ⚠️ Empty response")
                            else:
                                print(f"      ❌ Error: {response.status_code}")
                                if response.status_code == 404:
                                    print(f"      📄 Response: {response.text[:100]}")
                        except Exception as e:
                            print(f"      ❌ Exception: {e}")
        except Exception as e:
            print(f"   ❌ Overall error: {e}")


async def test_network_connectivity():
    """Test basic network connectivity"""
    print("\n🌐 Testing Network Connectivity...")
    print("="*60)
    
    test_urls = [
        "https://restcountries.com/v3.1/all",
        "https://restcountries.com/v3.1/name/india",
        "https://httpbin.org/get",  # Simple test endpoint
        "https://nominatim.openstreetmap.org/search?q=london&format=json&limit=1"
    ]
    
    for url in test_urls:
        print(f"\n🔗 Testing: {url}")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                print(f"   ✅ Status: {response.status_code}")
                if response.status_code == 200:
                    data_length = len(response.content)
                    print(f"   📊 Response size: {data_length} bytes")
                else:
                    print(f"   ⚠️ Non-200 status")
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def run_all_tests():
    """Run all tests"""
    print("🧪 REST Countries API Test Suite")
    print("="*60)
    
    await test_network_connectivity()
    await test_direct_api_calls()
    await test_rest_countries_api()
    
    print("\n" + "="*60)
    print("🏁 All tests completed!")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
