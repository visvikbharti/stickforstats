import axios from 'axios';

// Base API configuration
export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add authentication token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login if needed
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    // Log errors in development
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', error.response || error);
    }
    
    return Promise.reject(error);
  }
);

// API for PCA Analysis
export const pcaApi = {
  createProject: (data) => api.post('/api/v1/pca-analysis/projects/', data),
  getProjects: () => api.get('/api/v1/pca-analysis/projects/'),
  getProjectDetail: (id) => api.get(`/api/v1/pca-analysis/projects/${id}/`),
  uploadData: (projectId, data) => api.post(`/api/v1/pca-analysis/projects/${projectId}/upload_data/`, data),
  getSampleGroups: (projectId) => api.get(`/api/v1/pca-analysis/projects/${projectId}/sample-groups/`),
  runPCA: (projectId, data) => api.post(`/api/v1/pca-analysis/projects/${projectId}/run_pca/`, data),
  getPCAResults: (projectId) => api.get(`/api/v1/pca-analysis/projects/${projectId}/pca-results/`),
  createDemoData: () => api.post('/api/v1/pca-analysis/projects/create_demo_data/'),
};

// API for DOE Analysis
export const doeApi = {
  createExperimentDesign: (data) => api.post('/api/v1/doe-analysis/experiment-designs/', data),
  getExperimentDesigns: () => api.get('/api/v1/doe-analysis/experiment-designs/'),
  getExperimentDesignDetail: (id) => api.get(`/api/v1/doe-analysis/experiment-designs/${id}/`),
  generateDesign: (data) => api.post('/api/v1/doe-analysis/experiment-designs/generate_design/', data),
  uploadDesignData: (designId, data) => api.post(`/api/v1/doe-analysis/experiment-designs/${designId}/upload_design_data/`, data),
  runModelAnalysis: (data) => api.post('/api/v1/doe-analysis/model-analyses/run_analysis/', data),
  getModelAnalyses: () => api.get('/api/v1/doe-analysis/model-analyses/'),
  runOptimization: (data) => api.post('/api/v1/doe-analysis/optimization-analyses/run_optimization/', data),
  getOptimizationAnalyses: () => api.get('/api/v1/doe-analysis/optimization-analyses/'),
};

// API for SQC Analysis
export const sqcApi = {
  createControlChart: (data) => api.post('/api/v1/sqc-analysis/control-charts/', data),
  getControlCharts: () => api.get('/api/v1/sqc-analysis/control-charts/'),
  getControlChartDetail: (id) => api.get(`/api/v1/sqc-analysis/control-charts/${id}/`),
  getControlChartPlotData: (id) => api.get(`/api/v1/sqc-analysis/control-charts/${id}/plot_data/`),
  getControlChartRecommendations: (id) => api.get(`/api/v1/sqc-analysis/control-charts/${id}/recommendations/`),
  
  createProcessCapability: (data) => api.post('/api/v1/sqc-analysis/process-capability/', data),
  getProcessCapabilities: () => api.get('/api/v1/sqc-analysis/process-capability/'),
  
  createAcceptanceSampling: (data) => api.post('/api/v1/sqc-analysis/acceptance-sampling/', data),
  getAcceptanceSamplings: () => api.get('/api/v1/sqc-analysis/acceptance-sampling/'),
  getOCCurve: (id) => api.get(`/api/v1/sqc-analysis/acceptance-sampling/${id}/oc_curve/`),
  compareSamplingPlans: (data) => api.post('/api/v1/sqc-analysis/acceptance-sampling/compare_plans/', data),
  
  createMSA: (data) => api.post('/api/v1/sqc-analysis/msa/', data),
  getMSAs: () => api.get('/api/v1/sqc-analysis/msa/'),
  
  createEconomicDesign: (data) => api.post('/api/v1/sqc-analysis/economic-design/', data),
  getEconomicDesigns: () => api.get('/api/v1/sqc-analysis/economic-design/'),
  compareAlternatives: (data) => api.post('/api/v1/sqc-analysis/economic-design/compare_alternatives/', data),
  calculateROI: (data) => api.post('/api/v1/sqc-analysis/economic-design/calculate_roi/', data),
  
  createSPCImplementation: (data) => api.post('/api/v1/sqc-analysis/spc-implementation/', data),
  getSPCImplementations: () => api.get('/api/v1/sqc-analysis/spc-implementation/'),
  getIndustryRecommendations: () => api.get('/api/v1/sqc-analysis/spc-implementation/industry_recommendations/'),
};

// API for Confidence Intervals
export const confidenceIntervalsApi = {
  calculateInterval: (data) => api.post('/api/v1/confidence-intervals/calculate/', data),
  getSavedIntervals: () => api.get('/api/v1/confidence-intervals/saved/'),
  saveInterval: (data) => api.post('/api/v1/confidence-intervals/saved/', data),
};

