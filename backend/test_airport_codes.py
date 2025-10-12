#!/usr/bin/env python3
"""
Test airport code resolution
"""

import os
import sys
import asyncio

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.config import Settings
from services.serp_service import SerpService

async def test_airport_codes():
    """Test airport code resolution for common routes"""
    
    settings = Settings()
    serp_service = SerpService(settings)
    
    test_cases = [
        "Melbourne", "Colombo", "Beijing", "Paris",
        "Galle", "India", "Mumbai", "Delhi", "New Delhi"
    ]
    
    print("=" * 60)
    print("AIRPORT CODE RESOLUTION TEST")
    print("=" * 60)
    
    for city in test_cases:
        try:
            code = await serp_service.get_airport_code(city)
            print(f"{city:15} -> {code}")
        except Exception as e:
            print(f"{city:15} -> ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_airport_codes())
