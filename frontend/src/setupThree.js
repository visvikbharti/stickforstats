/**
 * This file is used to configure Three.js support.
 * It's imported by App.jsx to ensure Three.js is properly patched
 * when 3D visualization is enabled.
 */

// Only initialize Three.js when 3D is enabled
if (process.env.REACT_APP_DISABLE_3D !== 'true') {
  try {
    // Import patched THREE for react-three-fiber
    const patchedTHREE = require('./utils/patchedThree').default;
    // Make it globally available under the THREE namespace
    window.THREE = patchedTHREE;
    console.log('Three.js successfully initialized with BatchedMesh polyfill');
  } catch (error) {
    console.warn('Error initializing Three.js:', error);
  }
}