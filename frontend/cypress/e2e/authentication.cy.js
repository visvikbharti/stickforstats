/// <reference types="cypress" />

describe('Authentication', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should display login form', () => {
    cy.get('[data-testid="login-form"]').should('be.visible');
    cy.get('[data-testid="email-input"]').should('be.visible');
    cy.get('[data-testid="password-input"]').should('be.visible');
    cy.get('[data-testid="login-button"]').should('be.visible');
  });

  it('should login with valid credentials', () => {
    cy.fixture('users.json').then((users) => {
      cy.get('[data-testid="email-input"]').type(users.standard.email);
      cy.get('[data-testid="password-input"]').type(users.standard.password);
      cy.get('[data-testid="login-button"]').click();

      // Verify successful login - user should be redirected to dashboard
      cy.url().should('include', '/dashboard');
      cy.get('[data-testid="user-menu"]').should('be.visible');
      cy.get('[data-testid="dashboard-greeting"]').should('contain', 'Welcome');
    });
  });

  it('should show error with invalid credentials', () => {
    cy.get('[data-testid="email-input"]').type('wrong@example.com');
    cy.get('[data-testid="password-input"]').type('wrongpassword');
    cy.get('[data-testid="login-button"]').click();

    // Verify error message is displayed
    cy.get('[data-testid="login-error"]').should('be.visible');
    cy.get('[data-testid="login-error"]').should('contain', 'Invalid credentials');
    
    // User should still be on login page
    cy.url().should('not.include', '/dashboard');
  });

  it('should logout successfully', () => {
    // Login first
    cy.fixture('users.json').then((users) => {
      cy.get('[data-testid="email-input"]').type(users.standard.email);
      cy.get('[data-testid="password-input"]').type(users.standard.password);
      cy.get('[data-testid="login-button"]').click();

      // Verify successful login
      cy.url().should('include', '/dashboard');
      
      // Logout
      cy.get('[data-testid="user-menu"]').click();
      cy.get('[data-testid="logout-button"]').click();
      
      // Verify successful logout - user should be redirected to login page
      cy.url().should('not.include', '/dashboard');
      cy.get('[data-testid="login-form"]').should('be.visible');
    });
  });
});