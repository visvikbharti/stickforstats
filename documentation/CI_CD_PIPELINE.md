# CI/CD Pipeline Documentation

This document details the Continuous Integration and Continuous Deployment setup for the StickForStats platform.

## Overview

The CI/CD pipeline automates the testing, building, and deployment of the StickForStats platform to ensure consistent and reliable releases. The pipeline consists of the following stages:

1. Code Validation
2. Testing
3. Performance Testing
4. Build
5. Staging Deployment
6. Production Deployment

## Pipeline Architecture

The CI/CD pipeline is built using GitHub Actions, which provides seamless integration with our Git repository and supports automated workflows triggered by code changes.

### Workflow Files

The pipeline configuration is defined in the following workflow files in the `.github/workflows` directory:

- `code-validation.yml` - Runs linting and code quality checks
- `test.yml` - Runs unit and integration tests
- `websocket-performance-testing.yml` - Tests WebSocket performance and stability
- `build.yml` - Builds Docker images for all components
- `staging-deploy.yml` - Deploys to the staging environment
- `production-deploy.yml` - Deploys to the production environment

## Stage 1: Code Validation

This stage ensures that all code meets quality standards before proceeding to testing.

```yaml
# .github/workflows/code-validation.yml
name: Code Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8 black isort mypy
          pip install -r requirements.txt
          
      - name: Check formatting with black
        run: black --check .
        
      - name: Lint with flake8
        run: flake8 .
        
      - name: Check imports with isort
        run: isort --check-only --profile black .
        
      - name: Type check with mypy
        run: mypy .
        
  js-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          
      - name: Run ESLint
        run: |
          cd frontend
          npm run lint
```

## Stage 2: Testing

This stage runs all unit and integration tests to ensure functionality is working as expected.

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: ankane/pgvector:v0.5.0
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: stickforstats_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov
      
      - name: Run unit tests
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/stickforstats_test
          REDIS_URL: redis://localhost:6379/0
          DJANGO_SETTINGS_MODULE: stickforstats.settings
          SECRET_KEY: test-secret-key
          DEBUG: 'True'
        run: pytest --cov=. --cov-report=xml
      
      - name: Upload coverage report
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          
      - name: Run Jest tests
        run: |
          cd frontend
          npm test -- --coverage
      
      - name: Upload coverage report
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/lcov.info
          fail_ci_if_error: true
          
  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install backend dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Start services for E2E tests
        run: |
          docker-compose -f docker-compose.e2e.yml up -d
          
      - name: Run Cypress tests
        run: |
          cd frontend
          npm run cy:run
          
      - name: Upload Cypress screenshots if tests fail
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: cypress-screenshots
          path: frontend/cypress/screenshots
          
      - name: Stop services
        run: docker-compose -f docker-compose.e2e.yml down
```

## Stage 3: Performance Testing

This stage tests the performance and reliability of the WebSocket connections, ensuring that real-time features of the application meet performance requirements.

```yaml
# .github/workflows/websocket-performance-testing.yml
name: WebSocket Performance Testing

on:
  # Run on PRs to main and develop branches
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'stickforstats/**/*.py'
      - 'frontend/src/**/*.js'
      - 'frontend/src/**/*.jsx'
  
  # Run on push to main and develop branches
  push:
    branches: [ main, develop ]
    paths:
      - 'stickforstats/**/*.py'
      - 'frontend/src/**/*.js'
      - 'frontend/src/**/*.jsx'
  
  # Allow manual triggering
  workflow_dispatch:
    inputs:
      test_type:
        description: 'Test type to run'
        required: true
        default: 'all'
  
  # Run full suite weekly
  schedule:
    - cron: '0 2 * * 0'  # Sunday at 2 AM

