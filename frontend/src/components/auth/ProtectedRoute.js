import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { CircularProgress, Box } from '@mui/material';

const ProtectedRoute = ({ children, requiredRole = null }) => {
  const { user, loading, isAuthenticated } = useAuth();
  const location = useLocation();

  // In demo mode, allow access without authentication
  const isDemoMode = process.env.REACT_APP_DEMO_MODE === 'true' || process.env.REACT_APP_DISABLE_API === 'true';
  
  if (isDemoMode) {
    console.log('Demo mode active - bypassing authentication');
    return children;
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredRole && user?.role !== requiredRole && user?.role !== 'admin') {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default ProtectedRoute;