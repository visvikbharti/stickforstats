// E2E tests for report generation functionality

describe('Report Management', () => {
  beforeEach(() => {
    // Visit the reports page
    cy.visit('/reports');
    
    // Intercept API requests
    cy.intercept('GET', '/api/v1/mainapp/reports/**').as('getReports');
    
    // Log in (assuming a login form)
    // cy.get('#username').type('testuser');
    // cy.get('#password').type('testpassword');
    // cy.get('button[type="submit"]').click();
    
    // Wait for the reports to load
    cy.wait('@getReports');
  });

  it('displays the report list', () => {
    // Check the heading
    cy.contains('h1', 'Reports').should('exist');
    
    // Check for the create button
    cy.contains('button', 'Create Report').should('exist');
    
    // Check the table headers
    cy.contains('th', 'Title').should('exist');
    cy.contains('th', 'Format').should('exist');
    cy.contains('th', 'Created').should('exist');
    cy.contains('th', 'Analyses').should('exist');
    cy.contains('th', 'Size').should('exist');
    cy.contains('th', 'Actions').should('exist');
  });

  it('can generate a new report', () => {
    // Intercept the report generation request
    cy.intercept('POST', '/api/v1/mainapp/reports/generate/').as('generateReport');
    
    // Click the create button
    cy.contains('button', 'Create Report').click();
    
    // Fill in the report information
    cy.get('input[name="title"]').type('Test E2E Report');
    cy.get('textarea[name="description"]').type('This is a test report created by Cypress');
    
    // Go to the next step
    cy.contains('button', 'Next').click();
    
    // Select some analyses (assuming there are some available)
    cy.get('input[type="checkbox"]').first().check();
    cy.get('input[type="checkbox"]').eq(1).check();
    
    // Go to the next step
    cy.contains('button', 'Next').click();
    
    // Configure options
    cy.get('input[name="includeVisualizations"]').should('be.checked');
    
    // Generate the report
    cy.contains('button', 'Generate Report').click();
    
    // Wait for the report to be generated
    cy.wait('@generateReport');
    
    // Check that the report was generated successfully
    cy.contains('Report Generated Successfully').should('exist');
  });

  it('can view report details', () => {
    // Assuming there's at least one report in the list
    cy.get('table tbody tr').first().find('td').first().click();
    
    // Check that we're on the detail page
    cy.url().should('include', '/reports/');
    
    // Check for report sections
    cy.contains('Report Contents').should('exist');
    cy.contains('button', 'Download').should('exist');
  });

  it('can download a report', () => {
    // Intercept the download request
    cy.intercept('GET', '/api/v1/mainapp/reports/*/download/').as('downloadReport');
    
    // Find the first report and click download
    cy.get('table tbody tr').first().find('button[aria-label="Download"]').click();
    
    // Wait for the download request
    cy.wait('@downloadReport');
    
    // We can't verify the actual download in Cypress, but we can check that the request was made
  });

  it('can filter reports by format', () => {
    // Click on a format chip
    cy.contains('.MuiChip-root', 'PDF').click();
    
    // Check that only PDF reports are displayed
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).find('td').eq(1).should('contain', 'PDF');
    });
    
    // Click the chip again to clear the filter
    cy.contains('.MuiChip-root', 'PDF').click();
    
    // Check that all reports are displayed
    cy.get('table tbody tr').should('have.length.greaterThan', 0);
  });

  it('can search for reports', () => {
    // Type in the search box
    cy.get('input[placeholder="Search reports..."]').type('test');
    
    // Check that only matching reports are displayed
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).find('td').eq(0).invoke('text').should('match', /test/i);
    });
    
    // Clear the search
    cy.get('input[placeholder="Search reports..."]').clear();
    
    // Check that all reports are displayed
    cy.get('table tbody tr').should('have.length.greaterThan', 0);
  });

  it('displays report viewer tabs correctly', () => {
    // Navigate to a report detail
    cy.get('table tbody tr').first().find('td').first().click();
    
    // Check that the tabs exist
    cy.contains('button', 'Analyses').should('exist');
    cy.contains('button', 'Visualizations').should('exist');
    cy.contains('button', 'Data Tables').should('exist');
    cy.contains('button', 'Full Report').should('exist');
    
    // Click on the Visualizations tab
    cy.contains('button', 'Visualizations').click();
    
    // Check that the visualizations panel is displayed
    cy.get('[role="tabpanel"][id="tabpanel-1"]').should('be.visible');
    
    // Click on the Data Tables tab
    cy.contains('button', 'Data Tables').click();
    
    // Check that the data tables panel is displayed
    cy.get('[role="tabpanel"][id="tabpanel-2"]').should('be.visible');
  });
});