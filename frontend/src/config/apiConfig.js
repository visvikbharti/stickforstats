/**
 * Centralized API configuration for StickForStats application
 * 
 * This file provides a single source of truth for API endpoint URLs
 * and authentication configuration.
 */

// Base API URL - uses environment variable with fallback
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// API version prefix
export const API_VERSION = 'v1';

// Full API base path for REST endpoints
export const API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

// App environment detection
export const IS_PRODUCTION = process.env.NODE_ENV === 'production';
export const IS_DEVELOPMENT = process.env.NODE_ENV === 'development';

// Feature flags
export const FEATURES = {
  DEBUG_MODE: process.env.REACT_APP_ENABLE_DEBUG_MODE === 'true',
  ANALYTICS: process.env.REACT_APP_ENABLE_ANALYTICS === 'true',
  EXPERIMENTAL: process.env.REACT_APP_ENABLE_EXPERIMENTAL_FEATURES === 'true',
};

// Authentication configuration
export const AUTH_CONFIG = {
  // Token prefix (Bearer is standard for JWT)
  tokenPrefix: process.env.REACT_APP_AUTH_TOKEN_PREFIX || 'Bearer',
  
  // Authentication header name
  headerName: 'Authorization',
  
  // Local storage key for token
  storageKey: 'authToken',
  
  // Refresh token storage key
  refreshTokenKey: 'stickforstats_refresh_token',
  
  // Token expiration timeout (default 24 hours in ms)
  tokenExpiry: parseInt(process.env.REACT_APP_AUTH_TOKEN_EXPIRY || '86400000', 10),
  
  // Token expiration buffer in seconds (refresh 5 minutes before expiry)
  refreshBuffer: 300
};

// Performance tuning
export const PERFORMANCE = {
  POLLING_INTERVAL: parseInt(process.env.REACT_APP_POLLING_INTERVAL || '30000', 10),
  MAX_UPLOAD_SIZE: parseInt(process.env.REACT_APP_MAX_UPLOAD_SIZE || '50000000', 10),
  RESPONSE_TIMEOUT: parseInt(process.env.REACT_APP_RESPONSE_TIMEOUT || '30000', 10),
};

// WebSocket configuration
export const WS_CONFIG = {
  // WebSocket base URL
  baseUrl: process.env.REACT_APP_WEBSOCKET_URL || 
    (window.location.protocol === 'https:' ? 'wss:' : 'ws:') + 
    `//${window.location.host}`,
  
  // WebSocket API path
  apiPath: 'ws/api',
  
  // Reconnection configuration
  reconnect: {
    // Whether to automatically reconnect
    enabled: true,
    
    // Initial delay in milliseconds
    initialDelay: 1000,
    
    // Maximum delay in milliseconds
    maxDelay: 30000,
    
    // Backoff multiplier
    multiplier: 1.5,
    
    // Maximum reconnection attempts (0 = unlimited)
    maxAttempts: 0
  }
};

