import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Calendar, Users, MapPin, DollarSign, ArrowRight } from 'lucide-react'

const TravelForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    startDate: '',
    returnDate: '',
    travelers: 1,
    budget: 0
  })

  const [errors, setErrors] = useState({})

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

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validateForm()) {
      onSubmit(formData)
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const today = new Date().toISOString().split('T')[0]

  return (
    <motion.div
      className="max-w-2xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Plan Your Perfect Trip
        </h2>
        <p className="text-gray-600">
          Tell us about your travel preferences and let our AI agents create the perfect itinerary
        </p>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <MapPin className="w-4 h-4 inline mr-2" />
                Origin City
              </label>
              <input
                type="text"
                value={formData.origin}
                onChange={(e) => handleInputChange('origin', e.target.value)}
                className={`input-field ${errors.origin ? 'border-red-500' : ''}`}
                placeholder="e.g., New York"
              />
              {errors.origin && <p className="text-red-500 text-sm mt-1">{errors.origin}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <MapPin className="w-4 h-4 inline mr-2" />
                Destination City
              </label>
              <input
                type="text"
                value={formData.destination}
                onChange={(e) => handleInputChange('destination', e.target.value)}
                className={`input-field ${errors.destination ? 'border-red-500' : ''}`}
                placeholder="e.g., Tokyo"
              />
              {errors.destination && <p className="text-red-500 text-sm mt-1">{errors.destination}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Start Date
              </label>
              <input
                type="date"
                value={formData.startDate}
                onChange={(e) => handleInputChange('startDate', e.target.value)}
                min={today}
                className={`input-field ${errors.startDate ? 'border-red-500' : ''}`}
              />
              {errors.startDate && <p className="text-red-500 text-sm mt-1">{errors.startDate}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-2" />
                Return Date
              </label>
              <input
                type="date"
                value={formData.returnDate}
                onChange={(e) => handleInputChange('returnDate', e.target.value)}
                min={formData.startDate || today}
                className={`input-field ${errors.returnDate ? 'border-red-500' : ''}`}
              />
              {errors.returnDate && <p className="text-red-500 text-sm mt-1">{errors.returnDate}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Users className="w-4 h-4 inline mr-2" />
                Number of Travelers
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={formData.travelers}
                onChange={(e) => handleInputChange('travelers', parseInt(e.target.value))}
                className={`input-field ${errors.travelers ? 'border-red-500' : ''}`}
              />
              {errors.travelers && <p className="text-red-500 text-sm mt-1">{errors.travelers}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <DollarSign className="w-4 h-4 inline mr-2" />
                Budget (USD)
              </label>
              <input
                type="number"
                min="0"
                value={formData.budget}
                onChange={(e) => handleInputChange('budget', parseInt(e.target.value))}
                className="input-field"
                placeholder="Optional"
              />
            </div>
          </div>

          <motion.button
            type="submit"
            className="w-full btn-primary flex items-center justify-center space-x-2 py-3 text-lg"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <span>Continue to Vibe Selection</span>
            <ArrowRight className="w-5 h-5" />
          </motion.button>
        </form>
      </div>
    </motion.div>
  )
}

export default TravelForm
