import apiService from './apiService';

const API_URL = '/api/v1/doe';

// Check if in demo mode
const isDemoMode = process.env.REACT_APP_DEMO_MODE === 'true' || process.env.REACT_APP_DISABLE_API === 'true';

// Mock experiment designs for demo mode
const mockDesigns = [
  {
    id: 'demo-doe-1',
    name: 'Factorial Design - Process Optimization',
    design_type: 'factorial',
    factors: [
      { name: 'Temperature', levels: [150, 180, 210], units: '°C' },
      { name: 'Pressure', levels: [1, 2, 3], units: 'bar' },
      { name: 'Time', levels: [30, 45, 60], units: 'min' }
    ],
    responses: ['Yield', 'Purity'],
    run_order: Array.from({length: 27}, (_, i) => i + 1),
    created_at: new Date().toISOString()
  },
  {
    id: 'demo-doe-2', 
    name: 'Response Surface - Chemical Reaction',
    design_type: 'response_surface',
    factors: [
      { name: 'Catalyst', min: 0.5, max: 2.5, units: 'g' },
      { name: 'pH', min: 6, max: 8, units: '' }
    ],
    responses: ['Conversion', 'Selectivity'],
    created_at: new Date().toISOString()
  }
];

// Generate mock analysis results
const generateMockAnalysisResults = (designId) => {
  return {
    id: `demo-analysis-${Date.now()}`,
    design_id: designId,
    model_type: 'linear',
    r_squared: 0.92,
    adjusted_r_squared: 0.89,
    effects: [
      { factor: 'Temperature', effect: 15.2, p_value: 0.001, significant: true },
      { factor: 'Pressure', effect: 8.7, p_value: 0.023, significant: true },
      { factor: 'Time', effect: 3.4, p_value: 0.156, significant: false },
      { factor: 'Temperature*Pressure', effect: 6.1, p_value: 0.045, significant: true }
    ],
    anova: {
      model: { df: 6, sum_sq: 2340.5, mean_sq: 390.1, f_value: 28.4, p_value: 0.0001 },
      residual: { df: 20, sum_sq: 274.8, mean_sq: 13.74 },
      total: { df: 26, sum_sq: 2615.3 }
    },
    coefficients: [
      { term: 'Intercept', coefficient: 75.3, std_error: 1.2, t_value: 62.8, p_value: 0.0001 },
      { term: 'Temperature', coefficient: 0.152, std_error: 0.021, t_value: 7.24, p_value: 0.001 },
      { term: 'Pressure', coefficient: 4.35, std_error: 1.82, t_value: 2.39, p_value: 0.023 }
    ],
    residuals: Array.from({length: 27}, () => (Math.random() - 0.5) * 10),
    predictions: Array.from({length: 27}, () => 70 + Math.random() * 30)
  };
};

/**
 * Generate an experimental design based on user specifications
 * @param {Object} designData - Design specification including factors, responses, etc.
 * @returns {Promise<Object>} The generated design
 */
export async function generateDesign(designData) {
  if (isDemoMode) {
    // Simulate design generation in demo mode
    const newDesign = {
      id: `demo-doe-${Date.now()}`,
      name: designData.name || 'New Experimental Design',
      design_type: designData.design_type || 'factorial',
      factors: designData.factors || [],
      responses: designData.responses || ['Response 1'],
      runs: designData.design_type === 'factorial' ? 
        Math.pow(2, designData.factors?.length || 2) : 13,
      created_at: new Date().toISOString()
    };
    mockDesigns.push(newDesign);
    return newDesign;
  }
  
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
  if (isDemoMode) {
    return mockDesigns;
  }
  
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
  if (isDemoMode) {
    const design = mockDesigns.find(d => d.id === designId);
    if (design) return design;
    throw new Error('Design not found');
  }
  
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
  if (isDemoMode) {
    // Simulate analysis in demo mode
    await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate processing
    return generateMockAnalysisResults(analysisData.design_id);
  }
  
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
  if (isDemoMode) {
    // Return mock analysis data for demo mode
    const design = mockDesigns.find(d => d.id === experimentId);
    if (!design) throw new Error('Experiment not found');
    
    return {
      experiment: design,
      data: Array.from({length: design.run_order?.length || 27}, (_, i) => ({
        run: i + 1,
        ...Object.fromEntries(
          design.factors.map(f => [f.name, f.levels ? f.levels[i % f.levels.length] : f.min + Math.random() * (f.max - f.min)])
        ),
        Yield: 70 + Math.random() * 30,
        Purity: 85 + Math.random() * 15
      })),
      analysis: generateMockAnalysisResults(experimentId)
    };
  }
  
  try {
    return await apiService.get(
      `${API_URL}/experiment-analyses/${experimentId}/`
    );
  } catch (error) {
    console.error('Error fetching analysis data:', error);
    throw error;
  }
}