# Travel Cost Estimator - AI-Powered Multi-Agent Travel Planning System

A comprehensive travel planning application that uses multiple AI agents to create personalized travel experiences based on emotional intelligence, vibe analysis, and real-time data integration.

## 🌟 Features

### Multi-Agent Architecture
- **Emotional Intelligence Agent**: Analyzes travel vibes and emotional preferences
- **Flight Search Agent**: Finds optimal flight options using SERP API
- **Hotel Search Agent**: Recommends vibe-matched accommodations
- **Transportation Agent**: Plans local and inter-city transportation
- **Cost Estimation Agent**: Provides comprehensive budget analysis
- **Recommendation Agent**: Creates personalized day-by-day itineraries

### Emotional Intelligence & Vibe Detection
- 7 distinct travel vibes: Romantic, Adventure, Beach, Nature, Cultural, Culinary, Wellness
- Season-based recommendations with optimal timing analysis
- Image-based vibe selection with emotional compatibility scoring
- Mood indicator analysis and wellness tips

### Real-Time Data Integration
- **Grok AI**: Advanced language model for personalized recommendations
- **SERP API**: Real-time flight and hotel data
- **Google Maps API**: Distance matrix and route optimization
- **Seasonal Analysis**: Weather and timing recommendations

### Beautiful Modern UI
- React + Vite + Tailwind CSS
- Responsive design with smooth animations
- Image-based vibe selection interface
- Real-time loading states with agent progress
- Comprehensive results dashboard

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- API Keys (optional for demo mode):
  - Grok API key
  - SERP API key
  - Google Maps API key

### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your API keys (optional)
# The system works in demo mode without API keys

# Start the server
python main.py
```

## 🏗️ Architecture

### Frontend (React + Vite)
```
src/
├── components/
│   ├── Header.jsx          # Navigation and branding
│   ├── TravelForm.jsx      # Travel request form
│   ├── VibeSelector.jsx    # Image-based vibe selection
│   ├── LoadingSpinner.jsx  # Agent progress visualization
│   └── Results.jsx         # Comprehensive results display
├── hooks/
│   └── useTravelEstimation.js  # API integration hook
└── App.jsx                 # Main application component
```

### Backend (FastAPI + LangGraph)
```
backend/
├── agents/
│   ├── base_agent.py           # Base agent class
│   ├── emotional_intelligence_agent.py
│   ├── flight_search_agent.py
│   ├── hotel_search_agent.py
│   ├── transportation_agent.py
│   ├── cost_estimation_agent.py
│   ├── recommendation_agent.py
│   └── travel_orchestrator.py  # LangGraph workflow
├── models/
│   └── travel_models.py        # Pydantic models
├── services/
│   ├── config.py              # Configuration management
│   ├── grok_service.py        # Grok AI integration
│   └── serp_service.py        # SERP API integration
└── main.py                    # FastAPI application
```

## 🎯 How It Works

### 1. Travel Request
User fills out travel form with:
- Origin and destination cities
- Travel dates and duration
- Number of travelers
- Optional budget
- Travel vibe selection

### 2. Multi-Agent Processing
The system orchestrates 6 specialized agents:

1. **Emotional Intelligence Agent** analyzes the selected vibe and provides:
   - Vibe compatibility scoring
   - Season analysis
   - Mood indicators
   - Wellness recommendations

2. **Flight Search Agent** finds optimal flights:
   - Real-time flight data via SERP API
   - Price comparison and ranking
   - Duration and stop analysis

3. **Hotel Search Agent** recommends accommodations:
   - Vibe-matched hotel selection
   - Amenity analysis
   - Location optimization
   - Price and rating comparison

4. **Transportation Agent** plans local travel:
   - Airport transfers
   - Local transportation options
   - Route optimization via Google Maps
   - Cost estimation

5. **Cost Estimation Agent** provides budget analysis:
   - Comprehensive cost breakdown
   - Budget vs. estimated cost analysis
   - Optimization suggestions
   - Per-person cost calculation

6. **Recommendation Agent** creates itineraries:
   - Day-by-day activity planning
   - Vibe-specific experiences
   - Seasonal recommendations
   - Local insights and tips

### 3. Results Presentation
The system presents:
- **Overview**: Summary with key metrics
- **Flights**: Detailed flight options
- **Hotels**: Accommodation recommendations
- **Itinerary**: Day-by-day activity plan
- **Costs**: Comprehensive budget breakdown

## 🎨 Travel Vibes

### Romantic 💕
- **Optimal Season**: Spring, Autumn
- **Activities**: Sunset dinners, couples spa, romantic walks
- **Focus**: Intimate experiences, luxury accommodations

### Adventure 🏔️
- **Optimal Season**: Summer, Autumn
- **Activities**: Hiking, rock climbing, extreme sports
- **Focus**: Thrilling experiences, outdoor gear

### Beach 🏖️
- **Optimal Season**: Summer
- **Activities**: Beach relaxation, water sports, sunset views
- **Focus**: Coastal experiences, beachfront hotels

### Nature 🌲
- **Optimal Season**: Spring, Autumn
- **Activities**: Forest hiking, wildlife watching, camping
- **Focus**: Natural beauty, eco-friendly options

### Cultural 🏛️
- **Optimal Season**: Autumn, Spring
- **Activities**: Museum visits, historical tours, local festivals
- **Focus**: Education, local traditions

### Culinary 🍽️
- **Optimal Season**: Autumn, Spring
- **Activities**: Food tours, cooking classes, local markets
- **Focus**: Gastronomic experiences, local cuisine

### Wellness 🧘
- **Optimal Season**: Winter, Spring
- **Activities**: Spa treatments, yoga, meditation
- **Focus**: Rejuvenation, health, relaxation

## 🔧 Configuration

### Environment Variables
```bash
# API Keys (optional - system works in demo mode)
GROK_API_KEY=your_grok_api_key
SERP_API_KEY=your_serp_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Configuration
API_TIMEOUT=30
AGENT_TIMEOUT=60
MAX_TRAVELERS=10
```

### Demo Mode
The system works perfectly in demo mode without API keys:
- Mock data for flights and hotels
- Simulated AI responses
- Full functionality demonstration
- Perfect for presentations and testing

## 🚀 Deployment

### Frontend Deployment (Vercel/Netlify)
```bash
npm run build
# Deploy dist/ folder to your hosting service
```

### Backend Deployment (Railway/Heroku)
```bash
# Add Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port $PORT" > Procfile

