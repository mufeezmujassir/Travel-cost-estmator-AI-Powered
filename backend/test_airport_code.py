import asyncio
from services.serp_service import SerpService
from services.config import Settings

async def test():
    s = SerpService(Settings())
    await s.initialize()
    
    print("Testing airport code resolution:")
    print("-" * 50)
    
    cities = ["Galle", "Colombo", "Tokyo", "New York"]
    for city in cities:
        code = await s.get_airport_code(city)
        print(f"{city:15} → {code}")

asyncio.run(test())

