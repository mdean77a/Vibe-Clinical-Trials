/**
 * API utility functions for the Clinical Trial Accelerator frontend.
 * 
 * This module provides environment-aware API configuration and utility functions
 * for making HTTP requests to the backend.
 */

// API URL configuration - direct backend calls
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

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
    const endpoint = 'protocols/upload';
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
 * ICF Generation API functions
 */
export const icfApi = {
  /**
   * Generate ICF for a protocol collection
   */
  generate: async (collectionName: string, protocolMetadata?: unknown) => {
    return apiRequest('icf/generate', {
      method: 'POST',
      body: JSON.stringify({
        protocol_collection_name: collectionName,
        protocol_metadata: protocolMetadata,
      }),
    });
  },

  /**
   * Get protocol summary
   */
  getProtocolSummary: async (collectionName: string) => {
    return apiRequest(`icf/protocol/${collectionName}/summary`);
  },

  /**
   * Get ICF section requirements
   */
  getSectionRequirements: async () => {
    return apiRequest('icf/sections/requirements');
  },

  /**
   * Get generation status
   */
  getStatus: async (taskId: string) => {
    return apiRequest(`icf/status/${taskId}`);
  },

  /**
   * Regenerate a specific ICF section
   */
  regenerateSection: async (collectionName: string, sectionName: string, protocolMetadata?: unknown) => {
    return apiRequest('icf/regenerate-section', {
      method: 'POST',
      body: JSON.stringify({
        protocol_collection_name: collectionName,
        section_name: sectionName,
        protocol_metadata: protocolMetadata,
      }),
    });
  },

  /**
   * Generate ICF with streaming section results
   */
  generateStreaming: async function* (collectionName: string, protocolMetadata?: unknown) {
    const url = getApiUrl('icf/generate-stream');
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        protocol_collection_name: collectionName,
        protocol_metadata: protocolMetadata,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    if (!response.body) {
      throw new Error('Response body is null');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              yield data;
            } catch {
              console.warn('Failed to parse SSE data:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },

  /**
   * Health check for ICF service
   */
  health: async () => {
    const endpoint = 'icf/health';
    return apiRequest(endpoint);
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
    environment: process.env.NODE_ENV || 'development',
    mode: process.env.NODE_ENV || 'development',
  });
}; 