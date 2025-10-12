import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Subscription API Service
 * Handles all subscription-related API calls
 */
const subscriptionApi = {
  /**
   * Get current user's subscription status
   */
  async getSubscriptionStatus() {
    try {
      const response = await api.get('/api/subscription/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching subscription status:', error);
      throw error;
    }
  },

  /**
   * Get all available subscription tiers
   */
  async getTiers() {
    try {
      const response = await api.get('/api/subscription/tiers');
      return response.data;
    } catch (error) {
      console.error('Error fetching tiers:', error);
      throw error;
    }
  },

  /**
   * Check if user can generate trip for destination
   * @param {string} destination - Destination city
   */
  async checkTripLimit(destination) {
    try {
      const response = await api.post('/api/subscription/check-trip-limit', {
        destination,
      });
      return response.data;
    } catch (error) {
      console.error('Error checking trip limit:', error);
      throw error;
    }
  },

  /**
   * Get detailed usage statistics
   */
  async getUsageStats() {
    try {
      const response = await api.get('/api/subscription/usage');
      return response.data;
    } catch (error) {
      console.error('Error fetching usage stats:', error);
      throw error;
    }
  },

  /**
   * Create Stripe checkout session for Trip Pass
   * @param {string} destination - Destination for the trip pass
   * @param {string} successUrl - URL to redirect after successful payment
   * @param {string} cancelUrl - URL to redirect if payment is cancelled
   */
  async createTripPassCheckout(destination, successUrl, cancelUrl) {
    try {
      const response = await api.post('/api/payment/create-checkout-session', {
        destination,
        success_url: successUrl,
        cancel_url: cancelUrl,
      });
      return response.data;
    } catch (error) {
      console.error('Error creating trip pass checkout:', error);
      throw error;
    }
  },

  /**
   * Create Stripe checkout session for annual subscription
   * @param {string} tier - Target tier (explorer_annual or travel_pro)
   * @param {string} successUrl - URL to redirect after successful payment
   * @param {string} cancelUrl - URL to redirect if payment is cancelled
   */
  async createAnnualSubscriptionCheckout(tier, successUrl, cancelUrl) {
    try {
      const response = await api.post('/api/payment/create-subscription', {
        target_tier: tier,
        success_url: successUrl,
        cancel_url: cancelUrl,
      });
      return response.data;
    } catch (error) {
      console.error('Error creating subscription checkout:', error);
      throw error;
    }
  },

  /**
   * Cancel current subscription
   */
  async cancelSubscription() {
    try {
      const response = await api.post('/api/subscription/cancel');
      return response.data;
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      throw error;
    }
  },

  /**
   * Manually activate trip pass after successful payment
   * This is a temporary function for testing when webhooks aren't working
   * @param {string} destination - Destination for the trip pass
   */
  async manualActivateTripPass(destination) {
    try {
      const response = await api.post('/api/payment/manual-activate-trip-pass', {
        destination,
        success_url: window.location.origin + '/pricing',
        cancel_url: window.location.origin + '/pricing',
      });
      return response.data;
    } catch (error) {
      console.error('Error manually activating trip pass:', error);
      throw error;
    }
  },

  /**
   * Manually upgrade to annual subscription for testing
   * This bypasses Stripe payment and directly upgrades the user
   * @param {string} tier - Target tier (explorer_annual or travel_pro)
   */
  async manualUpgradeAnnual(tier) {
    try {
      const response = await api.post('/api/payment/manual-upgrade-annual', {
        tier,
      });
      return response.data;
    } catch (error) {
      console.error('Error manually upgrading subscription:', error);
      throw error;
    }
  },

  /**
   * Manually track a trip generation for testing purposes
   * This allows you to manually increment trip usage
   * @param {string} destination - Destination for the trip
   */
  async manualTrackTrip(destination) {
    try {
      const response = await api.post('/api/subscription/manual-track-trip', {
        destination,
      });
      return response.data;
    } catch (error) {
      console.error('Error manually tracking trip:', error);
      throw error;
    }
  },
};

export default subscriptionApi;

