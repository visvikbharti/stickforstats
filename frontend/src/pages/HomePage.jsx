import React from 'react';
import { 
  Container, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardActions, 
  Box,
  Paper,
  Chip
} from '@mui/material';
import { 
  BarChart as BarChartIcon, 
  BubbleChart as BubbleChartIcon,
  Timeline as TimelineIcon,
  Functions as FunctionsIcon,
  Assessment as AssessmentIcon,
  ShowChart as ShowChartIcon,
  Science as ScienceIcon,
  Calculate as CalculateIcon,
  QuestionAnswer as QuestionAnswerIcon
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import TranslatedText from '../components/common/TranslatedText';

function HomePage() {
  const { isAuthenticated, user } = useAuth();
  const { t } = useTranslation();
  
  const modules = [
    {
      id: 'confidence-intervals',
      title: t('modules.confidenceIntervals.title'),
      description: t('modules.confidenceIntervals.description'),
      icon: <CalculateIcon fontSize="large" color="primary" />,
      link: '/confidence-intervals',
      requiresAuth: true
    },
    {
      id: 'probability-distributions',
      title: t('modules.probability.title'),
      description: t('modules.probability.description'),
      icon: <ShowChartIcon fontSize="large" color="primary" />,
      link: '/probability-distributions',
      requiresAuth: true
    },
    {
      id: 'pca-analysis',
      title: t('modules.pca.title'),
      description: t('modules.pca.description'),
      icon: <BubbleChartIcon fontSize="large" color="primary" />,
      link: '/pca-analysis',
      requiresAuth: true
    },
    {
      id: 'doe-analysis',
      title: t('modules.doe.title'),
      description: t('modules.doe.description'),
      icon: <ScienceIcon fontSize="large" color="primary" />,
      link: '/doe-analysis',
      requiresAuth: true
    },
    {
      id: 'sqc-analysis',
      title: t('modules.sqc.title'),
      description: t('modules.sqc.description'),
      icon: <AssessmentIcon fontSize="large" color="primary" />,
      link: '/sqc-analysis',
      requiresAuth: true
    },
    {
      id: 'statistics',
      title: t('modules.categories.advanced'),
      description: t('modules.statistics.description', 'Access comprehensive statistical analysis tools for complex data analysis.'),
      icon: <BarChartIcon fontSize="large" color="primary" />,
      link: '/statistics',
      requiresAuth: true
    }
  ];
  return (
    <div>
      {/* Hero section */}
      <Box 
        sx={{ 
          bgcolor: 'primary.main', 
          color: 'white', 
          py: 8, 
          mb: 6 
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="h2" component="h1" gutterBottom>
            {isAuthenticated ? t('common.messages.welcome', { name: user?.first_name || t('common.labels.researcher', 'Researcher') }) : t('app.name')}
          </Typography>
          <Typography variant="h5" component="h2" gutterBottom>
            <TranslatedText i18nKey="app.tagline" />
          </Typography>
          {isAuthenticated ? (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                {t('home.readyToContinue', 'Ready to continue your analysis?')}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button 
                  variant="contained" 
                  color="secondary" 
                  size="large"
                  component={Link}
                  to="/statistics"
                >
                  {t('home.openStatistics', 'Open Statistics')}
                </Button>
                <Button 
                  variant="outlined" 
                  sx={{ color: 'white', borderColor: 'white' }}
                  size="large"
                  component={Link}
                  to="/workflows"
                >
                  {t('home.myWorkflows', 'My Workflows')}
                </Button>
              </Box>
            </Box>
          ) : (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                {t('home.joinResearchers', 'Join thousands of researchers using our platform')}
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button 
                  variant="contained" 
                  color="secondary" 
                  size="large"
                  component={Link}
                  to="/register"
                >
                  {t('home.getStartedFree', 'Get Started Free')}
                </Button>
                <Button 
                  variant="outlined" 
                  sx={{ color: 'white', borderColor: 'white' }}
                  size="large"
                  component={Link}
                  to="/login"
                >
                  {t('navigation.login')}
                </Button>
              </Box>
            </Box>
          )}
        </Container>
      </Box>

      {/* Modules section */}
      <Container maxWidth="lg" sx={{ mb: 8 }}>
        <Typography variant="h4" component="h2" align="center" gutterBottom>
          {t('modules.title')}
        </Typography>
        <Typography variant="subtitle1" align="center" color="text.secondary" paragraph>
          {t('modules.description')}
        </Typography>
        <Grid container spacing={4} sx={{ mt: 4 }}>
          {modules && modules.length > 0 ? modules.map((module) => (
            <Grid item key={module.id} xs={12} sm={6} md={4}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: '0.3s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: 6
                  }
                }}
              >
                <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
                  {module.icon}
                </Box>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2">
                    {module.title}
                  </Typography>
                  <Typography>
                    {module.description}
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'space-between', px: 2 }}>
                  {module.requiresAuth && !isAuthenticated ? (
                    <>
                      <Chip 
                        label={t('common.labels.loginRequired', 'Login Required')} 
                        size="small" 
                        color="warning" 
                        variant="outlined"
                      />
                      <Button 
                        size="small" 
                        color="primary" 
                        component={Link} 
                        to="/login"
                      >
                        Sign In
                      </Button>
                    </>
                  ) : (
                    <Button 
                      size="small" 
                      color="primary" 
                      component={Link} 
                      to={module.link}
                      fullWidth
                    >
                      Explore
                    </Button>
                  )}
                </CardActions>
              </Card>
            </Grid>
          )) : null}
        </Grid>
      </Container>

      {/* Features section */}
      <Box sx={{ bgcolor: 'grey.100', py: 6 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" component="h2" align="center" gutterBottom>
            Key Features
          </Typography>
          <Grid container spacing={4} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                Data-Driven Insights
              </Typography>
              <Typography variant="body1">
                Transform raw data into actionable insights with powerful statistical tools.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                Interactive Visualizations
              </Typography>
              <Typography variant="body1">
                Explore your data through interactive charts and dynamic visualizations.
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                Comprehensive Analysis
              </Typography>
              <Typography variant="body1">
                Access a wide range of statistical methods for complete data analysis.
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </div>
  );
}

export default HomePage;