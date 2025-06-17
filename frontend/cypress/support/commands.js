// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Login command to simplify authentication in tests
Cypress.Commands.add('login', (email, password) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/core/auth/login/`,
    body: {
      email,
      password,
    },
  }).then((response) => {
    // Store token in localStorage
    localStorage.setItem('auth_token', response.body.token);
    
    // Create cookie for API authentication
    cy.setCookie('auth_token', response.body.token);
    
    // Return the response for chaining
    return cy.wrap(response);
  });
});

// Custom command to upload file
Cypress.Commands.add('uploadFile', { prevSubject: 'element' }, (subject, fileName, fileType) => {
  cy.fixture(fileName, 'base64')
    .then(Cypress.Blob.base64StringToBlob)
    .then((blob) => {
      const el = subject[0];
      const testFile = new File([blob], fileName, { type: fileType });
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(testFile);
      el.files = dataTransfer.files;
      cy.wrap(subject).trigger('change', { force: true });
    });
});

// Custom command to check if element exists
Cypress.Commands.add('exists', { prevSubject: 'optional' }, (subject, selector) => {
  const getElement = selector => {
    if (subject) {
      return cy.wrap(subject).find(selector);
    }
    return cy.get(selector);
  };

  getElement(selector).then($el => {
    if ($el.length) {
      return cy.wrap($el);
    }
    return cy.wrap(null);
  });
});