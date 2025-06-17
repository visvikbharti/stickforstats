// E2E tests for workflow management functionality

describe('Workflow Management', () => {
  beforeEach(() => {
    // Visit the workflows page
    cy.visit('/workflows');
    
    // Intercept API requests
    cy.intercept('GET', '/api/v1/mainapp/workflows/**').as('getWorkflows');
    
    // Log in (assuming a login form)
    // cy.get('#username').type('testuser');
    // cy.get('#password').type('testpassword');
    // cy.get('button[type="submit"]').click();
    
    // Wait for the workflows to load
    cy.wait('@getWorkflows');
  });

  it('displays the workflow list', () => {
    // Check the heading
    cy.contains('h1', 'Workflows').should('exist');
    
    // Check for the create button
    cy.contains('button', 'Create Workflow').should('exist');
    
    // Check the table headers
    cy.contains('th', 'Name').should('exist');
    cy.contains('th', 'Status').should('exist');
    cy.contains('th', 'Last Updated').should('exist');
    cy.contains('th', 'Actions').should('exist');
  });

  it('can create a new workflow', () => {
    // Intercept the create request
    cy.intercept('POST', '/api/v1/mainapp/workflows/').as('createWorkflow');
    
    // Click the create button
    cy.contains('button', 'Create Workflow').click();
    
    // Fill in the form
    cy.get('input[name="name"]').type('Test E2E Workflow');
    cy.get('textarea[name="description"]').type('This is a test workflow created by Cypress');
    
    // Submit the form
    cy.contains('button', 'Save').click();
    
    // Wait for the request to complete
    cy.wait('@createWorkflow');
    
    // Check that we're redirected to the workflow detail page
    cy.url().should('include', '/workflows/');
    cy.contains('h1', 'Test E2E Workflow').should('exist');
  });

  it('can view workflow details', () => {
    // Assuming there's at least one workflow in the list
    cy.get('table tbody tr').first().click();
    
    // Check that we're on the detail page
    cy.url().should('include', '/workflows/');
    
    // Check for detail sections
    cy.contains('h6', 'Workflow Details').should('exist');
    cy.contains('h6', 'Workflow Steps').should('exist');
  });

  it('can add a step to a workflow', () => {
    // Intercept the step creation request
    cy.intercept('POST', '/api/v1/mainapp/workflows/*/steps/').as('createStep');
    
    // Navigate to a workflow
    cy.get('table tbody tr').first().click();
    
    // Click the add step button
    cy.contains('button', 'Add Step').click();
    
    // Fill in the step form
    cy.get('input[name="name"]').type('Test Step');
    cy.get('[data-testid="step-type-select"]').click();
    cy.contains('li', 'Data Loading').click();
    
    // Configure parameters (simplified for testing)
    cy.get('[data-testid="step-parameters"]').should('exist');
    
    // Submit the form
    cy.contains('button', 'Add Step').click();
    
    // Wait for the request to complete
    cy.wait('@createStep');
    
    // Check that we're back on the workflow detail page
    cy.url().should('match', /\/workflows\/[^/]+$/);
    
    // Check that the step appears in the list
    cy.contains('Test Step').should('exist');
  });

  it('can execute a workflow', () => {
    // Intercept the execution request
    cy.intercept('POST', '/api/v1/mainapp/workflows/*/execute/').as('executeWorkflow');
    
    // Navigate to a workflow
    cy.get('table tbody tr').first().click();
    
    // Click the run button
    cy.contains('button', 'Run Workflow').click();
    
    // Wait for the request to complete
    cy.wait('@executeWorkflow');
    
    // Verify execution started
    cy.contains('Execution Progress').should('exist');
  });

  it('can filter workflows by status', () => {
    // Click the filter button
    cy.contains('button', 'Filter').click();
    
    // Select the "Completed" filter
    cy.contains('li', 'Completed').click();
    
    // Check that only completed workflows are displayed
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).find('td').eq(2).should('contain', 'Completed');
    });
    
    // Clear the filter
    cy.contains('button', 'Filter: completed').click();
    cy.contains('li', 'All statuses').click();
    
    // Check that all workflows are displayed
    cy.get('table tbody tr').should('have.length.greaterThan', 0);
  });

  it('can search for workflows', () => {
    // Type in the search box
    cy.get('input[placeholder="Search workflows"]').type('test');
    
    // Check that only matching workflows are displayed
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).find('td').eq(0).invoke('text').should('match', /test/i);
    });
    
    // Clear the search
    cy.get('input[placeholder="Search workflows"]').clear();
    
    // Check that all workflows are displayed
    cy.get('table tbody tr').should('have.length.greaterThan', 0);
  });
});