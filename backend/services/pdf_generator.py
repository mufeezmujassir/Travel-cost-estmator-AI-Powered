"""
PDF Generator Service for Travel Plans
Generates beautiful PDF reports with travel plan details
"""

import io
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib import colors


class TravelPlanPDFGenerator:
    """Generate beautiful PDF reports for travel plans"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=HexColor('#374151'),
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=HexColor('#1f2937'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=HexColor('#e5e7eb'),
            borderPadding=8,
            backColor=HexColor('#f9fafb')
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=HexColor('#374151'),
            alignment=TA_JUSTIFY
        ))
        
        # Price style
        self.styles.add(ParagraphStyle(
            name='PriceText',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            textColor=HexColor('#059669'),
            fontName='Helvetica-Bold'
        ))
        
        # Meta info style
        self.styles.add(ParagraphStyle(
            name='MetaInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=HexColor('#6b7280'),
            fontName='Helvetica-Oblique'
        ))
    
    def generate_pdf(self, travel_data: Dict[str, Any]) -> bytes:
        """Generate PDF bytes from travel data"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build the story (content)
        story = []
        
        # Add header
        story.extend(self._build_header(travel_data))
        
        # Add overview section
        story.extend(self._build_overview_section(travel_data))
        
        # Add flights section
        if travel_data.get('flights'):
            story.extend(self._build_flights_section(travel_data['flights']))
        
        # Add hotels section
        if travel_data.get('hotels'):
            story.extend(self._build_hotels_section(travel_data['hotels']))
        
        # Add itinerary section
        if travel_data.get('itinerary'):
            story.extend(self._build_itinerary_section(travel_data['itinerary']))
        
        # Add cost breakdown section
        story.extend(self._build_cost_section(travel_data))
        
        # Add footer
        story.extend(self._build_footer())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _build_header(self, travel_data: Dict[str, Any]) -> List:
        """Build the header section"""
        elements = []
        
        # Main title
        elements.append(Paragraph("Your Perfect Travel Plan", self.styles['CustomTitle']))
        elements.append(Spacer(1, 12))
        
        # Trip details
        origin = travel_data.get('search_criteria', {}).get('origin', 'Unknown')
        destination = travel_data.get('search_criteria', {}).get('destination', 'Unknown')
        vibe = travel_data.get('search_criteria', {}).get('vibe', 'General')
        
        trip_title = f"{origin} → {destination}"
        elements.append(Paragraph(trip_title, self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 8))
        
        # Vibe description
        vibe_name = self._get_vibe_display_name(vibe)
        elements.append(Paragraph(f"{vibe_name} Experience", self.styles['CustomBodyText']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_overview_section(self, travel_data: Dict[str, Any]) -> List:
        """Build the overview section"""
        elements = []
        
        elements.append(Paragraph("Trip Overview", self.styles['SectionHeader']))
        
        # Trip details table
        criteria = travel_data.get('search_criteria', {})
        trip_data = [
            ['Origin', criteria.get('origin', 'N/A')],
            ['Destination', criteria.get('destination', 'N/A')],
            ['Departure Date', criteria.get('departure_date', 'N/A')],
            ['Return Date', criteria.get('return_date', 'N/A')],
            ['Travelers', str(criteria.get('travelers', 'N/A'))],
            ['Travel Style', self._get_vibe_display_name(criteria.get('vibe', 'general'))]
        ]
        
        trip_table = Table(trip_data, colWidths=[2*inch, 3*inch])
        trip_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0'))
        ]))
        
        elements.append(trip_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_flights_section(self, flights: List[Dict[str, Any]]) -> List:
        """Build the flights section"""
        elements = []
        
        elements.append(Paragraph("Flight Options", self.styles['SectionHeader']))
        
        if not flights:
            elements.append(Paragraph("No flight information available.", self.styles['CustomBodyText']))
            elements.append(Spacer(1, 20))
            return elements
        
        # Flight details table
        flight_data = [['Airline', 'Flight', 'Route', 'Departure', 'Arrival', 'Duration', 'Price']]
        
        for flight in flights[:5]:  # Show top 5 flights
            departure_airport = flight.get('departure_airport', 'N/A')
            arrival_airport = flight.get('arrival_airport', 'N/A')
            route = f"{departure_airport} → {arrival_airport}"
            
            flight_data.append([
                flight.get('airline', 'N/A'),
                flight.get('flight_number', 'N/A'),
                route,
                flight.get('departure_time', 'N/A'),
                flight.get('arrival_time', 'N/A'),
                flight.get('duration', 'N/A'),
                f"${flight.get('price', 0):.2f}" if flight.get('price') else 'N/A'
            ])
        
        flight_table = Table(flight_data, colWidths=[1.2*inch, 0.8*inch, 1.2*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch])
        flight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8fafc'))
        ]))
        
        elements.append(flight_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_hotels_section(self, hotels: List[Dict[str, Any]]) -> List:
        """Build the hotels section"""
        elements = []
        
        elements.append(Paragraph("Accommodation Options", self.styles['SectionHeader']))
        
        if not hotels:
            elements.append(Paragraph("No hotel information available.", self.styles['CustomBodyText']))
            elements.append(Spacer(1, 20))
            return elements
        
        # Hotel details
        for hotel in hotels[:3]:  # Show top 3 hotels
            hotel_name = hotel.get('name', 'Unknown Hotel')
            price = hotel.get('price_per_night', 0)
            rating = hotel.get('rating', 0)
            location = hotel.get('location', 'N/A')
            
            elements.append(Paragraph(f"<b>{hotel_name}</b>", self.styles['CustomBodyText']))
            elements.append(Paragraph(f"Location: {location}", self.styles['MetaInfo']))
            elements.append(Paragraph(f"Price: <font color='#059669'>${price:.2f}/night</font>", self.styles['PriceText']))
            if rating > 0:
                elements.append(Paragraph(f"Rating: {rating}/5 ⭐", self.styles['MetaInfo']))
            elements.append(Spacer(1, 12))
        
        elements.append(Spacer(1, 8))
        return elements
    
    def _build_itinerary_section(self, itinerary: List[Dict[str, Any]]) -> List:
        """Build the itinerary section"""
        elements = []
        
        elements.append(Paragraph("Suggested Itinerary", self.styles['SectionHeader']))
        
        if not itinerary:
            elements.append(Paragraph("No detailed itinerary available.", self.styles['CustomBodyText']))
            elements.append(Spacer(1, 20))
            return elements
        
        # Day-by-day itinerary
        for day_plan in itinerary:
            day = day_plan.get('day', 'N/A')
            activities = day_plan.get('activities', [])
            
            elements.append(Paragraph(f"<b>Day {day}</b>", self.styles['CustomBodyText']))
            
            for activity in activities:
                activity_name = activity.get('name', 'Activity')
                activity_time = activity.get('time', '')
                activity_desc = activity.get('description', '')
                
                if activity_time:
                    elements.append(Paragraph(f"• {activity_time}: {activity_name}", self.styles['CustomBodyText']))
                else:
                    elements.append(Paragraph(f"• {activity_name}", self.styles['CustomBodyText']))
                
                if activity_desc:
                    elements.append(Paragraph(f"  {activity_desc}", self.styles['MetaInfo']))
            
            elements.append(Spacer(1, 12))
        
        elements.append(Spacer(1, 8))
        return elements
    
    def _build_cost_section(self, travel_data: Dict[str, Any]) -> List:
        """Build the cost breakdown section"""
        elements = []
        
        elements.append(Paragraph("Cost Breakdown", self.styles['SectionHeader']))
        
        # Get cost data
        total_cost = travel_data.get('total_estimated_cost', 0)
        cost_breakdown = travel_data.get('cost_breakdown', {})
        travelers = travel_data.get('search_criteria', {}).get('travelers', 1)
        
        # Cost summary table
        cost_data = [['Category', 'Cost', 'Per Person']]
        
        categories = [
            ('Flights', cost_breakdown.get('flights', 0)),
            ('Hotels', cost_breakdown.get('hotels', 0)),
            ('Transportation', cost_breakdown.get('transportation', 0)),
            ('Activities', cost_breakdown.get('activities', 0)),
            ('Food', cost_breakdown.get('food', 0)),
            ('Miscellaneous', cost_breakdown.get('miscellaneous', 0))
        ]
        
        for category, amount in categories:
            per_person = amount / travelers if travelers > 0 else amount
            cost_data.append([
                category,
                f"${amount:.2f}",
                f"${per_person:.2f}"
            ])
        
        # Add total row
        per_person_total = total_cost / travelers if travelers > 0 else total_cost
        cost_data.append([
            '<b>TOTAL</b>',
            f'<font color="#059669"><b>${total_cost:.2f}</b></font>',
            f'<font color="#059669"><b>${per_person_total:.2f}</b></font>'
        ])
        
        cost_table = Table(cost_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#e2e8f0')),
            ('BACKGROUND', (0, 1), (-1, -2), HexColor('#f8fafc')),
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#f0f9ff'))
        ]))
        
        elements.append(cost_table)
        elements.append(Spacer(1, 20))
        
        # Add cost confidence info
        real_data_percentage = self._calculate_real_data_percentage(travel_data)
        elements.append(Paragraph("Data Sources", self.styles['SectionHeader']))
        elements.append(Paragraph(
            f"• Real market data: {real_data_percentage:.0f}% (Flights & Hotels from Google)",
            self.styles['MetaInfo']
        ))
        elements.append(Paragraph(
            f"• AI estimates: {100-real_data_percentage:.0f}% (Activities, Food & Misc based on destination pricing)",
            self.styles['MetaInfo']
        ))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_footer(self) -> List:
        """Build the footer section"""
        elements = []
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Generated by TravelCost AI", self.styles['MetaInfo']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", self.styles['MetaInfo']))
        elements.append(Paragraph("AI-Powered Travel Planning", self.styles['MetaInfo']))
        
        return elements
    
    def _get_vibe_display_name(self, vibe: str) -> str:
        """Convert vibe code to display name"""
        vibe_names = {
            'romantic': 'Romantic',
            'adventure': 'Adventure',
            'beach': 'Beach & Relaxation',
            'nature': 'Nature & Forest',
            'cultural': 'Cultural & Heritage',
            'culinary': 'Culinary & Food',
            'wellness': 'Wellness & Spa'
        }
        return vibe_names.get(vibe.lower(), 'General Travel')
    
    def _calculate_real_data_percentage(self, travel_data: Dict[str, Any]) -> float:
        """Calculate percentage of real vs estimated data"""
        cost_breakdown = travel_data.get('cost_breakdown', {})
        
        real_data_categories = ['flights', 'hotels']
        estimated_categories = ['transportation', 'activities', 'food', 'miscellaneous']
        
        real_total = sum(cost_breakdown.get(cat, 0) for cat in real_data_categories)
        estimated_total = sum(cost_breakdown.get(cat, 0) for cat in estimated_categories)
        
        total = real_total + estimated_total
        if total == 0:
            return 0
        
        return (real_total / total) * 100
