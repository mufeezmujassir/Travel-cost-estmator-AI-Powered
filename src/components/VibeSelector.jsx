import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, Heart, Mountain, Waves, TreePine, Camera, Utensils, Zap, Lock, Crown } from 'lucide-react'
import { useSubscription } from '../context/SubscriptionContext'

const VibeSelector = ({ onVibeSelect, onBack, formData }) => {
  const [selectedVibe, setSelectedVibe] = useState(null)
  const { subscription } = useSubscription()

  const vibes = [
    {
      id: 'romantic',
      name: 'Romantic',
      description: 'Perfect for couples seeking intimate moments',
      icon: Heart,
      color: 'from-pink-400 to-rose-500',
      bgImage: 'https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=400&h=300&fit=crop',
      season: 'spring',
      activities: ['Sunset dinners', 'Couples spa', 'Romantic walks', 'Wine tasting']
    },
    {
      id: 'adventure',
      name: 'Adventure',
      description: 'Thrilling experiences for adrenaline seekers',
      icon: Mountain,
      color: 'from-orange-400 to-red-500',
      bgImage: 'https://images.unsplash.com/photo-1551632811-561732d1e306?w=400&h=300&fit=crop',
      season: 'summer',
      activities: ['Hiking', 'Rock climbing', 'Water sports', 'Extreme sports']
    },
    {
      id: 'beach',
      name: 'Beach Vibes',
      description: 'Relaxing coastal experiences',
      icon: Waves,
      color: 'from-blue-400 to-cyan-500',
      bgImage: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop',
      season: 'summer',
      activities: ['Beach relaxation', 'Water activities', 'Seafood dining', 'Sunset views']
    },
    {
      id: 'nature',
      name: 'Nature & Forest',
      description: 'Connect with natural beauty and wildlife',
      icon: TreePine,
      color: 'from-green-400 to-emerald-500',
      bgImage: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop',
      season: 'spring',
      activities: ['Forest hiking', 'Wildlife watching', 'Nature photography', 'Camping']
    },
    {
      id: 'cultural',
      name: 'Cultural',
      description: 'Explore history, art, and local traditions',
      icon: Camera,
      color: 'from-purple-400 to-indigo-500',
      bgImage: 'https://images.unsplash.com/photo-1539650116574-75c0c6d73c6e?w=400&h=300&fit=crop',
      season: 'autumn',
      activities: ['Museum visits', 'Historical sites', 'Local festivals', 'Art galleries']
    },
    {
      id: 'culinary',
      name: 'Culinary',
      description: 'Food-focused experiences and local cuisine',
      icon: Utensils,
      color: 'from-yellow-400 to-orange-500',
      bgImage: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop',
      season: 'autumn',
      activities: ['Food tours', 'Cooking classes', 'Local markets', 'Fine dining']
    },
    {
      id: 'wellness',
      name: 'Wellness',
      description: 'Rejuvenating and healing experiences',
      icon: Zap,
      color: 'from-teal-400 to-blue-500',
      bgImage: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=300&fit=crop',
      season: 'winter',
      activities: ['Spa treatments', 'Yoga retreats', 'Meditation', 'Healthy cuisine']
    }
  ]

  // Check if a vibe is allowed for the user's subscription tier
  const isVibeAllowed = (vibeId) => {
    if (!subscription) return false
    
    // Get allowed vibes from subscription
    const allowedVibes = subscription.allowed_vibes || []
    return allowedVibes.includes(vibeId)
  }

  const handleVibeSelect = (vibe) => {
    console.log('🎯 Selecting vibe:', vibe.name);
    
    // Check if vibe is allowed
    if (!isVibeAllowed(vibe.id)) {
      console.log('🚫 Vibe not allowed for current subscription');
      // Could show upgrade modal here
      return
    }
    
    setSelectedVibe(vibe)
    // Call onVibeSelect immediately without delay
    onVibeSelect(vibe)
  }

  const getSeasonRecommendation = (vibe) => {
    if (!formData.startDate) {
      return {
        isOptimal: false,
        currentSeason: 'unknown',
        recommendedSeason: vibe.season,
        message: `Select travel dates to get season recommendations`
      }
    }

    const currentDate = new Date(formData.startDate)
    const currentMonth = currentDate.getMonth() + 1
    
    let currentSeason = 'winter'
    if (currentMonth >= 3 && currentMonth <= 5) currentSeason = 'spring'
    else if (currentMonth >= 6 && currentMonth <= 8) currentSeason = 'summer'
    else if (currentMonth >= 9 && currentMonth <= 11) currentSeason = 'autumn'
    
    const isOptimalSeason = vibe.season === currentSeason
    
    return {
      isOptimal: isOptimalSeason,
      currentSeason,
      recommendedSeason: vibe.season,
      message: isOptimalSeason 
        ? `Perfect timing! ${currentSeason} is ideal for ${vibe.name.toLowerCase()} experiences.`
        : `Consider visiting in ${vibe.season} for the best ${vibe.name.toLowerCase()} experience.`
    }
  }

  return (
    <motion.div
      className="max-w-6xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Choose Your Travel Vibe
        </h2>
        <p className="text-gray-600">
          Select the experience that matches your mood and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {vibes.map((vibe) => {
          const Icon = vibe.icon
          const seasonInfo = getSeasonRecommendation(vibe)
          const isAllowed = isVibeAllowed(vibe.id)
          
          return (
            <motion.div
              key={vibe.id}
              className={`relative rounded-xl shadow-lg transition-all duration-300 ${
                !isAllowed 
                  ? 'opacity-60 cursor-not-allowed' 
                  : selectedVibe?.id === vibe.id 
                    ? 'ring-4 ring-blue-500 scale-105 cursor-pointer' 
                    : 'hover:shadow-xl cursor-pointer'
              }`}
              onClick={() => handleVibeSelect(vibe)}
              whileHover={isAllowed ? { scale: 1.02 } : {}}
              whileTap={isAllowed ? { scale: 0.98 } : {}}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: vibes.indexOf(vibe) * 0.1 }}
            >
              <div className="relative h-48 overflow-hidden rounded-t-xl">
                <img
                  src={vibe.bgImage}
                  alt={vibe.name}
                  className="w-full h-full object-cover"
                />
                <div className={`absolute inset-0 bg-gradient-to-t ${vibe.color} opacity-60`} />
                
                {/* Lock overlay for restricted vibes */}
                {!isAllowed && (
                  <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-2">
                        <Lock className="w-8 h-8 text-white" />
                      </div>
                      <p className="text-white font-semibold">Premium Only</p>
                    </div>
                  </div>
                )}
                
                <div className="absolute top-4 right-4">
                  <div className={`p-2 rounded-full bg-white/20 backdrop-blur-sm`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div className="absolute bottom-4 left-4 right-4">
                  <h3 className="text-xl font-bold text-white mb-1">{vibe.name}</h3>
                  <p className="text-white/90 text-sm">{vibe.description}</p>
                </div>
              </div>
              
              <div className="p-4 bg-white rounded-b-xl">
                <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium mb-3 ${
                  seasonInfo.isOptimal 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {seasonInfo.isOptimal ? '✓ Optimal Season' : '⚠ Consider Timing'}
                </div>
                
                <p className="text-sm text-gray-600 mb-3">{seasonInfo.message}</p>
                
                <div className="space-y-1">
                  <p className="text-xs font-medium text-gray-700">Popular Activities:</p>
                  <div className="flex flex-wrap gap-1">
                    {vibe.activities.slice(0, 2).map((activity, index) => (
                      <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                        {activity}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="text-center">
        <button
          onClick={onBack}
          className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <ArrowLeft className="w-4 h-4 inline mr-2" />
          Back to Form
        </button>
      </div>

      {selectedVibe && (
        <motion.div
          className="mt-6 p-4 bg-blue-50 rounded-lg text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <p className="text-blue-800">
            Selected: <strong>{selectedVibe.name}</strong> - Generating your travel plan...
          </p>
        </motion.div>
      )}

      {/* Upgrade prompt for users with limited vibes */}
      {subscription && subscription.tier === 'free' && (
        <motion.div
          className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-center gap-3 mb-2">
            <Crown className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">Unlock All Travel Vibes</h3>
          </div>
          <p className="text-gray-600 text-sm text-center mb-3">
            Upgrade to access all 7 travel vibes including Romantic, Adventure, Beach, Nature, Cultural, Culinary, and Wellness experiences!
          </p>
          <div className="flex justify-center gap-2">
            <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
              Free: Limited vibes
            </span>
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
              Paid: All 7 vibes
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default VibeSelector