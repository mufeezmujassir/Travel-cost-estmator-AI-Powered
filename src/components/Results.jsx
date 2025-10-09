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
  Navigation
} from 'lucide-react'
import { AnimatePresence } from 'framer-motion'
const Results = ({ results, error, onReset, formData, selectedVibe }) => {
  const [activeTab, setActiveTab] = useState('overview')

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

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Heart },
    { id: 'flights', name: 'Flights', icon: Plane },
    { id: 'hotels', name: 'Hotels', icon: MapPin },
    { id: 'itinerary', name: 'Itinerary', icon: Calendar },
    { id: 'costs', name: 'Costs', icon: DollarSign }
  ]

  return (
    <motion.div
      className="max-w-6xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
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
        <button className="btn-secondary">
          <Download className="w-4 h-4 inline mr-2" />
          Download PDF
        </button>
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
        
        {activeTab === 'flights' && (
          <motion.div
            key="flights"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3 }}
          >
            <FlightsTab results={results} />
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
            <CostsTab results={results} formData={formData} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Overview Tab Component
const OverviewTab = ({ results, formData, selectedVibe }) => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="card text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Plane className="w-8 h-8 text-blue-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Best Flight</h3>
        <p className="text-2xl font-bold text-blue-600">
          ${results?.flights?.[0]?.price || 'N/A'}
        </p>
        <p className="text-sm text-gray-600">
          {results?.flights?.[0]?.airline || 'Multiple options'}
        </p>
      </div>
      
      <div className="card text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <MapPin className="w-8 h-8 text-green-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Recommended Hotel</h3>
        <div className="flex items-center justify-center gap-2">
          <p className="text-2xl font-bold text-green-600">
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
          ${results?.total_cost || 'N/A'}
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

// Flights Tab Component
const FlightsTab = ({ results }) => {
  const priceTrends = results?.price_trends
  const hasPriceTrends = priceTrends && priceTrends.status === 'success'
  
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
        {results?.flights?.map((flight, index) => (
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
                <p className="text-2xl font-bold text-gray-900">${flight.price}</p>
                <p className="text-sm text-gray-600">per person</p>
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
        ))}
      </div>
    </div>
  )
}

// Hotels Tab Component
const HotelsTab = ({ results }) => (
  <div className="space-y-4">
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
)

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
const CostsTab = ({ results, formData }) => (
  <div className="space-y-6">
    <div className="card">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">Cost Breakdown</h3>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center py-2 border-b border-gray-200">
          <span className="text-gray-700">Flights ({formData.travelers} travelers)</span>
          <span className="font-semibold">${results?.cost_breakdown?.flights || 0}</span>
        </div>
        
        <div className="flex justify-between items-center py-2 border-b border-gray-200">
          <span className="text-gray-700">Accommodation</span>
          <span className="font-semibold">${results?.cost_breakdown?.accommodation || 0}</span>
        </div>
        
        <div className="flex justify-between items-center py-2 border-b border-gray-200">
          <span className="text-gray-700">Transportation</span>
          <span className="font-semibold">${results?.cost_breakdown?.transportation || 0}</span>
        </div>
        
        <div className="flex justify-between items-center py-2 border-b border-gray-200">
          <span className="text-gray-700">Activities & Experiences</span>
          <span className="font-semibold">${results?.cost_breakdown?.activities || 0}</span>
        </div>
        
        <div className="flex justify-between items-center py-2 border-b border-gray-200">
          <span className="text-gray-700">Food & Dining</span>
          <span className="font-semibold">${results?.cost_breakdown?.food || 0}</span>
        </div>
        
        <div className="flex justify-between items-center py-2 border-b border-gray-200">
          <span className="text-gray-700">Miscellaneous</span>
          <span className="font-semibold">${results?.cost_breakdown?.miscellaneous || 0}</span>
        </div>
        
        <div className="flex justify-between items-center py-3 bg-primary-50 rounded-lg px-4">
          <span className="text-lg font-semibold text-gray-900">Total Estimated Cost</span>
          <span className="text-2xl font-bold text-primary-600">${results?.total_cost || 0}</span>
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
  </div>
)

export default Results
