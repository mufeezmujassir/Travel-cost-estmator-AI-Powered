import React, { createContext, useContext, useState, useEffect } from 'react';
import subscriptionApi from '../services/subscriptionApi';
import { useAuth } from './AuthContext';

const SubscriptionContext = createContext();

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

export const SubscriptionProvider = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  const [subscription, setSubscription] = useState(null);
  const [tiers, setTiers] = useState([]);
  const [usageStats, setUsageStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch subscription data when user logs in
  useEffect(() => {
    if (isAuthenticated && user) {
      fetchSubscriptionData();
    } else {
      // Reset subscription data when user logs out
      setSubscription(null);
      setUsageStats(null);
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  const fetchSubscriptionData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch subscription status and usage stats in parallel
      const [subscriptionData, usageData] = await Promise.all([
        subscriptionApi.getSubscriptionStatus(),
        subscriptionApi.getUsageStats(),
      ]);

      setSubscription(subscriptionData);
      setUsageStats(usageData);
    } catch (err) {
      console.error('Error fetching subscription data:', err);
      setError(err.response?.data?.detail || 'Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  // Fetch tiers (can be called without authentication)
  const fetchTiers = async () => {
    try {
      const tiersData = await subscriptionApi.getTiers();
      setTiers(tiersData.tiers);
      return tiersData;
    } catch (err) {
      console.error('Error fetching tiers:', err);
      throw err;
    }
  };

  // Check if user can generate trip for a destination
  const canGenerateTrip = async (destination) => {
    try {
      const result = await subscriptionApi.checkTripLimit(destination);
      return result;
    } catch (err) {
      console.error('Error checking trip limit:', err);
      // Return error response from API
      if (err.response?.status === 402) {
        return {
          can_generate: false,
          requires_upgrade: true,
          reason: err.response.data.detail?.message || 'Subscription upgrade required',
        };
      }
      throw err;
    }
  };

  // Check if user needs to upgrade
  const needsUpgrade = () => {
    if (!subscription) return false;
    return subscription.tier === 'free' && !subscription.can_generate_trip;
  };

  // Get remaining trips count
  const getRemainingTrips = () => {
    if (!usageStats) return null;
    return usageStats.trips_remaining;
  };

  // Get current tier name
  const getCurrentTierName = () => {
    if (!subscription) return 'Free';
    const tierNames = {
      free: 'Free Explorer',
      trip_pass: 'Trip Pass',
      explorer_annual: 'Explorer Annual',
      travel_pro: 'Travel Pro',
    };
    return tierNames[subscription.tier] || subscription.tier;
  };

  // Check if user has premium tier
  const isPremium = () => {
    return subscription?.is_premium || false;
  };

  // Check if user has specific tier or higher
  const hasTier = (requiredTier) => {
    if (!subscription) return false;
    
    const tierHierarchy = {
      free: 0,
      trip_pass: 1,
      explorer_annual: 2,
      travel_pro: 3,
    };
    
    const currentLevel = tierHierarchy[subscription.tier] || 0;
    const requiredLevel = tierHierarchy[requiredTier] || 0;
    
    return currentLevel >= requiredLevel;
  };

  // Initiate Trip Pass purchase
  const purchaseTripPass = async (destination) => {
    try {
      const successUrl = `${window.location.origin}/payment-success`;
      const cancelUrl = `${window.location.origin}/pricing`;
      
      const { checkout_url } = await subscriptionApi.createTripPassCheckout(
        destination,
        successUrl,
        cancelUrl
      );
      
      // Redirect to Stripe checkout
      window.location.href = checkout_url;
    } catch (err) {
      console.error('Error purchasing trip pass:', err);
      throw err;
    }
  };

  // Initiate annual subscription purchase
  const purchaseAnnualSubscription = async (tier) => {
    try {
      const successUrl = `${window.location.origin}/payment-success`;
      const cancelUrl = `${window.location.origin}/pricing`;
      
      const { checkout_url } = await subscriptionApi.createAnnualSubscriptionCheckout(
        tier,
        successUrl,
        cancelUrl
      );
      
      // Redirect to Stripe checkout
      window.location.href = checkout_url;
    } catch (err) {
      console.error('Error purchasing annual subscription:', err);
      throw err;
    }
  };

  // Cancel subscription
  const cancelSubscription = async () => {
    try {
      await subscriptionApi.cancelSubscription();
      // Refresh subscription data
      await fetchSubscriptionData();
      return true;
    } catch (err) {
      console.error('Error cancelling subscription:', err);
      throw err;
    }
  };

  // Refresh subscription data
  const refreshSubscription = async () => {
    await fetchSubscriptionData();
  };

  const value = {
    // State
    subscription,
    tiers,
    usageStats,
    loading,
    error,
    
    // Methods
    fetchTiers,
    canGenerateTrip,
    needsUpgrade,
    getRemainingTrips,
    getCurrentTierName,
    isPremium,
    hasTier,
    purchaseTripPass,
    purchaseAnnualSubscription,
    cancelSubscription,
    refreshSubscription,
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
};

