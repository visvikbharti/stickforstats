# Memory Optimization Guide

## JavaScript Heap Out of Memory Error

If you encounter a JavaScript heap out of memory error like this:
```
<--- Last few GCs --->
[9792:0x120008000] 75961793 ms: Mark-sweep 2032.9 (2088.8) -> 2030.9 (2089.0) MB, 444.4 / 0.0 ms (average mu = 0.103, current mu = 0.003) allocation failure; scavenge might not succeed
[9792:0x120008000] 75962237 ms: Mark-sweep 2033.1 (2089.0) -> 2031.0 (2089.0) MB, 442.6 / 0.0 ms (average mu = 0.056, current mu = 0.003) allocation failure; scavenge might not succeed

<--- JS stacktrace --->
FATAL ERROR: Ineffective mark-compacts near heap limit Allocation failed - JavaScript heap out of memory
```

This means Node.js has run out of available memory. This commonly happens when:
1. Building large React applications
2. Running bundle analyzers
3. Processing complex or large datasets

## Quick Solutions

### 1. Use Memory-Enhanced Scripts

We've added three scripts to help you run operations with increased memory:

```bash
# For building the application
npm run build:memory

# For starting the development server
npm run start:memory

# For analyzing bundle size
npm run analyze:memory
```

These scripts allocate 8GB of memory to Node.js, which should be sufficient for most operations.

### 2. Manually Set Node Memory

If you need to adjust the memory allocation, you can run any npm script with increased memory:

```bash
NODE_OPTIONS="--max-old-space-size=8192" npm run [script-name]
```

You can adjust the number from 4096 (4GB) to 16384 (16GB) based on your system's available RAM.

## Long-Term Optimization Strategies

While increasing memory allocation solves the immediate issue, consider these strategies for better performance:

### 1. Clean Up Unused Dependencies

The build errors show many unused imports. Remove these to reduce bundle size:

```bash
# Find unused dependencies
npm run lint

# Then fix them
npm run lint:fix
```

### 2. Implement Code Splitting

Use dynamic imports to split your code into smaller chunks:

```javascript
// Instead of
import HeavyComponent from './HeavyComponent';

// Use
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));
```

### 3. Use the Bundle Analyzer

Regularly analyze your bundle to identify large dependencies:

```bash
npm run analyze:memory
```

### 4. Configure CRACO for Better Chunking

Our current configuration in `craco.config.js` implements chunking strategies outlined in the bundle analysis report. Make sure it's properly configured for your needs.

## Related Documentation

- [React Code-Splitting Guide](https://reactjs.org/docs/code-splitting.html)
- [Webpack Optimization](https://webpack.js.org/guides/code-splitting/)
- [Node.js Memory Management](https://nodejs.org/api/cli.html#--max-old-space-sizesize-in-megabytes)
- [Review our Bundle Analysis Report](./bundle-analysis-report.md)