/// <reference types="cypress" />

describe('Dataset Management', () => {
  beforeEach(() => {
    // Login before each test
    cy.fixture('users.json').then((users) => {
      cy.login(users.standard.email, users.standard.password);
      
      // Navigate to datasets page
      cy.visit('/datasets');
    });
  });

  it('should display dataset management interface', () => {
    cy.get('[data-testid="dataset-management-title"]').should('be.visible');
    cy.get('[data-testid="upload-dataset-button"]').should('be.visible');
    cy.get('[data-testid="dataset-list"]').should('be.visible');
  });

  it('should upload a new dataset', () => {
    // Open upload dialog
    cy.get('[data-testid="upload-dataset-button"]').click();
    cy.get('[data-testid="upload-dialog"]').should('be.visible');
    
    // Enter dataset name
    cy.get('[data-testid="dataset-name-input"]').type('Test Dataset');
    
    // Select CSV file
    cy.get('input[type="file"]').attachFile('test_data.csv');
    
    // Submit form
    cy.get('[data-testid="upload-submit-button"]').click();
    
    // Verify success message
    cy.get('[data-testid="success-alert"]').should('be.visible');
    cy.get('[data-testid="success-alert"]').should('contain', 'Dataset uploaded successfully');
    
    // Verify dataset appears in list
    cy.get('[data-testid="dataset-list"]').should('contain', 'Test Dataset');
  });

  it('should preview dataset details', () => {
    // Click on dataset in list
    cy.get('[data-testid="dataset-item"]').contains('Test Dataset').click();
    
    // Verify details are displayed
    cy.get('[data-testid="dataset-details"]').should('be.visible');
    cy.get('[data-testid="dataset-preview-table"]').should('be.visible');
    
    // Verify preview shows correct data
    cy.get('[data-testid="dataset-preview-table"]').should('contain', 'measurement');
    cy.get('[data-testid="dataset-preview-table"]').should('contain', 'temperature');
    cy.get('[data-testid="dataset-preview-table"]').should('contain', '10.2');
  });

  it('should filter datasets by name', () => {
    // Type in search field
    cy.get('[data-testid="dataset-search-input"]').type('Test');
    
    // Verify filtered results
    cy.get('[data-testid="dataset-item"]').should('have.length.at.least', 1);
    cy.get('[data-testid="dataset-item"]').first().should('contain', 'Test');
    
    // Clear search
    cy.get('[data-testid="dataset-search-input"]').clear().type('NonexistentDataset');
    
    // Verify no results
    cy.get('[data-testid="dataset-item"]').should('have.length', 0);
    cy.get('[data-testid="no-results-message"]').should('be.visible');
  });

  it('should delete a dataset', () => {
    // Find dataset and click delete button
    cy.get('[data-testid="dataset-item"]').contains('Test Dataset')
      .parents('[data-testid="dataset-item"]')
      .find('[data-testid="delete-dataset-button"]')
      .click();
    
    // Confirm deletion
    cy.get('[data-testid="confirm-delete-dialog"]').should('be.visible');
    cy.get('[data-testid="confirm-delete-button"]').click();
    
    // Verify success message
    cy.get('[data-testid="success-alert"]').should('be.visible');
    cy.get('[data-testid="success-alert"]').should('contain', 'Dataset deleted successfully');
    
    // Verify dataset no longer in list
    cy.get('[data-testid="dataset-list"]').should('not.contain', 'Test Dataset');
  });
});