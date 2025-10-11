import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import TravelForm from './components/TravelForm'
import VibeSelector from './components/VibeSelector'
import Results from './components/Results'
import LoadingSpinner from './components/LoadingSpinner'
import Login from './components/auth/Login'
import Register from './components/auth/Register'
import Profile from './components/auth/Profile'
import Aboutus from './components/aboutus'
import { useTravelEstimation } from './hooks/useTravelEstimation'
import { useAuth } from './context/AuthContext'

function App() {
  const [currentStep, setCurrentStep] = useState(1)
  const [currentView, setCurrentView] = useState('travel') 
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    startDate: '',
    returnDate: '',
    travelers: 1,
    budget: 0
  })
  const [selectedVibe, setSelectedVibe] = useState(null)
  
  const { 
    estimateTravel, 
    results, 
    loading, 
    error 
  } = useTravelEstimation()

  const { user, isAuthenticated, loading: authLoading } = useAuth()

  // Redirect to travel view if user logs in while on auth pages
  useEffect(() => {
    if (isAuthenticated && (currentView === 'login' || currentView === 'register')) {
      setCurrentView('travel')
    }
  }, [isAuthenticated, currentView])

  const handleFormSubmit = (data) => {
    if (!isAuthenticated) {
      setCurrentView('login')
      setFormData(data) // Save form data for after login
      return
    }
    setFormData(data)
    setCurrentStep(2)
  }

const handleVibeSelect = async (vibe) => {
  console.log('🎯 Handling vibe selection:', vibe.name);
  setSelectedVibe(vibe);
  setCurrentStep(3); // Move to results step immediately
  
  try {
    // Start the travel estimation process
    await estimateTravel(formData, vibe);
    console.log('✅ Travel estimation completed');
  } catch (error) {
    console.error('❌ Travel estimation failed:', error);
    // You might want to handle this error in the UI
  }
}

  const handleReset = () => {
    setCurrentStep(1)
    setFormData({
      origin: '',
      destination: '',
      startDate: '',
      returnDate: '',
      travelers: 1,
      budget: 0
    })
    setSelectedVibe(null)
  }

  const handleAuthSuccess = () => {
    if (formData.origin && formData.destination) {
      // If user was filling out form before auth, continue to vibe selection
      setCurrentStep(2)
    }
    setCurrentView('travel')
  }

  const handleNavigateToAuth = (view) => {
    setCurrentView(view)
  }

  const handleNavigateToProfile = () => {
    setCurrentView('profile')
  }

  const handleBackToTravel = () => {
    setCurrentView('travel')
  }

  // Show loading spinner while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  // Handler for About Us navigation
  const handleNavigateToAbout = () => {
    setCurrentView('aboutus')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header 
        onAuthNavigate={handleNavigateToAuth}
        onProfileNavigate={handleNavigateToProfile}
        onTravelNavigate={handleBackToTravel}
        onAboutNavigate={handleNavigateToAbout}
        currentView={currentView}
      />
      
      <main className="container mx-auto px-4 py-8">
        <AnimatePresence mode="wait">
          {/* Authentication Views */}
          {currentView === 'login' && (
            <motion.div
              key="login"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Login 
                onSuccess={handleAuthSuccess}
                onSwitchToRegister={() => setCurrentView('register')}
                onBack={handleBackToTravel}
              />
            </motion.div>
          )}

          {currentView === 'register' && (
            <motion.div
              key="register"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Register 
                onSuccess={handleAuthSuccess}
                onSwitchToLogin={() => setCurrentView('login')}
                onBack={handleBackToTravel}
              />
            </motion.div>
          )}

          {currentView === 'profile' && (
            <motion.div
              key="profile"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Profile onBack={handleBackToTravel} />
            </motion.div>
          )}

          {/* About Us View */}
          {currentView === 'aboutus' && (
            <motion.div
              key="aboutus"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Aboutus />
            </motion.div>
          )}

          {/* Travel Planning Views - Show for both authenticated and non-authenticated users */}
          {currentView === 'travel' && (
            <>
              {currentStep === 1 && (
                <motion.div
                  key="form"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 50 }}
                  transition={{ duration: 0.3 }}
                >
                  {isAuthenticated && (
                    <motion.div
                      initial={{ opacity: 0, y: -20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg"
                    >
                      <p className="text-green-800 text-center">
                        Welcome back, {user?.name}! 🎉
                      </p>
                    </motion.div>
                  )}
                  <TravelForm 
                    onSubmit={handleFormSubmit}
                    initialData={formData}
                  />
                </motion.div>
              )}
              
              {currentStep === 2 && (
                <motion.div
                  key="vibe"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 50 }}
                  transition={{ duration: 0.3 }}
                >
                  <VibeSelector 
                    onVibeSelect={handleVibeSelect}
                    onBack={() => setCurrentStep(1)}
                    formData={formData}
                  />
                </motion.div>
              )}
              
              {currentStep === 3 && (
                <motion.div
                  key="results"
                  initial={{ opacity: 0, x: -50 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 50 }}
                  transition={{ duration: 0.3 }}
                >
                  {loading ? (
                    <LoadingSpinner />
                  ) : (
                    <Results 
                      results={results}
                      error={error}
                      onReset={handleReset}
                      formData={formData}
                      selectedVibe={selectedVibe}
                    />
                  )}
                </motion.div>
              )}
            </>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App