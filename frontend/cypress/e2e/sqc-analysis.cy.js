/// <reference types="cypress" />

describe('SQC Analysis Module', () => {
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
        if (!response.body.some(dataset => dataset.name === 'SQC Test Data')) {
          // Upload test dataset
          const formData = new FormData();
          formData.append('name', 'SQC Test Data');
          formData.append('description', 'Dataset for SQC testing');
          
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
      
      // Navigate to SQC Analysis page
      cy.visit('/sqc-analysis');
    });
  });

  it('should display SQC Analysis interface', () => {
    cy.get('[data-testid="sqc-analysis-title"]').should('be.visible');
    cy.get('[data-testid="control-chart-button"]').should('be.visible');
    cy.get('[data-testid="process-capability-button"]').should('be.visible');
    cy.get('[data-testid="acceptance-sampling-button"]').should('be.visible');
  });

  it('should create X-bar R control chart', () => {
    // Click on Control Charts option
    cy.get('[data-testid="control-chart-button"]').click();
    
    // Select Data Upload step
    cy.get('[data-testid="data-upload-step"]').should('be.visible');
    
    // Select dataset
    cy.get('[data-testid="dataset-selector"]').click();
    cy.get('[data-testid="dataset-option"]').contains('SQC Test Data').click();
    
    // Select variable to chart
    cy.get('[data-testid="variable-selector"]').click();
    cy.get('[data-testid="variable-option"]').contains('measurement').click();
    
    // Move to configuration step
    cy.get('[data-testid="next-step-button"]').click();
    
    // Configure chart
    cy.get('[data-testid="chart-type-selector"]').select('X-bar R');
    cy.get('[data-testid="subgroup-size"]').clear().type('4');
    cy.get('[data-testid="alpha-level"]').clear().type('0.05');
    
    // Generate chart
    cy.get('[data-testid="generate-chart-button"]').click();
    
    // Verify chart is displayed
    cy.get('[data-testid="control-chart-visualization"]').should('be.visible');
    cy.get('[data-testid="xbar-chart"]').should('be.visible');
    cy.get('[data-testid="r-chart"]').should('be.visible');
    
    // Verify interpretation panel
    cy.get('[data-testid="interpretation-panel"]').should('be.visible');
    cy.get('[data-testid="chart-statistics"]').should('be.visible');
    
    // Verify recommendations
    cy.get('[data-testid="recommendations-panel"]').should('be.visible');
  });

  it('should perform process capability analysis', () => {
    // Click on Process Capability option
    cy.get('[data-testid="process-capability-button"]').click();
    
    // Select dataset
    cy.get('[data-testid="dataset-selector"]').click();
    cy.get('[data-testid="dataset-option"]').contains('SQC Test Data').click();
    
    // Select variable
    cy.get('[data-testid="variable-selector"]').click();
    cy.get('[data-testid="variable-option"]').contains('measurement').click();
    
    // Enter specification limits
    cy.get('[data-testid="lower-spec-limit"]').clear().type('9.5');
    cy.get('[data-testid="upper-spec-limit"]').clear().type('10.7');
    cy.get('[data-testid="target-value"]').clear().type('10.1');
    
    // Perform analysis
    cy.get('[data-testid="analyze-button"]').click();
    
    // Verify analysis results
    cy.get('[data-testid="capability-results"]').should('be.visible');
    cy.get('[data-testid="cp-value"]').should('be.visible');
    cy.get('[data-testid="cpk-value"]').should('be.visible');
    cy.get('[data-testid="capability-histogram"]').should('be.visible');
    
    // Verify interpretation
    cy.get('[data-testid="capability-interpretation"]').should('be.visible');
  });

  it('should create acceptance sampling plan', () => {
    // Click on Acceptance Sampling option
    cy.get('[data-testid="acceptance-sampling-button"]').click();
    
    // Enter plan parameters
    cy.get('[data-testid="lot-size"]').clear().type('1000');
    cy.get('[data-testid="aql"]').clear().type('1.5');
    cy.get('[data-testid="sampling-type"]').select('Single');
    cy.get('[data-testid="inspection-level"]').select('II');
    
    // Generate plan
    cy.get('[data-testid="generate-plan-button"]').click();
    
    // Verify plan details
    cy.get('[data-testid="sampling-plan-details"]').should('be.visible');
    cy.get('[data-testid="sample-size"]').should('be.visible');
    cy.get('[data-testid="acceptance-number"]').should('be.visible');
    cy.get('[data-testid="rejection-number"]').should('be.visible');
    
    // Verify OC curve
    cy.get('[data-testid="oc-curve"]').should('be.visible');
  });
});