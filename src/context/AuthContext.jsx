import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await authAPI.getProfile();
        setUser(response.data);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        setIsAuthenticated(false);
      }
    }
    setLoading(false);
  };

  const register = async (name, email, password) => {
    try {
      setError('');
      const response = await authAPI.register({ name, email, password });
      
      // Auto login after registration
      const loginResponse = await authAPI.login({ email, password });
      const { access_token } = loginResponse.data;
      
      localStorage.setItem('token', access_token);
      
      // Fetch user profile
      const profileResponse = await authAPI.getProfile();
      setUser(profileResponse.data);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const login = async (email, password) => {
    try {
      setError('');
      const response = await authAPI.login({ email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      
      // Fetch user profile
      const profileResponse = await authAPI.getProfile();
      setUser(profileResponse.data);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateProfile = async (userData) => {
    try {
      const response = await authAPI.updateProfile(userData);
      setUser(response.data);
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Update failed';
      return { success: false, error: errorMessage };
    }
  };

  const deleteAccount = async () => {
    try {
      await authAPI.deleteProfile();
      logout();
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Delete failed';
      return { success: false, error: errorMessage };
    }
  };

  const value = {
    user,
    loading,
    error,
    isAuthenticated,
    register,
    login,
    logout,
    updateProfile,
    deleteAccount,
    setError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};