import React, { useState, useEffect } from 'react';
import { Tabs, Tab, Box, Typography, Container, Paper, Button } from '@mui/material';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { API_URL } from '../../config/apiConfig';
import { useAuth } from '../../context/AuthContext';

// Import sub-components
import TheoryFoundations from './education/TheoryFoundations';
import InteractiveSimulations from './simulations/InteractiveSimulations';
import AdvancedMethods from './education/AdvancedMethods';
import RealWorldApplications from './education/RealWorldApplications';
import MathematicalProofs from './education/MathematicalProofs';
import References from './education/References';
import CalculatorDashboard from './calculators/CalculatorDashboard';
import AdvancedConfidenceIntervals from './AdvancedConfidenceIntervals';

// Import styles and utility components
import { styled } from '@mui/material/styles';
import { useSnackbar } from 'notistack';

const StyledContainer = styled(Container)(({ theme }) => ({
  marginTop: theme.spacing(4),
  marginBottom: theme.spacing(4),
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginBottom: theme.spacing(3),
}));

/**
 * Main component for the Confidence Intervals module
 */
const ConfidenceIntervalsPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { enqueueSnackbar } = useSnackbar();
  const { isDemoMode } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);

  // Define the tabs for the module
  const tabs = React.useMemo(() => [
    { label: 'Overview', path: '' },
    { label: 'Calculators', path: 'calculators' },
    { label: 'Advanced Analysis', path: 'advanced-analysis' },
    { label: 'Theory & Foundations', path: 'theory' },
    { label: 'Interactive Simulations', path: 'simulations' },
    { label: 'Advanced Methods', path: 'advanced' },
    { label: 'Real-World Applications', path: 'applications' },
    { label: 'Mathematical Proofs', path: 'proofs' },
    { label: 'References', path: 'references' },
  ], []);

  // Set active tab based on current path
  useEffect(() => {
    const currentPath = location.pathname.split('/').pop();
    const tabIndex = tabs.findIndex(tab => 
      tab.path === currentPath || 
      (currentPath === 'confidence-intervals' && tab.path === '')
    );
    setActiveTab(tabIndex !== -1 ? tabIndex : 0);
  }, [location.pathname, tabs]);

  // Fetch user's confidence interval projects
  useEffect(() => {
    const fetchProjects = async () => {
      setLoading(true);
      
      // In demo mode, use mock projects
      if (isDemoMode) {
        const mockProjects = [
          {
            id: 'demo-project-1',
            name: 'Sample Analysis Project',
            description: 'Demo project for exploring confidence intervals',
            settings: { default_confidence_level: 0.95 },
            created_at: new Date().toISOString(),
            data_count: 3
          },
          {
            id: 'demo-project-2',
            name: 'Clinical Trial Data',
            description: 'Example clinical trial confidence interval analysis',
            settings: { default_confidence_level: 0.99 },
            created_at: new Date().toISOString(),
            data_count: 5
          }
        ];
        setProjects(mockProjects);
        setLoading(false);
        return;
      }
      
      try {
        const response = await axios.get(`${API_URL}/confidence-intervals/projects/`);
        setProjects(Array.isArray(response.data) ? response.data : []);
      } catch (error) {
        console.error('Error fetching projects:', error);
        enqueueSnackbar('Failed to load projects', { variant: 'error' });
        setProjects([]); // Ensure projects is always an array
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [enqueueSnackbar, isDemoMode]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    navigate(`/confidence-intervals/${tabs[newValue].path}`);
  };

  // Create a new project
  const handleCreateProject = async () => {
    // In demo mode, create a mock project
    if (isDemoMode) {
      const newProject = {
        id: `demo-project-${Date.now()}`,
        name: `Confidence Interval Project ${projects.length + 1}`,
        description: 'A new confidence interval project',
        settings: { default_confidence_level: 0.95 },
        created_at: new Date().toISOString(),
        data_count: 0
      };
      
      setProjects([...projects, newProject]);
      enqueueSnackbar('Demo project created successfully', { variant: 'success' });
      navigate(`/confidence-intervals/calculators?project=${newProject.id}`);
      return;
    }
    
    try {
      const response = await axios.post(`${API_URL}/confidence-intervals/projects/`, {
        name: `Confidence Interval Project ${projects.length + 1}`,
        description: 'A new confidence interval project',
        settings: { default_confidence_level: 0.95 }
      });
      
      setProjects([...projects, response.data]);
      enqueueSnackbar('Project created successfully', { variant: 'success' });
      
      // Navigate to calculators with the new project
      navigate(`/confidence-intervals/calculators?project=${response.data.id}`);
    } catch (error) {
      console.error('Error creating project:', error);
      enqueueSnackbar('Failed to create project', { variant: 'error' });
    }
  };

  return (
    <StyledContainer maxWidth="lg">
      <StyledPaper elevation={3}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Confidence Intervals
        </Typography>
        
        <Typography variant="subtitle1" gutterBottom align="center">
          Explore the theory, calculation, and application of confidence intervals in statistics
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            aria-label="confidence intervals navigation tabs"
          >
            {tabs.map((tab, index) => (
              <Tab key={index} label={tab.label} />
            ))}
          </Tabs>
        </Box>
        
        <Box sx={{ p: 3 }}>
          <Routes>
            <Route path="" element={<Overview onCreateProject={handleCreateProject} />} />
            <Route path="calculators" element={<CalculatorDashboard projects={projects} />} />
            <Route path="advanced-analysis" element={<AdvancedConfidenceIntervals />} />
            <Route path="theory" element={<TheoryFoundations />} />
            <Route path="simulations" element={<InteractiveSimulations projects={projects} />} />
            <Route path="advanced" element={<AdvancedMethods />} />
            <Route path="applications" element={<RealWorldApplications />} />
            <Route path="proofs" element={<MathematicalProofs />} />
            <Route path="references" element={<References />} />
          </Routes>
        </Box>
      </StyledPaper>
    </StyledContainer>
  );
};

// Overview component shown on the main tab
const Overview = ({ onCreateProject }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Welcome to the Confidence Intervals Module
      </Typography>
      
      <Typography paragraph>
        Confidence intervals are a fundamental concept in statistical inference that provide a range of 
        plausible values for an unknown population parameter. This module provides a comprehensive 
        exploration of confidence intervals, from basic theory to advanced applications.
      </Typography>
      
      <Typography paragraph>
        You can explore theoretical foundations, try out interactive simulations, perform calculations 
        for various types of confidence intervals, and see real-world applications.
      </Typography>
      
      <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
        What You'll Learn:
      </Typography>
      
      <ul>
        <li>
          <Typography>The conceptual meaning and interpretation of confidence intervals</Typography>
        </li>
        <li>
          <Typography>How to calculate confidence intervals for means, proportions, and variances</Typography>
        </li>
        <li>
          <Typography>Bootstrap and other resampling methods for constructing intervals</Typography>
        </li>
        <li>
          <Typography>The relationship between confidence intervals and hypothesis testing</Typography>
        </li>
        <li>
          <Typography>Applications of confidence intervals in real-world data analysis</Typography>
        </li>
      </ul>
      
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={onCreateProject}
          size="large"
        >
          Create New Project
        </Button>
        
        <Typography variant="body2" sx={{ mt: 1 }}>
          Create a project to start calculating confidence intervals
        </Typography>
      </Box>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          How to Use This Module:
        </Typography>
        
        <ol>
          <li>
            <Typography>
              <strong>Theory & Foundations</strong>: Start here to understand the basic concepts
            </Typography>
          </li>
          <li>
            <Typography>
              <strong>Calculators</strong>: Perform confidence interval calculations on your data
            </Typography>
          </li>
          <li>
            <Typography>
              <strong>Interactive Simulations</strong>: Visualize how confidence intervals work
            </Typography>
          </li>
          <li>
            <Typography>
              <strong>Advanced Methods</strong>: Explore bootstrap and Bayesian methods
            </Typography>
          </li>
          <li>
            <Typography>
              <strong>Real-World Applications</strong>: See how confidence intervals are used in practice
            </Typography>
          </li>
        </ol>
      </Box>
    </Box>
  );
};

export default ConfidenceIntervalsPage;