# Deploy with your preferred service
```

## 📊 API Endpoints

### Main Endpoints
- `POST /api/estimate-travel` - Main travel estimation endpoint
- `GET /api/vibes` - Get available travel vibes
- `GET /api/season-recommendation` - Get season recommendations
- `GET /health` - Health check

### Example Request
```json
{
  "origin": "New York",
  "destination": "Tokyo",
  "start_date": "2024-06-15",
  "return_date": "2024-06-22",
  "travelers": 2,
  "budget": 5000,
  "vibe": "cultural"
}
```

## 🎓 Educational Value

This project demonstrates:
- **Multi-Agent Systems**: LangGraph workflow orchestration
- **AI Integration**: Grok API for intelligent recommendations
- **Real-Time Data**: SERP API for live travel data
- **Emotional Intelligence**: Vibe-based travel planning
- **Modern Web Development**: React, FastAPI, TypeScript
- **API Design**: RESTful services with comprehensive error handling
- **User Experience**: Intuitive interface with smooth animations

## 🏆 Commercialization Potential

### Revenue Streams
1. **Freemium Model**: Basic features free, premium AI recommendations
2. **Commission-Based**: Partner with booking platforms
3. **Enterprise**: B2B travel planning for companies
4. **API Licensing**: License the multi-agent system
5. **White-Label**: Custom solutions for travel agencies

### Market Opportunities
- **Travel Planning**: $1.2T global travel market
- **AI-Powered Services**: Growing demand for personalized experiences
- **Emotional Intelligence**: Unique positioning in travel tech
- **B2B Solutions**: Corporate travel management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain/LangGraph**: Multi-agent orchestration
- **Grok AI**: Advanced language model capabilities
- **SERP API**: Real-time search data
- **Google Maps**: Location and routing services
- **React/Vite**: Modern frontend framework
- **FastAPI**: High-performance Python web framework

---

**Built with ❤️ for the future of intelligent travel planning**
