import React, { createContext, useContext, useState, useEffect } from 'react';
import { subscriptionAPI } from '../services/api';
import { useAuth } from './AuthContext';
import toast from 'react-hot-toast';

const SubscriptionContext = createContext();

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

export const SubscriptionProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user) {
      fetchSubscriptionStatus();
    } else {
      setSubscriptionStatus(null);
    }
  }, [isAuthenticated, user]);

  const fetchSubscriptionStatus = async () => {
    if (!isAuthenticated) {
      setSubscriptionStatus(null);
      return;
    }

    try {
      setLoading(true);
      const response = await subscriptionAPI.getSubscriptionStatus();
      setSubscriptionStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch subscription status:', error);
      // Set default status on error
      setSubscriptionStatus({
        type: 'basic',
        status: 'expired',
        hasUsedFreePlan: false,
        generationsRemaining: 1
      });
    } finally {
      setLoading(false);
    }
  };

  const createCheckoutSession = async () => {
    try {
      setLoading(true);
      const response = await subscriptionAPI.createCheckoutSession();
      const { url } = response.data;
      
      // Redirect to Stripe checkout
      window.location.href = url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      toast.error('Failed to start checkout process. Please try again.');
      setLoading(false);
    }
  };

  const cancelSubscription = async () => {
    try {
      setLoading(true);
      await subscriptionAPI.cancelSubscription();
      toast.success('Subscription cancelled successfully');
      await fetchSubscriptionStatus();
    } catch (error) {
      console.error('Failed to cancel subscription:', error);
      toast.error('Failed to cancel subscription');
    } finally {
      setLoading(false);
    }
  };

  const canGeneratePlan = () => {
    if (!subscriptionStatus) return false;
    
    // Premium users with active subscription
    if (subscriptionStatus.type === 'premium' && subscriptionStatus.status === 'active') {
      return true;
    }
    
    // Basic users with remaining generations
    if (subscriptionStatus.type === 'basic' && subscriptionStatus.generationsRemaining > 0) {
      return true;
    }
    
    return false;
  };

  const value = {
    subscriptionStatus,
    loading,
    fetchSubscriptionStatus,
    createCheckoutSession,
    cancelSubscription,
    canGeneratePlan,
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
};