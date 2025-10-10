"""
Price Calendar Service - Similar to Google Flights Date Grid
Shows price trends across different dates to help users find cheaper travel days
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from statistics import mean, median

class PriceCalendar:
    """Analyzes flight prices across multiple dates to find the best deals"""
    
    def __init__(self, serp_service):
        self.serp_service = serp_service
    
    async def get_price_trends(
        self, 
        origin: str, 
        destination: str, 
        target_date: str,
        duration_days: int = 5,
        search_window_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get price trends for flights around a target date
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            target_date: User's preferred departure date (YYYY-MM-DD)
            duration_days: Trip duration in days
            search_window_days: How many days before/after to check (±7 = 14 days total)
            
        Returns:
            Dict with price analysis, recommendations, and date grid
        """
        
        # Parse target date
        target = datetime.strptime(target_date, "%Y-%m-%d")
        
        # Generate date range to check
        dates_to_check = []
        for offset in range(-search_window_days, search_window_days + 1):
            departure = target + timedelta(days=offset)
            return_date = departure + timedelta(days=duration_days)
            dates_to_check.append({
                "departure": departure.strftime("%Y-%m-%d"),
                "return": return_date.strftime("%Y-%m-%d"),
                "offset": offset
            })
        
        print(f"📊 Analyzing prices for {len(dates_to_check)} date combinations...")
        
        # Search flights for each date (parallel for speed)
        tasks = []
        for date_combo in dates_to_check:
            task = self._get_cheapest_price(
                origin, 
                destination, 
                date_combo["departure"], 
                date_combo["return"]
            )
            tasks.append(task)
        
        # Execute all searches in parallel
        results = await asyncio.gather(*tasks)
        
        # Combine results
        price_data = []
        for i, date_combo in enumerate(dates_to_check):
            price_data.append({
                "departure_date": date_combo["departure"],
                "return_date": date_combo["return"],
                "price": results[i],
                "offset_days": date_combo["offset"]
            })
        
        # Analyze prices
        analysis = self._analyze_prices(price_data, target_date)
        
        return analysis
    
    async def _get_cheapest_price(
        self, 
        origin: str, 
        destination: str, 
        departure: str, 
        return_date: str
    ) -> float:
        """Get the cheapest flight price for a specific date"""
        try:
            flights = await self.serp_service.search_flights(
                origin, 
                destination, 
                departure, 
                return_date
            )
            
            if flights:
                prices = [f.get("price", 0) for f in flights if f.get("price", 0) > 0]
                return min(prices) if prices else 0.0
            return 0.0
            
        except Exception as e:
            print(f"Error getting price for {departure}: {e}")
            return 0.0
    
    def _analyze_prices(self, price_data: List[Dict], target_date: str) -> Dict[str, Any]:
        """Analyze price data and generate recommendations"""
        
        # Filter out zero prices
        valid_prices = [p for p in price_data if p["price"] > 0]
        
        if not valid_prices:
            return {
                "status": "no_data",
                "message": "No price data available for analysis"
            }
        
        # Calculate statistics
        all_prices = [p["price"] for p in valid_prices]
        avg_price = mean(all_prices)
        median_price = median(all_prices)
        min_price = min(all_prices)
        max_price = max(all_prices)
        
        # Find target date price
        target_price = next(
            (p["price"] for p in valid_prices if p["departure_date"] == target_date), 
            None
        )
        
        # Classify each date
        for item in valid_prices:
            price = item["price"]
            
            # Classification logic
            if price <= min_price * 1.1:  # Within 10% of minimum
                item["category"] = "cheap"
                item["savings_vs_average"] = avg_price - price
            elif price <= avg_price:
                item["category"] = "moderate"
                item["savings_vs_average"] = avg_price - price
            else:
                item["category"] = "expensive"
                item["savings_vs_average"] = avg_price - price  # Will be negative
        
        # Find best alternatives
        cheapest_option = min(valid_prices, key=lambda x: x["price"])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            valid_prices, 
            target_date, 
            target_price, 
            cheapest_option,
            avg_price
        )
        
        # Create price grid (for UI display)
        price_grid = self._create_price_grid(valid_prices)
        
        return {
            "status": "success",
            "target_date": target_date,
            "target_price": target_price,
            "statistics": {
                "average_price": round(avg_price, 2),
                "median_price": round(median_price, 2),
                "min_price": min_price,
                "max_price": max_price,
                "price_range": max_price - min_price
            },
            "cheapest_option": cheapest_option,
            "recommendations": recommendations,
            "price_grid": price_grid,
            "all_dates": valid_prices
        }
    
    def _generate_recommendations(
        self, 
        price_data: List[Dict],
        target_date: str,
        target_price: Optional[float],
        cheapest_option: Dict,
        avg_price: float
    ) -> List[str]:
        """Generate user-friendly recommendations"""
        
        recommendations = []
        
        # Recommendation 1: About target date
        if target_price:
            if target_price <= avg_price * 0.9:  # 10% below average
                recommendations.append(
                    f"✅ Great choice! Your selected date ({target_date}) has below-average prices at ${target_price:.0f}"
                )
            elif target_price >= avg_price * 1.2:  # 20% above average
                recommendations.append(
                    f"💰 Your selected date ({target_date}) is expensive at ${target_price:.0f}. "
                    f"Consider changing dates to save money."
                )
            else:
                recommendations.append(
                    f"📊 Your selected date ({target_date}) has moderate pricing at ${target_price:.0f}"
                )
        
        # Recommendation 2: Cheapest alternative
        if cheapest_option["departure_date"] != target_date:
            savings = (target_price or avg_price) - cheapest_option["price"]
            recommendations.append(
                f"💎 Best deal: Departing {cheapest_option['departure_date']} "
                f"costs only ${cheapest_option['price']:.0f} "
                f"(save ${savings:.0f}!)"
            )
        
        # Recommendation 3: Nearby cheap dates
        cheap_dates = [
            p for p in price_data 
            if p["category"] == "cheap" and p["departure_date"] != target_date
        ]
        if cheap_dates:
            nearby_cheap = [
                d for d in cheap_dates 
                if abs(d["offset_days"]) <= 3  # Within 3 days
            ]
            if nearby_cheap:
                dates_str = ", ".join([d["departure_date"] for d in nearby_cheap[:3]])
                recommendations.append(
                    f"📅 Cheap dates nearby: {dates_str}"
                )
        
        # Recommendation 4: Flexibility suggestion
        cheap_count = len([p for p in price_data if p["category"] == "cheap"])
        if cheap_count >= 3:
            recommendations.append(
                f"💡 Tip: Being flexible with dates can save you up to ${max(p['savings_vs_average'] for p in price_data if p['savings_vs_average'] > 0):.0f}"
            )
        
        # Recommendation 5: Weekend vs Weekday
        weekday_prices = []
        weekend_prices = []
        
        for p in price_data:
            date_obj = datetime.strptime(p["departure_date"], "%Y-%m-%d")
            if date_obj.weekday() >= 5:  # Saturday or Sunday
                weekend_prices.append(p["price"])
            else:
                weekday_prices.append(p["price"])
        
        if weekday_prices and weekend_prices:
            avg_weekday = mean(weekday_prices)
            avg_weekend = mean(weekend_prices)
            
            if avg_weekday < avg_weekend * 0.9:
                recommendations.append(
                    f"📆 Weekday flights are cheaper on average (${avg_weekday:.0f} vs ${avg_weekend:.0f})"
                )
            elif avg_weekend < avg_weekday * 0.9:
                recommendations.append(
                    f"📆 Weekend flights are cheaper on average (${avg_weekend:.0f} vs ${avg_weekday:.0f})"
                )
        
        return recommendations
    
    def _create_price_grid(self, price_data: List[Dict]) -> List[Dict]:
        """Create a formatted price grid for UI display"""
        
        grid = []
        for item in price_data:
            date_obj = datetime.strptime(item["departure_date"], "%Y-%m-%d")
            
            grid.append({
                "date": item["departure_date"],
                "day_of_week": date_obj.strftime("%A"),
                "price": item["price"],
                "category": item["category"],
                "is_cheap": item["category"] == "cheap",
                "is_expensive": item["category"] == "expensive",
                "savings": round(item["savings_vs_average"], 2)
            })
        
        return sorted(grid, key=lambda x: x["date"])
    
    def get_price_category_emoji(self, category: str) -> str:
        """Get emoji for price category"""
        return {
            "cheap": "💚",
            "moderate": "💛",
            "expensive": "🔴"
        }.get(category, "⚪")

