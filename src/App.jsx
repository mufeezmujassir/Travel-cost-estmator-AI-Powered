import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Header from './components/Header'
import TravelForm from './components/TravelForm'
import VibeSelector from './components/VibeSelector'
import Results from './components/Results'
import LoadingSpinner from './components/LoadingSpinner'
import { useTravelEstimation } from './hooks/useTravelEstimation'

function App() {
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

  const handleFormSubmit = (data) => {
    setFormData(data)
    setCurrentStep(2)
  }

  const handleVibeSelect = async (vibe) => {
    setSelectedVibe(vibe)
    setCurrentStep(3)
    
    // Start the travel estimation process
    await estimateTravel(formData, vibe)
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <AnimatePresence mode="wait">
          {currentStep === 1 && (
            <motion.div
              key="form"
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              transition={{ duration: 0.3 }}
            >
              <TravelForm onSubmit={handleFormSubmit} />
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
      </main>
    </div>
  )
}

export default App