jobs:
  basic-performance-test:
    name: Basic WebSocket Performance Test
    runs-on: ubuntu-latest
    # Only runs on PRs - simplified test to ensure no major regressions
    if: ${{ github.event_name == 'pull_request' }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      # Additional steps omitted for brevity...
      
      - name: Run basic WebSocket test suite
        run: |
          node performance_tests/run_websocket_tests.js --test constant --duration 30
      
      - name: Analyze performance against thresholds
        run: |
          # Check if metrics exceed thresholds
          # Fail the build if performance regressions are detected
  
  full-performance-test:
    name: Full WebSocket Performance Test Suite
    runs-on: ubuntu-latest
    # Run on scheduled events or manual triggers
    if: ${{ github.event_name == 'schedule' || github.event_name == 'workflow_dispatch' }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      # Additional steps omitted for brevity...
      
      - name: Run full WebSocket test suite
        run: |
          node performance_tests/run_websocket_tests.js --test all --duration 60
      
      - name: Generate comprehensive test report
        run: |
          node performance_tests/report_generator.js
      
      - name: Upload performance report
        uses: actions/upload-artifact@v3
        with:
          name: websocket-performance-full-report
          path: websocket_performance_report.html
```

### Performance Testing Types

The WebSocket performance testing pipeline includes several test types:

1. **Constant Connections Test**: Maintains a steady number of WebSocket connections to test stability.
2. **Ramp-up Test**: Gradually increases connection count to test scaling capabilities.
3. **Spike Test**: Simulates sudden connection surges to test how the system handles traffic spikes.
4. **Message Throughput Test**: Tests how many messages the system can process per second.

### Performance Budgets

The pipeline enforces the following performance thresholds:

- **Connection Time (P95)**: < 2000ms
- **Error Rate**: < 5%
- **Message Rate**: > 5 messages/second

If any test exceeds these thresholds, the build will fail, and a notification will be sent to the team.

### Reporting

Performance test results are:
1. Stored as artifacts in GitHub Actions
2. Generated as HTML reports for comprehensive analysis
3. Monitored for trends over time
4. Sent as notifications to the team's Slack channel

## Stage 4: Build

This stage builds Docker images for all components.

```yaml
# .github/workflows/build.yml
name: Build

on:
  push:
    branches: [ main, develop ]

jobs:
  build-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: .
          file: ./docker/Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
            ghcr.io/${{ github.repository }}/backend:latest
  
  build-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          file: ./frontend/Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
            ghcr.io/${{ github.repository }}/frontend:latest
```

## Stage 4: Staging Deployment

This stage deploys the application to the staging environment for testing.

```yaml
# .github/workflows/staging-deploy.yml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: [build-backend, build-frontend]
    environment: staging
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      
      - name: Deploy to staging server
        env:
          SERVER_HOST: ${{ secrets.STAGING_SERVER_HOST }}
          SERVER_USER: ${{ secrets.STAGING_SERVER_USER }}
        run: |
          # Prepare deployment files
          mkdir -p deploy
          cp docker-compose.prod.yml deploy/docker-compose.yml
          cp -r docker deploy/
          
          # Update container image references
          sed -i "s|build:|image: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}|g" deploy/docker-compose.yml
          sed -i "s|context: ./frontend|image: ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}|g" deploy/docker-compose.yml
          
          # Create environment file
          echo "SECRET_KEY=${{ secrets.SECRET_KEY }}" > deploy/.env.prod
          echo "DEBUG=False" >> deploy/.env.prod
          echo "ALLOWED_HOSTS=${{ secrets.STAGING_ALLOWED_HOSTS }}" >> deploy/.env.prod
          echo "CORS_ALLOWED_ORIGINS=${{ secrets.STAGING_CORS_ALLOWED_ORIGINS }}" >> deploy/.env.prod
          echo "DATABASE_URL=${{ secrets.STAGING_DATABASE_URL }}" >> deploy/.env.prod
          echo "REDIS_URL=${{ secrets.STAGING_REDIS_URL }}" >> deploy/.env.prod
          echo "CELERY_BROKER_URL=${{ secrets.STAGING_CELERY_BROKER_URL }}" >> deploy/.env.prod
          echo "CELERY_RESULT_BACKEND=${{ secrets.STAGING_CELERY_RESULT_BACKEND }}" >> deploy/.env.prod
          echo "EMAIL_HOST=${{ secrets.EMAIL_HOST }}" >> deploy/.env.prod
          echo "EMAIL_PORT=${{ secrets.EMAIL_PORT }}" >> deploy/.env.prod
          echo "EMAIL_HOST_USER=${{ secrets.EMAIL_HOST_USER }}" >> deploy/.env.prod
          echo "EMAIL_HOST_PASSWORD=${{ secrets.EMAIL_HOST_PASSWORD }}" >> deploy/.env.prod
          echo "EMAIL_USE_TLS=True" >> deploy/.env.prod
          echo "DEFAULT_FROM_EMAIL=${{ secrets.DEFAULT_FROM_EMAIL }}" >> deploy/.env.prod
          
          # Copy files to server
          scp -o StrictHostKeyChecking=no -r deploy/* $SERVER_USER@$SERVER_HOST:/home/$SERVER_USER/stickforstats
          
          # Execute deployment on server
          ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "cd /home/$SERVER_USER/stickforstats && docker-compose pull && docker-compose down && docker-compose up -d"
      
      - name: Verify deployment
        env:
          SERVER_HOST: ${{ secrets.STAGING_SERVER_HOST }}
        run: |
          # Wait for services to start
          sleep 30
          
          # Check if the API is responding
          curl -s -o /dev/null -w "%{http_code}" https://$SERVER_HOST/api/v1/health/ | grep 200
```

## Stage 5: Production Deployment

This stage deploys the application to the production environment after manual approval.

```yaml
# .github/workflows/production-deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: [build-backend, build-frontend]
    environment: production  # Requires manual approval
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.7.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
      
      - name: Deploy to production server
        env:
          SERVER_HOST: ${{ secrets.PRODUCTION_SERVER_HOST }}
          SERVER_USER: ${{ secrets.PRODUCTION_SERVER_USER }}
        run: |
          # Prepare deployment files
          mkdir -p deploy
          cp docker-compose.prod.yml deploy/docker-compose.yml
          cp -r docker deploy/
          
          # Update container image references
          sed -i "s|build:|image: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}|g" deploy/docker-compose.yml
          sed -i "s|context: ./frontend|image: ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}|g" deploy/docker-compose.yml
          
          # Create environment file
          echo "SECRET_KEY=${{ secrets.SECRET_KEY }}" > deploy/.env.prod
          echo "DEBUG=False" >> deploy/.env.prod
          echo "ALLOWED_HOSTS=${{ secrets.PRODUCTION_ALLOWED_HOSTS }}" >> deploy/.env.prod
          echo "CORS_ALLOWED_ORIGINS=${{ secrets.PRODUCTION_CORS_ALLOWED_ORIGINS }}" >> deploy/.env.prod
          echo "DATABASE_URL=${{ secrets.PRODUCTION_DATABASE_URL }}" >> deploy/.env.prod
          echo "REDIS_URL=${{ secrets.PRODUCTION_REDIS_URL }}" >> deploy/.env.prod
          echo "CELERY_BROKER_URL=${{ secrets.PRODUCTION_CELERY_BROKER_URL }}" >> deploy/.env.prod
          echo "CELERY_RESULT_BACKEND=${{ secrets.PRODUCTION_CELERY_RESULT_BACKEND }}" >> deploy/.env.prod
          echo "EMAIL_HOST=${{ secrets.EMAIL_HOST }}" >> deploy/.env.prod
          echo "EMAIL_PORT=${{ secrets.EMAIL_PORT }}" >> deploy/.env.prod
          echo "EMAIL_HOST_USER=${{ secrets.EMAIL_HOST_USER }}" >> deploy/.env.prod
          echo "EMAIL_HOST_PASSWORD=${{ secrets.EMAIL_HOST_PASSWORD }}" >> deploy/.env.prod
          echo "EMAIL_USE_TLS=True" >> deploy/.env.prod
          echo "DEFAULT_FROM_EMAIL=${{ secrets.DEFAULT_FROM_EMAIL }}" >> deploy/.env.prod
          
          # Copy files to server
          scp -o StrictHostKeyChecking=no -r deploy/* $SERVER_USER@$SERVER_HOST:/home/$SERVER_USER/stickforstats
          
          # Execute deployment on server
          ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST "cd /home/$SERVER_USER/stickforstats && docker-compose pull && docker-compose down && docker-compose up -d"
      
      - name: Verify deployment
        env:
          SERVER_HOST: ${{ secrets.PRODUCTION_SERVER_HOST }}
        run: |
          # Wait for services to start
          sleep 30
          
          # Check if the API is responding
          curl -s -o /dev/null -w "%{http_code}" https://$SERVER_HOST/api/v1/health/ | grep 200
      
      - name: Create release tag
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: v${{ github.run_number }}
          release_name: Release v${{ github.run_number }}
          body: |
            Production release v${{ github.run_number }}
            Commit: ${{ github.sha }}
          draft: false
          prerelease: false
```

## Setting Up GitHub Actions

To set up GitHub Actions:

1. Create the `.github/workflows` directory in your repository:
   ```bash
   mkdir -p .github/workflows
   ```

2. Add the workflow YAML files described above to the directory.

3. Configure the necessary secrets in your GitHub repository settings:
   - `SSH_PRIVATE_KEY` - SSH key for accessing deployment servers
   - `STAGING_SERVER_HOST` - Hostname for staging server
   - `STAGING_SERVER_USER` - Username for staging server
   - `PRODUCTION_SERVER_HOST` - Hostname for production server
   - `PRODUCTION_SERVER_USER` - Username for production server
   - Database and Redis connection strings for staging and production
   - Email configuration
   - Secret keys

## Workflow Triggers

- **Code Validation and Testing**: Triggered on all pushes to `main` and `develop` branches, and all pull requests to these branches.
- **Performance Testing**: 
  - Basic tests triggered on pull requests to ensure no regressions
  - Full test suite triggered by scheduled events (weekly) and manual triggers
  - Only runs when specific file paths are modified to avoid unnecessary testing
- **Build**: Triggered on pushes to `main` and `develop` branches.
- **Staging Deployment**: Triggered on pushes to the `develop` branch.
- **Production Deployment**: Triggered on pushes to the `main` branch, requires manual approval.

## Environment Setup

Two environments are defined in GitHub:

1. **Staging** - For testing before production deployment
2. **Production** - For live application

The production environment is configured to require manual approval before deployment.

## Rollback Procedure

In case a deployment needs to be rolled back:

1. Identify the last stable release tag
2. Manually trigger the production deployment workflow using the stable release commit
3. Or, use the rollback script on the server:

```bash
# Connect to the production server
ssh $SERVER_USER@$SERVER_HOST

# Navigate to the application directory
cd /home/$SERVER_USER/stickforstats

# List available images
docker image ls

# Roll back to a specific version
docker-compose down
# Edit docker-compose.yml to use previous image tags
nano docker-compose.yml
docker-compose up -d
```

## Monitoring Deployments

GitHub Actions provides a dashboard to monitor all workflow runs. Additionally, deployment status can be monitored through:

1. GitHub commit status checks
2. Slack notifications (can be set up by adding a notification step to workflows)
3. GitHub releases page for production deployments
4. Server logs and health endpoints

## Deployment Artifacts

The following artifacts are created during the CI/CD process:

1. Docker images in GitHub Container Registry (ghcr.io)
2. Release tags for production deployments
3. Test coverage reports
4. Cypress screenshots (on test failures)

## Security Considerations

1. All secrets are stored in GitHub Secrets and not exposed in logs
2. SSH keys have limited permissions on deployment servers
3. Docker images are scanned for vulnerabilities before deployment
4. Production deployments require manual approval

## Conclusion

This CI/CD pipeline provides an automated, secure, and reliable way to test, build, and deploy the StickForStats platform. By following this workflow, we ensure consistent quality and reduce the risk of deployment issues.