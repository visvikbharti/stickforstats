import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SnackbarProvider } from 'notistack';
import { MathJaxContext } from 'better-react-mathjax';
import ErrorBoundary from './components/common/ErrorBoundary';
import { ServiceWorkerUpdater } from './components/common';
import { Box, CircularProgress, Typography } from '@mui/material';

// Import Three.js setup (only loads Three.js when needed)
import './setupThree';

// Import theme context
import { ThemeProvider } from './context/ThemeContext';

// Import branding context
import { BrandingProvider } from './context/BrandingContext';

// Import layout components
// import Navigation from './components/Navigation';
import SimpleNavigation from './components/SimpleNavigation';
import Footer from './components/Footer';

// Import auth components
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AuthDebug from './components/auth/AuthDebug';

// Import prefetching components
import { PrefetchProvider } from './context/PrefetchContext';
import PrefetchDebug from './components/navigation/PrefetchDebug';

// Import command palette components
import { CommandPaletteProvider } from './context/CommandPaletteContext';
import CommandPalette from './components/common/CommandPalette';

// Import search components
import { SearchProvider } from './context/SearchContext';
import GlobalSearch from './components/common/GlobalSearch';

// Import onboarding components
import { OnboardingProvider } from './context/OnboardingContext';
import { 
  TourProvider, 
  WelcomeModal, 
  OnboardingChecklist, 
  HelpButton 
} from './components/onboarding';

// Performance testing components are lazy loaded below

// Import only the HomePage directly as it's crucial for first render
// import HomePage from './pages/HomePage';
import ShowcaseHomePage from './pages/ShowcaseHomePage';
import NotFoundPage from './pages/NotFoundPage';

// Lazy-load authentication pages
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const DebugLoginPage = lazy(() => import('./pages/DebugLoginPage'));

// Lazy-load all other main pages to reduce initial bundle size
const StatisticsPage = lazy(() => import('./pages/StatisticsPage'));
const SQCAnalysisPage = lazy(() => import('./pages/SQCAnalysisPage'));
const DOEAnalysisPage = lazy(() => import('./pages/DOEAnalysisPage'));
const PCAAnalysisPage = lazy(() => import('./pages/PCAAnalysisPage'));
const WorkflowManagementPage = lazy(() => import('./pages/WorkflowManagementPage'));
const ReportManagementPage = lazy(() => import('./pages/ReportManagementPage'));
const ConfidenceIntervalsPage = lazy(() => import('./components/confidence_intervals/ConfidenceIntervalsPage'));
const ProbabilityDistributionsPage = lazy(() => import('./pages/LazyProbabilityDistributionsPage'));
const TestCalculator = lazy(() => import('./components/probability_distributions/TestCalculator'));
const AdvancedStatisticsPage = lazy(() => import('./pages/AdvancedStatisticsPage'));
const VisualizationStudioPage = lazy(() => import('./pages/VisualizationStudioPage'));
const ReportingStudioPage = lazy(() => import('./pages/ReportingStudioPage'));
const SecurityDashboardPage = lazy(() => import('./pages/SecurityDashboardPage'));
const MLStudioPage = lazy(() => import('./pages/MLStudioPage'));
const CollaborationHubPage = lazy(() => import('./pages/CollaborationHubPage'));
const MarketplacePage = lazy(() => import('./pages/MarketplacePage'));
const PerformanceTestDashboard = lazy(() => import('./components/performance/PerformanceTestDashboard'));
const WebSocketMonitoringPage = lazy(() => import('./pages/WebSocketMonitoringPage'));
const RAGPerformanceMonitoringPage = lazy(() => import('./pages/RAGPerformanceMonitoringPage'));
const BrowserCompatibilityTestPage = lazy(() => import('./pages/BrowserCompatibilityTestPage'));
const EnterpriseDashboard = lazy(() => import('./components/enterprise/EnterpriseDashboard'));
const KeyboardShortcutsPage = lazy(() => import('./pages/KeyboardShortcutsPage'));
const SearchResultsPage = lazy(() => import('./pages/SearchResultsPage'));
const BrandingManager = lazy(() => import('./components/admin/BrandingManager'));

// Loading fallback component
const LoadingComponent = ({ message = "Loading module..." }) => (
  <Box 
    sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center', 
      minHeight: '50vh',
      p: 4 
    }}
  >
    <CircularProgress size={40} />
    <Typography variant="h6" sx={{ mt: 2 }}>
      {message}
    </Typography>
  </Box>
);

