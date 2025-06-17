/// <reference types="cypress" />

describe('Probability Distributions Module', () => {
  beforeEach(() => {
    // Login before each test
    cy.fixture('users.json').then((users) => {
      cy.login(users.standard.email, users.standard.password);
      
      // Navigate to Probability Distributions page
      cy.visit('/probability-distributions');
    });
  });

  it('should display Probability Distributions interface', () => {
    cy.get('[data-testid="probability-distributions-title"]').should('be.visible');
    cy.get('[data-testid="distribution-selector"]').should('be.visible');
    cy.get('[data-testid="parameter-controls"]').should('be.visible');
    cy.get('[data-testid="distribution-plot"]').should('be.visible');
  });

  it('should select and configure Normal distribution', () => {
    // Select Normal distribution
    cy.get('[data-testid="distribution-selector"]').click();
    cy.get('[data-testid="distribution-option"]').contains('Normal').click();
    
    // Verify parameters update
    cy.get('[data-testid="parameter-controls"]').should('contain', 'Mean');
    cy.get('[data-testid="parameter-controls"]').should('contain', 'Standard Deviation');
    
    // Set parameters
    cy.get('[data-testid="mean-input"]').clear().type('10');
    cy.get('[data-testid="std-dev-input"]').clear().type('2');
    
    // Verify plot updates
    cy.get('[data-testid="distribution-plot"]').should('be.visible');
    cy.get('[data-testid="plot-title"]').should('contain', 'Normal');
  });

  it('should calculate probability for Normal distribution', () => {
    // Select Normal distribution
    cy.get('[data-testid="distribution-selector"]').click();
    cy.get('[data-testid="distribution-option"]').contains('Normal').click();
    
    // Set parameters
    cy.get('[data-testid="mean-input"]').clear().type('10');
    cy.get('[data-testid="std-dev-input"]').clear().type('2');
    
    // Go to probability calculator tab
    cy.get('[data-testid="probability-calculator-tab"]').click();
    
    // Calculate probability for X < 12
    cy.get('[data-testid="calculate-less-than"]').click();
    cy.get('[data-testid="x-value-input"]').clear().type('12');
    cy.get('[data-testid="calculate-button"]').click();
    
    // Verify result
    cy.get('[data-testid="probability-result"]').should('be.visible');
    cy.get('[data-testid="probability-value"]').should('contain', '0.84');
    
    // Verify visualization
    cy.get('[data-testid="probability-visualization"]').should('be.visible');
  });

  it('should generate random samples from distribution', () => {
    // Select Normal distribution
    cy.get('[data-testid="distribution-selector"]').click();
    cy.get('[data-testid="distribution-option"]').contains('Normal').click();
    
    // Set parameters
    cy.get('[data-testid="mean-input"]').clear().type('10');
    cy.get('[data-testid="std-dev-input"]').clear().type('2');
    
    // Go to random samples tab
    cy.get('[data-testid="random-samples-tab"]').click();
    
    // Set sample size
    cy.get('[data-testid="sample-size-input"]').clear().type('100');
    
    // Generate samples
    cy.get('[data-testid="generate-samples-button"]').click();
    
    // Verify samples table
    cy.get('[data-testid="samples-table"]').should('be.visible');
    cy.get('[data-testid="samples-table"]').find('tr').should('have.length.above', 5);
    
    // Verify histogram
    cy.get('[data-testid="samples-histogram"]').should('be.visible');
  });

  it('should compare two distributions', () => {
    // Go to distribution comparison tab
    cy.get('[data-testid="distribution-comparison-tab"]').click();
    
    // Select first distribution
    cy.get('[data-testid="first-distribution-selector"]').click();
    cy.get('[data-testid="distribution-option"]').contains('Normal').click();
    
    // Set parameters for first distribution
    cy.get('[data-testid="first-mean-input"]').clear().type('10');
    cy.get('[data-testid="first-std-dev-input"]').clear().type('2');
    
    // Select second distribution
    cy.get('[data-testid="second-distribution-selector"]').click();
    cy.get('[data-testid="distribution-option"]').contains('Normal').click();
    
    // Set parameters for second distribution
    cy.get('[data-testid="second-mean-input"]').clear().type('12');
    cy.get('[data-testid="second-std-dev-input"]').clear().type('1.5');
    
    // Compare distributions
    cy.get('[data-testid="compare-button"]').click();
    
    // Verify comparison plot
    cy.get('[data-testid="comparison-plot"]').should('be.visible');
    
    // Verify statistics table
    cy.get('[data-testid="comparison-stats"]').should('be.visible');
    cy.get('[data-testid="comparison-stats"]').should('contain', 'Mean');
    cy.get('[data-testid="comparison-stats"]').should('contain', 'Standard Deviation');
  });

  it('should access educational content', () => {
    // Go to educational content tab
    cy.get('[data-testid="educational-content-tab"]').click();
    
    // Verify educational content sections
    cy.get('[data-testid="educational-content"]').should('be.visible');
    cy.get('[data-testid="distribution-theory"]').should('be.visible');
    
    // Select a specific topic
    cy.get('[data-testid="topic-selector"]').click();
    cy.get('[data-testid="topic-option"]').contains('Central Limit Theorem').click();
    
    // Verify content updates
    cy.get('[data-testid="topic-content"]').should('contain', 'Central Limit Theorem');
    
    // Verify interactive elements
    cy.get('[data-testid="interactive-demo"]').should('be.visible');
  });
});