import axios from 'axios';

// API base URL
const API_URL = '/api/v1/pca-analysis';

// Project endpoints
export const fetchPcaProjects = async () => {
  try {
    const response = await axios.get(`${API_URL}/projects/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const fetchPcaProject = async (projectId) => {
  try {
    const response = await axios.get(`${API_URL}/projects/${projectId}/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const createPcaProject = async (projectData) => {
  try {
    const response = await axios.post(`${API_URL}/projects/`, projectData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const updatePcaProject = async (projectId, projectData) => {
  try {
    const response = await axios.patch(`${API_URL}/projects/${projectId}/`, projectData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const deletePcaProject = async (projectId) => {
  try {
    const response = await axios.delete(`${API_URL}/projects/${projectId}/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Data upload
export const uploadPcaData = async (formData) => {
  try {
    const response = await axios.post(`${API_URL}/projects/upload_data/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const createPcaDemoProject = async (projectData) => {
  try {
    const response = await axios.post(`${API_URL}/projects/create_demo/`, projectData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// PCA analysis
export const runPcaAnalysis = async (projectId, analysisParams) => {
  try {
    const response = await axios.post(`${API_URL}/projects/${projectId}/run_pca/`, analysisParams);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Results endpoints
export const fetchPcaResults = async (resultId) => {
  try {
    const response = await axios.get(`${API_URL}/results/${resultId}/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Alias for fetchPcaResults for compatibility
export const getPcaResults = fetchPcaResults;

export const fetchProjectResults = async (projectId) => {
  try {
    const response = await axios.get(`${API_URL}/results/`, {
      params: { project: projectId }
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const fetchPcaVisualizationData = async (resultId, visualizationParams) => {
  try {
    const response = await axios.get(`${API_URL}/results/${resultId}/visualization_data/`, {
      params: visualizationParams
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const fetchPcaVisualizations = async (resultId) => {
  try {
    const response = await axios.get(`${API_URL}/results/${resultId}/visualizations/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const fetchGeneContributions = async (resultId, params) => {
  try {
    const response = await axios.get(`${API_URL}/results/${resultId}/gene_contributions/`, {
      params
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Visualization endpoints
export const createPcaVisualization = async (resultId, visualizationData) => {
  try {
    const response = await axios.post(`${API_URL}/results/${resultId}/visualizations/`, visualizationData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const fetchVisualizationData = async (resultId, visualizationId) => {
  try {
    const response = await axios.get(`${API_URL}/results/${resultId}/visualizations/${visualizationId}/data/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Sample group endpoints
export const fetchSampleGroups = async (projectId) => {
  try {
    const response = await axios.get(`${API_URL}/projects/${projectId}/groups/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const createSampleGroup = async (projectId, groupData) => {
  try {
    const response = await axios.post(`${API_URL}/projects/${projectId}/groups/`, groupData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const updateSampleGroup = async (projectId, groupId, groupData) => {
  try {
    const response = await axios.patch(`${API_URL}/projects/${projectId}/groups/${groupId}/`, groupData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const deleteSampleGroup = async (projectId, groupId) => {
  try {
    const response = await axios.delete(`${API_URL}/projects/${projectId}/groups/${groupId}/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Sample endpoints
export const fetchSamples = async (projectId) => {
  try {
    const response = await axios.get(`${API_URL}/projects/${projectId}/samples/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

export const updateSample = async (projectId, sampleId, sampleData) => {
  try {
    const response = await axios.patch(`${API_URL}/projects/${projectId}/samples/${sampleId}/`, sampleData);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Gene endpoints
export const fetchGenes = async (projectId) => {
  try {
    const response = await axios.get(`${API_URL}/projects/${projectId}/genes/`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
};

// All demo functionality has been removed for authenticity

// No demo data - only real user data
// All demo/mock data has been completely removed

// Demo wrapper removed - only real API calls

// Error handling
const handleApiError = (error) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const errorMessage = error.response.data.detail || 
                         error.response.data.message || 
                         error.response.data.error ||
                         'Server error';
    return new Error(errorMessage);
  } else if (error.request) {
    // The request was made but no response was received
    return new Error('No response from server. Please check your network connection.');
  } else {
    // Something happened in setting up the request that triggered an Error
    return new Error('An error occurred while making the request.');
  }
};

// No demo mode overrides - only real API calls
// Removed all demo mode logic

export default {
  fetchPcaProjects,
  fetchPcaProject,
  createPcaProject,
  updatePcaProject,
  deletePcaProject,
  uploadPcaData,
  createPcaDemoProject,
  runPcaAnalysis,
  fetchPcaResults,
  getPcaResults,
  fetchProjectResults,
  fetchPcaVisualizationData,
  fetchPcaVisualizations,
  fetchGeneContributions,
  createPcaVisualization,
  fetchVisualizationData,
  fetchSampleGroups,
  createSampleGroup,
  updateSampleGroup,
  deleteSampleGroup,
  fetchSamples,
  updateSample,
  fetchGenes
};