# StickForStats Debugging Guide

This document provides guidance for debugging common issues in the StickForStats Django/React application after migration from Streamlit.

## Backend Debugging

### Django Server Issues

#### Server Won't Start
```
Problem: Django server fails to start
```

**Debugging Steps:**
1. Check for syntax errors in Python files
   ```bash
   python -m compileall .
   ```
2. Verify database connection settings in settings.py
3. Check for migration issues
   ```bash
   python manage.py showmigrations
   ```
4. Look for import errors in Django initialization
   ```bash
   python -m django check
   ```

#### Migration Errors
```
Problem: Database migration errors
```

**Debugging Steps:**
1. Check migration files for errors
2. Try resetting conflicting migrations
   ```bash
   python manage.py migrate app_name zero
   python manage.py migrate app_name
   ```
3. Verify model field types against database schema
4. Check for missing dependencies between migrations

### API Endpoint Issues

#### 404 Not Found
```
Problem: API endpoint returns 404
```

**Debugging Steps:**
1. Verify URL patterns in urls.py
2. Check app is included in INSTALLED_APPS
3. Verify ViewSet/View is registered correctly
4. Check URL namespace and app_name settings
5. Use Django Debug Toolbar to trace URL resolution

#### 500 Server Error
```
Problem: API endpoint returns 500
```

**Debugging Steps:**
1. Check Django error logs
2. Add try/except with detailed logging in views
3. Verify serializer field validation
4. Check database constraints and integrity
5. Look for race conditions in concurrent requests

### Statistical Calculation Issues

#### Results Differ from Original Implementation
```
Problem: Statistical results don't match original Streamlit version
```

**Debugging Steps:**
1. Use identical input data for both implementations
2. Add debugging logs to show intermediate calculation steps
3. Check for differences in library versions
4. Verify handling of edge cases (NaNs, nulls, etc.)
5. Look for precision issues in floating-point operations

#### Performance Issues
```
Problem: Statistical calculations are slow
```

**Debugging Steps:**
1. Use Django Debug Toolbar to identify slow queries
2. Check for N+1 query patterns
3. Add appropriate database indexes
4. Consider using the @cached_property decorator for repeated calculations
5. Profile code with cProfile to identify bottlenecks
   ```python
   import cProfile
   profiler = cProfile.Profile()
   profiler.enable()
   # code to profile
   profiler.disable()
   profiler.print_stats(sort='cumtime')
   ```

## Frontend Debugging

### React Component Issues

#### Component Not Rendering
```
Problem: React component doesn't appear on screen
```

**Debugging Steps:**
1. Check browser console for JavaScript errors
2. Verify component is being imported correctly
3. Use React DevTools to inspect component hierarchy
4. Add console.log() statements to component lifecycle methods
5. Verify props being passed to the component

#### API Communication Issues
```
Problem: Frontend can't communicate with backend API
```

**Debugging Steps:**
1. Check network tab in browser developer tools
2. Verify API URL is correct
3. Check for CORS issues in browser console
4. Verify authentication headers are being sent
5. Look for payload formatting issues

### Visualization Issues

#### Charts Not Rendering
```
Problem: Data visualizations aren't appearing
```

**Debugging Steps:**
1. Check if data is being received by the component
2. Inspect data structure with console.log()
3. Verify visualization library is properly imported
4. Check for DOM container issues
5. Look for CSS conflicts affecting the visualization container

#### Incorrect Visualizations
```
Problem: Visualizations render incorrectly
```

**Debugging Steps:**
1. Compare data structure to expected format
2. Check for data transformation issues
3. Verify configuration options
4. Test with simplified test data
5. Check for library version differences between implementations

## Integration Debugging

### Authentication Issues

#### Login Failures
```
Problem: Users can't log in
```

**Debugging Steps:**
1. Check authentication backend configuration
2. Verify JWT token generation and validation
3. Look for CSRF token issues
4. Check for cookie/session storage problems
5. Verify user credentials in database

### WebSocket Issues

#### Connection Failures
```
Problem: WebSocket connection fails
```

