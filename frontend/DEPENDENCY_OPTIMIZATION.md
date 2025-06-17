# Dependency Optimization Strategy

This document outlines the strategy for optimizing third-party dependencies in the StickForStats frontend application to reduce bundle size and improve performance.

## Key Libraries to Optimize

### 1. D3.js
**Current issue**: Importing the entire library with `import * as d3 from 'd3'` results in a large bundle size.
**Solution**: Import only specific modules needed from D3 instead of the entire library.

### 2. MUI (Material UI)
**Current issue**: Extensive use across components but no tree-shaking optimization.
**Solution**: 
- Configure import paths to enable tree-shaking
- Replace `@mui/icons-material` with lightweight alternatives
- Lazy load dialogs and complex components

### 3. better-react-mathjax
**Current issue**: Large library for math formula rendering with significant bundle impact.
**Solution**: Replace with lighter alternative or optimize loading.

### 4. framer-motion
**Current issue**: Used for animations but impacts bundle size.
**Solution**: Replace with CSS transitions or reduce feature usage.

### 5. react-katex + katex
**Current issue**: Duplicate formula rendering capabilities with better-react-mathjax.
**Solution**: Standardize on one math rendering library.

### 6. recharts
**Current issue**: Used alongside D3.js for similar purposes.
**Solution**: Standardize visualization approach using either recharts or D3.js.

## Implementation Plan

1. **Create optimized D3 imports module**
   - Create utility file for common D3 operations
   - Import only necessary D3 modules in each component

2. **Optimize MUI usage**
   - Set up tree-shaking imports
   - Implement a single theme provider at the app root
   - Lazy load complex MUI components

3. **Standardize math rendering**
   - Select either KaTeX or MathJax based on feature needs
   - Implement dynamic loading of math libraries

4. **Reduce animation dependencies**
   - Replace framer-motion with CSS transitions where possible
   - Only load framer-motion for complex animations

5. **Unify charting library approach**
   - Select either recharts or D3.js as primary visualization library
   - Ensure consistent patterns across the application

## Measurement

To measure the impact of these optimizations:

1. Run bundle analysis before and after optimization
2. Document the size reduction for each dependency
3. Measure load time improvements
4. Track performance metrics with Lighthouse

## Implementation Priority

1. D3.js optimization (highest impact)
2. MUI optimization
3. Math libraries consolidation
4. Animation library optimization
5. Chart library standardization