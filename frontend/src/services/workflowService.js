import apiService from './apiService';
import { API_ENDPOINTS } from '../config/apiConfig';

/**
 * Service for interacting with the workflow management API
 */

/**
 * Get a list of workflows with optional filtering
 * 
 * @param {Object} params - Filter parameters
 * @returns {Promise} - Workflows list
 */
export const getWorkflows = async (params = {}) => {
  return await apiService.get(API_ENDPOINTS.workflow.list, params);
};

/**
 * Get a specific workflow by ID
 * 
 * @param {string} workflowId - Workflow ID
 * @returns {Promise} - Workflow details
 */
export const getWorkflow = async (workflowId) => {
  return await apiService.get(API_ENDPOINTS.workflow.detail(workflowId));
};

/**
 * Create a new workflow
 * 
 * @param {Object} workflowData - Workflow data
 * @returns {Promise} - Created workflow
 */
export const createWorkflow = async (workflowData) => {
  return await apiService.post(API_ENDPOINTS.workflow.list, workflowData);
};

/**
 * Update an existing workflow
 * 
 * @param {string} workflowId - Workflow ID
 * @param {Object} workflowData - Updated workflow data
 * @returns {Promise} - Updated workflow
 */
export const updateWorkflow = async (workflowId, workflowData) => {
  return await apiService.put(API_ENDPOINTS.workflow.detail(workflowId), workflowData);
};

/**
 * Delete a workflow
 * 
 * @param {string} workflowId - Workflow ID to delete
 * @returns {Promise} - Deletion result
 */
export const deleteWorkflow = async (workflowId) => {
  return await apiService.del(API_ENDPOINTS.workflow.detail(workflowId));
};

/**
 * Get workflow steps
 * 
 * @param {string} workflowId - Workflow ID
 * @returns {Promise} - Workflow steps
 */
export const getWorkflowSteps = async (workflowId) => {
  return await apiService.get(API_ENDPOINTS.workflow.steps(workflowId));
};

/**
 * Create a workflow step
 * 
 * @param {string} workflowId - Workflow ID
 * @param {Object} stepData - Step data
 * @returns {Promise} - Created step
 */
export const createWorkflowStep = async (workflowId, stepData) => {
  return await apiService.post(API_ENDPOINTS.workflow.steps(workflowId), stepData);
};

/**
 * Update a workflow step
 * 
 * @param {string} workflowId - Workflow ID
 * @param {string} stepId - Step ID
 * @param {Object} stepData - Updated step data
 * @returns {Promise} - Updated step
 */
export const updateWorkflowStep = async (workflowId, stepId, stepData) => {
  return await apiService.put(API_ENDPOINTS.workflow.step(workflowId, stepId), stepData);
};

/**
 * Delete a workflow step
 * 
 * @param {string} workflowId - Workflow ID
 * @param {string} stepId - Step ID to delete
 * @returns {Promise} - Deletion result
 */
export const deleteWorkflowStep = async (workflowId, stepId) => {
  return await apiService.del(API_ENDPOINTS.workflow.step(workflowId, stepId));
};

/**
 * Update step status
 * 
 * @param {string} workflowId - Workflow ID
 * @param {string} stepId - Step ID
 * @param {Object} statusData - Status update data
 * @returns {Promise} - Updated status
 */
export const updateStepStatus = async (workflowId, stepId, statusData) => {
  return await apiService.patch(
    API_ENDPOINTS.workflow.step(workflowId, stepId), 
    { status: statusData.status, error_message: statusData.error_message }
  );
};

/**
 * Execute a workflow
 * 
 * @param {string} workflowId - Workflow ID
 * @param {Object} options - Execution options
 * @returns {Promise} - Execution result
 */
export const executeWorkflow = async (workflowId, options = {}) => {
  return await apiService.post(API_ENDPOINTS.workflow.execute(workflowId), options);
};

/**
 * Get execution status
 * 
 * @param {string} workflowId - Workflow ID
 * @returns {Promise} - Execution status
 */
export const getExecutionStatus = async (workflowId) => {
  return await apiService.get(API_ENDPOINTS.workflow.status(workflowId));
};

/**
 * Cancel execution
 * 
 * @param {string} workflowId - Workflow ID
 * @returns {Promise} - Cancellation result
 */
export const cancelExecution = async (workflowId) => {
  return await apiService.post(API_ENDPOINTS.workflow.cancel(workflowId));
};

/**
 * Get execution history
 * 
 * @param {Object} params - Filter parameters
 * @returns {Promise} - Execution history
 */
export const getExecutionHistory = async (params = {}) => {
  return await apiService.get(`${API_ENDPOINTS.workflow.list}history/`, params);
};

/**
 * Clone a workflow
 * 
 * @param {string} workflowId - Workflow ID to clone
 * @param {Object} options - Clone options
 * @returns {Promise} - Cloned workflow
 */
export const cloneWorkflow = async (workflowId, options = {}) => {
  return await apiService.post(API_ENDPOINTS.workflow.clone(workflowId), options);
};

/**
 * Export a workflow
 * 
 * @param {string} workflowId - Workflow ID to export
 * @param {Object} options - Export options
 * @returns {Promise} - Export result
 */
export const exportWorkflow = async (workflowId, options = {}) => {
  return await apiService.downloadFile(
    API_ENDPOINTS.workflow.export(workflowId),
    options,
    `workflow_${workflowId}.json`
  );
};

/**
 * Import a workflow
 * 
 * @param {File|FormData} file - Workflow file or FormData
 * @param {boolean} importData - Whether to import associated data
 * @param {function} onProgress - Progress callback
 * @returns {Promise} - Import result
 */
export const importWorkflow = async (file, importData = false, onProgress = null) => {
  return await apiService.uploadFile(
    API_ENDPOINTS.workflow.import,
    file,
    { import_data: importData },
    onProgress
  );
};

export default {
  getWorkflows,
  getWorkflow,
  createWorkflow,
  updateWorkflow,
  deleteWorkflow,
  getWorkflowSteps,
  createWorkflowStep,
  updateWorkflowStep,
  deleteWorkflowStep,
  updateStepStatus,
  executeWorkflow,
  getExecutionStatus,
  cancelExecution,
  getExecutionHistory,
  cloneWorkflow,
  exportWorkflow,
  importWorkflow
};