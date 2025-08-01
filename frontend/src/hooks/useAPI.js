import { useState, useCallback } from 'react';
import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export const useAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callAPI = useCallback(async (endpoint, method = 'GET', data = null) => {
    setLoading(true);
    setError(null);

    try {
      let requestData = data;
      let contentType = 'application/json';

      // Convert JSON data to FormData for specific endpoints that expect form data
      const formDataEndpoints = ['/agentic-chat/', '/chat-with-memory/', '/evaluate-answer/'];
      
      if (data && typeof data === 'object' && !(data instanceof FormData) && 
            formDataEndpoints.some(ep => endpoint.includes(ep))) {
            const formData = new FormData();
            Object.keys(data).forEach(key => {
            if (data[key] !== null && data[key] !== undefined) {
            formData.append(key, String(data[key])); 
            }
        });
        requestData = formData;
        contentType = 'multipart/form-data';
        }


      const config = {
        method,
        url: `${BASE_URL}${endpoint}`,
        headers: {
          'Content-Type': contentType,
        },
        data: requestData,
      };

      // Remove Content-Type header for FormData to let axios set it with boundary
      if (requestData instanceof FormData) {
        delete config.headers['Content-Type'];
      }

      const response = await axios(config);
      return response.data;
    } catch (err) {
      console.error('API Error:', err);
      
      // Handle different types of errors
      let errorMessage = 'An error occurred';
      
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Handle FastAPI validation errors
        if (errorData.detail && Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(error => 
            `${error.loc?.join(' -> ') || 'Field'}: ${error.msg}`
          ).join(', ');
        } else if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.error) {
          errorMessage = errorData.error;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, callAPI };
};

export const Alert = ({ type, message }) => {
  const colors = {
    error: 'bg-red-100 text-red-700 border-red-200',
    success: 'bg-green-100 text-green-700 border-green-200',
    info: 'bg-blue-100 text-blue-700 border-blue-200',
  };

  // Ensure message is always a string
  const displayMessage = typeof message === 'string' ? message : JSON.stringify(message);

  return (
    <div className={`p-4 mb-4 rounded-lg border ${colors[type]}`}>
      {displayMessage}
    </div>
  );
};