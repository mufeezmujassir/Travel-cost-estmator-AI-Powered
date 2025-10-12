#!/usr/bin/env python3
"""
Test script to check SERP API flight responses for specific routes
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.serp_service import SerpService
from services.config import Settings

async def test_flight_search(origin, destination, departure_date):
    """Test flight search for a specific route"""
    print(f"\n{'='*60}")
    print(f"[TEST] SERP API for: {origin} -> {destination}")
    print(f"[DATE] Departure Date: {departure_date}")
    print(f"{'='*60}")
    
    # Load settings to get API key
    try:
        settings = Settings()
        if not settings.serp_api_key:
            print("[ERROR] SERP_API_KEY not found in settings")
            print("[INFO] Make sure your .env file has SERP_API_KEY configured")
            return
        print(f"[OK] SERP API Key loaded (length: {len(settings.serp_api_key)})")
    except Exception as e:
        print(f"[ERROR] Loading settings: {e}")
        return
    
    serp_service = SerpService(settings)
    
    try:
        # Search for flights
        flights = await serp_service.search_flights(origin, destination, departure_date, departure_date, 1)
        
        print(f"[RAW] Response:")
        print(json.dumps(flights, indent=2, default=str))
        
        if flights:
            print(f"\n[OK] Found {len(flights)} flights")
            for i, flight in enumerate(flights[:3], 1):  # Show first 3 flights
                print(f"\n[FLIGHT] {i}:")
                print(f"   Airline: {flight.get('airline', 'N/A')}")
                print(f"   Flight Number: {flight.get('flight_number', 'N/A')}")
                print(f"   Price: ${flight.get('price', 'N/A')}")
                print(f"   Class: {flight.get('class_type', 'N/A')}")
                print(f"   Duration: {flight.get('duration', 'N/A')}")
                print(f"   Departure: {flight.get('departure_time', 'N/A')}")
                print(f"   Arrival: {flight.get('arrival_time', 'N/A')}")
        else:
            print("[ERROR] No flights found")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Test multiple routes"""
    # Get departure date (7 days from now)
    departure_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Test routes
    routes = [
        ("MEL", "CMB", departure_date),  # Melbourne to Colombo
    ]
    
    for origin, destination, date in routes:
        await test_flight_search(origin, destination, date)
    
    print(f"\n{'='*60}")
    print("[DONE] Testing complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
