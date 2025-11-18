import axios, { AxiosRequestConfig } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT_MS = 30000; // 30 seconds timeout

const api = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT_MS, // Request timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    // Log API URL in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`API Request: ${config.baseURL}${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    } else if (error.response) {
      // Server responded with error status
      console.error(`API Error ${error.response.status}:`, error.response.data);
      console.error(`Request URL: ${error.config?.baseURL}${error.config?.url}`);
    } else if (error.request) {
      // Request made but no response received
      console.error('No response from API:', error.request);
      console.error(`Trying to connect to: ${API_URL}`);
      console.error('Check if backend is running and CORS is configured correctly');
    } else {
      // Error setting up request
      console.error('Request setup error:', error.message);
    }
    return Promise.reject(error);
  }
);

export interface OverviewData {
  total_reprints: number;
  previous_period_total: number;
  change_percentage: number;
  quality_reprints: number;
  quality_percentage: number;
  top_shipping_country: { country: string | null; count: number };
  top_shipping_service: { service: string | null; count: number };
  reason_categories: Array<{ category: string; count: number; percentage: number }>;
  trend_by_category: Record<string, Array<{ date: string; count: number }>>;
  top_products: Array<{ product_type: string; count: number; percentage: number }>;
  top_facilities: Array<{ facility: string; count: number; percentage: number }>;
  top_reasons: Array<{ reason: string; count: number; percentage: number }>;
  trend: Array<{ date: string; count: number }>;
}

export interface ReviewAnalysis {
  products: Record<string, number>;
  issues: Record<string, number>;
  facilities: Record<string, number>;
  sentiments: Record<string, number>;
  total_reviews: number;
  reviews_with_issues: number;
  top_products_with_issues: Array<{ product: string; count: number; percentage: number }>;
  trending_concerns: Array<{ issue: string; count: number; percentage: number }>;
}

export interface TrendDataPoint {
  date: string;
  count: number;
  by_product?: Record<string, number>;
  by_facility?: Record<string, number>;
  by_reason?: Record<string, number>;
}

export const apiClient = {
  // Overview
  getOverview: async (days: number = 7): Promise<OverviewData> => {
    const response = await api.get(`/api/reprints/overview?days=${days}`);
    return response.data;
  },

  // Reprints
  getReprintMetrics: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/api/reprints/metrics?${params.toString()}`);
    return response.data;
  },

  getProductMetrics: async (startDate?: string, endDate?: string, topN: number = 10) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('top_n', topN.toString());
    const response = await api.get(`/api/reprints/products?${params.toString()}`);
    return response.data;
  },

  getFacilityMetrics: async (startDate?: string, endDate?: string, topN: number = 10) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('top_n', topN.toString());
    const response = await api.get(`/api/reprints/facilities?${params.toString()}`);
    return response.data;
  },

  getReasonMetrics: async (startDate?: string, endDate?: string, topN: number = 10) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('top_n', topN.toString());
    const response = await api.get(`/api/reprints/reasons?${params.toString()}`);
    return response.data;
  },

  getTrend: async (startDate: string, endDate: string, groupBy: string = 'day'): Promise<TrendDataPoint[]> => {
    const response = await api.get(
      `/api/reprints/trend?start_date=${startDate}&end_date=${endDate}&group_by=${groupBy}`
    );
    return response.data;
  },

  getComparison: async (startDate: string, endDate: string, comparisonType: string = 'week') => {
    const response = await api.get(
      `/api/reprints/compare?start_date=${startDate}&end_date=${endDate}&comparison_type=${comparisonType}`
    );
    return response.data;
  },

  getFacilityDetails: async (facility: string, days: number = 30) => {
    const response = await api.get(`/api/reprints/facility/${facility}?days=${days}`);
    return response.data;
  },

  getProductDetails: async (product: string, days: number = 30) => {
    const response = await api.get(`/api/reprints/product/${product}?days=${days}`);
    return response.data;
  },

  // Reviews
  getReviewAnalysis: async (startDate?: string, endDate?: string): Promise<ReviewAnalysis> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/api/reviews/analyze?${params.toString()}`);
    return response.data;
  },

  getReviewSummary: async (days: number = 7): Promise<ReviewAnalysis> => {
    const response = await api.get(`/api/reviews/summary?days=${days}`);
    return response.data;
  },

  getProductQuality: async (product: string, days: number = 30) => {
    const response = await api.get(`/api/reviews/product/${product}?days=${days}`);
    return response.data;
  },

  // Freshdesk
  getFreshdeskStats: async (days: number = 30) => {
    const response = await api.get(`/api/freshdesk/stats?days=${days}`);
    return response.data;
  },

  // Shipping
  getShippingCountryMetrics: async (startDate?: string, endDate?: string, topN: number = 10) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('top_n', topN.toString());
    const response = await api.get(`/api/reprints/shipping/countries?${params.toString()}`);
    return response.data;
  },

  getShippingServiceMetrics: async (startDate?: string, endDate?: string, topN: number = 10) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('top_n', topN.toString());
    const response = await api.get(`/api/reprints/shipping/services?${params.toString()}`);
    return response.data;
  },

  // Categories
  getReasonCategoryMetrics: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/api/reprints/categories?${params.toString()}`);
    return response.data;
  },

  // Records
  getReprintRecords: async (
    startDate?: string,
    endDate?: string,
    facility?: string,
    productType?: string,
    reasonCategory?: string,
    shippingCountry?: string,
    shippingService?: string,
    limit: number = 1000,
    offset: number = 0
  ) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (facility) params.append('facility', facility);
    if (productType) params.append('product_type', productType);
    if (reasonCategory) params.append('reason_category', reasonCategory);
    if (shippingCountry) params.append('shipping_country', shippingCountry);
    if (shippingService) params.append('shipping_service', shippingService);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    const response = await api.get(`/api/reprints/records?${params.toString()}`);
    return response.data;
  },

  // Matrix
  getMatrix: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const response = await api.get(`/api/reprints/matrix?${params.toString()}`);
    return response.data;
  },
};

