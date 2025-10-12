import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { travelAPI } from '../services/api'

export const useTravelEstimation = (refreshSubscription = null) => {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const estimateTravel = async (formData, vibe, options = {}) => {
    setLoading(true)
    setError(null)
    setResults(null)
    
    const payload = {
      origin: formData.origin.trim(),
      destination: formData.destination.trim(),
      start_date: formData.startDate,
      return_date: formData.returnDate,
      travelers: parseInt(formData.travelers, 10),
      budget: parseFloat(formData.budget) || null,  // Optional, send null if 0
      vibe: vibe.id.toLowerCase(),  // Send string like "adventure"
      include_price_trends: options.includePriceTrends !== false  // Default to true
    };

    console.log('🚀 Sending travel estimation request:', payload);

    try {
      const response = await travelAPI.estimateTravel(payload);
      
      console.log('✅ Travel estimation successful:', response.data);
      setResults(response.data);
      toast.success('Travel plan generated successfully!');
      
      // Refresh subscription data to update trip usage (if provided)
      if (refreshSubscription) {
        try {
          await refreshSubscription();
          console.log('✅ Subscription data refreshed after trip generation');
        } catch (refreshError) {
          console.warn('⚠️ Failed to refresh subscription data:', refreshError);
        }
      }
      
      return { success: true, data: response.data };
      
    } catch (err) {
      console.error('❌ Travel estimation failed:', err);
      
      let errorMessage = 'Failed to generate travel plan';
      
      if (err.response?.status === 422) {
        if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n');
        } else {
          errorMessage = err.response.data.detail || 'Validation error';
        }
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }

  const resetResults = () => {
    setResults(null);
    setError(null);
  }

  return {
    estimateTravel,
    loading,
    results,
    error,
    resetResults
  }
}