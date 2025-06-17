# Cross-Browser Testing Guide for StickForStats - RAG System

This guide provides instructions for setting up and running cross-browser tests for the RAG (Retrieval Augmented Generation) system to ensure consistent functionality across different web browsers.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Test Setup](#test-setup)
4. [Running Tests](#running-tests)
5. [Analyzing Results](#analyzing-results)
6. [Troubleshooting](#troubleshooting)
7. [Extending Tests](#extending-tests)

## Overview

Cross-browser testing is crucial for the RAG system due to its reliance on advanced web technologies, particularly WebSockets for real-time communication. The testing suite validates:

- WebSocket connection and communication
- UI rendering and responsiveness
- Form submission and validation
- Real-time updates and notifications

Tests are designed to run on the following browsers:
- Google Chrome (and Chromium-based browsers)
- Mozilla Firefox
- Microsoft Edge
- Safari (on macOS)
- Mobile browsers (through responsive testing)

## Testing Environment

### Browsers to Test
- **Chrome** (latest version)
- **Firefox** (latest version)
- **Safari** (latest version)
- **Edge** (latest version)
- **Mobile Safari** (iOS)
- **Chrome for Android**

### Screen Sizes to Test
- Desktop (1920×1080)
- Laptop (1366×768)
- Tablet (768×1024)
- Mobile (375×667)

## Prerequisites

### Required Software

1. **Node.js** (v14+) and npm (v7+)
2. **Cypress** (v12+)
3. **Web Browsers**:
   - Google Chrome
   - Mozilla Firefox
   - Microsoft Edge
   - Safari (macOS only)

### Installation

#### Install Required Browsers

**macOS**:
```bash
# Install using Homebrew
brew install --cask google-chrome firefox microsoft-edge
# Safari is pre-installed on macOS
```

**Linux**:
```bash
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

sudo apt install firefox

# Edge requires manual download from Microsoft website
```

**Windows**:
```powershell
# Using Chocolatey
choco install googlechrome firefox microsoft-edge
```

#### Install Cypress and Dependencies

```bash
# Navigate to project root
cd /path/to/StickForStats_Migration/new_project/frontend

# Install dependencies
npm install

# Install Cypress globally (optional)
npm install -g cypress
```

## Test Setup

### Configuration Files

The cross-browser testing setup uses a dedicated configuration file:

- `cypress.cross-browser.config.js`: Specific settings for cross-browser testing

### Test Files

- `cypress/e2e/cross-browser-rag-system.cy.js`: Main test file for cross-browser RAG system tests
- `cypress/fixtures/rag_system_cross_browser.json`: Test data for cross-browser tests

### Custom Commands

The tests use custom Cypress commands defined in:

- `cypress/support/rag_commands.js`: Custom commands for RAG system testing

## Running Tests

### Starting the Application

Before running tests, ensure both the backend and frontend are running:

```bash
# Terminal 1: Start backend server
cd /path/to/StickForStats_Migration/new_project
python manage.py runserver

# Terminal 2: Start frontend development server
cd /path/to/StickForStats_Migration/new_project/frontend
npm start
```

### Running Tests with the Script

The easiest way to run all cross-browser tests is using the provided script:

```bash
# Navigate to frontend directory
cd /path/to/StickForStats_Migration/new_project/frontend

# Run the cross-browser test script
./scripts/run_cross_browser_tests.sh
```

The script will:
1. Check for installed browsers
2. Run tests on each available browser
3. Generate combined test reports
4. Open the report in your default browser

### Running Tests Manually

To run tests on a specific browser manually:

```bash
# Navigate to frontend directory
cd /path/to/StickForStats_Migration/new_project/frontend

# Run tests on Chrome
npx cypress run --browser chrome --config-file cypress.cross-browser.config.js --spec "cypress/e2e/cross-browser-rag-system.cy.js"

# Run tests on Firefox
npx cypress run --browser firefox --config-file cypress.cross-browser.config.js --spec "cypress/e2e/cross-browser-rag-system.cy.js"

# Run tests on Edge
npx cypress run --browser edge --config-file cypress.cross-browser.config.js --spec "cypress/e2e/cross-browser-rag-system.cy.js"

# Run tests on Safari (macOS only)
npx cypress run --browser webkit --config-file cypress.cross-browser.config.js --spec "cypress/e2e/cross-browser-rag-system.cy.js"
```

### Running Tests in Interactive Mode

For debugging and development, you can run tests in interactive mode:

```bash
# Open Cypress Test Runner with cross-browser config
npx cypress open --config-file cypress.cross-browser.config.js
```

Then:
1. Select E2E Testing
2. Choose a browser
3. Select the `cross-browser-rag-system.cy.js` test file

## Testing Procedure

### 1. WebSocket Communication
- **Connection Establishment**: Verify connection establishment across browsers
- **Message Sending/Receiving**: Test query submission and response
- **Reconnection Handling**: Test reconnection after disconnect
- **Real-time Updates**: Verify typing indicators and live updates

### 2. UI Rendering
- **Component Layout**: Verify that all components display correctly
- **Responsive Design**: Check that the layout adapts appropriately to different screen sizes
- **Markdown and Code Rendering**: Verify that formatted responses render correctly
- **Animations and Transitions**: Check that animations run smoothly

### 3. Form Submission and Validation
- **Query Input**: Test text entry and submission
- **Document Upload**: Test knowledge base document creation
- **Form Validation**: Test input validation across browsers

### 4. Performance Testing
- **Response Time**: Measure query response time
- **UI Responsiveness**: Assess general UI responsiveness
- **Connection Stability**: Test stability during extended usage

## Analyzing Results

### Test Reports

After running tests, reports are generated in:

- `cypress/reports/cross-browser/`: Directory containing all test reports
  - `[browser]/`: Browser-specific reports
  - `combined-report.html`: Combined HTML report for all browsers

### Visual Test Results

For visual review, Cypress captures:

- **Screenshots**: Captured on test failures
- **Videos**: Recorded for each test run (can be disabled in config)

### Interpreting Results

Results are organized by test categories:

1. **WebSocket Connection Tests**: Verify connection establishment and stability
2. **UI Rendering Tests**: Check consistent UI presentation
3. **Form Submission Tests**: Validate form handling
4. **Real-time Updates Tests**: Ensure real-time features work
5. **Performance Tests**: Measure response times and performance
6. **Browser-Specific Tests**: Target unique browser behaviors

### Test Reporting Format

For each browser/device combination, record:

1. **Test Environment**
   - Browser name and version
   - Device/screen size
   - Operating system

2. **Issues Found**
   - Description of the issue
   - Steps to reproduce
   - Severity (Critical, High, Medium, Low)
   - Screenshots or screen recordings

3. **Performance Metrics**
   - Time to establish WebSocket connection
   - Query response time
   - Overall responsiveness (subjective 1-5 rating)

## Troubleshooting

### Common Issues

#### WebSocket Connection Failures

- **Chrome/Edge**: Check for network isolation issues
- **Firefox**: Verify security settings aren't blocking connections
- **Safari**: WebSocket implementation may require explicit configuration

#### UI Rendering Differences

- Check for CSS prefixes (-webkit, -moz, etc.)
- Verify SVG rendering support
- Check flexbox/grid compatibility

#### Slow Test Execution

- Increase timeouts in the configuration file
- Use `{ timeout: 10000 }` for specific assertions
- Consider running fewer tests in parallel

### Debugging Tools

- Use `cy.log()` to output debug information
- Add `.debug()` to a Cypress command chain
- Use browser developer tools with `debugger` statements

## Cross-Browser Compatibility Solutions

### Common Issues and Solutions

1. **WebSocket Compatibility**
   - Implement reconnection logic with exponential backoff
   - Support both secure (wss://) and non-secure (ws://) connections
   - Track connection state and provide clear user feedback

2. **CSS Compatibility**
   - Use autoprefixer for vendor prefixes
   - Test with multiple browsers during development
   - Consider feature detection over browser detection

3. **JavaScript Compatibility**
   - Use Babel for transpiling modern JavaScript
   - Test with polyfills for older browsers
   - Prefer standard DOM APIs over browser-specific features

4. **Performance Optimization**
   - Implement request throttling to prevent overwhelming the server
   - Use efficient message payloads to minimize data transfer
   - Implement proper error handling and user feedback

## Extending Tests

### Adding New Test Cases

1. Open `cypress/e2e/cross-browser-rag-system.cy.js`
2. Add new test cases within appropriate describe blocks
3. Follow existing patterns for WebSocket testing

### Creating Browser-Specific Tests

Use Cypress browser detection to create conditional tests:

```javascript
if (Cypress.browser.name === 'chrome') {
  // Chrome-specific test
} else if (Cypress.browser.name === 'firefox') {
  // Firefox-specific test
} else if (Cypress.browser.name === 'edge') {
  // Edge-specific test
} else if (Cypress.browser.name === 'webkit') {
  // Safari-specific test
}
```

### Testing WebSocket Features

When testing WebSocket features:

1. Always check connection status before proceeding
2. Use appropriate timeouts for asynchronous operations
3. Verify both message sending and receiving
4. Test reconnection scenarios
5. Validate UI updates when WebSocket events occur

---

## Additional Resources

- [Cypress Documentation](https://docs.cypress.io/)
- [WebSocket API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Cross-Browser Testing Best Practices](https://www.browserstack.com/guide/cross-browser-testing-best-practices)

For questions or issues, contact the development team.