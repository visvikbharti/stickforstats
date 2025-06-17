// API Base URLs
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1';
export const WS_BASE_URL = process.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8000/ws';

// Module paths
export const MODULE_PATHS = {
  DASHBOARD: '/dashboard',
  PCA: '/pca',
  SQC: '/sqc',
  DOE: '/doe',
  CONFIDENCE_INTERVAL: '/confidence-interval',
  PROBABILITY_DISTRIBUTIONS: '/probability-distributions'
};

// Color themes for visualizations
export const VISUALIZATION_COLOR_THEMES = {
  CATEGORY10: 'Category10',
  SET2: 'Set2',
  PAIRED: 'Paired',
  VIRIDIS: 'Viridis',
  PLASMA: 'Plasma'
};

// Default PCA settings
export const DEFAULT_PCA_SETTINGS = {
  n_components: 5,
  scaling_method: 'STANDARD',
  plot_type: '2D',
  marker_size: 60,
  show_labels: true,
  include_gene_loadings: true,
  top_genes_count: 10,
  ellipse_transparency: 0.2,
  color_palette: VISUALIZATION_COLOR_THEMES.CATEGORY10
};

// File formats for data upload
export const SUPPORTED_FILE_FORMATS = {
  CSV: '.csv',
  TSV: '.tsv',
  TXT: '.txt',
  EXCEL: ['.xlsx', '.xls']
};

// Export formats for PCA results
export const EXPORT_FORMATS = {
  PDF: 'pdf',
  PNG: 'png',
  JPG: 'jpg',
  CSV: 'csv'
};