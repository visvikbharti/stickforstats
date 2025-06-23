# Missing Imports Report - Frontend Codebase

## Summary
- **Total missing imports**: 13
- **Files affected**: 9
- **Date**: $(date)

## Issues by Priority

### Priority 1: Context Import Path Issues (3 occurrences)
These imports are looking in the wrong directory. The correct path should be `context` not `contexts`.

1. **`components/dashboard/Dashboard.jsx`** (Line 41)
   - Current: `import { useAuth } from '../../contexts/AuthContext';`
   - Fix: `import { useAuth } from '../../context/AuthContext';`

2. **`components/layout/AppBar.jsx`** (Line 36)
   - Current: `import { useAuth } from '../../contexts/AuthContext';`
   - Fix: `import { useAuth } from '../../context/AuthContext';`

### Priority 2: Missing Service Files (4 occurrences)
These service files don't exist and need to be created.

3. **`components/doe/DoePage.jsx`** (Lines 24-25)
   - Missing: `../../services/authService`
   - Missing: `../../services/contentService`

4. **`components/doe/__tests__/DoePage.test.jsx`** (Lines 5-6)
   - Missing: `../../../services/authService`
   - Missing: `../../../services/contentService`

**Action Required**: Create the following service files:
- `/frontend/src/services/authService.js`
- `/frontend/src/services/contentService.js`

### Priority 3: Missing Hook Files (3 occurrences)
These custom hooks don't exist and need to be created.

5. **`components/doe/__tests__/DOEWebSocketIntegration.test.jsx`** (Line 4)
   - Missing: `../../../hooks/useDOEWebSocket`

6. **`components/rag/QueryInterface.jsx`** (Line 35)
   - Missing: `../../hooks/useRAGWebSocket`

7. **`hooks/__tests__/useDOEWebSocket.test.js`** (Line 2)
   - Missing: `../useDOEWebSocket`

**Action Required**: Create the following hook files:
- `/frontend/src/hooks/useDOEWebSocket.js`
- `/frontend/src/hooks/useRAGWebSocket.js`

### Priority 4: Missing Component Files (3 occurrences)
These component files don't exist and need to be created.

8. **`components/doe/DoePage.jsx`** (Line 19)
   - Missing: `./CaseStudies`
   - **Action**: Create `/frontend/src/components/doe/CaseStudies.jsx`

9. **`components/pca/PcaPage.jsx`** (Line 6)
   - Missing: `../common/LoadingOverlay`
   - **Action**: Create `/frontend/src/components/common/LoadingOverlay.jsx`

10. **`components/doe/__tests__/DOEWebSocketIntegration.test.jsx`** (Line 5)
    - Missing: `../ProgressTracker`
    - **Note**: There's a `PcaProgressTracker.jsx` that might be reusable
    - **Action**: Create `/frontend/src/components/doe/ProgressTracker.jsx` or update import to use PCA version

### Priority 5: Syntax Error (1 occurrence)
11. **`components/rag/index.js`** (Line 16)
    - Issue: Invalid import syntax with just `'...'`
    - This appears to be a comment or placeholder that needs to be removed

## Quick Fix Script

To fix the context import issues (Priority 1), run:

```bash
# Fix Dashboard.jsx
sed -i '' "s|'../../contexts/AuthContext'|'../../context/AuthContext'|g" frontend/src/components/dashboard/Dashboard.jsx

# Fix AppBar.jsx
sed -i '' "s|'../../contexts/AuthContext'|'../../context/AuthContext'|g" frontend/src/components/layout/AppBar.jsx
```

## Files That Need to Be Created

1. **Services** (create in `/frontend/src/services/`):
   - `authService.js`
   - `contentService.js`

2. **Hooks** (create in `/frontend/src/hooks/`):
   - `useDOEWebSocket.js`
   - `useRAGWebSocket.js`

3. **Components**:
   - `/frontend/src/components/doe/CaseStudies.jsx`
   - `/frontend/src/components/common/LoadingOverlay.jsx`
   - `/frontend/src/components/doe/ProgressTracker.jsx`

## Recommended Next Steps

1. **Immediate**: Fix the context import paths (2 files)
2. **High Priority**: Create stub files for missing services and hooks to prevent build errors
3. **Medium Priority**: Implement the missing components
4. **Low Priority**: Review and clean up the rag/index.js file

This will resolve all 13 missing import errors and allow the Vercel build to proceed.