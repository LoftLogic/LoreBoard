import axios, { AxiosInstance, AxiosError } from 'axios';
import { Entity, Content, AutoFillSlot, ApiResponse, PaginatedResponse } from '../types/index';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout for LLM operations
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Entity API
export const entityApi = {
  // Get all entities with optional filtering
  getAll: async (params?: {
    type?: string;
    search?: string;
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<Entity>> => {
    const response = await apiClient.get('/entities', { params });
    return response.data;
  },

  // Get single entity by ID
  getById: async (id: string): Promise<Entity> => {
    const response = await apiClient.get(`/entities/${id}`);
    return response.data;
  },

  // Create new entity
  create: async (entity: Omit<Entity, 'id' | 'createdAt' | 'updatedAt'>): Promise<Entity> => {
    const response = await apiClient.post('/entities', entity);
    return response.data;
  },

  // Update entity
  update: async (id: string, entity: Partial<Entity>): Promise<Entity> => {
    const response = await apiClient.put(`/entities/${id}`, entity);
    return response.data;
  },

  // Delete entity
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/entities/${id}`);
  },

  // Get entity relationships
  getRelationships: async (id: string): Promise<Entity[]> => {
    const response = await apiClient.get(`/entities/${id}/relationships`);
    return response.data;
  },
};

// Content API
export const contentApi = {
  // Get all content
  getAll: async (params?: {
    search?: string;
    entityId?: string;
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<Content>> => {
    const response = await apiClient.get('/content', { params });
    return response.data;
  },

  // Get single content by ID
  getById: async (id: string): Promise<Content> => {
    const response = await apiClient.get(`/content/${id}`);
    return response.data;
  },

  // Create new content
  create: async (content: Omit<Content, 'id' | 'createdAt' | 'updatedAt'>): Promise<Content> => {
    const response = await apiClient.post('/content', content);
    return response.data;
  },

  // Update content
  update: async (id: string, content: Partial<Content>): Promise<Content> => {
    const response = await apiClient.put(`/content/${id}`, content);
    return response.data;
  },

  // Delete content
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/content/${id}`);
  },

  // Auto-save content
  autoSave: async (id: string, body: string): Promise<void> => {
    await apiClient.post(`/content/${id}/autosave`, { body });
  },
};

// LLM API
export const llmApi = {
  // Generate auto-fill suggestions
  generateAutoFill: async (slot: AutoFillSlot): Promise<string[]> => {
    const response = await apiClient.post('/llm/autofill', slot);
    return response.data.suggestions;
  },

  // Extract entities from content
  extractEntities: async (contentId: string): Promise<Entity[]> => {
    const response = await apiClient.post(`/llm/extract-entities/${contentId}`);
    return response.data.entities;
  },

  // Get entity information summary
  getEntitySummary: async (entityId: string, query: string): Promise<string> => {
    const response = await apiClient.post(`/llm/entity-summary/${entityId}`, { query });
    return response.data.summary;
  },

  // Analyze content for consistency
  analyzeConsistency: async (contentId: string): Promise<any> => {
    const response = await apiClient.post(`/llm/analyze-consistency/${contentId}`);
    return response.data;
  },
};

// Export the api client for custom requests
export default apiClient;
