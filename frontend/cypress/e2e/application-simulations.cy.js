/// <reference types="cypress" />

describe('Probability Distributions - Application Simulations', () => {
  beforeEach(() => {
    // Login before each test
    cy.fixture('users.json').then((users) => {
      cy.login(users.standard.email, users.standard.password);
      
      // Navigate to Probability Distributions page
      cy.visit('/probability-distributions');
      
      // Navigate to Application Simulations tab
      cy.get('[data-testid="application-simulations-tab"]').click();
    });
  });

  describe('Email Arrivals (Poisson) Simulation', () => {
    beforeEach(() => {
      // Select Email Arrivals simulation
      cy.contains('Email Arrivals (Poisson)').click();
    });

    it('should display Email Arrivals simulation with D3.js visualizations', () => {
      // Verify main components are visible
      cy.contains('Email Arrivals (Poisson)').should('be.visible');
      cy.get('[data-testid="email-arrivals-parameters"]').should('be.visible');
      cy.get('[data-testid="email-arrivals-chart"]').should('be.visible');
      cy.get('[data-testid="arrival-rate-slider"]').should('be.visible');
    });

    it('should update visualization when parameters change', () => {
      // Change arrival rate
      cy.get('[data-testid="arrival-rate-slider"]').invoke('val', 20).trigger('change');
      
      // Run simulation
      cy.get('[data-testid="run-simulation-button"]').click();
      
      // Verify visualization updates
      cy.get('[data-testid="email-arrivals-chart"]').should('be.visible');
      cy.get('[data-testid="arrivals-count"]').should('contain.text');
      
      // Verify metrics are calculated
      cy.get('[data-testid="simulation-metrics"]').should('be.visible');
      cy.get('[data-testid="simulation-metrics"]').should('contain', 'Average');
    });

    it('should display educational content with KaTeX formulas', () => {
      // Open educational content
      cy.get('[data-testid="show-educational-content"]').click();
      
      // Verify KaTeX formulas are rendered
      cy.get('.katex').should('exist');
      cy.contains('Poisson Distribution').should('be.visible');
      
      // Verify educational content sections
      cy.contains('Poisson Process').should('be.visible');
      cy.contains('Exponential Distribution').should('be.visible');
    });
  });

  describe('Quality Control (Normal) Simulation', () => {
    beforeEach(() => {
      // Select Quality Control simulation
      cy.contains('Quality Control (Normal)').click();
    });

    it('should display Quality Control simulation with D3.js visualizations', () => {
      // Verify main components are visible
      cy.contains('Quality Control (Normal)').should('be.visible');
      cy.get('[data-testid="quality-control-parameters"]').should('be.visible');
      cy.get('[data-testid="control-chart"]').should('be.visible');
      cy.get('[data-testid="process-mean-slider"]').should('be.visible');
      cy.get('[data-testid="process-std-slider"]').should('be.visible');
    });

    it('should update visualization when parameters change', () => {
      // Change process parameters
      cy.get('[data-testid="process-mean-slider"]').invoke('val', 55).trigger('change');
      cy.get('[data-testid="process-std-slider"]').invoke('val', 2.5).trigger('change');
      
      // Run simulation
      cy.get('[data-testid="run-simulation-button"]').click();
      
      // Verify visualization updates
      cy.get('[data-testid="control-chart"]').should('be.visible');
      
      // Verify process capability indices are calculated
      cy.get('[data-testid="process-capability"]').should('be.visible');
      cy.get('[data-testid="process-capability"]').should('contain', 'Cp');
      cy.get('[data-testid="process-capability"]').should('contain', 'Cpk');
    });

    it('should display specification limits and control limits', () => {
      // Set specification limits
      cy.get('[data-testid="lower-spec-limit-input"]').clear().type('45');
      cy.get('[data-testid="upper-spec-limit-input"]').clear().type('65');
      
      // Run simulation
      cy.get('[data-testid="run-simulation-button"]').click();
      
      // Verify limits are displayed on chart
      cy.get('[data-testid="control-chart"]').should('be.visible');
      cy.get('[data-testid="specification-limits"]').should('be.visible');
      cy.get('[data-testid="control-limits"]').should('be.visible');
    });
  });

  describe('Clinical Trial (Binomial/Normal) Simulation', () => {
    beforeEach(() => {
      // Select Clinical Trial simulation
      cy.contains('Clinical Trials (Binomial/Normal)').click();
    });

    it('should display Clinical Trial simulation with D3.js visualizations', () => {
      // Verify main components are visible
      cy.contains('Clinical Trials').should('be.visible');
      cy.get('[data-testid="clinical-trial-parameters"]').should('be.visible');
      cy.get('[data-testid="clinical-trial-chart"]').should('be.visible');
      cy.get('[data-testid="sample-size-slider"]').should('be.visible');
      cy.get('[data-testid="effect-size-slider"]').should('be.visible');
    });

    it('should update visualization when parameters change', () => {
      // Change trial parameters
      cy.get('[data-testid="sample-size-slider"]').invoke('val', 100).trigger('change');
      cy.get('[data-testid="effect-size-slider"]').invoke('val', 0.2).trigger('change');
      
      // Run simulation
      cy.get('[data-testid="run-simulation-button"]').click();
      
      // Verify visualization updates
      cy.get('[data-testid="clinical-trial-chart"]').should('be.visible');
      
      // Verify p-value is calculated
      cy.get('[data-testid="p-value-display"]').should('be.visible');
    });

    it('should display power analysis results', () => {
      // Enable power analysis
      cy.get('[data-testid="show-power-analysis"]').click();
      
      // Run power analysis
      cy.get('[data-testid="run-power-analysis"]').click();
      
      // Verify power analysis results
      cy.get('[data-testid="power-analysis-results"]').should('be.visible');
      cy.get('[data-testid="power-curve"]').should('be.visible');
    });
  });

  describe('Network Traffic (Poisson) Simulation', () => {
    beforeEach(() => {
      // Select Network Traffic simulation
      cy.contains('Network Traffic (Poisson)').click();
    });

    it('should display Network Traffic simulation with D3.js visualizations', () => {
      // Verify main components are visible
      cy.contains('Network Traffic').should('be.visible');
      cy.get('[data-testid="network-traffic-parameters"]').should('be.visible');
      cy.get('[data-testid="queue-chart"]').should('be.visible');
      cy.get('[data-testid="arrival-rate-slider"]').should('be.visible');
      cy.get('[data-testid="service-rate-slider"]').should('be.visible');
    });

    it('should update visualization when parameters change', () => {
      // Change queueing parameters
      cy.get('[data-testid="arrival-rate-slider"]').invoke('val', 8).trigger('change');
      cy.get('[data-testid="service-rate-slider"]').invoke('val', 10).trigger('change');
      
      // Run simulation
      cy.get('[data-testid="run-simulation-button"]').click();
      
      // Verify visualization updates
      cy.get('[data-testid="queue-chart"]').should('be.visible');
      
      // Verify queueing metrics are calculated
      cy.get('[data-testid="utilization-metric"]').should('be.visible');
      cy.get('[data-testid="avg-queue-size-metric"]').should('be.visible');
    });

    it('should display queue distribution visualization', () => {
      // Run simulation
      cy.get('[data-testid="run-simulation-button"]').click();
      
      // Switch to distribution view
      cy.get('[data-testid="show-queue-distribution"]').click();
      
      // Verify distribution chart
      cy.get('[data-testid="queue-distribution-chart"]').should('be.visible');
    });
  });

  describe('Manufacturing Defects (Binomial/Poisson) Simulation', () => {
    beforeEach(() => {
      // Select Manufacturing Defects simulation
      cy.contains('Manufacturing Defects (Binomial/Poisson)').click();
    });

    it('should display Manufacturing Defects simulation with D3.js visualizations', () => {
      // Verify main components are visible
      cy.contains('Manufacturing Defects').should('be.visible');
      cy.get('[data-testid="manufacturing-defects-parameters"]').should('be.visible');
      cy.get('[data-testid="defects-chart"]').should('be.visible');
      cy.get('[data-testid="defect-rate-slider"]').should('be.visible');
      cy.get('[data-testid="sample-size-slider"]').should('be.visible');
    });

    it('should update visualization when parameters change', () => {
      // Change parameters
      cy.get('[data-testid="defect-rate-slider"]').invoke('val', 0.05).trigger('change');
      cy.get('[data-testid="sample-size-slider"]').invoke('val', 100).trigger('change');
      
      // Run simulation
      cy.get('[data-testid="run-simulation-button"]').click();
      
      // Verify visualization updates
      cy.get('[data-testid="defects-chart"]').should('be.visible');
      
      // Verify metrics are calculated
      cy.get('[data-testid="defect-metrics"]').should('be.visible');
    });

    it('should display operating characteristic curve', () => {
      // Show OC curve
      cy.get('[data-testid="show-oc-curve"]').click();
      
      // Set acceptance number
      cy.get('[data-testid="acceptance-number-input"]').clear().type('2');
      
      // Generate OC curve
      cy.get('[data-testid="generate-oc-curve"]').click();
      
      // Verify OC curve is displayed
      cy.get('[data-testid="oc-curve-chart"]').should('be.visible');
      
      // Verify producer's and consumer's risk
      cy.get('[data-testid="producer-risk"]').should('be.visible');
      cy.get('[data-testid="consumer-risk"]').should('be.visible');
    });
  });

  describe('Navigation between simulations', () => {
    it('should navigate between simulation types and maintain state', () => {
      // Start with Email Arrivals
      cy.contains('Email Arrivals (Poisson)').click();
      
      // Change a parameter
      cy.get('[data-testid="arrival-rate-slider"]').invoke('val', 25).trigger('change');
      
      // Run simulation
      cy.get('[data-testid="run-simulation-button"]').click();
      
      // Navigate back to selection
      cy.contains('← Back to Applications').click();
      
      // Select another simulation
      cy.contains('Quality Control (Normal)').click();
      
      // Verify new simulation loads
      cy.contains('Quality Control').should('be.visible');
      
      // Navigate back again
      cy.contains('← Back to Applications').click();
      
      // Return to first simulation
      cy.contains('Email Arrivals (Poisson)').click();
      
      // Verify parameter was maintained
      cy.get('[data-testid="arrival-rate-slider"]').should('have.value', '25');
    });
  });
});