import React, { useState } from 'react'
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
import ChatWidget from './components/ChatWidget'
import { useTravelEstimation } from './hooks/useTravelEstimation'
import { useAuth } from './context/AuthContext'
import { SubscriptionProvider } from './context/SubscriptionContext'
import toast from 'react-hot-toast'

function App() {
  const [currentView, setCurrentView] = useState('travel') // 'travel', 'login', 'register', 'profile', 'about'
  const [currentStep, setCurrentStep] = useState(1)
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

  const handleFormSubmit = (data) => {
    if (!isAuthenticated) {
      toast.error('Please sign in to continue')
      setFormData(data)
      setCurrentView('login')
      return
    }
    setFormData(data)
    setCurrentStep(2)
  }

  const handleVibeSelect = async (vibe) => {
    console.log('🎯 Handling vibe selection:', vibe.name)
    setSelectedVibe(vibe)
    setCurrentStep(3)
    
    try {
      await estimateTravel(formData, vibe)
      console.log('✅ Travel estimation completed')
    } catch (error) {
      console.error('❌ Travel estimation failed:', error)
      if (error.response?.status === 403) {
        toast.error('Generation limit reached. Please upgrade to premium.')
        setCurrentStep(1)
      }
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

  const handleAuthNavigate = (view) => {
    setCurrentView(view)
  }

  const handleProfileNavigate = () => {
    setCurrentView('profile')
  }

  const handleTravelNavigate = () => {
    setCurrentView('travel')
    setCurrentStep(1)
  }

  const handleAboutNavigate = () => {
    setCurrentView('about')
  }

  const handleLoginSuccess = () => {
    toast.success('Welcome back!')
    setCurrentView('travel')
  }

  const handleRegisterSuccess = () => {
    toast.success('Account created successfully! Welcome!')
    setCurrentView('travel')
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <SubscriptionProvider>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <Header 
          onAuthNavigate={handleAuthNavigate}
          onProfileNavigate={handleProfileNavigate}
          onTravelNavigate={handleTravelNavigate}
          onAboutNavigate={handleAboutNavigate}
          currentView={currentView}
        />
        
        <main className="container mx-auto px-4 py-8">
          <AnimatePresence mode="wait">
            {currentView === 'login' && (
              <motion.div
                key="login"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Login 
                  onSuccess={handleLoginSuccess}
                  onSwitchToRegister={() => setCurrentView('register')}
                />
              </motion.div>
            )}

            {currentView === 'register' && (
              <motion.div
                key="register"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Register 
                  onSuccess={handleRegisterSuccess}
                  onSwitchToLogin={() => setCurrentView('login')}
                />
              </motion.div>
            )}

            {currentView === 'profile' && (
              <motion.div
                key="profile"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Profile onBack={handleTravelNavigate} />
              </motion.div>
            )}

            {currentView === 'about' && (
              <motion.div
                key="about"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Aboutus />
              </motion.div>
            )}

            {currentView === 'travel' && (
              <AnimatePresence mode="wait">
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
              </AnimatePresence>
            )}
          </AnimatePresence>
        </main>
         <ChatWidget />
      </div>
    </SubscriptionProvider>
  )
}

export default App