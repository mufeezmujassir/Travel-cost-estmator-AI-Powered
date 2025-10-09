import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

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
    if (error.response?.status === 401 || error.response?.status === 422) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

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
  getPublicVibes: () => api.get('/public/vibes'),
};

export default api;