// MathJax configuration
const mathJaxConfig = {
  loader: { load: ["[tex]/html"] },
  tex: {
    packages: { "[+]": ["html"] },
    inlineMath: [
      ["$", "$"],
      ["\\(", "\\)"]
    ],
    displayMath: [
      ["$$", "$$"],
      ["\\[", "\\]"]
    ]
  }
};

// Prefetch manager configuration
const prefetchOptions = {
  // Navigation pattern tracking
  maxPathLength: 10,                // Maximum length of navigation path to track
  maxPathsToStore: 100,             // Maximum number of unique paths to remember
  minimumVisitThreshold: 2,         // Minimum visits to a path before prediction is made
  
  // Prefetching behavior
  prefetchThreshold: 0.25,          // Probability threshold for prefetching (0.0 to 1.0)
  maxPrefetchResources: 5,          // Maximum resources to prefetch at once
  prefetchDocuments: true,          // Whether to prefetch HTML documents
  prefetchAssets: true,             // Whether to prefetch assets (JS, CSS, images)
  
  // Prefetching constraints
  respectDataSaver: true,           // Respect data-saver mode
  onlyFastConnections: true,        // Only prefetch on fast connections (4G+)
  
  // Debug
  debug: process.env.NODE_ENV === 'development' // Enable debug logging in development
};