// API endpoint paths by module
export const API_ENDPOINTS = {
  // Auth endpoints
  auth: {
    login: '/auth/login/',
    logout: '/auth/logout/',
    refreshToken: '/auth/refresh-token/',
    register: '/auth/register/',
    profile: '/auth/profile/'
  },
  
  // Core endpoints
  core: {
    datasets: '/core/datasets/',
    upload: '/core/datasets/upload/',
    session: '/core/session/'
  },
  
  // Workflow endpoints
  workflow: {
    list: '/workflows/api/workflows/',
    detail: (id) => `/workflows/api/workflows/${id}/`,
    steps: (id) => `/workflows/api/workflows/${id}/steps/`,
    step: (workflowId, stepId) => `/workflows/api/workflows/${workflowId}/steps/${stepId}/`,
    execute: (id) => `/workflows/api/workflows/${id}/execute/`,
    status: (id) => `/workflows/api/workflows/${id}/status/`,
    cancel: (id) => `/workflows/api/workflows/${id}/cancel/`,
    clone: (id) => `/workflows/api/workflows/${id}/clone/`,
    export: (id) => `/workflows/api/workflows/${id}/export/`,
    import: '/workflows/api/workflows/import/',
    duplicate: (id) => `/workflows/api/workflows/${id}/duplicate/`,
    executions: '/workflows/api/executions/',
    executionDetail: (id) => `/workflows/api/executions/${id}/`,
    executionCancel: (id) => `/workflows/api/executions/${id}/cancel/`,
    executionResults: (id) => `/workflows/api/executions/${id}/results/`,
    nodes: '/workflows/api/nodes/',
    templates: '/workflows/api/templates/',
    templateLibrary: '/workflows/api/templates/library/',
    schedules: '/workflows/api/schedules/',
    scheduleDetail: (id) => `/workflows/api/schedules/${id}/`,
    schedulePause: (id) => `/workflows/api/schedules/${id}/pause/`,
    scheduleResume: (id) => `/workflows/api/schedules/${id}/resume/`,
    shares: '/workflows/api/shares/'
  },
  
  // Report endpoints
  report: {
    list: '/mainapp/reports/',
    detail: (id) => `/mainapp/reports/${id}/`,
    generate: '/mainapp/reports/generate/',
    download: (id) => `/mainapp/reports/${id}/download/`
  },
  
  // Statistical analysis endpoints
  statistics: {
    descriptive: '/statistics/descriptive/',
    hypothesis: '/statistics/hypothesis/',
    correlation: '/statistics/correlation/',
    regression: '/statistics/regression/'
  },
  
  // SQC analysis endpoints
  sqc: {
    controlCharts: '/sqc-analysis/control-charts/',
    processCapability: '/sqc-analysis/process-capability/',
    acceptanceSampling: '/sqc-analysis/acceptance-sampling/',
    msaStudies: '/sqc-analysis/msa-studies/',
    economicDesign: '/sqc-analysis/economic-design/'
  },
  
  // DOE analysis endpoints
  doe: {
    designs: '/doe-analysis/designs/',
    analysis: '/doe-analysis/analysis/',
    optimization: '/doe-analysis/optimization/'
  },
  
  // PCA analysis endpoints
  pca: {
    analysis: '/pca-analysis/analysis/',
    visualization: '/pca-analysis/visualization/'
  },
  
  // Probability distributions endpoints
  probability: {
    distributions: '/probability-distributions/distributions/',
    fitting: '/probability-distributions/fitting/',
    sampling: '/probability-distributions/sampling/'
  },
  
  // Confidence intervals endpoints
  confidence: {
    calculate: '/confidence-intervals/calculate/',
    bootstrap: '/confidence-intervals/bootstrap/'
  },
  
  // RAG system endpoints
  rag: {
    query: '/rag-system/query/',
    sources: '/rag-system/sources/'
  }
};

// WebSocket endpoints by module
export const WS_ENDPOINTS = {
  // DOE WebSocket endpoints
  doe: {
    analysis: (id) => `${WS_CONFIG.apiPath}/${API_VERSION}/doe-analysis/analysis/${id}/`,
    designGeneration: (id) => `${WS_CONFIG.apiPath}/${API_VERSION}/doe-analysis/design/${id}/`,
    optimization: (id) => `${WS_CONFIG.apiPath}/${API_VERSION}/doe-analysis/optimization/${id}/`
  },
  
  // PCA WebSocket endpoints
  pca: {
    progress: (id) => `${WS_CONFIG.apiPath}/${API_VERSION}/pca-analysis/progress/${id}/`
  },
  
  // Workflow WebSocket endpoints (merged)
  workflow: {
    execution: (id) => `${WS_CONFIG.apiPath}/${API_VERSION}/mainapp/workflows/${id}/execution/`,
    monitoring: (workflowId) => `workflow/monitoring/${workflowId}/`,
    collaboration: (workflowId) => `workflow/collaboration/${workflowId}/`
  },
  
  // RAG system WebSocket endpoints
  rag: {
    query: 'rag/query/',
    search: 'rag/search/'
  },
  
  // Analysis module WebSocket endpoints
  analysis: {
    doe: (analysisId) => `doe/analysis/${analysisId}/`,
    pca: (analysisId) => `pca/analysis/${analysisId}/`,
    sqc: (analysisId) => `sqc/analysis/${analysisId}/`,
    confidence: (analysisId) => `confidence/analysis/${analysisId}/`
  }
};

// Helper function to get WebSocket URL for any path
export const getWebSocketUrl = (path) => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = process.env.REACT_APP_WEBSOCKET_HOST || window.location.host;
  return `${wsProtocol}//${wsHost}/ws/${path}`;
};

export default {
  API_BASE_URL,
  API_VERSION,
  API_URL,
  AUTH_CONFIG,
  WS_CONFIG,
  API_ENDPOINTS,
  WS_ENDPOINTS
};