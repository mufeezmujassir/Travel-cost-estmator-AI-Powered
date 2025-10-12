import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, Sparkles, Zap, Crown } from 'lucide-react';
import { useSubscription } from '../context/SubscriptionContext';

const UpgradeModal = ({ isOpen, onClose }) => {
  const { createCheckoutSession, loading } = useSubscription();

  const handleUpgrade = async () => {
    await createCheckoutSession();
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
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              {/* Close button */}
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>

              {/* Header */}
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-8 text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring" }}
                  className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4"
                >
                  <Crown className="w-10 h-10" />
                </motion.div>
                <h2 className="text-4xl font-bold mb-2">Upgrade to Premium</h2>
                <p className="text-xl opacity-90">Unlock unlimited travel planning</p>
              </div>

              {/* Plans Comparison */}
              <div className="p-8">
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                  {/* Free Plan */}
                  <div className="border-2 border-gray-200 rounded-2xl p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-gray-600" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">Free Plan</h3>
                        <p className="text-sm text-gray-600">Current Plan</p>
                      </div>
                    </div>
                    
                    <div className="mb-6">
                      <span className="text-3xl font-bold text-gray-900">$0</span>
                      <span className="text-gray-600">/lifetime</span>
                    </div>

                    <ul className="space-y-3">
                      <li className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">1 travel plan generation</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">Basic AI recommendations</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <X className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-400 line-through">Unlimited generations</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <X className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-400 line-through">Price calendar insights</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <X className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-400 line-through">Priority support</span>
                      </li>
                    </ul>
                  </div>

                  {/* Premium Plan */}
                  <div className="border-4 border-purple-500 rounded-2xl p-6 relative bg-gradient-to-br from-purple-50 to-blue-50">
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-gradient-to-r from-purple-500 to-blue-500 text-white px-4 py-1 rounded-full text-sm font-bold">
                        RECOMMENDED
                      </span>
                    </div>

                    <div className="flex items-center gap-2 mb-4">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
                        <Zap className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">Premium Plan</h3>
                        <p className="text-sm text-purple-600">Best Value</p>
                      </div>
                    </div>
                    
                    <div className="mb-6">
                      <span className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">$9.99</span>
                      <span className="text-gray-600">/month</span>
                    </div>

                    <ul className="space-y-3">
                      <li className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-900 font-medium">Unlimited travel plans</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-900 font-medium">Advanced AI insights</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-900 font-medium">Price calendar & savings tips</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-900 font-medium">Detailed itineraries</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-900 font-medium">Priority customer support</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-purple-500 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-900 font-medium">Cancel anytime</span>
                      </li>
                    </ul>

                    <button
                      onClick={handleUpgrade}
                      disabled={loading}
                      className="w-full mt-6 py-4 bg-gradient-to-r from-purple-500 to-blue-500 text-white font-bold rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? (
                        <div className="flex items-center justify-center gap-2">
                          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Processing...</span>
                        </div>
                      ) : (
                        'Upgrade Now'
                      )}
                    </button>
                  </div>
                </div>

                {/* Benefits */}
                <div className="bg-gray-50 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Why Go Premium?</h3>
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Sparkles className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Save Money</p>
                        <p className="text-sm text-gray-600">Get the best flight and hotel deals</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Zap className="w-4 h-4 text-purple-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Save Time</p>
                        <p className="text-sm text-gray-600">Instant AI-powered planning</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Check className="w-4 h-4 text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Better Trips</p>
                        <p className="text-sm text-gray-600">Personalized recommendations</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Money Back Guarantee */}
                <div className="text-center mt-6">
                  <p className="text-sm text-gray-600">
                    🔒 Secure payment powered by Stripe • Cancel anytime
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default UpgradeModal;