function App() {
  // Global error handler for production errors
  const handleGlobalError = (error, errorInfo) => {
    // In a real app, you might want to log this to a service like Sentry
    console.error('Global error caught:', error);
    console.error('Component stack:', errorInfo?.componentStack);
  };

  // Show prefetch debug panel only in development
  const showPrefetchDebug = process.env.NODE_ENV === 'development';

  return (
    <ErrorBoundary onError={handleGlobalError}>
      <MathJaxContext config={mathJaxConfig}>
        <ThemeProvider>
          <BrandingProvider>
            <SnackbarProvider 
              maxSnack={3}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              autoHideDuration={5000}
            >
              <PrefetchProvider options={prefetchOptions}>
                <Router>
                  <AuthProvider>
                    <OnboardingProvider>
                      <SearchProvider>
                        <CommandPaletteProvider>
                          <TourProvider>
                            <div className="App">
                              <SimpleNavigation />
                              <CommandPalette />
                              <GlobalSearch />
                              <WelcomeModal />
                              <OnboardingChecklist />
                              <HelpButton />
                              <main style={{ minHeight: 'calc(100vh - 120px)', padding: '0' }}>
                        <Routes>
                        {/* Home page is loaded eagerly for fast initial load */}
                        <Route path="/" element={<ShowcaseHomePage />} />
                        
                        {/* Enterprise Dashboard */}
                        <Route 
                          path="/enterprise" 
                          element={
                            <ProtectedRoute>
                              <Suspense fallback={<LoadingComponent message="Loading Enterprise Dashboard..." />}>
                                <EnterpriseDashboard />
                              </Suspense>
                            </ProtectedRoute>
                          } 
                        />
                        
                        {/* Authentication routes */}
                        <Route 
                          path="/login" 
                          element={
                            <Suspense fallback={<LoadingComponent message="Loading login..." />}>
                              <LoginPage />
                            </Suspense>
                          } 
                        />
                        
                        <Route 
                          path="/register" 
                          element={
                            <Suspense fallback={<LoadingComponent message="Loading registration..." />}>
                              <RegisterPage />
                            </Suspense>
                          } 
                        />
                        
                        <Route 
                          path="/debug-login" 
                          element={
                            <Suspense fallback={<LoadingComponent message="Loading debug login..." />}>
                              <DebugLoginPage />
                            </Suspense>
                          } 
                        />
                        
                        {/* All main module routes are lazy loaded - Protected */}
                        <Route 
                          path="/statistics/*" 
                          element={
                            <ProtectedRoute>
                              <Suspense fallback={<LoadingComponent message="Loading Statistics Module..." />}>
                                <StatisticsPage />
                              </Suspense>
                            </ProtectedRoute>
                          } 
                        />
                      
                      <Route 
                        path="/sqc-analysis/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading SQC Analysis Module..." />}>
                              <SQCAnalysisPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/doe-analysis/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading DOE Analysis Module..." />}>
                              <DOEAnalysisPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/pca-analysis/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading PCA Analysis Module..." />}>
                              <PCAAnalysisPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/probability-distributions/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Probability Distributions Module..." />}>
                              <ProbabilityDistributionsPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/confidence-intervals/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Confidence Intervals Module..." />}>
                              <ConfidenceIntervalsPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/advanced-statistics/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Advanced Statistics Module..." />}>
                              <AdvancedStatisticsPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/visualization-studio/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Visualization Studio..." />}>
                              <VisualizationStudioPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/workflows/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Workflow Management Module..." />}>
                              <WorkflowManagementPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/reports/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Report Management Module..." />}>
                              <ReportManagementPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/reporting-studio/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Reporting Studio..." />}>
                              <ReportingStudioPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/ml-studio/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading ML Studio..." />}>
                              <MLStudioPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/collaboration/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Collaboration Hub..." />}>
                              <CollaborationHubPage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      <Route 
                        path="/marketplace/*" 
                        element={
                          <ProtectedRoute>
                            <Suspense fallback={<LoadingComponent message="Loading Marketplace..." />}>
                              <MarketplacePage />
                            </Suspense>
                          </ProtectedRoute>
                        } 
                      />
                      
                      {/* Test routes - for development only */}
                      <Route 
                        path="/test/calculator" 
                        element={
                          <Suspense fallback={<LoadingComponent message="Loading Test Calculator..." />}>
                            <TestCalculator />
                          </Suspense>
                        } 
                      />
                      
                      <Route
                        path="/test/performance"
                        element={
                          <Suspense fallback={<LoadingComponent message="Loading Performance Test Dashboard..." />}>
                            <PerformanceTestDashboard />
                          </Suspense>
                        }
                      />
                      
                      {/* Security Dashboard (admin only) */}
                      <Route
                        path="/security"
                        element={
                          <ProtectedRoute requiredRole="admin">
                            <Suspense fallback={<LoadingComponent message="Loading Security Dashboard..." />}>
                              <SecurityDashboardPage />
                            </Suspense>
                          </ProtectedRoute>
                        }
                      />
                      
                      {/* WebSocket Monitoring Dashboard (admin only) */}
                      <Route
                        path="/monitoring/websocket"
                        element={
                          <ProtectedRoute requiredRole="admin">
                            <Suspense fallback={<LoadingComponent message="Loading WebSocket Monitoring..." />}>
                              <WebSocketMonitoringPage />
                            </Suspense>
                          </ProtectedRoute>
                        }
                      />
                      
                      {/* RAG Performance Monitoring Dashboard (admin only) */}
                      <Route
                        path="/monitoring/rag-performance"
                        element={
                          <ProtectedRoute requiredRole="admin">
                            <Suspense fallback={<LoadingComponent message="Loading RAG Performance Monitoring..." />}>
                              <RAGPerformanceMonitoringPage />
                            </Suspense>
                          </ProtectedRoute>
                        }
                      />
                      
                      {/* Browser Compatibility Testing Page */}
                      <Route
                        path="/testing/browser-compatibility"
                        element={
                          <Suspense fallback={<LoadingComponent message="Loading Browser Compatibility Testing..." />}>
                            <BrowserCompatibilityTestPage />
                          </Suspense>
                        }
                      />
                      
                      {/* Keyboard Shortcuts Page */}
                      <Route
                        path="/shortcuts"
                        element={
                          <Suspense fallback={<LoadingComponent message="Loading Keyboard Shortcuts..." />}>
                            <KeyboardShortcutsPage />
                          </Suspense>
                        }
                      />
                      
                      {/* Search Results Page */}
                      <Route
                        path="/search"
                        element={
                          <Suspense fallback={<LoadingComponent message="Loading Search Results..." />}>
                            <SearchResultsPage />
                          </Suspense>
                        }
                      />
                      
                      {/* Branding Management (admin only) */}
                      <Route
                        path="/admin/branding"
                        element={
                          <ProtectedRoute requiredRole="admin">
                            <Suspense fallback={<LoadingComponent message="Loading Branding Manager..." />}>
                              <BrandingManager />
                            </Suspense>
                          </ProtectedRoute>
                        }
                      />
                      
                      {/* Catch-all route for 404 */}
                      <Route path="*" element={<NotFoundPage />} />
                    </Routes>
                  </main>
                  <Footer />
                    <ServiceWorkerUpdater />
                    {showPrefetchDebug && <PrefetchDebug position={{ bottom: 16, right: 16 }} />}
                    {process.env.NODE_ENV === 'development' && <AuthDebug />}
                  </div>
                        </TourProvider>
                      </CommandPaletteProvider>
                    </SearchProvider>
                  </OnboardingProvider>
                </AuthProvider>
              </Router>
            </PrefetchProvider>
          </SnackbarProvider>
        </BrandingProvider>
      </ThemeProvider>
      </MathJaxContext>
    </ErrorBoundary>
  );
}

export default App;