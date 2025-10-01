import React from 'react'
import { motion } from 'framer-motion'
import { Plane, Brain, MapPin, DollarSign } from 'lucide-react'

const Header = () => {
  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <motion.div 
          className="flex items-center justify-between"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl">
              <Plane className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gradient">
                Travel Cost Estimator
              </h1>
              <p className="text-sm text-gray-600">
                AI-Powered Travel Planning
              </p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Brain className="w-4 h-4 text-primary-500" />
              <span>Emotional Intelligence</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <MapPin className="w-4 h-4 text-secondary-500" />
              <span>Smart Routing</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <DollarSign className="w-4 h-4 text-green-500" />
              <span>Cost Optimization</span>
            </div>
          </div>
        </motion.div>
      </div>
    </header>
  )
}

export default Header
