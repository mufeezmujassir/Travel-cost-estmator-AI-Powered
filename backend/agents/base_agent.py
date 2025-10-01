from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import time
from datetime import datetime

from models.travel_models import AgentResponse, TravelRequest
from services.config import Settings

class BaseAgent(ABC):
    """Base class for all travel planning agents"""
    
    def __init__(self, name: str, settings: Settings):
        self.name = name
        self.settings = settings
        self.initialized = False
    
    async def initialize(self):
        """Initialize the agent"""
        self.initialized = True
        print(f"✅ {self.name} initialized")
    
    @abstractmethod
    async def process(self, request: TravelRequest, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process the travel request and return data dictionary
        NOTE: This should return a dict, NOT an AgentResponse
        """
        pass
    
    async def execute_with_timeout(self, request: TravelRequest, context: Dict[str, Any] = None) -> AgentResponse:
        """Execute agent with timeout protection"""
        start_time = time.time()
        
        try:
            # Execute with timeout
            result_data = await asyncio.wait_for(
                self.process(request, context),
                timeout=self.settings.agent_timeout
            )
            
            processing_time = time.time() - start_time
            
            # Check if result_data contains an error
            if isinstance(result_data, dict) and result_data.get('error'):
                return AgentResponse(
                    agent_name=self.name,
                    success=False,
                    data={},
                    error=result_data['error'],
                    processing_time=processing_time
                )
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                data=result_data,
                error=None,
                processing_time=processing_time
            )
            
        except asyncio.TimeoutError:
            processing_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.name,
                success=False,
                data={},
                error=f"Agent timeout after {self.settings.agent_timeout} seconds",
                processing_time=processing_time
            )
        except Exception as e:
            processing_time = time.time() - start_time
            return AgentResponse(
                agent_name=self.name,
                success=False,
                data={},
                error=str(e),
                processing_time=processing_time
            )
    
    def validate_request(self, request: TravelRequest) -> bool:
        """Validate the travel request"""
        if not self.initialized:
            raise RuntimeError(f"Agent {self.name} not initialized")
        
        if not request.origin or not request.destination:
            raise ValueError("Origin and destination are required")
        
        if request.travelers < 1 or request.travelers > self.settings.max_travelers:
            raise ValueError(f"Number of travelers must be between 1 and {self.settings.max_travelers}")
        
        return True
    
    def get_season_from_date(self, date_str: str) -> str:
        """Get season from date string"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            month = date_obj.month
            
            if month in [12, 1, 2]:
                return "winter"
            elif month in [3, 4, 5]:
                return "spring"
            elif month in [6, 7, 8]:
                return "summer"
            else:
                return "autumn"
        except:
            return "unknown"
    
    def calculate_trip_duration(self, start_date: str, return_date: str) -> int:
        """Calculate trip duration in days"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(return_date, '%Y-%m-%d')
            return (end - start).days
        except:
            return 0