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
      const config = {
        method,
        url: `${BASE_URL}${endpoint}`,
        headers: {
          'Content-Type': data instanceof FormData ? 'multipart/form-data' : 'application/json',
        },
        data: data,
      };

      const response = await axios(config);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
      throw err;
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

  return (
    <div className={`p-4 mb-4 rounded-lg border ${colors[type]}`}>
      {message}
    </div>
  );
};
