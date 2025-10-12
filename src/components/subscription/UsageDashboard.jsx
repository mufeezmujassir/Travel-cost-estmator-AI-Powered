import React from 'react';
import { motion } from 'framer-motion';
import { 
  Star, Zap, Crown, Calendar, TrendingUp, 
  MapPin, Award, Clock, ArrowRight 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useSubscription } from '../../context/SubscriptionContext';
import subscriptionApi from '../../services/subscriptionApi';

const UsageDashboard = () => {
  const { subscription, usageStats, getCurrentTierName, isPremium, loading, refreshSubscription } = useSubscription();
  const navigate = useNavigate();

  const handleManualUpgrade = async (tier) => {
    try {
      const result = await subscriptionApi.manualUpgradeAnnual(tier);
      alert(`Successfully upgraded to ${tier.replace('_', ' ')}!`);
      // Refresh subscription data
      await refreshSubscription();
    } catch (error) {
      console.error('Manual upgrade failed:', error);
      alert('Failed to upgrade subscription. Please try again.');
    }
  };

  const handleManualTrackTrip = async () => {
    const destination = prompt('Enter destination for trip tracking:');
    if (destination) {
      try {
        const result = await subscriptionApi.manualTrackTrip(destination);
        alert(`Trip to ${destination} tracked successfully!`);
        // Refresh subscription data
        await refreshSubscription();
      } catch (error) {
        console.error('Manual trip tracking failed:', error);
        alert('Failed to track trip. Please try again.');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!subscription || !usageStats) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800">Unable to load subscription data</p>
      </div>
    );
  }

  const getTierIcon = () => {
    switch (subscription.tier) {
      case 'trip_pass':
        return <Star className="w-6 h-6" />;
      case 'explorer_annual':
        return <Zap className="w-6 h-6" />;
      case 'travel_pro':
        return <Crown className="w-6 h-6" />;
      default:
        return <Award className="w-6 h-6" />;
    }
  };

  const getTierColor = () => {
    switch (subscription.tier) {
      case 'trip_pass':
        return 'blue';
      case 'explorer_annual':
        return 'purple';
      case 'travel_pro':
        return 'amber';
      default:
        return 'gray';
    }
  };

  const color = getTierColor();

  const calculateProgress = () => {
    if (usageStats.trips_remaining === null) {
      return 100; // Unlimited
    }
    const total = usageStats.usage.trips_generated_this_year + usageStats.trips_remaining;
    if (total === 0) return 0;
    return (usageStats.usage.trips_generated_this_year / total) * 100;
  };

  const progress = calculateProgress();

  return (
    <div className="space-y-6">
      {/* Tier Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className={`bg-gradient-to-r from-${color}-500 to-${color}-600 rounded-xl shadow-lg p-6 text-white`}
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            {getTierIcon()}
            <div>
              <h3 className="text-2xl font-bold">{getCurrentTierName()}</h3>
              <p className="text-white/80 text-sm">
                {subscription.status === 'active' ? 'Active' : 'Inactive'}
              </p>
            </div>
          </div>
          {!isPremium() && (
            <button
              onClick={() => navigate('/pricing')}
              className="bg-white text-gray-900 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition"
            >
              Upgrade
            </button>
          )}
          {subscription.tier === 'trip_pass' && (
            <div className="space-y-2">
              <button
                onClick={() => handleManualUpgrade('explorer_annual')}
                className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition"
              >
                Upgrade (Test)
              </button>
              <button
                onClick={() => navigate('/pricing')}
                className="w-full bg-white text-gray-900 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition"
              >
                Pay with Stripe
              </button>
            </div>
          )}
        </div>

        {/* Expiry Info */}
        {subscription.expires_at && (
          <div className="flex items-center text-white/90 text-sm">
            <Clock className="w-4 h-4 mr-2" />
            <span>
              {usageStats.subscription_expires_in_days !== null && 
                `Expires in ${usageStats.subscription_expires_in_days} days`
              }
            </span>
          </div>
        )}
      </motion.div>

      {/* Usage Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-xl shadow-lg p-6"
      >
        <h3 className="text-lg font-bold text-gray-900 mb-4">Usage Statistics</h3>

        {/* Trip Counter */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-700 font-medium">Trips Generated</span>
            <span className="text-gray-900 font-bold">
              {usageStats.usage.trips_generated_this_year}
              {usageStats.trips_remaining !== null && ` / ${usageStats.usage.trips_generated_this_year + usageStats.trips_remaining}`}
              {usageStats.trips_remaining === null && ' / ∞'}
            </span>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(progress, 100)}%` }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className={`bg-gradient-to-r from-${color}-500 to-${color}-600 h-2.5 rounded-full`}
            />
          </div>

          {usageStats.trips_remaining !== null && usageStats.trips_remaining > 0 && (
            <p className="text-sm text-gray-500 mt-1">
              {usageStats.trips_remaining} {usageStats.trips_remaining === 1 ? 'trip' : 'trips'} remaining this year
            </p>
          )}
          
          {usageStats.trips_remaining === 0 && (
            <p className="text-sm text-red-500 mt-1">
              You've used all your trips for this year. Upgrade for more!
            </p>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center text-gray-600 mb-1">
              <TrendingUp className="w-4 h-4 mr-2" />
              <span className="text-sm">Lifetime Trips</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {usageStats.usage.trips_generated_lifetime}
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center text-gray-600 mb-1">
              <Calendar className="w-4 h-4 mr-2" />
              <span className="text-sm">Last Trip</span>
            </div>
            <p className="text-sm font-semibold text-gray-900">
              {usageStats.usage.last_trip_date 
                ? new Date(usageStats.usage.last_trip_date).toLocaleDateString()
                : 'Never'
              }
            </p>
          </div>
        </div>

        {/* Reset Date */}
        {usageStats.days_until_reset !== null && usageStats.days_until_reset > 0 && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <Clock className="w-4 h-4 inline mr-1" />
              Your yearly limits reset in <strong>{usageStats.days_until_reset} days</strong>
            </p>
            <button
              onClick={handleManualTrackTrip}
              className="mt-2 bg-green-600 text-white px-3 py-1 rounded text-sm font-semibold hover:bg-green-700 transition"
            >
              Track Trip (Test)
            </button>
          </div>
        )}
      </motion.div>

      {/* Active Trip Passes */}
      {usageStats.active_trip_passes && usageStats.active_trip_passes.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h3 className="text-lg font-bold text-gray-900 mb-4">Active Trip Passes</h3>
          
          <div className="space-y-3">
            {usageStats.active_trip_passes.map((pass, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200"
              >
                <div className="flex items-center space-x-3">
                  <MapPin className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-semibold text-gray-900">{pass.region}</p>
                    <p className="text-sm text-gray-600">
                      {pass.trips_generated} trips generated
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-blue-600">
                    {pass.days_remaining} days left
                  </p>
                  <p className="text-xs text-gray-500">
                    Expires {new Date(pass.expires_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Upgrade CTA (for free users) */}
      {!isPremium() && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white"
        >
          <h3 className="text-xl font-bold mb-2">Unlock Premium Features</h3>
          <p className="text-white/90 mb-4">
            Get unlimited access to all travel planning features and create the perfect itinerary.
          </p>
          <button
            onClick={() => navigate('/pricing')}
            className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition inline-flex items-center"
          >
            View Plans
            <ArrowRight className="w-5 h-5 ml-2" />
          </button>
        </motion.div>
      )}

      {/* Upgrade Options for Explorer Annual Users */}
      {subscription.tier === 'explorer_annual' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-200"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-4">Upgrade to Travel Pro</h3>
          <p className="text-gray-600 mb-6">
            You're currently on Explorer Annual with 3 trips per year to ANY destination. Upgrade to Travel Pro for unlimited trips to ANY destination and premium features!
          </p>
          
          <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-lg p-4 border border-amber-200">
            <div className="flex items-center mb-3">
              <Crown className="w-5 h-5 text-amber-600 mr-2" />
              <h4 className="font-bold text-gray-900">Travel Pro</h4>
              <span className="ml-auto bg-amber-200 text-amber-800 px-2 py-1 rounded-full text-xs font-semibold">
                Recommended
              </span>
            </div>
            <p className="text-2xl font-bold text-amber-600 mb-2">$149/year</p>
              <ul className="text-sm text-gray-600 space-y-1 mb-4">
                <li>• UNLIMITED trip estimates to ANY destination (vs 3 per year)</li>
                <li>• All premium features</li>
                <li>• Up to 10 flight & hotel options (vs 5)</li>
                <li>• Extended 60-day itinerary (vs 30 days)</li>
                <li>• Multi-city trip planning</li>
                <li>• API access & white-label PDFs</li>
                <li>• Priority support</li>
              </ul>
            <div className="space-y-2">
              <button
                onClick={() => handleManualUpgrade('travel_pro')}
                className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition"
              >
                Upgrade (Test)
              </button>
              <button
                onClick={() => navigate('/pricing')}
                className="w-full bg-amber-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-amber-700 transition"
              >
                Pay with Stripe
              </button>
            </div>
          </div>

          <div className="mt-4 text-center">
            <button
              onClick={() => navigate('/pricing')}
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
            >
              View All Plans
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </div>
        </motion.div>
      )}

      {/* Upgrade Options for Trip Pass Users */}
      {subscription.tier === 'trip_pass' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-xl shadow-lg p-6 border border-gray-200"
        >
          <h3 className="text-xl font-bold text-gray-900 mb-4">Upgrade to Annual Plans</h3>
          <p className="text-gray-600 mb-6">
            Your Trip Pass is great for one destination, but annual plans give you access to plan trips to ANY destination in the world!
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Explorer Annual */}
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
              <div className="flex items-center mb-3">
                <Zap className="w-5 h-5 text-purple-600 mr-2" />
                <h4 className="font-bold text-gray-900">Explorer Annual</h4>
              </div>
              <p className="text-2xl font-bold text-purple-600 mb-2">$59/year</p>
              <ul className="text-sm text-gray-600 space-y-1 mb-4">
                <li>• 3 complete trip estimates per year to ANY destination</li>
                <li>• All 7 travel vibes available</li>
                <li>• Up to 5 flight & hotel options</li>
                <li>• Full 30-day itinerary</li>
              </ul>
              <div className="space-y-2">
                <button
                  onClick={() => handleManualUpgrade('explorer_annual')}
                  className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition"
                >
                  Upgrade (Test)
                </button>
                <button
                  onClick={() => navigate('/pricing')}
                  className="w-full bg-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-purple-700 transition"
                >
                  Pay with Stripe
                </button>
              </div>
            </div>

            {/* Travel Pro */}
            <div className="bg-gradient-to-r from-amber-50 to-amber-100 rounded-lg p-4 border border-amber-200">
              <div className="flex items-center mb-3">
                <Crown className="w-5 h-5 text-amber-600 mr-2" />
                <h4 className="font-bold text-gray-900">Travel Pro</h4>
              </div>
              <p className="text-2xl font-bold text-amber-600 mb-2">$149/year</p>
              <ul className="text-sm text-gray-600 space-y-1 mb-4">
                <li>• UNLIMITED trip estimates to ANY destination</li>
                <li>• All premium features</li>
                <li>• Up to 10 flight & hotel options</li>
                <li>• Extended 60-day itinerary</li>
              </ul>
              <div className="space-y-2">
                <button
                  onClick={() => handleManualUpgrade('travel_pro')}
                  className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition"
                >
                  Upgrade (Test)
                </button>
                <button
                  onClick={() => navigate('/pricing')}
                  className="w-full bg-amber-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-amber-700 transition"
                >
                  Pay with Stripe
                </button>
              </div>
            </div>
          </div>

          <div className="mt-4 text-center">
            <button
              onClick={() => navigate('/pricing')}
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center"
            >
              View All Plans
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default UsageDashboard;

