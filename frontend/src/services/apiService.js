import axios from 'axios';
import { API_URL, AUTH_CONFIG } from '../config/apiConfig';

/**
 * Centralized API service for StickForStats
 * 
 * This service provides a unified way to make API calls with proper
 * authentication, error handling, and response transformation.
 */

// Function to get CSRF token from cookies
const getCSRFToken = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true // Important for CSRF to work
});

// Request interceptor for adding auth token and CSRF token
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token
    const token = localStorage.getItem(AUTH_CONFIG.storageKey);
    if (token) {
      config.headers[AUTH_CONFIG.headerName] = `${AUTH_CONFIG.tokenPrefix} ${token}`;
    }
    
    // Add CSRF token for non-GET requests
    if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
      const csrfToken = getCSRFToken();
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized errors (token expired)
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem(AUTH_CONFIG.refreshTokenKey);
        
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh-token/`, {
            refresh: refreshToken
          });
          
          const newToken = response.data.access;
          localStorage.setItem(AUTH_CONFIG.storageKey, newToken);
          
          // Update the authorization header
          originalRequest.headers[AUTH_CONFIG.headerName] = `${AUTH_CONFIG.tokenPrefix} ${newToken}`;
          
          // Retry the original request
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, redirect to login
        console.error('Token refresh failed:', refreshError);
        
        // Clear tokens
        localStorage.removeItem(AUTH_CONFIG.storageKey);
        localStorage.removeItem(AUTH_CONFIG.refreshTokenKey);
        
        // Dispatch logout event
        window.dispatchEvent(new CustomEvent('auth:logout'));
        
        return Promise.reject({
          status: 401,
          message: 'Your session has expired. Please login again.',
          type: 'AUTH_ERROR',
          data: {},
          originalError: refreshError
        });
      }
    }
    
    // Categorize errors by HTTP status code for consistent handling
    let errorType = 'UNKNOWN_ERROR';
    let errorMessage = 'An unexpected error occurred. Please try again later.';
    
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const status = error.response.status;
      
      switch (status) {
        case 400:
          errorType = 'BAD_REQUEST';
          errorMessage = 'Invalid request. Please check your input and try again.';
          break;
        case 401:
          errorType = 'AUTH_ERROR';
          errorMessage = 'Authentication required. Please login to continue.';
          break;
        case 403:
          errorType = 'FORBIDDEN';
          errorMessage = 'You do not have permission to perform this action.';
          break;
        case 404:
          errorType = 'NOT_FOUND';
          errorMessage = 'The requested resource was not found.';
          break;
        case 409:
          errorType = 'CONFLICT';
          errorMessage = 'This operation caused a conflict. Please refresh and try again.';
          break;
        case 422:
          errorType = 'VALIDATION_ERROR';
          errorMessage = 'Validation failed. Please check the provided data.';
          break;
        case 429:
          errorType = 'RATE_LIMIT';
          errorMessage = 'Too many requests. Please try again later.';
          break;
        case 500:
        case 501:
        case 502:
        case 503:
          errorType = 'SERVER_ERROR';
          errorMessage = 'A server error occurred. Please try again later.';
          break;
        default:
          if (status >= 400 && status < 500) {
            errorType = 'CLIENT_ERROR';
            errorMessage = 'There was a problem with your request.';
          } else if (status >= 500) {
            errorType = 'SERVER_ERROR';
            errorMessage = 'A server error occurred. Please try again later.';
          }
      }
    } else if (error.request) {
      // The request was made but no response was received
      errorType = 'NETWORK_ERROR';
      errorMessage = 'Unable to connect to the server. Please check your internet connection.';
    } else {
      // Something happened in setting up the request that triggered an Error
      errorType = 'REQUEST_ERROR';
      errorMessage = 'Error setting up the request.';
    }

    // Extract any specific error message from the response
    const serverMessage = error.response?.data?.message || 
                        error.response?.data?.error || 
                        error.response?.data?.detail ||
                        null;
    
    // If we have server-provided field errors, collect them
    const fieldErrors = {};
    if (error.response?.data && typeof error.response.data === 'object') {
      Object.entries(error.response.data).forEach(([key, value]) => {
        if (key !== 'message' && key !== 'error' && key !== 'detail') {
          fieldErrors[key] = Array.isArray(value) ? value.join(', ') : value;
        }
      });
    }
    
    // Log error in development environment
    if (process.env.NODE_ENV !== 'production') {
      console.group('API Error');
      console.error('Type:', errorType);
      console.error('Status:', error.response?.status || 'N/A');
      console.error('Message:', serverMessage || errorMessage);
      console.error('URL:', originalRequest?.url);
      console.error('Method:', originalRequest?.method);
      
      if (Object.keys(fieldErrors).length > 0) {
        console.error('Field Errors:', fieldErrors);
      }
      
      console.error('Raw Error:', error);
      console.groupEnd();
    }
    
    // Transform error response for consistent format
    const errorResponse = {
      status: error.response?.status || 0,
      message: serverMessage || errorMessage,
      type: errorType,
      fieldErrors: Object.keys(fieldErrors).length > 0 ? fieldErrors : null,
      data: error.response?.data || {},
      originalError: error
    };
    
    return Promise.reject(errorResponse);
  }
);

/**
 * Make a GET request to the API
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} params - URL parameters
 * @param {Object} options - Additional axios options
 * @returns {Promise} - API response
 */
export const get = async (url, params = {}, options = {}) => {
  try {
    const response = await apiClient.get(url, { params, ...options });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Make a POST request to the API
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} data - Request body data
 * @param {Object} options - Additional axios options
 * @returns {Promise} - API response
 */
export const post = async (url, data = {}, options = {}) => {
  try {
    const response = await apiClient.post(url, data, options);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Make a PUT request to the API
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} data - Request body data
 * @param {Object} options - Additional axios options
 * @returns {Promise} - API response
 */
export const put = async (url, data = {}, options = {}) => {
  try {
    const response = await apiClient.put(url, data, options);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Make a PATCH request to the API
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} data - Request body data
 * @param {Object} options - Additional axios options
 * @returns {Promise} - API response
 */
export const patch = async (url, data = {}, options = {}) => {
  try {
    const response = await apiClient.patch(url, data, options);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Make a DELETE request to the API
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} options - Additional axios options
 * @returns {Promise} - API response
 */
export const del = async (url, options = {}) => {
  try {
    const response = await apiClient.delete(url, options);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Download a file from the API
 * 
 * @param {string} url - API endpoint URL
 * @param {Object} params - URL parameters
 * @param {string} filename - Name to save the file as
 * @param {Object} options - Additional axios options
 * @returns {Promise} - Download result
 */
export const downloadFile = async (url, params = {}, filename = null, options = {}) => {
  try {
    const response = await apiClient.get(url, {
      params,
      responseType: 'blob',
      ...options
    });
    
    // Create a blob URL
    const blob = new Blob([response.data]);
    const downloadUrl = window.URL.createObjectURL(blob);
    
    // Get filename from Content-Disposition header if not provided
    let downloadFilename = filename;
    if (!downloadFilename) {
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch.length === 2) {
          downloadFilename = filenameMatch[1];
        }
      }
    }
    
    // If still no filename, use a default
    if (!downloadFilename) {
      downloadFilename = 'download';
    }
    
    // Create a temporary link and click it
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', downloadFilename);
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    window.URL.revokeObjectURL(downloadUrl);
    document.body.removeChild(link);
    
    return {
      success: true,
      filename: downloadFilename
    };
  } catch (error) {
    throw error;
  }
};

/**
 * Upload a file to the API
 * 
 * @param {string} url - API endpoint URL
 * @param {File|FormData} file - File or FormData to upload
 * @param {Object} data - Additional form data
 * @param {function} onProgress - Progress callback
 * @returns {Promise} - Upload result
 */
export const uploadFile = async (url, file, data = {}, onProgress = null) => {
  // Create FormData if file is not already FormData
  let formData;
  if (file instanceof FormData) {
    formData = file;
    
    // Add additional data
    Object.entries(data).forEach(([key, value]) => {
      formData.append(key, value);
    });
  } else {
    formData = new FormData();
    formData.append('file', file);
    
    // Add additional data
    Object.entries(data).forEach(([key, value]) => {
      formData.append(key, value);
    });
  }
  
  // Configure request
  const config = {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  };
  
  // Add progress handler if provided
  if (onProgress) {
    config.onUploadProgress = (progressEvent) => {
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      onProgress(percentCompleted);
    };
  }
  
  try {
    const response = await apiClient.post(url, formData, config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default {
  get,
  post,
  put,
  patch,
  del,
  downloadFile,
  uploadFile,
  client: apiClient
};