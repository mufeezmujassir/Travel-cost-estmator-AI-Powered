import React from 'react'
import { motion } from 'framer-motion'
import { Plane, Brain, MapPin, DollarSign, User, LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

const Header = ({ onAuthNavigate, onProfileNavigate, onTravelNavigate, currentView }) => {
  const { user, isAuthenticated, logout } = useAuth()

  const handleLogout = () => {
    // Show logout confirmation toast
    toast.success('Logged out successfully. See you next time!')
    logout()
    if (currentView === 'profile') {
      onTravelNavigate()
    }
  }

  const handleLogin = () => {
    onAuthNavigate('login')
  }

  const handleRegister = () => {
    onAuthNavigate('register')
  }

  const handleProfile = () => {
    onProfileNavigate()
  }

  const handleTravel = () => {
    onTravelNavigate()
  }

  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <motion.div 
          className="flex items-center justify-between"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleTravel}
              className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
            >
              <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl">
                <Plane className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  TravelCost
                </h1>
                <p className="text-sm text-gray-600">
                  AI-Powered Travel Planning
                </p>
              </div>
            </motion.button>
          </div>
          
          {/* Features - Only show on travel view */}
          {currentView === 'travel' && (
            <div className="hidden md:flex items-center space-x-6">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Brain className="w-4 h-4 text-blue-500" />
                <span>Emotional Intelligence</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <MapPin className="w-4 h-4 text-purple-500" />
                <span>Smart Routing</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <DollarSign className="w-4 h-4 text-green-500" />
                <span>Cost Optimization</span>
              </div>
            </div>
          )}

          {/* User Navigation */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              // Authenticated User Menu
              <motion.div 
                className="flex items-center space-x-4"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                {/* Welcome Message - Show on all views except profile */}
                {currentView !== 'profile' && (
                  <div className="hidden sm:block text-sm text-gray-600">
                    Welcome back, <span className="font-semibold text-gray-900">{user?.name}</span>
                  </div>
                )}

                {/* Profile Button - Show when not on profile page */}
                {currentView !== 'profile' && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleProfile}
                    className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all duration-200"
                  >
                    <User className="w-4 h-4" />
                    <span className="hidden sm:block">Profile</span>
                  </motion.button>
                )}

                {/* Back to Travel Button - Show when on profile page */}
                {currentView === 'profile' && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleTravel}
                    className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-all duration-200"
                  >
                    <Plane className="w-4 h-4" />
                    <span>Back to Travel</span>
                  </motion.button>
                )}

                {/* Logout Button */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleLogout}
                  className="flex items-center space-x-2 px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-all duration-200"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden sm:block">Logout</span>
                </motion.button>
              </motion.div>
            ) : (
              // Non-authenticated User Menu
              <motion.div 
                className="flex items-center space-x-3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                {/* Show Home button when not on travel view */}
                {currentView !== 'travel' && (
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleTravel}
                    className="px-4 py-2 text-gray-700 hover:text-blue-600 transition-colors duration-200"
                  >
                    Home
                  </motion.button>
                )}

                {/* Login Button */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleLogin}
                  className="px-4 py-2 text-gray-700 hover:text-blue-600 transition-colors duration-200"
                >
                  Sign In
                </motion.button>

                {/* Register Button */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleRegister}
                  className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-lg hover:shadow-lg transition-all duration-200"
                >
                  Sign Up
                </motion.button>
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Mobile Features - Only show on travel view */}
        {currentView === 'travel' && (
          <motion.div 
            className="md:hidden flex justify-center space-x-6 mt-4 pt-4 border-t border-gray-200"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <div className="flex items-center space-x-2 text-xs text-gray-600">
              <Brain className="w-3 h-3 text-blue-500" />
              <span>AI Powered</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-600">
              <MapPin className="w-3 h-3 text-purple-500" />
              <span>Smart Routes</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-600">
              <DollarSign className="w-3 h-3 text-green-500" />
              <span>Best Prices</span>
            </div>
          </motion.div>
        )}
      </div>
    </header>
  )
}

export default Header