import { useState } from 'react'
import { toast } from 'react-hot-toast'
import axios from 'axios'

export const useTravelEstimation = () => {
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
      start_date: formData.startDate,  // Rename to start_date
      return_date: formData.returnDate,  // Rename to return_date
      travelers: parseInt(formData.travelers, 10),
      budget: parseFloat(formData.budget) || null,  // Optional, send null if 0
      vibe: vibe.id.toLowerCase(),  // Send string like "adventure"
      include_price_trends: options.includePriceTrends !== false  // Default to true
    };
    console.log('Sending payload to backend:', payload);  // Debug log
    try {
      // Simulate API call delay for demo
      const response = await axios.post('http://localhost:8000/api/estimate-travel', payload, {
        headers: { 'Content-Type': 'application/json' }
      });
      
      setResults(response.data)
      
      
      toast.success('Travel plan generated successfully!')
      
    } catch (err) {
      let errorMessage = 'Failed to generate travel plan';
      if (err.response?.status === 422) {
        errorMessage = err.response.data.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n');
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      }
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return {
    estimateTravel,
    loading,
    results,
    error
  }
}
