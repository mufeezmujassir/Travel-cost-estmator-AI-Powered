import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Check, X, Star, Zap, Crown, ArrowLeft, LogOut, MapPin } from 'lucide-react';
import { useSubscription } from '../../context/SubscriptionContext';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import subscriptionApi from '../../services/subscriptionApi';

const PricingPage = () => {
  const { fetchTiers, purchaseTripPass, purchaseAnnualSubscription, subscription, loading: subLoading } = useSubscription();
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [tiers, setTiers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingTier, setProcessingTier] = useState(null);
  const [showDestinationModal, setShowDestinationModal] = useState(false);
  const [selectedTier, setSelectedTier] = useState(null);
  const [destination, setDestination] = useState('');

  useEffect(() => {
    loadTiers();
  }, []);

  const loadTiers = async () => {
    try {
      const data = await fetchTiers();
      setTiers(data.tiers || []);
    } catch (error) {
      console.error('Failed to load tiers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (tier) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (tier.tier === 'trip_pass') {
      // For trip pass, show destination modal
      setSelectedTier(tier);
      setShowDestinationModal(true);
    } else if (tier.tier === 'explorer_annual' || tier.tier === 'travel_pro') {
      setProcessingTier(tier.tier);
      try {
        await purchaseAnnualSubscription(tier.tier);
      } catch (error) {
        console.error('Purchase failed:', error);
        alert('Failed to initiate purchase. Please try again.');
      } finally {
        setProcessingTier(null);
      }
    }
  };

  const handleDestinationSubmit = async () => {
    if (!destination.trim()) {
      alert('Please enter a destination city');
      return;
    }

    setProcessingTier('trip_pass');
    setShowDestinationModal(false);
    
    try {
      await purchaseTripPass(destination.trim());
    } catch (error) {
      console.error('Purchase failed:', error);
      alert('Failed to initiate purchase. Please try again.');
    } finally {
      setProcessingTier(null);
      setDestination('');
    }
  };

  const handleDestinationCancel = () => {
    setShowDestinationModal(false);
    setDestination('');
    setSelectedTier(null);
  };

  const handleManualActivation = async () => {
    if (!destination.trim()) {
      alert('Please enter a destination city');
      return;
    }

    try {
      const result = await subscriptionApi.manualActivateTripPass(destination.trim());
      alert(`Trip pass activated successfully for ${destination}!`);
      setShowDestinationModal(false);
      setDestination('');
      setSelectedTier(null);
      
      // Refresh subscription data
      window.location.reload();
    } catch (error) {
      console.error('Manual activation failed:', error);
      alert('Failed to activate trip pass. Please try again.');
    }
  };

  const handleTestUpgrade = async (tier) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (tier.tier === 'trip_pass') {
      // For trip pass, show destination modal for test
      setSelectedTier(tier);
      setShowDestinationModal(true);
    } else if (tier.tier === 'explorer_annual' || tier.tier === 'travel_pro') {
      try {
        const result = await subscriptionApi.manualUpgradeAnnual(tier.tier);
        alert(`${tier.name} activated successfully!`);
        window.location.reload();
      } catch (error) {
        console.error('Test upgrade failed:', error);
        alert('Failed to activate upgrade. Please try again.');
      }
    }
  };

  const getTierIcon = (tierName) => {
    switch (tierName) {
      case 'trip_pass':
        return <Star className="w-6 h-6" />;
      case 'explorer_annual':
        return <Zap className="w-6 h-6" />;
      case 'travel_pro':
        return <Crown className="w-6 h-6" />;
      default:
        return null;
    }
  };

  const getTierColor = (tierName) => {
    switch (tierName) {
      case 'free':
        return 'from-gray-500 to-gray-600';
      case 'trip_pass':
        return 'from-blue-500 to-blue-600';
      case 'explorer_annual':
        return 'from-purple-500 to-purple-600';
      case 'travel_pro':
        return 'from-amber-500 to-amber-600';
      default:
        return 'from-gray-500 to-gray-600';
    }
  };

  const isCurrentTier = (tierName) => {
    if (tierName === 'trip_pass') {
      // For Trip Pass, check if user has any active Trip Passes
      const hasActiveTripPass = subscription?.active_trip_passes?.some(pass => pass.is_active);
      return hasActiveTripPass;
    }
    return subscription?.tier === tierName;
  };

  const getTripPassButtonText = () => {
    const hasActiveTripPass = subscription?.active_trip_passes?.some(pass => pass.is_active);
    if (hasActiveTripPass) {
      const activePasses = subscription.active_trip_passes.filter(pass => pass.is_active);
      if (activePasses.length === 1) {
        return `Active for ${activePasses[0].destination}`;
      } else {
        return `Active for ${activePasses.length} destinations`;
      }
    }
    return 'Get Started';
  };

  if (loading || subLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Navigation Header */}
        <div className="flex justify-between items-center mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Travel</span>
          </button>
          
          {isAuthenticated && (
            <button
              onClick={logout}
              className="flex items-center gap-2 text-red-600 hover:text-red-700 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Logout</span>
            </button>
          )}
        </div>

        {/* Header */}
        <div className="text-center mb-12">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-gray-900 mb-4"
          >
            Choose Your Perfect Plan
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-gray-600"
          >
            AI-powered travel planning that fits your needs
          </motion.p>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {tiers.map((tier, index) => (
            <motion.div
              key={tier.tier}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`relative bg-white rounded-2xl shadow-xl overflow-hidden ${
                tier.is_recommended ? 'ring-4 ring-blue-500 scale-105' : ''
              }`}
            >
              {/* Recommended Badge */}
              {tier.is_recommended && (
                <div className="absolute top-0 right-0 bg-blue-500 text-white px-4 py-1 rounded-bl-lg text-sm font-semibold">
                  Recommended
                </div>
              )}

              {/* Card Header */}
              <div className={`bg-gradient-to-r ${getTierColor(tier.tier)} p-6 text-white`}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-2xl font-bold">{tier.name}</h3>
                  {getTierIcon(tier.tier)}
                </div>
                <p className="text-white/90 text-sm mb-4">{tier.description}</p>
                <div className="flex items-baseline">
                  <span className="text-4xl font-bold">${tier.price}</span>
                  <span className="ml-2 text-white/80">
                    /{tier.billing_period === 'annual' ? 'year' : tier.billing_period}
                  </span>
                </div>
                {tier.billing_period === 'annual' && (
                  <p className="text-white/80 text-sm mt-1">
                    ${(tier.price / 12).toFixed(2)}/month
                  </p>
                )}
              </div>

              {/* Features List */}
              <div className="p-6">
                <ul className="space-y-3 mb-6">
                  {tier.features.slice(0, 8).map((feature, idx) => (
                    <li key={idx} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700 text-sm">{feature}</span>
                    </li>
                  ))}
                  {tier.features.length > 8 && (
                    <li className="text-gray-500 text-sm italic">
                      +{tier.features.length - 8} more features
                    </li>
                  )}
                </ul>

                {/* CTA Buttons */}
                {tier.tier === 'trip_pass' ? (
                  // Special handling for Trip Pass - always allow purchase
                  <div className="space-y-2">
                    <button
                      onClick={() => handlePurchase(tier)}
                      disabled={processingTier === 'trip_pass'}
                      className={`w-full py-3 px-4 rounded-lg font-semibold transition ${
                        processingTier === 'trip_pass'
                          ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {processingTier === 'trip_pass' ? 'Processing...' : getTripPassButtonText()}
                    </button>
                    {/* Test Button for Trip Pass */}
                    <button
                      onClick={() => handleTestUpgrade(tier)}
                      className="w-full py-2 px-4 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600 transition"
                    >
                      Test (No Payment)
                    </button>
                    {subscription?.active_trip_passes?.some(pass => pass.is_active) && (
                      <p className="text-xs text-gray-500 text-center">
                        Buy additional Trip Passes for other destinations
                      </p>
                    )}
                  </div>
                ) : isCurrentTier(tier.tier) ? (
                  <button
                    disabled
                    className="w-full py-3 px-4 bg-gray-300 text-gray-600 rounded-lg font-semibold cursor-not-allowed"
                  >
                    Current Plan
                  </button>
                ) : tier.tier === 'free' ? (
                  <button
                    onClick={() => navigate('/')}
                    className="w-full py-3 px-4 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
                  >
                    Get Started
                  </button>
                ) : (
                  <div className="space-y-2">
                    <button
                      onClick={() => handlePurchase(tier)}
                      disabled={processingTier === tier.tier}
                      className={`w-full py-3 px-4 bg-gradient-to-r ${getTierColor(tier.tier)} text-white rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50`}
                    >
                      {processingTier === tier.tier ? 'Processing...' : 'Get Started'}
                    </button>
                    {/* Test Button */}
                    <button
                      onClick={() => handleTestUpgrade(tier)}
                      className="w-full py-2 px-4 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600 transition"
                    >
                      Test (No Payment)
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Feature Comparison Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl shadow-xl p-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Feature Comparison</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b-2 border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Feature</th>
                  {tiers.map((tier) => (
                    <th key={tier.tier} className="text-center py-3 px-4 font-semibold text-gray-700">
                      {tier.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                <tr>
                  <td className="py-3 px-4 text-gray-700">Trips per Year</td>
                  {tiers.map((tier) => (
                    <td key={tier.tier} className="text-center py-3 px-4">
                      {tier.limits.trips_per_year === null ? '∞' : tier.limits.trips_per_year}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-3 px-4 text-gray-700">Travel Vibes</td>
                  {tiers.map((tier) => (
                    <td key={tier.tier} className="text-center py-3 px-4">
                      {tier.limits.allowed_vibes.length}/7
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-3 px-4 text-gray-700">Flight Options</td>
                  {tiers.map((tier) => (
                    <td key={tier.tier} className="text-center py-3 px-4">
                      {tier.limits.max_flight_options}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-3 px-4 text-gray-700">Hotel Options</td>
                  {tiers.map((tier) => (
                    <td key={tier.tier} className="text-center py-3 px-4">
                      {tier.limits.max_hotel_options}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-3 px-4 text-gray-700">Itinerary Days</td>
                  {tiers.map((tier) => (
                    <td key={tier.tier} className="text-center py-3 px-4">
                      {tier.limits.max_itinerary_days}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-3 px-4 text-gray-700">Price Calendar</td>
                  {tiers.map((tier) => (
                    <td key={tier.tier} className="text-center py-3 px-4">
                      {tier.limits.has_price_calendar ? (
                        <Check className="w-5 h-5 text-green-500 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-gray-300 mx-auto" />
                      )}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="py-3 px-4 text-gray-700">PDF Export</td>
                  {tiers.map((tier) => (
                    <td key={tier.tier} className="text-center py-3 px-4">
                      {tier.limits.has_pdf_export ? (
                        <Check className="w-5 h-5 text-green-500 mx-auto" />
                      ) : (
                        <X className="w-5 h-5 text-gray-300 mx-auto" />
                      )}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Frequently Asked Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left max-w-4xl mx-auto">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">What is a Trip Pass?</h3>
              <p className="text-gray-600 text-sm">
                A Trip Pass gives you unlimited trip planning for ONE destination for 90 days. Perfect for planning your annual vacation!
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">Can I upgrade later?</h3>
              <p className="text-gray-600 text-sm">
                Yes! You can upgrade to a higher tier anytime. Your unused benefits will be prorated.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">What payment methods do you accept?</h3>
              <p className="text-gray-600 text-sm">
                We accept all major credit cards through our secure Stripe payment processor.
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-semibold text-gray-900 mb-2">Can I cancel anytime?</h3>
              <p className="text-gray-600 text-sm">
                Annual subscriptions can be cancelled anytime. You'll retain access until the end of your billing period.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Destination Modal */}
        {showDestinationModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <MapPin className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Choose Your Destination</h3>
                  <p className="text-gray-600 text-sm">Where would you like to plan your trip?</p>
                </div>
              </div>

              <div className="mb-6">
                <label htmlFor="destination" className="block text-sm font-medium text-gray-700 mb-2">
                  Destination City
                </label>
                <input
                  id="destination"
                  type="text"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  placeholder="e.g., Tokyo, Paris, New York"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  autoFocus
                />
                <p className="text-xs text-gray-500 mt-2">
                  Your Trip Pass will be valid for this destination for 90 days
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleDestinationCancel}
                  className="flex-1 px-4 py-3 text-gray-700 bg-gray-100 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleManualActivation}
                  disabled={!destination.trim()}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Activate (Test)
                </button>
                <button
                  onClick={handleDestinationSubmit}
                  disabled={!destination.trim()}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Pay with Stripe
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PricingPage;

