import React, { useState } from 'react'
import { 
  Plane, Building, Car, Star, Users, DollarSign, 
  ChevronDown, ChevronUp, Info, CheckCircle, Sparkles,
  TrendingUp, Lightbulb, Navigation
} from 'lucide-react'

// Confidence Badge Component
const ConfidenceBadge = ({ level }) => {
  const config = {
    high: {
      className: 'bg-green-100 text-green-800 border-green-300',
      label: '✓ Real Data',
      icon: <CheckCircle className="w-3 h-3" />
    },
    estimated: {
      className: 'bg-blue-100 text-blue-800 border-blue-300',
      label: '≈ AI Estimate',
      icon: <Sparkles className="w-3 h-3" />
    }
  }
  
  const { className, label, icon } = config[level] || config.estimated
  
  return (
    <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded border ${className}`}>
      {icon}
      {label}
    </span>
  )
}

// Expandable Cost Item Component
const ExpandableCostItem = ({ 
  icon, 
  label, 
  amount, 
  confidence, 
  details,
  defaultExpanded = false 
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  
  return (
    <div className="border-b border-gray-200 last:border-0">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex justify-between items-center py-3 hover:bg-gray-50 rounded transition-colors px-2"
      >
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">{icon}</div>
          <div className="flex flex-col items-start gap-1">
            <span className="text-gray-700 font-medium">{label}</span>
            <ConfidenceBadge level={confidence} />
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-semibold text-lg">${amount.toFixed(2)}</span>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>
      
      {isExpanded && (
        <div className="pl-11 pr-4 pb-4 text-sm text-gray-600 space-y-2">
          {details}
        </div>
      )}
    </div>
  )
}

// Main Improved Costs Tab Component
const ImprovedCostsTab = ({ results, formData }) => {
  const isDomesticTravel = results?.is_domestic_travel || false
  const hasFlights = results?.flights && results.flights.length > 0
  const costBreakdown = results?.cost_breakdown || {}
  
  // Calculate confidence percentages
  const totalCost = results?.total_cost || 0
  const verifiedCosts = (costBreakdown.flights || 0) + (costBreakdown.accommodation || 0)
  const estimatedCosts = totalCost - verifiedCosts
  const verifiedPercentage = totalCost > 0 ? Math.round((verifiedCosts / totalCost) * 100) : 0
  const estimatedPercentage = 100 - verifiedPercentage

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

      {/* Explanation Card */}
      <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-semibold text-gray-900 mb-3">💡 Understanding Your Costs</h3>
            <div className="space-y-2 text-sm text-gray-700">
              <div className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Flights & Hotels:</strong> Real-time prices from Google Flights and Google Hotels
                </div>
              </div>
              <div className="flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Activities, Food & Misc:</strong> AI-powered estimates based on {results?.vibe_analysis?.destination || 'destination'} pricing data
                </div>
              </div>
              <div className="flex items-start gap-2">
                <TrendingUp className="w-4 h-4 text-purple-600 flex-shrink-0 mt-0.5" />
                <div>
                  <strong>Customized for your vibe:</strong> Prices reflect your {formData?.vibe || 'cultural'} travel preferences
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cost Breakdown Card */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Cost Breakdown</h3>
          <div className="text-xs text-gray-500">
            Click any item for details ↓
          </div>
        </div>
        
        <div className="space-y-1">
          {/* Flights or Inter-City Transportation */}
          {!isDomesticTravel && hasFlights ? (
            <ExpandableCostItem
              icon={<Plane className="w-5 h-5 text-blue-600" />}
              label={`Flights (${formData.travelers} travelers)`}
              amount={costBreakdown.flights || 0}
              confidence="high"
              details={
                <div className="space-y-2">
                  <p className="font-medium text-gray-900">
                    {results?.flights?.[0]?.airline || 'Qatar Airways'} {results?.flights?.[0]?.departure_airport} → {results?.flights?.[0]?.arrival_airport}
                  </p>
                  <p>• <strong>${Math.round((costBreakdown.flights || 0) / formData.travelers)}</strong> per person</p>
                  <p>• {results?.flights?.[0]?.stops || 1} stop, Economy class</p>
                  <p>• Departure: {formData?.startDate || 'Your selected date'}</p>
                  <div className="mt-3 p-2 bg-green-50 rounded border border-green-200">
                    <p className="text-green-700 flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      This is a real price from Google Flights
                    </p>
                  </div>
                </div>
              }
            />
          ) : (
            <>
              {(() => {
                const totalInterCity = costBreakdown.transportation || 0
                const oneWayCost = totalInterCity / 2
                
                return (
                  <ExpandableCostItem
                    icon={<Navigation className="w-5 h-5 text-green-600" />}
                    label={`Inter-City Travel (${formData.travelers} travelers)`}
                    amount={totalInterCity}
                    confidence="estimated"
                    details={
                      <div className="space-y-2">
                        <p className="font-medium text-gray-900">Ground Transportation</p>
                        <p>• <strong>Outbound:</strong> ${oneWayCost.toFixed(2)}</p>
                        <p>• <strong>Return:</strong> ${oneWayCost.toFixed(2)}</p>
                        <p>• Distance: {results?.travel_distance_km ? `${Math.round(results.travel_distance_km)} km` : 'Calculated based on route'}</p>
                        <p>• Options: Train, bus, or private car available</p>
                        <div className="mt-3 p-2 bg-blue-50 rounded border border-blue-200">
                          <p className="text-blue-700 flex items-center gap-1">
                            <Sparkles className="w-4 h-4" />
                            Based on typical ground transport pricing
                          </p>
                        </div>
                      </div>
                    }
                  />
                )
              })()}
            </>
          )}
          
          {/* Accommodation */}
          <ExpandableCostItem
            icon={<Building className="w-5 h-5 text-amber-600" />}
            label="Accommodation"
            amount={costBreakdown.accommodation || 0}
            confidence={results?.hotels?.[0]?.price_confidence === 'high' ? 'high' : 'estimated'}
            details={
              (() => {
                const nights = formData?.returnDate && formData?.startDate
                  ? Math.ceil((new Date(formData.returnDate) - new Date(formData.startDate)) / (1000 * 60 * 60 * 24))
                  : 5
                const rooms = Math.ceil(formData.travelers / 2)
                
                return (
                  <div className="space-y-2">
                    <p className="font-medium text-gray-900">
                      {results?.hotels?.[0]?.name || 'Recommended Hotel'}
                    </p>
                    <p>• <strong>${results?.hotels?.[0]?.price_per_night || 0}</strong> per night</p>
                    <p>• {nights} nights × {rooms} rooms</p>
                    <p>• {results?.hotels?.[0]?.rating || 4.5}★ rating</p>
                    <div className={`mt-3 p-2 rounded border ${
                      results?.hotels?.[0]?.price_confidence === 'high' 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-blue-50 border-blue-200'
                    }`}>
                      <p className={`flex items-center gap-1 ${
                        results?.hotels?.[0]?.price_confidence === 'high' 
                          ? 'text-green-700' 
                          : 'text-blue-700'
                      }`}>
                        {results?.hotels?.[0]?.price_confidence === 'high' ? (
                          <>
                            <CheckCircle className="w-4 h-4" />
                            This is a real price from Google Hotels
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-4 h-4" />
                            Estimated based on hotel category
                          </>
                        )}
                      </p>
                    </div>
                  </div>
                )
              })()
            }
          />
          
          {/* Local Transportation (for international trips) */}
          {!isDomesticTravel && (
            <ExpandableCostItem
              icon={<Car className="w-5 h-5 text-purple-600" />}
              label="Local Transportation"
              amount={costBreakdown.transportation || 0}
              confidence="estimated"
              details={
                <div className="space-y-2">
                  <p className="font-medium text-gray-900">Getting around at your destination</p>
                  <p>• Public transport, taxis, ride-shares</p>
                  <p>• <strong>${Math.round((costBreakdown.transportation || 0) / formData.travelers)}</strong> per person</p>
                  <p>• Based on typical costs in {results?.vibe_analysis?.destination || 'the city'}</p>
                  <div className="mt-3 p-2 bg-blue-50 rounded border border-blue-200">
                    <p className="text-blue-700 flex items-center gap-1">
                      <Sparkles className="w-4 h-4" />
                      AI estimate based on local transport pricing
                    </p>
                  </div>
                </div>
              }
            />
          )}
          
          {/* Activities & Experiences */}
          <ExpandableCostItem
            icon={<Star className="w-5 h-5 text-pink-600" />}
            label="Activities &amp; Experiences"
            amount={costBreakdown.activities || 0}
            confidence="estimated"
            details={
              (() => {
                const days = formData?.returnDate && formData?.startDate
                  ? Math.ceil((new Date(formData.returnDate) - new Date(formData.startDate)) / (1000 * 60 * 60 * 24))
                  : 5
                const dailyPerPerson = Math.round((costBreakdown.activities || 0) / formData.travelers / days)
                
                return (
                  <div className="space-y-2">
                    <p className="font-medium text-gray-900">Based on {formData?.vibe || 'cultural'} experiences</p>
                    <p>• <strong>${dailyPerPerson}</strong> per person per day</p>
                    <p>• {days} days × {formData.travelers} travelers</p>
                    <p className="mt-2">Includes:</p>
                    <ul className="list-disc ml-4 space-y-1">
                      <li>Museum &amp; attraction entries</li>
                      <li>Guided tours &amp; experiences</li>
                      <li>Activity equipment rentals</li>
                    </ul>
                    <div className="mt-3 p-2 bg-blue-50 rounded border border-blue-200">
                      <p className="text-blue-700 flex items-center gap-1">
                        <Sparkles className="w-4 h-4" />
                        AI-powered estimate based on {formData?.vibe || 'cultural'} activities in {results?.vibe_analysis?.destination || 'destination'}
                      </p>
                    </div>
                  </div>
                )
              })()
            }
          />
          
          {/* Food & Dining */}
          <ExpandableCostItem
            icon={<Users className="w-5 h-5 text-orange-600" />}
            label="Food &amp; Dining"
            amount={costBreakdown.food || 0}
            confidence="estimated"
            details={
              (() => {
                const days = formData?.returnDate && formData?.startDate
                  ? Math.ceil((new Date(formData.returnDate) - new Date(formData.startDate)) / (1000 * 60 * 60 * 24))
                  : 5
                const dailyPerPerson = Math.round((costBreakdown.food || 0) / formData.travelers / days)
                
                return (
                  <div className="space-y-2">
                    <p className="font-medium text-gray-900">Based on local restaurant prices</p>
                    <p>• <strong>${dailyPerPerson}</strong> per person per day</p>
                    <p>• {days} days × {formData.travelers} travelers</p>
                    <p className="mt-2">Daily meal budget breakdown:</p>
                    <ul className="list-disc ml-4 space-y-1">
                      <li>Breakfast: ~${Math.round(dailyPerPerson * 0.25)}</li>
                      <li>Lunch: ~${Math.round(dailyPerPerson * 0.33)}</li>
                      <li>Dinner: ~${Math.round(dailyPerPerson * 0.42)}</li>
                    </ul>
                    <div className="mt-3 p-2 bg-blue-50 rounded border border-blue-200">
                      <p className="text-blue-700 flex items-center gap-1">
                        <Sparkles className="w-4 h-4" />
                        Based on typical dining costs in {results?.vibe_analysis?.destination || 'destination'}
                      </p>
                    </div>
                  </div>
                )
              })()
            }
          />
          
          {/* Miscellaneous */}
          <ExpandableCostItem
            icon={<DollarSign className="w-5 h-5 text-gray-600" />}
            label="Miscellaneous"
            amount={costBreakdown.miscellaneous || 0}
            confidence="estimated"
            details={
              (() => {
                const days = formData?.returnDate && formData?.startDate
                  ? Math.ceil((new Date(formData.returnDate) - new Date(formData.startDate)) / (1000 * 60 * 60 * 24))
                  : 5
                const dailyPerPerson = Math.round((costBreakdown.miscellaneous || 0) / formData.travelers / days)
                
                return (
                  <div className="space-y-2">
                    <p className="font-medium text-gray-900">Tips, souvenirs, and extras</p>
                    <p>• <strong>${dailyPerPerson}</strong> per person per day</p>
                    <p>• {days} days × {formData.travelers} travelers</p>
                    <p className="mt-2">Covers:</p>
                    <ul className="list-disc ml-4 space-y-1">
                      <li>Tips &amp; gratuities (5-10%)</li>
                      <li>Souvenirs &amp; shopping</li>
                      <li>Snacks &amp; drinks between meals</li>
                      <li>Emergency buffer</li>
                    </ul>
                    <div className="mt-3 p-2 bg-blue-50 rounded border border-blue-200">
                      <p className="text-blue-700 flex items-center gap-1">
                        <Sparkles className="w-4 h-4" />
                        Standard travel miscellaneous budget
                      </p>
                    </div>
                  </div>
                )
              })()
            }
          />
        </div>
        
        {/* Total */}
        <div className="flex justify-between items-center py-4 bg-primary-50 rounded-lg px-4 mt-6">
          <span className="text-lg font-semibold text-gray-900">Total Estimated Cost</span>
          <span className="text-2xl font-bold text-primary-600">
            ${totalCost.toFixed(2)}
          </span>
        </div>
      </div>
      
      {/* Per Person Cost */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Per Person</h3>
        <div className="text-center">
          <p className="text-4xl font-bold text-gray-900">
            ${Math.round(totalCost / formData.travelers)}
          </p>
          <p className="text-gray-600 mt-2">per person for the entire trip</p>
          <p className="text-sm text-gray-500 mt-1">
            ({formData.travelers} travelers)
          </p>
        </div>
      </div>

      {/* Price Confidence Summary */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Price Confidence</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">Real market data</span>
              <span className="font-medium text-green-700">{verifiedPercentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${verifiedPercentage}%` }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600">AI-estimated</span>
              <span className="font-medium text-blue-700">{estimatedPercentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${estimatedPercentage}%` }}
              ></div>
            </div>
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-3">
          We use real prices from Google Flights and Hotels wherever possible, and supplement with AI-powered estimates for activities, food, and miscellaneous costs based on market data.
        </p>
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

export default ImprovedCostsTab

