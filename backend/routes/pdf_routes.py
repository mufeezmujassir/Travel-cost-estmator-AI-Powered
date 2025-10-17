"""
PDF Routes
API endpoints for generating travel plan PDFs
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response
from typing import Dict, Any, Optional
import logging

from services.pdf_generator import TravelPlanPDFGenerator
from services.auth_service import get_current_user
from schemas.user_schema import UserResponse

router = APIRouter()

# Initialize PDF generator
pdf_generator = TravelPlanPDFGenerator()

@router.get("/generate-pdf")
async def generate_travel_pdf(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate PDF for the user's latest travel plan
    """
    try:
        # For now, we'll generate a sample PDF
        # In a real implementation, you'd fetch the user's latest travel plan from the database
        
        # Sample travel data (replace with actual data from database)
        sample_travel_data = {
            "search_criteria": {
                "origin": "Colombo",
                "destination": "Tokyo",
                "departure_date": "2025-10-28",
                "return_date": "2025-11-03",
                "travelers": 1,
                "vibe": "nature"
            },
            "flights": [
                {
                    "airline": "Singapore Airlines",
                    "flight_number": "SQ 469",
                    "departure_airport": "CMB",
                    "arrival_airport": "HND",
                    "departure_time": "2025-10-28 00:45",
                    "arrival_time": "2025-10-28 15:35",
                    "duration": "680 min",
                    "price": 543.0,
                    "stops": 1
                },
                {
                    "airline": "Cathay Pacific",
                    "flight_number": "CX 610",
                    "departure_airport": "CMB",
                    "arrival_airport": "HND",
                    "departure_time": "2025-10-28 00:45",
                    "arrival_time": "2025-10-28 21:15",
                    "duration": "1020 min",
                    "price": 560.0,
                    "stops": 1
                }
            ],
            "hotels": [
                {
                    "name": "MIKAMI HOTEL ASAKUSABASHI",
                    "location": "Tokyo, Japan",
                    "price_per_night": 36.0,
                    "rating": 4.4,
                    "description": "Comfortable hotel in Asakusa district"
                }
            ],
            "itinerary": [
                {
                    "day": 1,
                    "activities": [
                        {
                            "name": "Arrival & Check-in",
                            "time": "Afternoon",
                            "description": "Arrive at hotel and get settled"
                        },
                        {
                            "name": "Sensoji Temple Visit",
                            "time": "Evening",
                            "description": "Visit the famous Buddhist temple in Asakusa"
                        }
                    ]
                },
                {
                    "day": 2,
                    "activities": [
                        {
                            "name": "Tokyo National Museum",
                            "time": "Morning",
                            "description": "Explore Japanese art and history"
                        },
                        {
                            "name": "Ueno Park",
                            "time": "Afternoon",
                            "description": "Relax in the beautiful park"
                        }
                    ]
                }
            ],
            "cost_breakdown": {
                "flights": 543.0,
                "hotels": 216.0,
                "transportation": 202.31,
                "activities": 300.0,
                "food": 210.0,
                "miscellaneous": 210.0
            },
            "total_estimated_cost": 1138.31
        }
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_pdf(sample_travel_data)
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=travel_plan_{current_user.email}_{sample_travel_data['search_criteria']['destination']}.pdf"
            }
        )
        
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

@router.post("/generate-pdf-from-data")
async def generate_pdf_from_data(
    travel_data: Dict[str, Any],
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Generate PDF from provided travel data
    """
    try:
        # Validate travel data
        if not travel_data:
            raise HTTPException(status_code=400, detail="Travel data is required")
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_pdf(travel_data)
        
        # Get destination for filename
        destination = travel_data.get('search_criteria', {}).get('destination', 'travel_plan')
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=travel_plan_{destination}.pdf"
            }
        )
        
    except Exception as e:
        logging.error(f"Error generating PDF from data: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
