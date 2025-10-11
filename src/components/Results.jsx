import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Plane, 
  MapPin, 
  Calendar, 
  Users, 
  DollarSign, 
  Heart,
  ArrowLeft,
  Download,
  Share2,
  Star,
  Clock,
  Navigation,
  Building,
  Train,
  Bus,
  Car,
  Globe,
  MapPinned,
  Info,
  Crown,
  Lock,
  Zap
} from 'lucide-react'
import { AnimatePresence } from 'framer-motion'
import { useSubscription } from '../context/SubscriptionContext'
import { useNavigate } from 'react-router-dom'
import ImprovedCostsTab from './ImprovedCostsTab'
const Results = ({ results, error, onReset, formData, selectedVibe }) => {
  const [activeTab, setActiveTab] = useState('overview')
  const { subscription, isPremium } = useSubscription()
  const navigate = useNavigate()

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg"
      >
        <div className="flex items-center gap-2 text-red-600 mb-4">
          <XCircle size={24} />
          <h2 className="text-xl font-bold">Error</h2>
        </div>
        <p className="text-gray-700 mb-6">{error}</p>
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <ArrowLeft size={20} />
          Try Again
        </button>
      </motion.div>
    )
  }

  if (!results) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg"
      >
        <p className="text-gray-700">No results available. Please try again.</p>
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          <ArrowLeft size={20} />
          Try Again
        </button>
      </motion.div>
    )
  }

  // Determine if this is domestic travel
  const isDomesticTravel = results?.is_domestic_travel || false
  const hasFlights = results?.flights && results.flights.length > 0

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Heart },
    // Show Transportation tab for domestic travel, otherwise show Flights tab
    ...(isDomesticTravel 
      ? [{ id: 'transportation', name: 'Transportation', icon: Navigation }]
      : [{ id: 'flights', name: 'Flights', icon: Plane }]
    ),
    { id: 'hotels', name: 'Hotels', icon: MapPin },
    { id: 'itinerary', name: 'Itinerary', icon: Calendar },
    { id: 'costs', name: 'Costs', icon: DollarSign }
  ]

  // Get tier icon
  const getTierIcon = () => {
    switch (subscription?.tier) {
      case 'trip_pass':
        return <Star className="w-4 h-4" />
      case 'explorer_annual':
        return <Zap className="w-4 h-4" />
      case 'travel_pro':
        return <Crown className="w-4 h-4" />
      default:
        return null
    }
  }

  const getTierColor = () => {
    switch (subscription?.tier) {
      case 'trip_pass':
        return 'from-blue-500 to-blue-600'
      case 'explorer_annual':
        return 'from-purple-500 to-purple-600'
      case 'travel_pro':
        return 'from-amber-500 to-amber-600'
      default:
        return 'from-gray-500 to-gray-600'
    }
  }

  const getTierName = () => {
    switch (subscription?.tier) {
      case 'trip_pass':
        return 'Trip Pass'
      case 'explorer_annual':
        return 'Explorer Annual'
      case 'travel_pro':
        return 'Travel Pro'
      default:
        return 'Free Explorer'
    }
  }

  return (
    <motion.div
      className="max-w-6xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Subscription Tier Badge */}
      {subscription && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 flex justify-center"
        >
          <div className={`inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r ${getTierColor()} text-white rounded-full shadow-lg`}>
            {getTierIcon()}
            <span className="font-semibold">{getTierName()}</span>
          </div>
        </motion.div>
      )}

      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Your Perfect Travel Plan
        </h2>
        <p className="text-gray-600">
          {formData.origin} → {formData.destination} • {selectedVibe?.name} Experience
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4 mb-8">
        <button className="btn-secondary">
          <Share2 className="w-4 h-4 inline mr-2" />
          Share
        </button>
        {isPremium() ? (
          <button className="btn-secondary">
            <Download className="w-4 h-4 inline mr-2" />
            Download PDF
          </button>
        ) : (
          <button 
            onClick={() => navigate('/pricing')}
            className="btn-secondary relative"
          >
            <Lock className="w-4 h-4 inline mr-2" />
            Download PDF
            <span className="ml-2 text-xs bg-yellow-400 text-yellow-900 px-2 py-0.5 rounded-full">Premium</span>
          </button>
        )}
        <button onClick={onReset} className="btn-primary">
          <ArrowLeft className="w-4 h-4 inline mr-2" />
          Plan Another Trip
        </button>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap justify-center mb-8">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors duration-200 ${
                activeTab === tab.id
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.name}</span>
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <OverviewTab results={results} formData={formData} selectedVibe={selectedVibe} />
          </motion.div>
        )}
        
        {activeTab === 'transportation' && (
          <motion.div
            key="transportation"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <TransportationTab results={results} formData={formData} travelDistance={results?.travel_distance_km || 0} />
          </motion.div>
        )}
        
        {activeTab === 'flights' && (
          <motion.div
            key="flights"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <FlightsTab results={results} formData={formData} />
          </motion.div>
        )}
        
        {activeTab === 'hotels' && (
          <motion.div
            key="hotels"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <HotelsTab results={results} />
          </motion.div>
        )}
        
        {activeTab === 'itinerary' && (
          <motion.div
            key="itinerary"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <ItineraryTab results={results} />
          </motion.div>
        )}
        
        {activeTab === 'costs' && (
          <motion.div
            key="costs"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <ImprovedCostsTab results={results} formData={formData} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Overview Tab Component
const OverviewTab = ({ results, formData, selectedVibe }) => {
  const isDomesticTravel = results?.is_domestic_travel || false
  const hasFlights = results?.flights && results.flights.length > 0
  const travelDistance = results?.travel_distance_km || 0

  return (
    <div className="space-y-6">
      {/* Travel Type Indicator for Domestic Travel */}
      {isDomesticTravel && (
        <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
              <MapPinned className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-1">Domestic Travel Detected</h3>
              <p className="text-gray-700 mb-2">
                Great choice! Ground transportation is more practical and eco-friendly for this route.
              </p>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Navigation className="w-4 h-4" />
                  <span>Distance: {travelDistance > 0 ? `${Math.round(travelDistance)} km` : 'Calculated'}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Globe className="w-4 h-4" />
                  <span>Type: Domestic</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Conditionally show Flight or Transportation card */}
        {!isDomesticTravel ? (
          (() => {
            // Find the actually cheapest flight (by price)
            const cheapestFlight = results?.flights?.length > 0
              ? results.flights.reduce((min, flight) => flight.price < min.price ? flight : min)
              : null;
            const cheapestPrice = cheapestFlight 
              ? Math.round(cheapestFlight.price / formData.travelers)
              : 'N/A';

            return (
              <div className="card text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Plane className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Best Flight</h3>
                <p className="text-2xl font-bold text-blue-600">
                  ${cheapestPrice}
                </p>
                <p className="text-sm text-gray-600">
                  {cheapestFlight?.airline || 'Multiple options'}
                </p>
                <p className="text-xs text-gray-500">per person</p>
              </div>
            );
          })()
        ) : (
          <div className="card text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Navigation className="w-8 h-8 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Transportation</h3>
            <p className="text-2xl font-bold text-green-600">
              ${results?.transportation?.inter_city_options?.[0]?.cost || results?.cost_breakdown?.transportation || 'N/A'}
            </p>
            <p className="text-sm text-gray-600">
              {results?.transportation?.inter_city_options?.[0]?.type 
                ? `${results.transportation.inter_city_options[0].type.charAt(0).toUpperCase() + results.transportation.inter_city_options[0].type.slice(1)} available`
                : 'Multiple options'}
            </p>
          </div>
        )}
        
        <div className="card text-center">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <MapPin className="w-8 h-8 text-amber-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommended Hotel</h3>
          <div className="flex items-center justify-center gap-2">
            <p className="text-2xl font-bold text-amber-600">
              ${results?.hotels?.[0]?.price_per_night || 'N/A'}
            </p>
            {results?.hotels?.[0]?.price_confidence === 'estimated' && (
              <span 
                className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium"
                title="Estimated price based on hotel category"
              >
                Est.
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600">
            per night
            {results?.hotels?.[0]?.price_confidence === 'estimated' && (
              <span className="text-amber-600"> (estimated)</span>
            )}
          </p>
        </div>
        
        <div className="card text-center">
          <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <DollarSign className="w-8 h-8 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Estimated</h3>
          <p className="text-2xl font-bold text-purple-600">
            ${(results?.total_cost || 0).toFixed(2)}
          </p>
          <p className="text-sm text-gray-600">for {formData.travelers} traveler(s)</p>
        </div>
      </div>

      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          Why This Plan is Perfect for You
        </h3>
        <div className="space-y-3">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <Heart className="w-3 h-3 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Emotional Intelligence Match</p>
              <p className="text-gray-600">
                This itinerary is perfectly aligned with your {selectedVibe?.name.toLowerCase()} preferences, 
                ensuring you'll have the experience you're looking for.
              </p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <Calendar className="w-3 h-3 text-green-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Optimal Timing</p>
              <p className="text-gray-600">
                Your travel dates are perfectly timed for the best weather and seasonal activities 
                in {formData.destination}.
              </p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <Star className="w-3 h-3 text-blue-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">Curated Experiences</p>
              <p className="text-gray-600">
                Every activity and location has been carefully selected to match your vibe and 
                maximize your enjoyment.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Transportation Tab Component (for Domestic Travel)
const TransportationTab = ({ results, formData, travelDistance = 0 }) => {
  const transportation = results?.transportation
  const interCityOptions = transportation?.inter_city_options || []
  const localTransportation = transportation?.local_transportation || {}

  return (
    <div className="space-y-6">
      {/* Domestic Travel Info Banner */}
      <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200">
        <div className="flex items-center gap-3 mb-4">
          <Info className="w-6 h-6 text-blue-600" />
          <h3 className="text-lg font-bold text-gray-900">About Your Domestic Journey</h3>
        </div>
        <p className="text-gray-700 mb-3">
          Since this is a domestic trip covering approximately {travelDistance > 0 ? Math.round(travelDistance) : '...'} km, 
          we've focused on ground transportation options that are more practical, cost-effective, and environmentally friendly.
        </p>
        <p className="text-sm text-gray-600 italic mb-3">
          💡 Prices shown are <strong>one-way per trip</strong>. For round-trip, multiply by 2. 
          Total cost for {formData?.travelers || 1} traveler{(formData?.travelers || 1) > 1 ? 's' : ''}.
        </p>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2 px-3 py-2 bg-white rounded-lg">
            <span className="text-green-600 font-semibold">✓</span>
            <span>Eco-friendly</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-white rounded-lg">
            <span className="text-green-600 font-semibold">✓</span>
            <span>Cost-effective</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-2 bg-white rounded-lg">
            <span className="text-green-600 font-semibold">✓</span>
            <span>Scenic routes</span>
          </div>
        </div>
      </div>

      {/* Inter-City Transportation Options */}
      <div className="space-y-4">
        <h3 className="text-xl font-bold text-gray-900 flex items-center">
          <Navigation className="w-6 h-6 mr-2 text-blue-600" />
          Inter-City Transportation Options
        </h3>
        
        {interCityOptions.length > 0 ? (
          interCityOptions.map((option, index) => {
            const getIcon = (type) => {
              switch (type?.toLowerCase()) {
                case 'train': return <Train className="w-6 h-6 text-blue-600" />
                case 'bus': return <Bus className="w-6 h-6 text-green-600" />
                case 'car': 
                case 'car rental':
                case 'private car': return <Car className="w-6 h-6 text-purple-600" />
                default: return <Navigation className="w-6 h-6 text-gray-600" />
              }
            }

            const getColor = (type) => {
              switch (type?.toLowerCase()) {
                case 'train': return 'bg-blue-100'
                case 'bus': return 'bg-green-100'
                case 'car':
                case 'car rental':
                case 'private car': return 'bg-purple-100'
                default: return 'bg-gray-100'
              }
            }

            // Helper function to format duration from hours to readable string
            const formatDuration = (durationHours) => {
              if (!durationHours) return 'Varies'
              const hours = Math.floor(durationHours)
              const minutes = Math.round((durationHours - hours) * 60)
              if (hours > 0 && minutes > 0) {
                return `${hours}h ${minutes}m`
              } else if (hours > 0) {
                return `${hours}h`
              } else {
                return `${minutes}m`
              }
            }

            return (
              <div key={index} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className={`w-14 h-14 ${getColor(option.type)} rounded-lg flex items-center justify-center`}>
                      {getIcon(option.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg capitalize">{option.type || 'Transportation'}</h3>
                      <p className="text-sm text-gray-600">{option.description || 'Comfortable travel option'}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-gray-900">${option.cost_per_trip || option.cost || 'N/A'}</p>
                    <p className="text-sm text-gray-600">
                      {formData.travelers > 1 ? `for ${formData.travelers} travelers` : 'per person'}
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <div>
                      <p className="text-xs text-gray-500">Duration</p>
                      <p className="font-semibold text-gray-900">
                        {option.duration_str || formatDuration(option.duration_hours)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Navigation className="w-4 h-4 text-gray-500" />
                    <div>
                      <p className="text-xs text-gray-500">Distance</p>
                      <p className="font-semibold text-gray-900">
                        {option.distance_km ? `${Math.round(option.distance_km)} km` : `${Math.round(travelDistance)} km`}
                      </p>
                    </div>
                  </div>
                </div>

                {option.notes && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-600 italic">{option.notes}</p>
                  </div>
                )}
              </div>
            )
          })
        ) : (
          <div className="card text-center py-8">
            <Navigation className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">Transportation options are being calculated...</p>
          </div>
        )}
      </div>

      {/* Local Transportation Info */}
      {localTransportation && Object.keys(localTransportation).length > 0 && (
        <div className="card bg-gray-50">
          <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
            <MapPin className="w-5 h-5 mr-2" />
            Local Transportation at Destination
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {localTransportation.daily_cost && (
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <DollarSign className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Daily Cost</p>
                  <p className="font-semibold text-gray-900">${localTransportation.daily_cost}</p>
                </div>
              </div>
            )}
            {localTransportation.options && localTransportation.options.length > 0 && (
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <Navigation className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-600">Available Options</p>
                  <p className="font-semibold text-gray-900">{localTransportation.options.join(', ')}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Flights Tab Component
const FlightsTab = ({ results, formData }) => {
  const priceTrends = results?.price_trends
  const hasPriceTrends = priceTrends && priceTrends.status === 'success'
  const isDomesticTravel = results?.is_domestic_travel || false
  const hasFlights = results?.flights && results.flights.length > 0
  
  // Show domestic travel message if no flights
  if (!hasFlights || isDomesticTravel) {
    return (
      <div className="space-y-6">
        <div className="card text-center py-16">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Navigation className="w-10 h-10 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">
            Domestic Travel - No Flights Needed
          </h3>
          <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
            Great news! For this domestic route, ground transportation is more practical, economical, 
            and environmentally friendly. Check out the Transportation tab for the best travel options.
          </p>
          <div className="flex items-center justify-center gap-8 text-sm">
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">🌱</span>
              </div>
              <p className="font-semibold text-gray-900">Eco-Friendly</p>
              <p className="text-gray-600">Lower carbon footprint</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">💰</span>
              </div>
              <p className="font-semibold text-gray-900">Cost-Effective</p>
              <p className="text-gray-600">Save on travel costs</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">🎭</span>
              </div>
              <p className="font-semibold text-gray-900">Scenic Journey</p>
              <p className="text-gray-600">Enjoy the landscape</p>
            </div>
          </div>
          {results?.travel_distance_km && (
            <div className="mt-6 pt-6 border-t border-gray-200 max-w-md mx-auto">
              <div className="flex items-center justify-center gap-2 text-gray-600">
                <Navigation className="w-4 h-4" />
                <span>Distance: {Math.round(results.travel_distance_km)} km</span>
                <span>•</span>
                <Globe className="w-4 h-4" />
                <span>Type: Domestic</span>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Price Calendar Section */}
      {hasPriceTrends && (
        <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900">💡 Price Calendar - Find Cheaper Dates!</h3>
              <p className="text-sm text-gray-600">Save money by being flexible with your travel dates</p>
            </div>
          </div>
          
          {/* Price Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <p className="text-xs text-gray-500 mb-1">Your Date</p>
              <p className="text-xl font-bold text-blue-600">${priceTrends.target_price || 'N/A'}</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-green-200">
              <p className="text-xs text-gray-500 mb-1">💚 Cheapest</p>
              <p className="text-xl font-bold text-green-600">${priceTrends.statistics?.min_price || 'N/A'}</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-gray-200">
              <p className="text-xs text-gray-500 mb-1">Average</p>
              <p className="text-xl font-bold text-gray-600">${Math.round(priceTrends.statistics?.average_price || 0)}</p>
            </div>
            <div className="bg-white rounded-lg p-3 border border-red-200">
              <p className="text-xs text-gray-500 mb-1">🔴 Most Expensive</p>
              <p className="text-xl font-bold text-red-600">${priceTrends.statistics?.max_price || 'N/A'}</p>
            </div>
          </div>
          
          {/* Recommendations */}
          {priceTrends.recommendations && priceTrends.recommendations.length > 0 && (
            <div className="bg-white rounded-lg p-4 mb-6 border border-blue-200">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <span className="text-xl">💡</span>
                Smart Travel Tips
              </h4>
              <div className="space-y-2">
                {priceTrends.recommendations.map((rec, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-sm">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <p className="text-gray-700">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Price Grid */}
          {priceTrends.price_grid && priceTrends.price_grid.length > 0 && (
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">📅 Prices by Date</h4>
              <div className="overflow-x-auto">
                <div className="grid grid-cols-1 gap-2">
                  {priceTrends.price_grid.slice(0, 10).map((item, idx) => {
                    const isTarget = item.date === priceTrends.target_date
                    const bgColor = item.is_cheap ? 'bg-green-50 border-green-200' : 
                                   item.is_expensive ? 'bg-red-50 border-red-200' : 
                                   'bg-gray-50 border-gray-200'
                    const emoji = item.is_cheap ? '💚' : item.is_expensive ? '🔴' : '💛'
                    
                    return (
                      <div 
                        key={idx} 
                        className={`flex items-center justify-between p-3 rounded-lg border-2 ${bgColor} ${isTarget ? 'ring-2 ring-blue-500' : ''}`}
                      >
                        <div className="flex items-center gap-3">
                          {isTarget && <span className="text-blue-500 font-bold">→</span>}
                          <div>
                            <p className="font-semibold text-gray-900">{item.date}</p>
                            <p className="text-xs text-gray-600">{item.day_of_week}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{emoji}</span>
                            <p className="text-xl font-bold text-gray-900">${item.price}</p>
                          </div>
                          {item.savings !== 0 && (
                            <p className={`text-xs ${item.savings > 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {item.savings > 0 ? `Save $${Math.round(item.savings)}` : `+$${Math.abs(Math.round(item.savings))}`}
                            </p>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
              
              {/* Legend */}
              <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-lg">💚</span>
                  <span className="text-gray-600">Cheap</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg">💛</span>
                  <span className="text-gray-600">Moderate</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-lg">🔴</span>
                  <span className="text-gray-600">Expensive</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Flight Options */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Available Flights</h3>
        {results?.flights?.map((flight, index) => {
          // Flight prices are stored as total for all travelers, divide to get per-person price
          const pricePerPerson = Math.round(flight.price / (formData?.travelers || 1));
          const totalPrice = flight.price;
          
          return (
            <div key={index} className="card">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Plane className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{flight.airline}</h3>
                    <p className="text-sm text-gray-600">{flight.flight_number}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">${pricePerPerson}</p>
                  <p className="text-sm text-gray-600">per person</p>
                  {formData?.travelers > 1 && (
                    <p className="text-xs text-gray-500">${totalPrice} total</p>
                  )}
                </div>
              </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-700">Departure</p>
                <p className="text-lg font-semibold">{flight.departure_time}</p>
                <p className="text-sm text-gray-600">{flight.departure_airport}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Arrival</p>
                <p className="text-lg font-semibold">{flight.arrival_time}</p>
                <p className="text-sm text-gray-600">{flight.arrival_airport}</p>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Duration: {flight.duration}</span>
                <span className="text-gray-600">Class: {flight.class_type || flight.class || 'Economy'}</span>
              </div>
            </div>
          </div>
          );
        })}
      </div>
    </div>
  )
}

// Hotels Tab Component
const HotelsTab = ({ results }) => {
  return (
    <div className="space-y-6">
      {/* Hotels List */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-gray-900 flex items-center">
          <Building className="w-5 h-5 mr-2" />
          Recommended Hotels
        </h3>
        {results?.hotels?.map((hotel, index) => (
      <div key={index} className="card">
        <div className="flex items-start space-x-4">
          <img
            src={hotel.image_url || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=200&h=150&fit=crop'}
            alt={hotel.name}
            className="w-32 h-24 object-cover rounded-lg"
          />
          <div className="flex-1">
            <div className="flex items-start justify-between mb-2">
              <div>
                <h3 className="font-semibold text-gray-900">{hotel.name}</h3>
                <p className="text-sm text-gray-600">{hotel.location}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center justify-end gap-2">
                  <p className="text-xl font-bold text-gray-900">${hotel.price_per_night}</p>
                  {hotel.price_confidence === 'estimated' && (
                    <span 
                      className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-medium"
                      title="Estimated price based on hotel category"
                    >
                      Est.
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600">per night</p>
                {hotel.price_confidence === 'estimated' && (
                  <p className="text-xs text-amber-600 mt-1">Estimated price</p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2 mb-2">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < hotel.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                  }`}
                />
              ))}
              <span className="text-sm text-gray-600">({hotel.rating}/5)</span>
            </div>
            
            <p className="text-sm text-gray-600 mb-2">{hotel.description}</p>
            
            <div className="flex flex-wrap gap-2">
              {hotel.amenities?.map((amenity, i) => (
                <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  {amenity}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
        ))}
      </div>
    </div>
  )
}

// Itinerary Tab Component
const ItineraryTab = ({ results }) => (
  <div className="space-y-6">
    {results?.itinerary?.map((day, dayIndex) => (
      <div key={dayIndex} className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Day {dayIndex + 1} - {day.date}
        </h3>
        
        <div className="space-y-4">
          {day.activities?.map((activity, activityIndex) => (
            <div key={activityIndex} className="flex items-start space-x-4">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                <Clock className="w-4 h-4 text-primary-600" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-medium text-gray-900">{activity.name}</h4>
                  <span className="text-sm text-gray-600">{activity.time}</span>
                </div>
                <p className="text-sm text-gray-600 mb-2">{activity.description}</p>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <MapPin className="w-3 h-3" />
                  <span>{activity.location}</span>
                  {activity.duration && (
                    <>
                      <span>•</span>
                      <span>{activity.duration}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    ))}
  </div>
)

// Costs Tab Component
const CostsTab = ({ results, formData }) => {
  const isDomesticTravel = results?.is_domestic_travel || false
  const hasFlights = results?.flights && results.flights.length > 0

  return (
    <div className="space-y-6">
      {/* Domestic Travel Info */}
      {isDomesticTravel && (
        <div className="card bg-green-50 border-2 border-green-200">
          <div className="flex items-center gap-3">
            <Info className="w-6 h-6 text-green-600 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">Domestic Travel Cost Savings</h4>
              <p className="text-sm text-gray-700">
                Since this is a domestic trip, you're saving money by using ground transportation instead of flights!
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Cost Breakdown</h3>
        
        <div className="space-y-4">
          {/* Show Flights OR Transportation based on travel type */}
          {!isDomesticTravel && hasFlights ? (
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <Plane className="w-4 h-4 text-gray-500" />
                <span className="text-gray-700">Flights ({formData.travelers} travelers)</span>
              </div>
              <span className="font-semibold">${(results?.cost_breakdown?.flights || 0).toFixed(2)}</span>
            </div>
          ) : (
            <>
              {/* Breakdown for Inter-City Transportation: Outbound + Return */}
              {(() => {
                const totalInterCity = results?.cost_breakdown?.transportation || 0
                const oneWayCost = totalInterCity / 2
                
                return (
                  <>
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <div className="flex items-center gap-2">
                        <Navigation className="w-4 h-4 text-green-600" />
                        <span className="text-gray-700">Inter-City (Outbound - {formData.travelers} travelers)</span>
                      </div>
                      <span className="font-semibold text-green-600">
                        ${oneWayCost.toFixed(2)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <div className="flex items-center gap-2">
                        <Navigation className="w-4 h-4 text-green-600" />
                        <span className="text-gray-700">Inter-City (Return - {formData.travelers} travelers)</span>
                      </div>
                      <span className="font-semibold text-green-600">
                        ${oneWayCost.toFixed(2)}
                      </span>
                    </div>
                  </>
                )
              })()}
            </>
          )}
          
          <div className="flex justify-between items-center py-2 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <Building className="w-4 h-4 text-gray-500" />
              <span className="text-gray-700">Accommodation</span>
            </div>
            <span className="font-semibold">${(results?.cost_breakdown?.accommodation || 0).toFixed(2)}</span>
          </div>
          
          {!isDomesticTravel && (
            <div className="flex justify-between items-center py-2 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <Car className="w-4 h-4 text-gray-500" />
                <span className="text-gray-700">Local Transportation</span>
              </div>
              <span className="font-semibold">${(results?.cost_breakdown?.transportation || 0).toFixed(2)}</span>
            </div>
          )}
          
          <div className="flex justify-between items-center py-2 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-gray-500" />
              <span className="text-gray-700">Activities & Experiences</span>
            </div>
            <span className="font-semibold">${(results?.cost_breakdown?.activities || 0).toFixed(2)}</span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-gray-500" />
              <span className="text-gray-700">Food & Dining</span>
            </div>
            <span className="font-semibold">${(results?.cost_breakdown?.food || 0).toFixed(2)}</span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-gray-500" />
              <span className="text-gray-700">Miscellaneous</span>
            </div>
            <span className="font-semibold">${(results?.cost_breakdown?.miscellaneous || 0).toFixed(2)}</span>
          </div>
          
          <div className="flex justify-between items-center py-3 bg-primary-50 rounded-lg px-4 mt-4">
            <span className="text-lg font-semibold text-gray-900">Total Estimated Cost</span>
            <span className="text-2xl font-bold text-primary-600">${(results?.total_cost || 0).toFixed(2)}</span>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Per Person</h3>
        <div className="text-center">
          <p className="text-3xl font-bold text-gray-900">
            ${Math.round((results?.total_cost || 0) / formData.travelers)}
          </p>
          <p className="text-gray-600">per person for the entire trip</p>
        </div>
      </div>

      {/* Savings indicator for domestic travel */}
      {isDomesticTravel && (
        <div className="card bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200">
          <div className="text-center py-4">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="text-3xl">💚</span>
            </div>
            <h4 className="text-lg font-bold text-gray-900 mb-2">Smart Travel Choice!</h4>
            <p className="text-gray-700">
              By choosing ground transportation, you're not only saving money but also reducing your carbon footprint.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default Results
