"""
Test Price Calendar Feature - Similar to Google Flights
Shows users which dates are cheaper/more expensive
"""

import asyncio
from agents.flight_search_agent import FlightSearchAgent
from models.travel_models import TravelRequest, VibeType
from services.config import Settings

async def test_price_calendar():
    print("=" * 80)
    print("📊 TESTING PRICE CALENDAR FEATURE (Like Google Flights)")
    print("=" * 80)
    print()
    
    settings = Settings()
    
    # Test request
    request = TravelRequest(
        origin="Galle",
        destination="Tokyo",
        start_date="2025-10-22",
        return_date="2025-10-27",
        travelers=2,
        budget=3000.0,
        vibe=VibeType.CULTURAL
    )
    
    print("📋 Search Parameters:")
    print(f"   Route: {request.origin} → {request.destination}")
    print(f"   Target dates: {request.start_date} to {request.return_date}")
    print(f"   Travelers: {request.travelers}")
    print()
    
    # Initialize agent
    flight_agent = FlightSearchAgent(settings)
    await flight_agent.initialize()
    
    # Get flight results WITH price calendar
    print("🔍 Searching flights with price trend analysis...")
    print("-" * 80)
    
    result = await flight_agent.process(
        request, 
        context={"include_price_trends": True}  # Enable price calendar
    )
    
    print("-" * 80)
    print()
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    # Display regular flight results
    flights = result.get("flights", [])
    print(f"✈️ FLIGHT OPTIONS FOR YOUR DATES:")
    print("=" * 80)
    
    if flights:
        for i, flight in enumerate(flights[:3], 1):
            print(f"\n{i}. {flight['airline']} {flight['flight_number']}")
            print(f"   💰 Price: ${flight['price']:.0f} for {request.travelers} travelers")
            print(f"   🛫 {flight['departure_airport']} → {flight['arrival_airport']}")
            print(f"   ⏱️ Duration: {flight['duration']}")
    
    print("\n" + "=" * 80)
    print()
    
    # Display price trend analysis
    if "price_trends" in result:
        trends = result["price_trends"]
        
        if trends.get("status") == "success":
            print("📊 PRICE CALENDAR ANALYSIS")
            print("=" * 80)
            print()
            
            # Statistics
            stats = trends["statistics"]
            print("📈 Price Statistics:")
            print(f"   Lowest price:  ${stats['min_price']:.0f}")
            print(f"   Highest price: ${stats['max_price']:.0f}")
            print(f"   Average price: ${stats['average_price']:.0f}")
            print(f"   Your date:     ${trends.get('target_price', 0):.0f}")
            print()
            
            # Recommendations
            print("💡 RECOMMENDATIONS:")
            print("-" * 80)
            for i, rec in enumerate(trends.get("recommendations", []), 1):
                print(f"{i}. {rec}")
            print()
            
            # Price grid (calendar view)
            print("📅 PRICE CALENDAR (±7 days from your date):")
            print("-" * 80)
            
            price_grid = trends.get("price_grid", [])
            
            # Print header
            print(f"{'Date':<12} {'Day':<10} {'Price':<10} {'Category':<12} {'Savings'}")
            print("-" * 80)
            
            # Print each date
            for item in price_grid:
                emoji = "💚" if item["is_cheap"] else ("🔴" if item["is_expensive"] else "💛")
                
                savings_text = ""
                if item["savings"] > 0:
                    savings_text = f"+${item['savings']:.0f} cheaper"
                elif item["savings"] < 0:
                    savings_text = f"${abs(item['savings']):.0f} more"
                else:
                    savings_text = "average"
                
                # Highlight target date
                date_str = item["date"]
                if item["date"] == request.start_date:
                    date_str = f"➤ {date_str}"
                
                print(f"{date_str:<12} {item['day_of_week']:<10} ${item['price']:<9.0f} {emoji} {item['category']:<10} {savings_text}")
            
            print("-" * 80)
            print()
            
            # Cheapest option highlight
            cheapest = trends.get("cheapest_option", {})
            if cheapest:
                print("🏆 BEST DEAL:")
                print(f"   Date: {cheapest['departure_date']}")
                print(f"   Price: ${cheapest['price']:.0f}")
                print(f"   Category: {cheapest['category']}")
                
                if cheapest['departure_date'] != request.start_date:
                    savings = trends.get('target_price', 0) - cheapest['price']
                    print(f"   💰 Save ${savings:.0f} by changing your dates!")
    
    print()
    print("=" * 80)
    print("✅ PRICE CALENDAR TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_price_calendar())

