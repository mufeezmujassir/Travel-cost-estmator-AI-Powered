"""
Test the smart airport resolver with various cities
Including cities not in the manual map
"""

import asyncio
from services.airport_resolver import AirportResolver
from services.config import Settings

async def test_smart_resolver():
    print("=" * 80)
    print("🧠 TESTING SMART AIRPORT RESOLVER")
    print("=" * 80)
    print()
    
    settings = Settings()
    resolver = AirportResolver(settings.serp_api_key)
    
    # Test cases: (city, country, expected_airport)
    test_cases = [
        # Cities in manual map (should be instant)
        ("Galle", "Sri Lanka", "CMB"),
        ("Tokyo", "Japan", "HND"),
        ("New York", "USA", "JFK"),
        ("London", "UK", "LHR"),
        
        # Sri Lankan cities not in manual map
        ("Matara", "Sri Lanka", "CMB"),  # Should detect Sri Lanka → CMB
        ("Ella", "Sri Lanka", "CMB"),
        ("Sigiriya", "Sri Lanka", "CMB"),
        
        # Other cities that might not be in map
        ("Bali", "Indonesia", "DPS"),  # Should search for nearest
        ("Phuket", "Thailand", "HKT"),
        ("Kyoto", "Japan", "HND or KIX"),  # Could be either
        ("Maldives", None, "MLE"),
        
        # Airport codes (should return as-is)
        ("CMB", None, "CMB"),
        ("JFK", None, "JFK"),
        ("NYC", None, "JFK"),  # Metro code normalization
    ]
    
    print("Testing airport resolution for various cities:")
    print("-" * 80)
    
    results = []
    for city, country, expected in test_cases:
        code = await resolver.get_airport_code(city, country)
        status = "✅" if expected in code or code in expected else "⚠️"
        results.append((city, country, code, expected, status))
        print(f"{status} {city:20} ({country or 'N/A':15}) → {code:5} (expected: {expected})")
    
    print("-" * 80)
    print()
    
    # Statistics
    success = sum(1 for r in results if r[4] == "✅")
    total = len(results)
    print(f"📊 Success Rate: {success}/{total} ({success/total*100:.1f}%)")
    print()
    
    # Test caching
    print("Testing cache performance...")
    print("-" * 80)
    
    import time
    
    # First call (not cached)
    start = time.time()
    code1 = await resolver.get_airport_code("Galle")
    time1 = time.time() - start
    
    # Second call (should be cached)
    start = time.time()
    code2 = await resolver.get_airport_code("Galle")
    time2 = time.time() - start
    
    print(f"First call:  {time1*1000:.2f}ms → {code1}")
    print(f"Second call: {time2*1000:.2f}ms → {code2} (from cache)")
    print(f"Speed improvement: {time1/time2:.1f}x faster")
    print()
    
    print("=" * 80)
    print("✅ SMART RESOLVER TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_smart_resolver())

