# Frontend Optimization Guide

This document outlines the optimization strategies implemented in the StickForStats frontend application to improve performance, reduce bundle size, and enhance user experience.

## Table of Contents

1. [Performance Optimization Overview](#performance-optimization-overview)
2. [Code Splitting](#code-splitting)
3. [Bundle Analysis](#bundle-analysis)
4. [Webpack Configuration](#webpack-configuration)
5. [CSS Optimization](#css-optimization)
6. [Image Optimization](#image-optimization)
7. [Runtime Performance](#runtime-performance)
8. [Future Improvements](#future-improvements)

## Performance Optimization Overview

The StickForStats frontend has been optimized using several strategies:

1. **Code Splitting**: Dynamically loading components to reduce initial bundle size
2. **Bundle Analysis**: Analyzing and optimizing bundle size with specific tools
3. **Webpack Configuration**: Custom webpack configuration for optimal chunking
4. **CSS Optimization**: CSS extraction and minimization for better performance
5. **Lazy Loading**: Loading components on demand to improve initial page load
6. **Preloading**: Intelligently preloading likely-to-be-used components
7. **Resource Optimization**: Optimizing images, fonts, and other assets
8. **Runtime Optimization**: Improving component rendering performance

## Code Splitting

Code splitting has been implemented using React's lazy loading functionality with Suspense. This allows components to be loaded only when needed, significantly reducing the initial bundle size.

### Implementation

- **Route-Based Splitting**: Major modules are lazy-loaded at the route level
- **Component-Level Splitting**: Heavy components within modules are lazy-loaded
- **Simulation Components**: Resource-intensive simulation components use dedicated lazy loading

For detailed implementation, see the [CODE_SPLITTING.md](./src/components/probability_distributions/CODE_SPLITTING.md) document.

### Usage Example

```jsx
// In App.jsx
const LazyProbabilityDistributionsPage = lazy(() => import('./pages/LazyProbabilityDistributionsPage'));

// In routes
<Route 
  path="/probability-distributions/*" 
  element={
    <Suspense fallback={<LoadingComponent message="Loading..." />}>
      <LazyProbabilityDistributionsPage />
    </Suspense>
  } 
/>
```

## Bundle Analysis

Bundle analysis tools have been set up to provide insights into bundle composition and opportunities for optimization.

### Available Tools

1. **source-map-explorer**: Detailed visualization of bundle contents
2. **webpack-bundle-analyzer**: Interactive treemap of bundle modules
3. **Custom analysis script**: Combined analysis with recommendations

### Using the Analysis Tools

Run these npm scripts to analyze the bundle:

```bash
# Full bundle analysis with recommendations
npm run analyze:bundle

# Interactive analysis with webpack-bundle-analyzer
npm run analyze:interactive

# Simple source-map-explorer analysis
npm run build:analyze
```

### Understanding the Results

The bundle analysis provides insights into:

- Overall bundle size and composition
- Size of individual modules and dependencies
- Duplicate code across chunks
- Opportunity for further optimizations

## Webpack Configuration

A custom webpack configuration has been implemented using CRACO (Create React App Configuration Override) to optimize the build process.

### Key Features

1. **Chunk Optimization**: Intelligent chunking strategy for improved loading
2. **Vendor Separation**: Major dependencies separated into dedicated chunks
3. **Runtime Extraction**: Runtime code extracted to improve caching
4. **Compression**: Gzip compression for production assets

### Configuration Details

The configuration in `craco.config.js` includes:

1. **Vendor Chunks**:
   - `vendor.d3.js`: D3.js visualization library
   - `vendor.mui.js`: Material UI components
   - `vendor.katex.js`: KaTeX math rendering
   - `vendor.chartjs.js`: Chart.js visualization library
   - `vendor.react.js`: React core libraries
   - `vendor.router.js`: React Router components
   - `vendor.bundle.js`: Other smaller dependencies

2. **Feature Chunks**:
   - `component.simulations.js`: Simulation components
   - `component.visualizations.js`: Visualization components
   - `component.probability.js`: Probability distribution components
   - `component.educational.js`: Educational content components

3. **Optimization Settings**:
   - MinSize threshold: 25KB
   - MaxInitialRequests: Infinity (optimizing for HTTP/2)
   - Aggressive caching with deterministic filenames

## CSS Optimization

CSS has been optimized to improve loading performance and reduce blocking time.

### CSS Splitting and Minification

1. **CSS Extraction**: Used MiniCssExtractPlugin to extract CSS into separate files
2. **CSS Chunking**: Split CSS into logical chunks that match JavaScript chunks
3. **CSS Minification**: Implemented CssMinimizerPlugin for aggressive optimization

### Configuration

```javascript
// CSS splitting in cacheGroups
styles: {
  name: 'styles',
  test: /\.css$/,
  chunks: 'all',
  enforce: true,
  priority: 30,
},

// Extract CSS in production
webpackConfig.plugins.push(
  new MiniCssExtractPlugin({
    filename: 'static/css/[name].[contenthash:8].css',
    chunkFilename: 'static/css/[name].[contenthash:8].chunk.css',
  })
);

// Optimize and minify CSS
webpackConfig.optimization.minimizer = [
  ...webpackConfig.optimization.minimizer,
  new CssMinimizerPlugin({
    minimizerOptions: {
      preset: [
        'default',
        {
          discardComments: { removeAll: true },
          minifyFontValues: { removeQuotes: false },
        },
      ],
    },
  }),
];
```

### CSS Performance Improvements

- CSS files are no longer render-blocking
- Reduced duplicate CSS across components
- Minified CSS with optimized rules
- CSS is cached separately from JavaScript

## Image Optimization

Images have been optimized to reduce page weight while maintaining quality.

### Strategies Implemented

1. **Format Selection**:
   - JPEG for photographic images
   - PNG for images with transparency
   - SVG for icons and simple graphics
   - WebP where browser support is available

2. **Responsive Images**:
   - Different sizes for different viewports
   - Appropriate resolution for device pixel ratio

3. **Loading Strategies**:
   - Lazy loading for below-the-fold images
   - Preloading for critical above-the-fold images

## Runtime Performance

Several runtime performance optimizations have been implemented:

### React Component Optimization

1. **Memoization**: React.memo for pure components
2. **useCallback/useMemo**: For expensive calculations and event handlers
3. **Virtual List**: For long scrollable lists of items

### D3.js Optimization

1. **Incremental Updates**: Updating only changed elements
2. **Debounced Rendering**: Preventing excessive rerendering
3. **SVG Optimization**: Minimizing SVG complexity

### Animation Performance

1. **requestAnimationFrame**: For smooth animations
2. **CSS Transitions**: Where appropriate instead of JS animations
3. **Transform/Opacity**: For GPU-accelerated animations

## Future Improvements

Several areas have been identified for future optimization:

1. **Module Federation**: Sharing modules between separate builds
2. **Service Worker Caching**: Caching assets for offline support
3. **Streaming Server-Side Rendering**: For improved initial load
4. **Custom D3.js Build**: Including only required modules
5. **Preact Compatibility Layer**: For reduced React footprint in production

## Implementation Notes

The optimization process is continual. The `analyze:bundle` script should be run periodically, especially after adding new dependencies or features, to identify new optimization opportunities.

When adding new components:
1. Consider whether they should be lazy-loaded
2. Follow existing patterns for code splitting
3. Consider the impact on bundle size
4. Write unit tests to ensure optimization doesn't break functionality