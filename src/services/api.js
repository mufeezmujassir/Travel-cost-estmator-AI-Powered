import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // Don't auto-redirect, let the app handle it
      console.log('Session expired. Please login again.');
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (userData) => api.put('/auth/profile', userData),
  deleteProfile: () => api.delete('/auth/profile'),
  getUserById: (userId) => api.get(`/auth/users/${userId}`),
};

// Travel APIs (protected)
export const travelAPI = {
  estimateTravel: (travelData) => api.post('/api/estimate-travel', travelData),
  getVibes: () => api.get('/api/vibes'),
  getSeasonRecommendation: (vibe, destination, startDate) => 
    api.get(`/api/season-recommendation?vibe=${vibe}&destination=${destination}&start_date=${startDate}`),
  getVibeSuitability: (params) => api.get('/api/vibe-suitability', { params }),
  getBatchVibeSuitability: (params) => api.get('/api/vibe-suitability/batch', { params }),
  getPublicVibes: () => axios.get(`${API_BASE_URL}/public/vibes`), // Public endpoint, no auth needed
  listTrips: () => api.get('/api/trips/'),
  getTrip: (id) => api.get(`/api/trips/${id}`),
  deleteTrip: (id) => api.delete(`/api/trips/${id}`),
};

// Subscription APIs
export const subscriptionAPI = {
  createCheckoutSession: () => api.post('/subscription/create-checkout-session'),
  cancelSubscription: () => api.post('/subscription/cancel'),
  getSubscriptionStatus: () => api.get('/subscription/status'),
};

export default api;