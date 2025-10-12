// src/components/SubscriptionSuccess.jsx
import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Sparkles, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useSubscription } from '../context/SubscriptionContext';
import toast from 'react-hot-toast';

const SubscriptionSuccess = () => {
  const navigate = useNavigate();
  const { fetchSubscriptionStatus } = useSubscription();

  useEffect(() => {
    // Refresh subscription status
    fetchSubscriptionStatus();
    toast.success('🎉 Welcome to Premium!');
  }, []);

  const handleContinue = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md w-full bg-white rounded-3xl shadow-2xl p-8 text-center"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring" }}
          className="w-20 h-20 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6"
        >
          <CheckCircle className="w-12 h-12 text-white" />
        </motion.div>

        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Subscription Activated!
        </h1>
        
        <p className="text-gray-600 mb-8">
          You now have unlimited access to AI-powered travel planning. Start creating amazing trips!
        </p>

        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-6 mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-purple-600" />
            <h3 className="font-semibold text-gray-900">Premium Benefits</h3>
          </div>
          <ul className="text-left space-y-2 text-sm text-gray-700">
            <li className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              Unlimited travel plans
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              Advanced AI insights
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              Price calendar & savings tips
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              Priority support
            </li>
          </ul>
        </div>

        <button
          onClick={handleContinue}
          className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold rounded-xl shadow-lg transition-all duration-200 flex items-center justify-center gap-2"
        >
          <span>Start Planning Your Trip</span>
          <ArrowRight className="w-5 h-5" />
        </button>
      </motion.div>
    </div>
  );
};

export { SubscriptionSuccess } ;