# Three.js Compatibility Guide

This document explains how to handle Three.js compatibility issues in the StickForStats frontend application.

## Background

The frontend uses `@react-three/fiber` and `@react-three/drei` for 3D visualizations in the PCA Analysis module. These libraries depend on Three.js, and there was a compatibility issue with the `BatchedMesh` class which doesn't exist in Three.js v0.155.0.

## Solution Implemented

We've implemented a comprehensive solution with multiple layers to ensure compatibility:

1. **Dynamic Component Selection**:
   - Created a separate fallback implementation (`FallbackPcaVisualization.jsx`) that doesn't depend on Three.js
   - Used dynamic imports to conditionally select between real and fallback implementations based on environment flags
   - This approach ensures Three.js code is never imported when disabled

2. **Patched Three.js Utility**:
   - Created a `patchedThree.js` utility that provides a stub implementation of `BatchedMesh`
   - This utility is used in place of direct Three.js imports

3. **Conditional Three.js Setup**:
   - Created a `setupThree.js` file that only loads Three.js code when 3D is enabled
   - Imported from App.jsx to ensure global availability only when needed

4. **Environment Flag for 3D**:
   - Added `REACT_APP_DISABLE_3D` environment variable to control 3D features
   - When set to `true`, 3D visualization is completely bypassed
   - This allows deployment in environments where Three.js compatibility issues cannot be resolved

5. **patch-package Patches**:
   - Added patches for `@react-three/fiber` and `@react-three/drei` to handle missing `BatchedMesh`
   - These patches are applied automatically during `npm install` via the `postinstall` script

6. **Graceful UI Fallbacks**:
   - Updated UI components to disable 3D options when not available
   - Added informative messages to guide users when 3D features are disabled

## How to Use

### Running with 3D Support

```bash
# Normal development with 3D visualizations enabled
npm start

# Production build with 3D visualizations enabled
npm run build
```

### Running without 3D Support

```bash
# Development without 3D visualizations
npm run start:no3d

# Production build without 3D visualizations
npm run build:no3d
```

## Implementation Details

### 1. Component Architecture

- **src/components/pca/index.js**
  - Dynamic module selector that imports the appropriate implementation
  - Uses conditional require() calls to prevent webpack from bundling unused code

- **src/components/pca/fallback/FallbackPcaVisualization.jsx**
  - Complete implementation of PCA visualization without Three.js dependencies
  - Contains the same API and UI structure, but with 3D features disabled

### 2. Three.js Patching

- **src/utils/patchedThree.js**
  - Provides a stub implementation of BatchedMesh and other missing classes
  - Ensures all required Three.js methods have appropriate fallbacks

- **src/setupThree.js**
  - Conditionally initializes Three.js based on environment variables
  - Applies global patches to ensure compatibility

### 3. Environment Configuration

- **package.json scripts**
  - Added specialized scripts for running with and without 3D support
  - Uses environment variables to control build behavior

## Troubleshooting

If you encounter Three.js related errors:

1. **BatchedMesh errors**:
   - Ensure `patch-package` is installed and patches are applied
   - Check if `patchedThree.js` is being imported correctly
   - Verify that `postinstall` script ran successfully

2. **Missing other Three.js features**:
   - Check Three.js version compatibility with your @react-three/fiber version
   - Consider downgrading Three.js if necessary

3. **Build failures**:
   - Use the 3D-disabled mode (`npm run build:no3d`) to create a production build without 3D features
   - This should work even if Three.js compatibility issues cannot be resolved

## Adding New 3D Features

When adding new 3D features:

1. Always check for the 3D disabled flag:
   ```javascript
   const disable3D = process.env.REACT_APP_DISABLE_3D === 'true';
   ```

2. Provide fallback UIs for when 3D is disabled:
   ```javascript
   if (disable3D) {
     return <FallbackComponent />;
   }
   ```

3. If using Three.js directly, import from the patched utility:
   ```javascript
   import patchedTHREE from '../../utils/patchedThree';
   ```

4. Consider creating a fallback implementation for any component that depends on Three.js:
   ```javascript
   // Fallback.jsx
   export const Fallback3DComponent = () => {
     return (
       <Box sx={{ p: 3, textAlign: 'center' }}>
         <Typography>3D visualization is disabled</Typography>
       </Box>
     );
   };
   ```