**Debugging Steps:**
1. Check WebSocket URL configuration
2. Verify ASGI server is running correctly
3. Check for authentication in WebSocket handshake
4. Verify proxy configuration for WebSockets
5. Look for connection timeout issues

#### Message Handling Issues
```
Problem: WebSocket messages aren't being processed
```

**Debugging Steps:**
1. Add logging to WebSocket consumer methods
2. Verify message format matches expected schema
3. Check for exceptions in message handling
4. Verify client-side message listeners are set up
5. Test with simplified message structure

### Cross-Module Integration

#### Module Registration Issues
```
Problem: Modules aren't being registered correctly
```

**Debugging Steps:**
1. Check module_info.py in each module
2. Verify registry service initialization order
3. Look for import errors in module initialization
4. Check for duplicate module registrations
5. Verify module dependencies are satisfied

#### Data Sharing Issues
```
Problem: Data isn't being shared between modules
```

**Debugging Steps:**
1. Verify service singleton instances are working correctly
2. Check for serialization/deserialization issues
3. Look for transaction isolation problems
4. Verify consistent data models across modules
5. Check permission issues for cross-module access

## Common Database Issues

### Query Performance
```
Problem: Database queries are slow
```

**Debugging Steps:**
1. Use Django Debug Toolbar to identify slow queries
2. Add appropriate indexes to models
3. Use select_related() and prefetch_related() to reduce queries
4. Consider denormalizing data for performance-critical operations
5. Use database-specific EXPLAIN to analyze query execution plans

### Data Integrity
```
Problem: Data integrity issues
```

**Debugging Steps:**
1. Verify model constraints match business rules
2. Check for race conditions in concurrent operations
3. Use database transactions for multi-step operations
4. Verify foreign key relationships
5. Check for uncaught exceptions during data saving

## Environment-Specific Issues

### Development Environment
```
Problem: Issues only in development environment
```

**Debugging Steps:**
1. Check development-specific settings
2. Verify DEBUG=True for detailed error information
3. Check for environment variable differences
4. Verify development database is properly set up
5. Check for browser caching issues during development

### Production Environment
```
Problem: Issues only in production environment
```

**Debugging Steps:**
1. Check production logs
2. Verify static file serving
3. Check for HTTPS/SSL issues
4. Verify database connection pool settings
5. Check for resource limitations (memory, CPU, etc.)

## Debugging Tools

### Django Tools
- Django Debug Toolbar: For database and performance debugging
- Django Extensions: For enhanced shell and debugging tools
- django-silk: For request profiling
- ipdb: Enhanced debugging with iPython

### JavaScript Tools
- React DevTools: For React component debugging
- Redux DevTools: If using Redux for state management
- Chrome/Firefox Developer Tools: For network, console, and performance debugging
- Jest: For unit test debugging

### API Testing Tools
- Postman: For manual API testing
- curl: For command-line API testing
- Swagger/OpenAPI: For API documentation and testing

## Logging Best Practices

1. Use structured logging for machine-parseable logs
2. Include request IDs to trace requests across services
3. Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
4. Include contextual information in log messages
5. Use try/except blocks with detailed error logging
6. Implement custom logging for critical business operations

## Example Debug Configuration

### Django Settings
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'stickforstats': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### React Debug Configuration
```javascript
// config.js
export const DEBUG = process.env.NODE_ENV !== 'production';

// Logging utility
export const logger = {
  debug: (...args) => DEBUG && console.debug(...args),
  info: (...args) => console.info(...args),
  warn: (...args) => console.warn(...args),
  error: (...args) => console.error(...args),
};
```

## Conclusion

This debugging guide provides a structured approach to identifying and resolving issues in the StickForStats Django/React application. By following these debugging steps and best practices, developers can efficiently troubleshoot problems across different components of the system.

Remember that most issues in a migrated application stem from:
1. Different handling of edge cases between implementations
2. Integration points between components
3. Asynchronous operation timing issues
4. Environment-specific configuration differences

Always start debugging with the simplest possible test case, and incrementally add complexity until the issue is reproduced. Then work backward to identify the root cause.