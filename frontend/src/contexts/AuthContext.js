import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios defaults
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await api.get('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login', {
        email,
        password,
      });
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      setUser(user);
      setIsAuthenticated(true);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      throw error.response?.data?.error || 'Login failed';
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await api.post('/api/auth/register', {
        username,
        email,
        password,
      });
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      setUser(user);
      setIsAuthenticated(true);
      return true;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error.response?.data?.error || 'Registration failed';
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  // Add token to all requests
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Handle 401 responses
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        setUser(null);
        setIsAuthenticated(false);
      }
      return Promise.reject(error);
    }
  );

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 