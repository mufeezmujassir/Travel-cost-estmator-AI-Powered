import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Star, Zap, Crown, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const UpgradeModal = ({ isOpen, onClose, currentTier, reason, suggestedTier }) => {
  const navigate = useNavigate();

  const tierInfo = {
    free: {
      name: 'Free Explorer',
      icon: null,
      color: 'gray',
    },
    trip_pass: {
      name: 'Trip Pass',
      icon: Star,
      color: 'blue',
      price: '$15',
      period: 'one-time',
      benefits: [
        'Unlimited planning for ONE destination',
        'Valid for 90 days',
        'All 7 travel vibes',
        'Up to 5 flight & hotel options',
        'Full 30-day itinerary',
        'Price trend calendar',
        'PDF export',
      ],
    },
    explorer_annual: {
      name: 'Explorer Annual',
      icon: Zap,
      color: 'purple',
      price: '$59',
      period: 'per year',
      benefits: [
        '3 complete trip estimates per year',
        'All premium features',
        'Trip comparison tool',
        'Unlimited saved versions',
        'Priority support',
      ],
    },
    travel_pro: {
      name: 'Travel Pro',
      icon: Crown,
      color: 'amber',
      price: '$149',
      period: 'per year',
      benefits: [
        'UNLIMITED trip estimates',
        'Multi-city trip planning',
        'Up to 10 flight & hotel options',
        '60-day itineraries',
        'API access',
        'White-label PDFs',
        '24-hour priority support',
      ],
    },
  };

  const current = tierInfo[currentTier] || tierInfo.free;
  const suggested = tierInfo[suggestedTier] || tierInfo.trip_pass;
  const Icon = suggested.icon;

  const handleUpgrade = () => {
    onClose();
    navigate('/pricing');
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className={`bg-gradient-to-r from-${suggested.color}-500 to-${suggested.color}-600 p-6 text-white relative`}>
                <button
                  onClick={onClose}
                  className="absolute top-4 right-4 p-1 hover:bg-white/20 rounded-full transition"
                >
                  <X className="w-6 h-6" />
                </button>
                
                <div className="flex items-center space-x-3 mb-2">
                  {Icon && <Icon className="w-8 h-8" />}
                  <h2 className="text-2xl font-bold">Upgrade Required</h2>
                </div>
                
                <p className="text-white/90">
                  {reason || 'You\'ve reached the limit for your current plan'}
                </p>
              </div>

              {/* Content */}
              <div className="p-6">
                {/* Current vs Suggested Comparison */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  {/* Current Tier */}
                  <div className="bg-gray-50 rounded-lg p-4 border-2 border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Current Plan</p>
                    <h3 className="text-lg font-bold text-gray-900">{current.name}</h3>
                    <p className="text-sm text-gray-600 mt-2">Limited features</p>
                  </div>

                  {/* Suggested Tier */}
                  <div className={`bg-gradient-to-br from-${suggested.color}-50 to-${suggested.color}-100 rounded-lg p-4 border-2 border-${suggested.color}-300 relative`}>
                    <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full font-semibold">
                      Recommended
                    </div>
                    <p className="text-xs text-gray-600 mb-1">Upgrade To</p>
                    <h3 className="text-lg font-bold text-gray-900">{suggested.name}</h3>
                    <p className={`text-sm font-semibold text-${suggested.color}-600 mt-2`}>
                      {suggested.price} <span className="text-xs font-normal">{suggested.period}</span>
                    </p>
                  </div>
                </div>

                {/* Benefits */}
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">What you'll get:</h3>
                  <ul className="space-y-2">
                    {suggested.benefits.map((benefit, index) => (
                      <motion.li
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="flex items-start"
                      >
                        <ArrowRight className={`w-5 h-5 text-${suggested.color}-500 mr-2 flex-shrink-0 mt-0.5`} />
                        <span className="text-gray-700">{benefit}</span>
                      </motion.li>
                    ))}
                  </ul>
                </div>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={handleUpgrade}
                    className={`flex-1 py-3 px-6 bg-gradient-to-r from-${suggested.color}-500 to-${suggested.color}-600 text-white rounded-lg font-semibold hover:shadow-lg transition`}
                  >
                    Upgrade Now
                  </button>
                  <button
                    onClick={onClose}
                    className="flex-1 py-3 px-6 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
                  >
                    Maybe Later
                  </button>
                </div>

                {/* Additional Info */}
                <p className="text-xs text-gray-500 text-center mt-4">
                  {suggestedTier === 'trip_pass' && '✨ One-time payment, no recurring charges'}
                  {(suggestedTier === 'explorer_annual' || suggestedTier === 'travel_pro') && '💳 Cancel anytime, keep access until end of period'}
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default UpgradeModal;

