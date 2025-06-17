import apiService from './apiService';

const API_URL = '/api/v1/doe';

/**
 * Generate an experimental design based on user specifications
 * @param {Object} designData - Design specification including factors, responses, etc.
 * @returns {Promise<Object>} The generated design
 */
export async function generateDesign(designData) {
  try {
    return await apiService.post(
      `${API_URL}/experiment-designs/generate_design/`,
      designData
    );
  } catch (error) {
    console.error('Error generating design:', error);
    throw error;
  }
}

/**
 * Get a list of experiment designs
 * @param {Object} params - Query parameters
 * @returns {Promise<Array>} List of experiment designs
 */
export async function getExperimentDesigns(params = {}) {
  try {
    return await apiService.get(
      `${API_URL}/experiment-designs/`,
      params
    );
  } catch (error) {
    console.error('Error fetching experiment designs:', error);
    throw error;
  }
}

/**
 * Get details of a specific experiment design
 * @param {number} designId - ID of the experiment design
 * @returns {Promise<Object>} Experiment design details
 */
export async function getExperimentDesign(designId) {
  try {
    return await apiService.get(
      `${API_URL}/experiment-designs/${designId}/`
    );
  } catch (error) {
    console.error('Error fetching experiment design:', error);
    throw error;
  }
}

/**
 * Upload experimental data for an existing design
 * @param {number} designId - ID of the experiment design
 * @param {FormData} formData - Form data containing the file to upload
 * @returns {Promise<Object>} Upload result
 */
export async function uploadExperimentData(designId, formData) {
  try {
    return await apiService.uploadFile(
      `${API_URL}/experiment-designs/${designId}/upload_design_data/`,
      formData
    );
  } catch (error) {
    console.error('Error uploading experiment data:', error);
    throw error;
  }
}

/**
 * Run model analysis on experiment data
 * @param {Object} analysisData - Analysis specification
 * @returns {Promise<Object>} Analysis results
 */
export async function runModelAnalysis(analysisData) {
  try {
    return await apiService.post(
      `${API_URL}/model-analyses/run_analysis/`,
      analysisData
    );
  } catch (error) {
    console.error('Error running model analysis:', error);
    throw error;
  }
}

/**
 * Get details of a specific model analysis
 * @param {number} analysisId - ID of the model analysis
 * @returns {Promise<Object>} Model analysis details
 */
export async function getModelAnalysis(analysisId) {
  try {
    return await apiService.get(
      `${API_URL}/model-analyses/${analysisId}/`
    );
  } catch (error) {
    console.error('Error fetching model analysis:', error);
    throw error;
  }
}

/**
 * Generate a report for a model analysis
 * @param {number} analysisId - ID of the model analysis
 * @returns {Promise<Blob>} PDF report blob
 */
export async function generateAnalysisReport(analysisId) {
  try {
    return await apiService.downloadFile(
      `${API_URL}/model-analyses/${analysisId}/generate_report/`
    );
  } catch (error) {
    console.error('Error generating analysis report:', error);
    throw error;
  }
}

/**
 * Run optimization on a model analysis
 * @param {Object} optimizationData - Optimization specification
 * @returns {Promise<Object>} Optimization results
 */
export async function optimizeResponse(optimizationData) {
  try {
    return await apiService.post(
      `${API_URL}/optimization-analyses/run_optimization/`,
      optimizationData
    );
  } catch (error) {
    console.error('Error running optimization:', error);
    throw error;
  }
}

/**
 * Get details of a specific optimization analysis
 * @param {number} optimizationId - ID of the optimization analysis
 * @returns {Promise<Object>} Optimization analysis details
 */
export async function getOptimizationAnalysis(optimizationId) {
  try {
    return await apiService.get(
      `${API_URL}/optimization-analyses/${optimizationId}/`
    );
  } catch (error) {
    console.error('Error fetching optimization analysis:', error);
    throw error;
  }
}

/**
 * Generate a report for an optimization analysis
 * @param {number} optimizationId - ID of the optimization analysis
 * @returns {Promise<Blob>} PDF report blob
 */
export async function generateOptimizationReport(optimizationId) {
  try {
    return await apiService.downloadFile(
      `${API_URL}/optimization-analyses/${optimizationId}/generate_report/`
    );
  } catch (error) {
    console.error('Error generating optimization report:', error);
    throw error;
  }
}

/**
 * Set up a WebSocket connection for real-time updates during analysis
 * @param {number} userId - User ID
 * @param {number} experimentId - Experiment design ID
 * @param {function} onStatusUpdate - Callback for status updates
 * @returns {WebSocket} WebSocket connection
 */
export function setupAnalysisWebSocket(userId, experimentId, onStatusUpdate) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/doe/analysis/${userId}/${experimentId}/`);
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'analysis_status') {
      onStatusUpdate(data.message);
    }
  };
  
  return socket;
}

/**
 * Set up a WebSocket connection for real-time updates during optimization
 * @param {number} userId - User ID
 * @param {number} analysisId - Model analysis ID
 * @param {function} onStatusUpdate - Callback for status updates
 * @returns {WebSocket} WebSocket connection
 */
export function setupOptimizationWebSocket(userId, analysisId, onStatusUpdate) {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/doe/optimization/${userId}/${analysisId}/`);
  
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'optimization_status') {
      onStatusUpdate(data.message);
    }
  };
  
  return socket;
}

/**
 * Fetch educational content for DOE module
 * @returns {Promise<Object>} Educational content
 */
export async function fetchEducationalContent() {
  try {
    return await apiService.get(`/api/v1/content/doe/`);
  } catch (error) {
    console.error('Error fetching educational content:', error);
    throw error;
  }
}

/**
 * Fetch analysis data for a specific experiment
 * @param {number} experimentId - ID of the experiment
 * @returns {Promise<Object>} Analysis data
 */
export async function fetchAnalysisData(experimentId) {
  try {
    return await apiService.get(
      `${API_URL}/experiment-analyses/${experimentId}/`
    );
  } catch (error) {
    console.error('Error fetching analysis data:', error);
    throw error;
  }
}