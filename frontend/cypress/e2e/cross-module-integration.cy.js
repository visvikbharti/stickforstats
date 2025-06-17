/// <reference types="cypress" />

describe('Cross-Module Integration', () => {
  beforeEach(() => {
    // Login before each test
    cy.fixture('users.json').then((users) => {
      cy.login(users.standard.email, users.standard.password);
      
      // Upload test dataset if it doesn't exist
      cy.request({
        method: 'GET',
        url: `${Cypress.env('apiUrl')}/core/datasets/`,
        headers: {
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`
        }
      }).then((response) => {
        if (!response.body.some(dataset => dataset.name === 'Integration Test Data')) {
          // Upload test dataset
          const formData = new FormData();
          formData.append('name', 'Integration Test Data');
          formData.append('description', 'Dataset for cross-module integration testing');
          
          cy.fixture('test_data.csv', 'binary')
            .then(binary => Cypress.Blob.binaryStringToBlob(binary))
            .then(blob => {
              formData.append('file', blob, 'test_data.csv');
              
              cy.request({
                method: 'POST',
                url: `${Cypress.env('apiUrl')}/core/datasets/`,
                headers: {
                  Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
                  'Content-Type': 'multipart/form-data'
                },
                body: formData
              });
            });
        }
      });
    });
  });

  it('should create and execute workflow across modules', () => {
    // Navigate to workflow management page
    cy.visit('/workflows');
    
    // Create new workflow
    cy.get('[data-testid="create-workflow-button"]').click();
    
    // Enter workflow details
    cy.get('[data-testid="workflow-name-input"]').type('Cross-Module Test Workflow');
    cy.get('[data-testid="workflow-description-input"]').type('Testing integration between SQC and Probability Distributions');
    
    // Add first step - SQC Analysis
    cy.get('[data-testid="add-step-button"]').click();
    cy.get('[data-testid="step-type-selector"]').select('SQC Analysis');
    cy.get('[data-testid="step-name-input"]').type('Process Capability Analysis');
    cy.get('[data-testid="step-config-dataset-selector"]').click();
    cy.get('[data-testid="dataset-option"]').contains('Integration Test Data').click();
    cy.get('[data-testid="step-config-variable-selector"]').select('measurement');
    cy.get('[data-testid="step-config-lower-spec"]').type('9.5');
    cy.get('[data-testid="step-config-upper-spec"]').type('10.7');
    cy.get('[data-testid="save-step-button"]').click();
    
    // Add second step - Probability Distribution
    cy.get('[data-testid="add-step-button"]').click();
    cy.get('[data-testid="step-type-selector"]').select('Probability Distribution');
    cy.get('[data-testid="step-name-input"]').type('Distribution Fitting');
    cy.get('[data-testid="step-config-source-selector"]').select('Previous Step Output');
    cy.get('[data-testid="step-config-distribution-selector"]').select('Auto-detect');
    cy.get('[data-testid="save-step-button"]').click();
    
    // Save workflow
    cy.get('[data-testid="save-workflow-button"]').click();
    
    // Verify success message
    cy.get('[data-testid="success-alert"]').should('be.visible');
    cy.get('[data-testid="success-alert"]').should('contain', 'Workflow created successfully');
    
    // Execute workflow
    cy.contains('Cross-Module Test Workflow')
      .parents('[data-testid="workflow-item"]')
      .find('[data-testid="execute-workflow-button"]')
      .click();
    
    // Verify execution status
    cy.get('[data-testid="workflow-execution-status"]').should('be.visible');
    
    // Wait for execution to complete (with timeout)
    cy.get('[data-testid="workflow-execution-status"]', { timeout: 30000 })
      .should('contain', 'Completed');
    
    // Verify results
    cy.get('[data-testid="workflow-results-button"]').click();
    
    // Verify step 1 results
    cy.get('[data-testid="step-result-1"]').should('be.visible');
    cy.get('[data-testid="capability-indices"]').should('be.visible');
    
    // Verify step 2 results
    cy.get('[data-testid="step-result-2"]').should('be.visible');
    cy.get('[data-testid="fitted-distribution"]').should('be.visible');
    cy.get('[data-testid="distribution-parameters"]').should('be.visible');
  });

  it('should create report combining multiple module analyses', () => {
    // Navigate to dashboard
    cy.visit('/dashboard');
    
    // Start new report
    cy.get('[data-testid="create-report-button"]').click();
    
    // Enter report details
    cy.get('[data-testid="report-name-input"]').type('Cross-Module Integration Report');
    cy.get('[data-testid="report-description-input"]').type('Report combining analyses from multiple modules');
    
    // Add SQC analysis section
    cy.get('[data-testid="add-section-button"]').click();
    cy.get('[data-testid="section-type-selector"]').select('SQC Analysis');
    cy.get('[data-testid="section-title-input"]').type('Process Control Analysis');
    cy.get('[data-testid="section-dataset-selector"]').click();
    cy.get('[data-testid="dataset-option"]').contains('Integration Test Data').click();
    cy.get('[data-testid="sqc-analysis-type-selector"]').select('Control Chart');
    cy.get('[data-testid="variable-selector"]').select('measurement');
    cy.get('[data-testid="chart-type-selector"]').select('X-bar R');
    cy.get('[data-testid="generate-analysis-button"]').click();
    cy.get('[data-testid="add-to-report-button"]').click();
    
    // Add Probability Distribution section
    cy.get('[data-testid="add-section-button"]').click();
    cy.get('[data-testid="section-type-selector"]').select('Probability Distribution');
    cy.get('[data-testid="section-title-input"]').type('Distribution Analysis');
    cy.get('[data-testid="section-dataset-selector"]').click();
    cy.get('[data-testid="dataset-option"]').contains('Integration Test Data').click();
    cy.get('[data-testid="distribution-variable-selector"]').select('measurement');
    cy.get('[data-testid="generate-analysis-button"]').click();
    cy.get('[data-testid="add-to-report-button"]').click();
    
    // Generate report
    cy.get('[data-testid="generate-report-button"]').click();
    
    // Verify report generation
    cy.get('[data-testid="report-preview"]', { timeout: 30000 }).should('be.visible');
    
    // Verify report sections
    cy.get('[data-testid="report-section-1"]').should('contain', 'Process Control Analysis');
    cy.get('[data-testid="report-section-2"]').should('contain', 'Distribution Analysis');
    
    // Verify charts and visuals
    cy.get('[data-testid="control-chart-visual"]').should('be.visible');
    cy.get('[data-testid="distribution-plot-visual"]').should('be.visible');
    
    // Save report
    cy.get('[data-testid="save-report-button"]').click();
    
    // Verify success message
    cy.get('[data-testid="success-alert"]').should('be.visible');
    cy.get('[data-testid="success-alert"]').should('contain', 'Report saved successfully');
  });

  it('should use RAG system to get recommendations across modules', () => {
    // Navigate to dataset details
    cy.visit('/datasets');
    cy.contains('Integration Test Data').click();
    
    // Open RAG assistance
    cy.get('[data-testid="rag-assistance-button"]').click();
    
    // Ask for cross-module analysis recommendation
    cy.get('[data-testid="rag-query-input"]')
      .type('What statistical analyses should I perform on this dataset?');
    cy.get('[data-testid="submit-query-button"]').click();
    
    // Verify response contains recommendations for multiple modules
    cy.get('[data-testid="rag-response"]', { timeout: 15000 }).should('be.visible');
    cy.get('[data-testid="rag-response"]').should('contain', 'process capability');
    cy.get('[data-testid="rag-response"]').should('contain', 'distribution analysis');
    
    // Verify source references
    cy.get('[data-testid="rag-sources"]').should('be.visible');
    cy.get('[data-testid="source-item"]').should('have.length.at.least', 2);
    
    // Follow a recommendation link
    cy.get('[data-testid="recommendation-link"]').first().click();
    
    // Verify navigation to recommended module
    cy.url().should('include', '/sqc-analysis');
  });
});