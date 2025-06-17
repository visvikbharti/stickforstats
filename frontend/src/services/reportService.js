import apiService from './apiService';
import { API_ENDPOINTS } from '../config/apiConfig';

// DEMO MODE flag - set to true to enable offline demo functionality
const DEMO_MODE = true;

/**
 * Service for interacting with the report generation API
 */

/**
 * Get a list of generated reports
 * 
 * @param {Object} params - Filter parameters
 * @returns {Promise} - Reports list
 */
export const getReports = async (params = {}) => {
  // In demo mode, return mock report data
  if (DEMO_MODE) {
    await new Promise(resolve => setTimeout(resolve, 800)); // Simulate API delay
    
    // Generate some demo reports
    const demoReports = [
      {
        id: 'demo-report-1',
        title: 'T-Test Analysis Report',
        description: 'Statistical comparison between control and treatment groups',
        status: 'completed',
        format: 'pdf',
        created_at: '2025-05-15T09:34:12Z',
        updated_at: '2025-05-15T09:35:24Z',
        analyses_count: 3,
        has_visualizations: true,
        has_raw_data: false,
        size_bytes: 1873642
      },
      {
        id: 'demo-report-2',
        title: 'ANOVA Analysis Report',
        description: 'One-way ANOVA of gene expression data',
        status: 'completed',
        format: 'pdf',
        created_at: '2025-05-10T15:22:46Z',
        updated_at: '2025-05-10T15:24:18Z',
        analyses_count: 5,
        has_visualizations: true,
        has_raw_data: true,
        size_bytes: 2543921
      },
      {
        id: 'demo-report-3',
        title: 'Regression Analysis Report',
        description: 'Multiple regression analysis of experimental data',
        status: 'completed',
        format: 'xlsx',
        created_at: '2025-05-05T11:12:33Z',
        updated_at: '2025-05-05T11:15:02Z',
        analyses_count: 2,
        has_visualizations: true,
        has_raw_data: true,
        size_bytes: 1254763
      }
    ];
    
    // Apply any filtering from params
    let filteredReports = [...demoReports];
    
    if (params.search) {
      const searchLower = params.search.toLowerCase();
      filteredReports = filteredReports.filter(report => 
        report.title.toLowerCase().includes(searchLower) || 
        (report.description && report.description.toLowerCase().includes(searchLower))
      );
    }
    
    if (params.format) {
      filteredReports = filteredReports.filter(report => 
        report.format === params.format
      );
    }
    
    // Sort by created_at by default (newest first)
    filteredReports.sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    );
    
    return {
      results: filteredReports,
      count: filteredReports.length,
      total: demoReports.length
    };
  }
  
  // Normal API call for non-demo mode
  return await apiService.get(API_ENDPOINTS.report.list, params);
};

/**
 * Get a specific report by ID
 * 
 * @param {string} reportId - Report ID
 * @returns {Promise} - Report details
 */
export const getReportDetails = async (reportId) => {
  return await apiService.get(API_ENDPOINTS.report.detail(reportId));
};

/**
 * Generate a new report
 * 
 * @param {Object} reportData - Report generation parameters
 * @returns {Promise} - Generated report metadata
 */
export const generateReport = async (reportData) => {
  // In demo mode, bypass the API and simulate a successful report generation
  if (DEMO_MODE) {
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate API delay
    
    const reportId = 'demo-report-' + Date.now();
    const timestamp = new Date().toISOString();
    
    return {
      id: reportId,
      title: reportData.title || 'Analysis Report',
      description: reportData.description || null,
      status: 'completed',
      format: reportData.format || 'pdf',
      created_at: timestamp,
      updated_at: timestamp,
      url: `/static/demo-reports/${reportId}.${reportData.format || 'pdf'}`,
      size_bytes: 1024 * 1024 * (Math.random() * 2 + 0.5), // Random size between 0.5-2.5MB
      analyses_count: reportData.analyses?.length || 0,
      has_visualizations: reportData.includeVisualizations !== false,
      has_raw_data: reportData.includeRawData === true
    };
  }
  
  // Normal API call for non-demo mode
  return await apiService.post(API_ENDPOINTS.report.generate, {
    title: reportData.title || 'Analysis Report',
    description: reportData.description || null,
    analyses: reportData.analyses || [],
    format: reportData.format || 'pdf',
    include_visualizations: reportData.includeVisualizations !== undefined 
      ? reportData.includeVisualizations : true,
    include_raw_data: reportData.includeRawData !== undefined 
      ? reportData.includeRawData : false
  });
};

/**
 * Download a report
 * 
 * @param {string} reportId - Report ID to download
 * @param {string} filename - Optional filename
 * @returns {Promise} - Download result
 */
export const downloadReport = async (reportId, filename = null) => {
  // Demo mode - simulate a download by creating a simple PDF download
  if (DEMO_MODE) {
    // Add delay to simulate downloading
    await new Promise(resolve => setTimeout(resolve, 1200));
    
    if (!filename) {
      filename = `statistical_analysis_report_${reportId.substring(0, 8)}.pdf`;
    }
    
    // Create a simple demo PDF download
    try {
      // Create a simple HTML string for the PDF
      const htmlContent = `
        <html>
          <head>
            <title>StickForStats Analysis Report</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 40px; }
              h1 { color: #2c3e50; }
              .header { border-bottom: 1px solid #eee; padding-bottom: 20px; }
              .section { margin: 20px 0; }
              .footer { margin-top: 50px; color: #7f8c8d; font-size: 12px; }
            </style>
          </head>
          <body>
            <div class="header">
              <h1>StickForStats Analysis Report</h1>
              <p>Generated: ${new Date().toLocaleString()}</p>
              <p>Report ID: ${reportId}</p>
            </div>
            <div class="section">
              <h2>Statistical Analysis Summary</h2>
              <p>This is a demonstration report generated by StickForStats.</p>
              <p>In a real report, this would contain detailed statistical analysis results.</p>
            </div>
            <div class="section">
              <h2>Visualizations</h2>
              <p>Graphs and charts would appear in this section.</p>
            </div>
            <div class="footer">
              <p>© ${new Date().getFullYear()} StickForStats - Demo Report</p>
            </div>
          </body>
        </html>
      `;
      
      // Create a Blob with the HTML content
      const blob = new Blob([htmlContent], { type: 'text/html' });
      
      // Create a download link and trigger it
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      return { success: true, filename };
    } catch (error) {
      console.error('Error creating demo PDF:', error);
      throw new Error('Failed to generate demo report');
    }
  }
  
  // Normal API call for non-demo mode
  // Get report details first to determine appropriate filename if not provided
  if (!filename) {
    try {
      const reportDetails = await getReportDetails(reportId);
      filename = `${reportDetails.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${reportDetails.format}`;
    } catch (error) {
      filename = `report_${reportId}.pdf`;
    }
  }
  
  return await apiService.downloadFile(
    API_ENDPOINTS.report.download(reportId),
    {},
    filename
  );
};

/**
 * Delete a report
 * 
 * @param {string} reportId - Report ID to delete
 * @returns {Promise} - Deletion result
 */
export const deleteReport = async (reportId) => {
  return await apiService.del(API_ENDPOINTS.report.detail(reportId));
};

export default {
  getReports,
  getReportDetails,
  generateReport,
  downloadReport,
  deleteReport
};