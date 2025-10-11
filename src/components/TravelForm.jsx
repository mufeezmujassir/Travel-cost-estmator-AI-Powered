import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Calendar, Users, MapPin, DollarSign, ArrowRight, Plane, Sparkles, AlertCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useSubscription } from '../context/SubscriptionContext'
import UpgradeModal from './subscription/UpgradeModal'

const TravelForm = ({ onSubmit, initialData = {} }) => {
  const navigate = useNavigate()
  const { canGenerateTrip, usageStats, subscription, loading: subLoading } = useSubscription()
  const [formData, setFormData] = useState({
    origin: initialData.origin || '',
    destination: initialData.destination || '',
    startDate: initialData.startDate || '',
    returnDate: initialData.returnDate || '',
    travelers: initialData.travelers || 1,
    budget: initialData.budget || 0
  })

  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showUpgradeModal, setShowUpgradeModal] = useState(false)
  const [limitCheckResult, setLimitCheckResult] = useState(null)

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.origin.trim()) newErrors.origin = 'Origin is required'
    if (!formData.destination.trim()) newErrors.destination = 'Destination is required'
    if (!formData.startDate) newErrors.startDate = 'Start date is required'
    if (!formData.returnDate) newErrors.returnDate = 'Return date is required'
    if (formData.travelers < 1) newErrors.travelers = 'At least 1 traveler required'
    if (new Date(formData.startDate) >= new Date(formData.returnDate)) {
      newErrors.returnDate = 'Return date must be after start date'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    
    // Check trip limit before proceeding
    const limitCheck = await canGenerateTrip(formData.destination)
    setLimitCheckResult(limitCheck)
    
    if (!limitCheck.can_generate) {
      setIsSubmitting(false)
      setShowUpgradeModal(true)
      return
    }
    
    // Simulate a brief loading state for better UX
    await new Promise(resolve => setTimeout(resolve, 500))
    
    onSubmit(formData)
    setIsSubmitting(false)
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const today = new Date().toISOString().split('T')[0]

  return (
    <>
      <motion.div
        className="max-w-4xl mx-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Usage Stats Banner */}
        {!subLoading && usageStats && subscription && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-2xl"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">
                  {subscription.tier === 'free' ? '🆓 Free Explorer' : 
                   subscription.tier === 'trip_pass' ? '⭐ Trip Pass' :
                   subscription.tier === 'explorer_annual' ? '⚡ Explorer Annual' : 
                   '👑 Travel Pro'}
                </h3>
                <p className="text-sm text-gray-600">
                  {usageStats.trips_remaining === null ? 
                    'Unlimited trips remaining' : 
                    usageStats.trips_remaining === 0 ?
                    '⚠️ No trips remaining - upgrade to continue' :
                    `${usageStats.trips_remaining} trip${usageStats.trips_remaining === 1 ? '' : 's'} remaining this year`
                  }
                </p>
              </div>
              {(subscription.tier === 'free' || usageStats.trips_remaining === 0) && (
                <button
                  onClick={() => navigate('/pricing')}
                  className="px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg text-sm font-semibold hover:shadow-lg transition"
                >
                  Upgrade
                </button>
              )}
            </div>
          </motion.div>
        )}

        {/* Header Section */}
      <div className="text-center mb-12">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl mx-auto mb-6"
        >
          <Sparkles className="w-10 h-10 text-white" />
        </motion.div>
        <h2 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
          Start Your Journey
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
          Tell us about your travel dreams and our AI will craft the perfect adventure just for you
        </p>
      </div>

      {/* Main Form Card */}
      <motion.div
        className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl p-8 border border-white/60"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.5 }}
      >
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Location Section */}
          <div className="space-y-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-blue-100 rounded-2xl">
                <MapPin className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Where to?</h3>
                <p className="text-gray-500">Tell us your starting point and destination</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Departure City
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={formData.origin}
                    onChange={(e) => handleInputChange('origin', e.target.value)}
                    className={`w-full px-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 transition-all duration-300 placeholder-gray-400 text-lg ${
                      errors.origin ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''
                    }`}
                    placeholder="Where are you starting from?"
                  />
                  {errors.origin && (
                    <motion.p 
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-red-500 text-sm mt-2 flex items-center space-x-1"
                    >
                      <span>⚠</span>
                      <span>{errors.origin}</span>
                    </motion.p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Destination City
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={formData.destination}
                    onChange={(e) => handleInputChange('destination', e.target.value)}
                    className={`w-full px-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/20 transition-all duration-300 placeholder-gray-400 text-lg ${
                      errors.destination ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''
                    }`}
                    placeholder="Where are you heading?"
                  />
                  {errors.destination && (
                    <motion.p 
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-red-500 text-sm mt-2 flex items-center space-x-1"
                    >
                      <span>⚠</span>
                      <span>{errors.destination}</span>
                    </motion.p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Dates Section */}
          <div className="space-y-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-green-100 rounded-2xl">
                <Calendar className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">When are you traveling?</h3>
                <p className="text-gray-500">Select your travel dates</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Start Date
                </label>
                <div className="relative">
                  <input
                    type="date"
                    value={formData.startDate}
                    onChange={(e) => handleInputChange('startDate', e.target.value)}
                    min={today}
                    className={`w-full px-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all duration-300 text-lg ${
                      errors.startDate ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''
                    }`}
                  />
                  {errors.startDate && (
                    <motion.p 
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-red-500 text-sm mt-2 flex items-center space-x-1"
                    >
                      <span>⚠</span>
                      <span>{errors.startDate}</span>
                    </motion.p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Return Date
                </label>
                <div className="relative">
                  <input
                    type="date"
                    value={formData.returnDate}
                    onChange={(e) => handleInputChange('returnDate', e.target.value)}
                    min={formData.startDate || today}
                    className={`w-full px-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-green-500 focus:ring-4 focus:ring-green-500/20 transition-all duration-300 text-lg ${
                      errors.returnDate ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''
                    }`}
                  />
                  {errors.returnDate && (
                    <motion.p 
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-red-500 text-sm mt-2 flex items-center space-x-1"
                    >
                      <span>⚠</span>
                      <span>{errors.returnDate}</span>
                    </motion.p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Travel Details Section */}
          <div className="space-y-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="p-3 bg-orange-100 rounded-2xl">
                <Users className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">Travel Details</h3>
                <p className="text-gray-500">Tell us about your group and budget</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Number of Travelers
                </label>
                <div className="relative">
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.travelers}
                    onChange={(e) => handleInputChange('travelers', parseInt(e.target.value) || 1)}
                    className={`w-full px-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-orange-500 focus:ring-4 focus:ring-orange-500/20 transition-all duration-300 text-lg ${
                      errors.travelers ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''
                    }`}
                  />
                  {errors.travelers && (
                    <motion.p 
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-red-500 text-sm mt-2 flex items-center space-x-1"
                    >
                      <span>⚠</span>
                      <span>{errors.travelers}</span>
                    </motion.p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Budget (USD)
                </label>
                <div className="relative">
                  <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
                    <DollarSign className="w-5 h-5 text-gray-400" />
                  </div>
                  <input
                    type="number"
                    min="0"
                    value={formData.budget}
                    onChange={(e) => handleInputChange('budget', parseInt(e.target.value) || 0)}
                    className="w-full px-12 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl focus:outline-none focus:border-yellow-500 focus:ring-4 focus:ring-yellow-500/20 transition-all duration-300 text-lg placeholder-gray-400"
                    placeholder="Optional - Enter your budget"
                  />
                </div>
                <p className="text-gray-500 text-sm mt-2">
                  Leave empty for automatic budget optimization
                </p>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-5 px-8 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold text-xl rounded-2xl shadow-2xl transition-all duration-300 transform hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-blue-500/25 disabled:opacity-50 disabled:transform-none disabled:hover:from-blue-500 disabled:hover:to-purple-600 group"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isSubmitting ? (
              <div className="flex items-center justify-center space-x-3">
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Planning Your Journey...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-3">
                <span>Continue to Vibe Selection</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform duration-300" />
              </div>
            )}
          </motion.button>
        </form>
      </motion.div>

      {/* Features Preview */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <div className="text-center p-6 bg-blue-50 rounded-2xl border border-blue-100">
          <div className="w-12 h-12 bg-blue-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h4 className="font-semibold text-gray-900 mb-2">AI-Powered Planning</h4>
          <p className="text-gray-600 text-sm">Smart recommendations based on your preferences</p>
        </div>

        <div className="text-center p-6 bg-purple-50 rounded-2xl border border-purple-100">
          <div className="w-12 h-12 bg-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <DollarSign className="w-6 h-6 text-white" />
          </div>
          <h4 className="font-semibold text-gray-900 mb-2">Cost Optimization</h4>
          <p className="text-gray-600 text-sm">Get the best value for your budget</p>
        </div>

        <div className="text-center p-6 bg-green-50 rounded-2xl border border-green-100">
          <div className="w-12 h-12 bg-green-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Plane className="w-6 h-6 text-white" />
          </div>
          <h4 className="font-semibold text-gray-900 mb-2">Personalized Experience</h4>
          <p className="text-gray-600 text-sm">Tailored recommendations just for you</p>
        </div>
      </motion.div>
      </motion.div>

      {/* Upgrade Modal */}
      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        currentTier={subscription?.tier || 'free'}
        reason={limitCheckResult?.reason || 'You\'ve reached your trip limit'}
        suggestedTier={limitCheckResult?.upgrade_required || 'trip_pass'}
      />
    </>
  )
}

export default TravelForm