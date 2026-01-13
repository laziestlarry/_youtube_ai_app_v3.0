import axios, { AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { AnalyticsSummary, VideoAnalytics, SystemHealth, EarningsData, AIModel } from '../types/dashboard';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.location.origin;

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      if (config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    console.error('API Error:', error);
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Authentication
  async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    const response = await apiClient.post('/api/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  async loginWithKey(accessKey: string): Promise<{ access_token: string; token_type: string; message: string }> {
    const response = await apiClient.post('/api/auth/login-with-key', { access_key: accessKey });
    return response.data;
  },

  async register(userData: any): Promise<any> {
    const response = await apiClient.post('/api/auth/register', userData);
    return response.data;
  },

  async getCurrentUser(): Promise<any> {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },

  // Health and Status
  async getHealth(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Channel Analytics (Updated to use new analytics service)
  async getAnalyticsSummary(): Promise<AnalyticsSummary> {
    const response = await apiClient.get('/api/analytics/summary');
    return response.data;
  },

  async getRevenueHistory(days: number = 30): Promise<any> {
    const response = await apiClient.get(`/api/analytics/revenue-history?days=${days}`);
    return response.data;
  },

  async getVideoAnalytics(): Promise<VideoAnalytics[]> {
    // Note: This endpoint should ideally be implemented in the backend analytics router
    // For now, we reuse the summary or add it if missing.
    const response = await apiClient.get('/api/analytics/summary');
    // In a real prod app, you might have a dedicated /api/analytics/videos endpoint
    return response.data.recent_videos || [];
  },

  // System Health
  async getSystemHealth(): Promise<SystemHealth> {
    const response = await apiClient.get('/api/system/health');
    return response.data;
  },

  // AI Models
  async getAIModels(): Promise<AIModel[]> {
    const response = await apiClient.get('/api/models');
    return response.data;
  },

  async updateAIModel(modelId: string, updates: Partial<AIModel>): Promise<AIModel> {
    const response = await apiClient.put(`/api/models/${modelId}`, updates);
    return response.data;
  },

  // Content Management
  async generateContent(prompt: string, contentType: string): Promise<{ script: string; thumbnail: string; title: string }> {
    const response = await apiClient.post('/api/content/generate', { prompt, contentType });
    return response.data;
  },

  async uploadVideo(videoData: FormData): Promise<{ videoId: string; status: string }> {
    const response = await apiClient.post('/api/videos/upload', videoData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // YouTube Integration
  async getYouTubeAuthUrl(): Promise<{ url: string }> {
    const response = await apiClient.get('/api/youtube/auth-url');
    return response.data;
  },

  async connectYouTube(code: string): Promise<{ status: string; message: string }> {
    const response = await apiClient.get(`/api/youtube/callback?code=${code}`);
    return response.data;
  },

  async getYouTubeChannels(): Promise<Array<{ id: string; title: string; subscriberCount: number }>> {
    const response = await apiClient.get('/api/youtube/channels');
    return response.data;
  },

  // Performance Analytics (Updated to use live trends)
  async getPerformanceMetrics(days: number = 30): Promise<{ views: any[]; revenue: any[] }> {
    const response = await apiClient.get(`/api/analytics/performance-metrics?days=${days}`);
    return response.data;
  },

  // Content Strategy
  async getContentSuggestions(keywords: string[]): Promise<Array<{
    title: string;
    description: string;
    estimatedViews: number;
    estimatedRevenue: number;
  }>> {
    const response = await apiClient.post('/api/content/suggestions', { keywords });
    return response.data;
  },

  // Monetization
  async getMonetizationStatus(): Promise<{
    isMonetized: boolean;
    requirements: string[];
    nextReviewDate?: string;
  }> {
    const response = await apiClient.get('/api/monetization/status');
    return response.data;
  },

  // Settings and Configuration
  async updateSettings(settings: Record<string, unknown>): Promise<{ success: boolean }> {
    const response = await apiClient.put('/api/settings', settings);
    return response.data;
  },

  async getSettings(): Promise<Record<string, unknown>> {
    const response = await apiClient.get('/api/settings');
    return response.data;
  },

  // Notifications
  async getNotifications(): Promise<Array<{
    id: string;
    type: 'info' | 'warning' | 'error' | 'success';
    message: string;
    timestamp: string;
    read: boolean;
  }>> {
    const response = await apiClient.get('/api/notifications');
    return response.data;
  },

  async markNotificationAsRead(notificationId: string): Promise<{ success: boolean }> {
    const response = await apiClient.put(`/api/notifications/${notificationId}/read`);
    return response.data;
  },

  // AI Agency (Project Ignite)
  async getAgencyDepartments(): Promise<Array<{ name: string; description: string }>> {
    const response = await apiClient.get('/api/agency/departments');
    return response.data;
  },

  async executeAgencyTask(objective: string, department: string): Promise<{
    department: string;
    objective: string;
    status: string;
    result: string;
  }> {
    const response = await apiClient.post('/api/agency/execute', { objective, department });
    return response.data;
  },

  async getIgniteRevenueStats(): Promise<{
    monthly_estimate: number;
    daily_average: number;
    active_campaigns: number;
    projected_yearly: number;
    currency: string;
  }> {
    const response = await apiClient.get('/api/agency/revenue-stats');
    return response.data;
  },
};
