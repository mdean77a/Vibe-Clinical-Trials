/**
 * API utility functions for the Clinical Trial Accelerator frontend.
 * 
 * This module provides environment-aware API configuration and utility functions
 * for making HTTP requests to the backend.
 */

// Environment-based API URL configuration
const API_BASE_URL = import.meta.env.PROD 
  ? '/api'  // Vercel Functions in production
  : 'http://localhost:8000';  // Local FastAPI development server

/**
 * Get the full API URL for a given endpoint
 */
export const getApiUrl = (endpoint: string): string => {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

/**
 * Default headers for API requests
 */
const getDefaultHeaders = (): HeadersInit => ({
  'Content-Type': 'application/json',
});

/**
 * Generic API request function with error handling
 */
export const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = getApiUrl(endpoint);
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...getDefaultHeaders(),
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    // Handle 204 No Content responses
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${url}:`, error);
    throw error;
  }
};

/**
 * Protocol-specific API functions
 */
export const protocolsApi = {
  /**
   * Create a new protocol
   */
  create: async (protocolData: {
    study_acronym: string;
    protocol_title: string;
    file_path?: string;
  }) => {
    return apiRequest('protocols', {
      method: 'POST',
      body: JSON.stringify(protocolData),
    });
  },

  /**
   * Upload and process a protocol PDF file
   */
  upload: async (file: File, protocolData: {
    study_acronym: string;
    protocol_title: string;
  }) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('study_acronym', protocolData.study_acronym);
    formData.append('protocol_title', protocolData.protocol_title);

    // Use different endpoints for development vs production
    const endpoint = import.meta.env.PROD ? 'upload-protocol' : 'protocols/upload';
    const url = getApiUrl(endpoint);
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        // Don't set Content-Type header - let browser set it for multipart/form-data
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Protocol upload failed for ${url}:`, error);
      throw error;
    }
  },

  /**
   * Get a protocol by ID
   */
  getById: async (id: number) => {
    return apiRequest(`protocols/${id}`);
  },

  /**
   * Get a protocol by collection name
   */
  getByCollection: async (collectionName: string) => {
    return apiRequest(`protocols/collection/${collectionName}`);
  },

  /**
   * List all protocols with optional status filter
   */
  list: async (statusFilter?: string) => {
    const params = statusFilter ? `?status_filter=${encodeURIComponent(statusFilter)}` : '';
    return apiRequest(`protocols${params}`);
  },

  /**
   * Update protocol status
   */
  updateStatus: async (id: number, status: string) => {
    return apiRequest(`protocols/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  },

  /**
   * Delete a protocol
   */
  delete: async (id: number) => {
    return apiRequest(`protocols/${id}`, {
      method: 'DELETE',
    });
  },
};

/**
 * Health check API functions
 */
export const healthApi = {
  /**
   * Check API health
   */
  check: async () => {
    return apiRequest('health');
  },

  /**
   * Get API root information
   */
  root: async () => {
    return apiRequest('');
  },
};

/**
 * Development helper to log current API configuration
 */
export const logApiConfig = () => {
  console.log('API Configuration:', {
    baseUrl: API_BASE_URL,
    environment: import.meta.env.PROD ? 'production' : 'development',
    mode: import.meta.env.MODE,
  });
}; 