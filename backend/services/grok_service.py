import asyncio
import httpx
from typing import Dict, Any, Optional
import json

from .config import Settings

class GrokService:
    """Service for interacting with Grok API"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.grok_api_key
        self.base_url = settings.grok_base_url
        self.model = settings.grok_model
        self.temperature = settings.grok_temperature
        self.max_tokens = settings.grok_max_tokens
        self.initialized = False
    
    async def initialize(self):
        if not self.api_key:
            print("⚠️ Grok API key not provided, using mock responses")
        else:
            print("✅ Grok service initialized with API key")
        
        self.initialized = True
    
    async def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        if not self.api_key:
            return self._get_mock_response(prompt)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "response_format": {"type": "json_object"}  # Add this to force JSON
            }
            
            async with httpx.AsyncClient(timeout=self.settings.api_timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    print(f"Grok API error: {response.status_code} - {response.text}")
                    return self._get_mock_response(prompt)
                    
        except Exception as e:
            print(f"Error calling Grok API: {e}")
            return self._get_mock_response(prompt)


    def _get_mock_response(self, prompt: str) -> str:
        if "emotional intelligence" in prompt.lower():
            return json.dumps({
                "activities": ["Sunset dinner cruise", "Couples spa treatment", "Romantic walk in gardens"],
                "wellness_tips": ["Plan intimate moments", "Disconnect from technology", "Focus on each other"],
                "enhancement_suggestions": ["Book private experiences", "Choose romantic accommodations"]
            })
        
        elif "hotel" in prompt.lower() and "vibe" in prompt.lower():
            return json.dumps({
                "vibe_score": 0.9,
                "reasoning": "This hotel is perfect for romantic getaways because of its intimate atmosphere and luxury amenities",
                "vibe_enhancements": ["Book a room with a view", "Request romantic amenities"]
            })
        
        elif "cost optimization" in prompt.lower():
            return """1. Book flights 2-3 months in advance for better prices
2. Look for hotels slightly outside the city center for lower rates
3. Use public transportation instead of taxis for local travel
4. Book activities in advance for potential discounts
5. Eat at local restaurants instead of tourist areas
6. Travel during off-peak seasons for better deals
7. Consider alternative accommodations like Airbnb"""
        
        elif "recommendations" in prompt.lower():
            return """1. Book activities in advance to secure the best experiences
2. Pack according to the seasonal weather patterns
3. Learn a few basic phrases in the local language
4. Download offline maps and translation apps
5. Keep emergency contact information handy
6. Research local customs and traditions
7. Plan some free time for spontaneous discoveries"""
        
        else:
            return "This is a mock response. Please provide a valid Grok API key for real AI responses."