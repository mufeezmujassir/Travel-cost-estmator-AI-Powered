import React from 'react'
import { motion } from 'framer-motion'
import { Plane, Brain, MapPin, DollarSign, Users } from 'lucide-react'

const LoadingSpinner = () => {
  const agents = [
    { icon: Brain, name: 'Emotional Intelligence Agent', color: 'text-purple-500' },
    { icon: Plane, name: 'Flight Search Agent', color: 'text-blue-500' },
    { icon: MapPin, name: 'Transportation Agent', color: 'text-green-500' },
    { icon: DollarSign, name: 'Cost Estimation Agent', color: 'text-yellow-500' },
    { icon: Users, name: 'Recommendation Agent', color: 'text-pink-500' }
  ]

  return (
    <div className="max-w-4xl mx-auto text-center">
      <motion.div
        className="mb-8"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="relative w-32 h-32 mx-auto mb-6">
          <motion.div
            className="absolute inset-0 border-4 border-primary-200 rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          />
          <motion.div
            className="absolute inset-2 border-4 border-primary-500 rounded-full border-t-transparent"
            animate={{ rotate: -360 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <Plane className="w-8 h-8 text-primary-600 animate-float" />
          </div>
        </div>
        
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Our AI Agents Are Working
        </h2>
        <p className="text-gray-600 text-lg">
          Analyzing your preferences and creating the perfect travel plan...
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {agents.map((agent, index) => {
          const Icon = agent.icon
          return (
            <motion.div
              key={agent.name}
              className="card text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <motion.div
                className={`w-12 h-12 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center`}
                animate={{ 
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity, 
                  delay: index * 0.2 
                }}
              >
                <Icon className={`w-6 h-6 ${agent.color}`} />
              </motion.div>
              <h3 className="font-medium text-gray-900 mb-1">{agent.name}</h3>
              <motion.div
                className="flex space-x-1 justify-center"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.1 + 0.5 }}
              >
                {[0, 1, 2].map((dot) => (
                  <motion.div
                    key={dot}
                    className="w-2 h-2 bg-primary-400 rounded-full"
                    animate={{
                      scale: [1, 1.5, 1],
                      opacity: [0.5, 1, 0.5]
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      delay: dot * 0.2 + index * 0.1
                    }}
                  />
                ))}
              </motion.div>
            </motion.div>
          )
        })}
      </div>

      <motion.div
        className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          What Our Agents Are Doing:
        </h3>
        <div className="space-y-2 text-left max-w-2xl mx-auto">
          <motion.div
            className="flex items-center space-x-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-gray-700">Analyzing your selected vibe and emotional preferences</span>
          </motion.div>
          <motion.div
            className="flex items-center space-x-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.9 }}
          >
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span className="text-gray-700">Searching for the best flight options and prices</span>
          </motion.div>
          <motion.div
            className="flex items-center space-x-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 1.1 }}
          >
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
            <span className="text-gray-700">Finding hotels that match your vibe and budget</span>
          </motion.div>
          <motion.div
            className="flex items-center space-x-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 1.3 }}
          >
            <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
            <span className="text-gray-700">Calculating transportation costs and routes</span>
          </motion.div>
          <motion.div
            className="flex items-center space-x-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 1.5 }}
          >
            <div className="w-2 h-2 bg-pink-500 rounded-full animate-pulse" />
            <span className="text-gray-700">Creating personalized day-by-day itinerary</span>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}

export default LoadingSpinner
