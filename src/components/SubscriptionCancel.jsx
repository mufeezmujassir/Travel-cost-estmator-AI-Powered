import React from 'react';
import { motion } from 'framer-motion';
import { XCircle, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const SubscriptionCancel = () => {
  const navigate = useNavigate();

  const handleBack = () => {
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
          className="w-20 h-20 bg-gradient-to-r from-gray-400 to-gray-500 rounded-full flex items-center justify-center mx-auto mb-6"
        >
          <XCircle className="w-12 h-12 text-white" />
        </motion.div>

        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Subscription Cancelled
        </h1>
        
        <p className="text-gray-600 mb-8">
          You cancelled the subscription process. No charges have been made to your account.
        </p>

        <div className="bg-blue-50 rounded-2xl p-6 mb-8">
          <p className="text-gray-700 text-sm">
            💡 You still have your free plan available. Upgrade anytime to unlock unlimited travel planning!
          </p>
        </div>

        <button
          onClick={handleBack}
          className="w-full py-4 bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700 text-white font-bold rounded-xl shadow-lg transition-all duration-200 flex items-center justify-center gap-2"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Home</span>
        </button>
      </motion.div>
    </div>
  );
};

export {  SubscriptionCancel };