// API for Probability Distributions
export const probabilityDistributionsApi = {
  getDistributionInfo: (distribution) => api.get(`/api/v1/probability-distributions/${distribution}/`),
  calculatePDF: (distribution, params) => api.post(`/api/v1/probability-distributions/${distribution}/pdf/`, params),
  calculateCDF: (distribution, params) => api.post(`/api/v1/probability-distributions/${distribution}/cdf/`, params),
  calculateQuantile: (distribution, params) => api.post(`/api/v1/probability-distributions/${distribution}/quantile/`, params),
  generateSamples: (distribution, params) => api.post(`/api/v1/probability-distributions/${distribution}/random/`, params),
  fitDistribution: (data) => api.post('/api/v1/probability-distributions/fit/', data),
  compareDistributions: (data) => api.post('/api/v1/probability-distributions/compare/', data),
};

// API for Authentication
export const authApi = {
  login: (credentials) => api.post('/api/v1/core/auth/login/', credentials),
  register: (userData) => api.post('/api/v1/core/auth/register/', userData),
  getUser: () => api.get('/api/v1/core/auth/profile/'),
  logout: () => api.post('/api/v1/core/auth/logout/'),
};

// API for Data Management
export const dataApi = {
  uploadDataset: (data) => api.post('/api/v1/core/datasets/', data),
  getDatasets: () => api.get('/api/v1/core/datasets/'),
  getDatasetDetail: (id) => api.get(`/api/v1/core/datasets/${id}/`),
  deleteDataset: (id) => api.delete(`/api/v1/core/datasets/${id}/`),
};

// API for RAG System
export const ragApi = {
  query: (data) => api.post('/api/v1/rag/query/', data),
  getConversations: () => api.get('/api/v1/rag/conversations/'),
  getConversationDetail: (id) => api.get(`/api/v1/rag/conversations/${id}/`),
  submitFeedback: (data) => api.post('/api/v1/rag/feedback/', data),
};

// API for Workflow Management
export const workflowApi = {
  // Workflow operations
  getWorkflows: (params) => api.get('/api/v1/mainapp/workflows/', { params }),
  getWorkflow: (id) => api.get(`/api/v1/mainapp/workflows/${id}/`),
  createWorkflow: (data) => api.post('/api/v1/mainapp/workflows/', data),
  updateWorkflow: (id, data) => api.put(`/api/v1/mainapp/workflows/${id}/`, data),
  deleteWorkflow: (id) => api.delete(`/api/v1/mainapp/workflows/${id}/`),
  
  // Workflow step operations
  getWorkflowSteps: (workflowId) => api.get(`/api/v1/mainapp/workflows/${workflowId}/steps/`),
  getWorkflowStep: (workflowId, stepId) => api.get(`/api/v1/mainapp/workflows/${workflowId}/steps/${stepId}/`),
  createWorkflowStep: (workflowId, data) => api.post(`/api/v1/mainapp/workflows/${workflowId}/steps/`, data),
  updateWorkflowStep: (workflowId, stepId, data) => api.put(`/api/v1/mainapp/workflows/${workflowId}/steps/${stepId}/`, data),
  deleteWorkflowStep: (workflowId, stepId) => api.delete(`/api/v1/mainapp/workflows/${workflowId}/steps/${stepId}/`),
  updateStepStatus: (workflowId, stepId, data) => api.put(`/api/v1/mainapp/workflows/${workflowId}/steps/${stepId}/status/`, data),
  
  // Workflow execution
  executeWorkflow: (workflowId, data) => api.post(`/api/v1/mainapp/workflows/${workflowId}/execute/`, data),
  getExecutionStatus: (workflowId) => api.get(`/api/v1/mainapp/workflows/${workflowId}/execution-status/`),
  cancelExecution: (workflowId) => api.delete(`/api/v1/mainapp/workflows/${workflowId}/execution-status/`),
  getExecutionHistory: (params) => api.get('/api/v1/mainapp/workflows/execution-history/', { params }),
  
  // Workflow management
  cloneWorkflow: (workflowId, data) => api.post(`/api/v1/mainapp/workflows/${workflowId}/clone/`, data),
  exportWorkflow: (workflowId, params) => api.get(`/api/v1/mainapp/workflows/${workflowId}/export/`, { 
    params, 
    responseType: 'blob' 
  }),
  importWorkflow: (formData) => api.post('/api/v1/mainapp/workflows/import/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
};

// API for Report Generation
export const reportApi = {
  generateReport: (data) => api.post('/api/v1/mainapp/reports/generate/', data),
  getReports: () => api.get('/api/v1/mainapp/reports/'),
  getReportDetails: (reportId) => api.get(`/api/v1/mainapp/reports/${reportId}/`),
  downloadReport: (reportId) => api.get(`/api/v1/mainapp/reports/${reportId}/?download=true`, {
    responseType: 'blob'
  }),
};