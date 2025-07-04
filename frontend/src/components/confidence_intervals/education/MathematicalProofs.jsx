import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
  Grid,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Alert,
  CircularProgress,
  Tab,
  Tabs,
  TextField,
  Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FunctionsIcon from '@mui/icons-material/Functions';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import axios from 'axios';

// Import for rendering math formulas
import { MathJaxContext, MathJax } from 'better-react-mathjax';

/**
 * Mathematical Proofs component for Confidence Intervals module
 * Provides rigorous mathematical proofs and derivations for different confidence interval methods
 */
const MathematicalProofs = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [mathematicalContent, setMathematicalContent] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Fallback mathematical content in case API fails
  const fallbackContent = [
    {
      id: 'fallback-1',
      title: 'Interactive Z-Score Calculator',
      content: `For a confidence level of $(1-\\alpha)$, the critical value $z_{\\alpha/2}$ satisfies: $P(-z_{\\alpha/2} \\leq Z \\leq z_{\\alpha/2}) = 1-\\alpha$. Common critical values: 90% confidence: $z_{0.05} = 1.645$, 95% confidence: $z_{0.025} = 1.96$, 99% confidence: $z_{0.005} = 2.576$`
    },
    {
      id: 'fallback-2',
      title: 'Sample Size Determination',
      content: `To achieve a margin of error $E$ with confidence level $(1-\\alpha)$: $n = \\left(\\frac{z_{\\alpha/2} \\cdot \\sigma}{E}\\right)^2$ where $n$ = required sample size, $\\sigma$ = population standard deviation, $E$ = desired margin of error`
    }
  ];

  // Fetch mathematical content from the backend
  useEffect(() => {
    const fetchContent = async () => {
      try {
        const response = await axios.get('/api/v1/confidence-intervals/educational/?section=PROOFS');
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          setMathematicalContent(response.data);
        } else {
          // Use fallback content if API returns empty
          setMathematicalContent(fallbackContent);
        }
      } catch (error) {
        console.error('Error fetching mathematical content:', error);
        // Use fallback content on error
        setMathematicalContent(fallbackContent);
      } finally {
        setLoading(false);
      }
    };
    
    fetchContent();
  }, []);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // MathJax configuration
  const mathJaxConfig = {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      macros: {
        prob: ['\\mathbb{P}'],
        expect: ['\\mathbb{E}'],
        var: ['\\mathbb{V}ar'],
        cov: ['\\mathbb{C}ov'],
        R: ['\\mathbb{R}'],
        indic: ['\\mathbf{1}'],
        abs: ['\\lvert #1 \\rvert', 1]
      },
      processEscapes: true
    },
    svg: {
      fontCache: 'global'
    }
  };

  return (
    <MathJaxContext config={mathJaxConfig}>
      <Box>
        <Typography variant="h5" gutterBottom>
          Mathematical Proofs and Derivations
        </Typography>
        
        <Typography paragraph>
          This section provides rigorous mathematical derivations of confidence interval methods, 
          exploring the theoretical foundations and properties that ensure their validity.
        </Typography>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="proofs tabs">
            <Tab label="Parametric Methods" icon={<FunctionsIcon />} iconPosition="start" />
            <Tab label="Nonparametric Methods" icon={<AutoGraphIcon />} iconPosition="start" />
            <Tab label="Asymptotic Theory" icon={<ShowChartIcon />} iconPosition="start" />
          </Tabs>
        </Box>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            {/* Parametric Methods */}
            {activeTab === 0 && (
              <Box>
                <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Parametric Confidence Interval Derivations
                  </Typography>
                  
                  <Alert severity="info" sx={{ mb: 3 }}>
                    <Typography variant="body2">
                      These derivations rely on known probability distributions and assume specific parameterized models for the data.
                      They provide exact (rather than approximate) confidence intervals when all assumptions are met.
                    </Typography>
                  </Alert>
                  
                  <Accordion defaultExpanded>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Derivation for Normal Mean (Known Variance)
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Assumptions:
                      </Typography>
                      <ul>
                        <li>
                          <Typography variant="body2">
                            Random sample <MathJax inline>{"X_1, X_2, \\ldots, X_n \\sim N(\\mu, \\sigma^2)"}</MathJax> where <MathJax inline>{"\\sigma^2"}</MathJax> is known
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Sample mean <MathJax inline>{"\\bar{X} = \\frac{1}{n}\\sum_{i=1}^n X_i"}</MathJax>
                          </Typography>
                        </li>
                      </ul>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Derivation:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          We know that if $X_i \sim N(\mu, \sigma^2)$, then:
                        </Typography>
                        <MathJax>
                          {"$$\\bar{X} \\sim N\\left(\\mu, \\frac{\\sigma^2}{n}\\right)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Standardizing gives a pivotal quantity (distribution does not depend on $\mu$):
                        </Typography>
                        <MathJax>
                          {"$$Z = \\frac{\\bar{X} - \\mu}{\\sigma/\\sqrt{n}} \\sim N(0, 1)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          For confidence level (1-α), we find values z(α/2) such that:
                        </Typography>
                        <MathJax>
                          {"$$P(-z_{\\alpha/2} \\leq Z \\leq z_{\\alpha/2}) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Substituting the definition of $Z$:
                        </Typography>
                        <MathJax>
                          {"$$P\\left(-z_{\\alpha/2} \\leq \\frac{\\bar{X} - \\mu}{\\sigma/\\sqrt{n}} \\leq z_{\\alpha/2}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Multiplying all parts by <MathJax inline>{"\\sigma/\\sqrt{n}"}</MathJax>:
                        </Typography>
                        <MathJax>
                          {"$$P\\left(-z_{\\alpha/2} \\cdot \\frac{\\sigma}{\\sqrt{n}} \\leq \\bar{X} - \\mu \\leq z_{\\alpha/2} \\cdot \\frac{\\sigma}{\\sqrt{n}}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Rearranging to isolate $\mu$:
                        </Typography>
                        <MathJax>
                          {"$$P\\left(\\bar{X} - z_{\\alpha/2} \\cdot \\frac{\\sigma}{\\sqrt{n}} \\leq \\mu \\leq \\bar{X} + z_{\\alpha/2} \\cdot \\frac{\\sigma}{\\sqrt{n}}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Therefore, the $(1-\alpha)$ confidence interval for $\mu$ is:
                        </Typography>
                        <MathJax>
                          {"$$\\bar{X} \\pm z_{\\alpha/2} \\cdot \\frac{\\sigma}{\\sqrt{n}}$$"}
                        </MathJax>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Key Steps in the Proof:
                      </Typography>
                      <ol>
                        <li>
                          <Typography variant="body2">
                            Identify a pivotal quantity (<MathJax inline>{"Z = \\frac{\\bar{X} - \\mu}{\\sigma/\\sqrt{n}}"}</MathJax>)
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Determine critical values of the pivotal quantity
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Manipulate the inequalities to isolate the parameter of interest
                          </Typography>
                        </li>
                      </ol>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Derivation for Normal Mean (Unknown Variance)
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Assumptions:
                      </Typography>
                      <ul>
                        <li>
                          <Typography variant="body2">
                            Random sample $X_1, X_2, \ldots, X_n \sim N(\mu, \sigma^2)$ where $\sigma^2$ is unknown
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Sample mean <MathJax inline>{"\\bar{X} = \\frac{1}{n}\\sum_{i=1}^n X_i"}</MathJax>
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Sample variance <MathJax inline>{"S^2 = \\frac{1}{n-1}\\sum_{i=1}^n (X_i - \\bar{X})^2"}</MathJax>
                          </Typography>
                        </li>
                      </ul>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Derivation:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          We need a pivotal quantity. For normally distributed data with unknown variance, we use the t-distribution:
                        </Typography>
                        <MathJax>
                          {"$$T = \\frac{\\bar{X} - \\mu}{S/\\sqrt{n}} \\sim t_{n-1}$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Where $t_{n-1}$ is the t-distribution with <MathJax inline>{"n-1"}</MathJax> degrees of freedom.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          For confidence level <MathJax inline>{"1-\\alpha"}</MathJax>, we find values <MathJax inline>{"t_{\\alpha/2, n-1}"}</MathJax> such that:
                        </Typography>
                        <MathJax>
                          {"$$P(-t_{\\alpha/2, n-1} \\leq T \\leq t_{\\alpha/2, n-1}) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Substituting the definition of $T$:
                        </Typography>
                        <MathJax>
                          {"$$P\\left(-t_{\\alpha/2, n-1} \\leq \\frac{\\bar{X} - \\mu}{S/\\sqrt{n}} \\leq t_{\\alpha/2, n-1}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Multiplying all parts by $S/\sqrt{n}$:
                        </Typography>
                        <MathJax>
                          {"$$P\\left(-t_{\\alpha/2, n-1} \\cdot \\frac{S}{\\sqrt{n}} \\leq \\bar{X} - \\mu \\leq t_{\\alpha/2, n-1} \\cdot \\frac{S}{\\sqrt{n}}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Rearranging to isolate $\mu$:
                        </Typography>
                        <MathJax>
                          {"$$P\\left(\\bar{X} - t_{\\alpha/2, n-1} \\cdot \\frac{S}{\\sqrt{n}} \\leq \\mu \\leq \\bar{X} + t_{\\alpha/2, n-1} \\cdot \\frac{S}{\\sqrt{n}}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Therefore, the $(1-\alpha)$ confidence interval for $\mu$ is:
                        </Typography>
                        <MathJax>
                          {"$$\\bar{X} \\pm t_{\\alpha/2, n-1} \\cdot \\frac{S}{\\sqrt{n}}$$"}
                        </MathJax>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Key Theorem:
                      </Typography>
                      <Box sx={{ p: 2, bgcolor: 'rgba(63, 81, 181, 0.08)', borderRadius: 1 }}>
                        <Typography variant="body2">
                          If $X_1, X_2, \ldots, X_n \sim N(\mu, \sigma^2)$, then:
                        </Typography>
                        <ol>
                          <li>
                            <Typography variant="body2">
                              $\bar{X}$ and $S^2$ are independent
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              <MathJax inline>{"\\frac{(n-1)S^2}{\\sigma^2} \\sim \\chi^2_{n-1}"}</MathJax> where <MathJax inline>{"n"}</MathJax> is the sample size
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              <MathJax inline>{"\\frac{\\bar{X} - \\mu}{S/\\sqrt{n}} \\sim t_{n-1}"}</MathJax>
                            </Typography>
                          </li>
                        </ol>
                      </Box>
                      
                      <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          <strong>Note:</strong> As $n$ increases, the t-distribution approaches the standard normal distribution, 
                          and the t-interval approaches the z-interval. This is because the uncertainty in estimating $\sigma$ becomes 
                          relatively less important with larger samples.
                        </Typography>
                      </Alert>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Derivation for Variance and Standard Deviation
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Assumptions:
                      </Typography>
                      <ul>
                        <li>
                          <Typography variant="body2">
                            Random sample $X_1, X_2, \ldots, X_n \sim N(\mu, \sigma^2)$
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Sample variance <MathJax inline>{"S^2 = \\frac{1}{n-1}\\sum_{i=1}^n (X_i - \\bar{X})^2"}</MathJax>
                          </Typography>
                        </li>
                      </ul>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Derivation for Variance:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          From statistical theory, we know that for normal data:
                        </Typography>
                        <MathJax>
                          {"$$\\frac{(n-1)S^2}{\\sigma^2} \\sim \\chi^2_{n-1}$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          For confidence level <MathJax inline>{"1-\\alpha"}</MathJax>, we find values <MathJax inline>{"\\chi^2_{\\alpha/2, n-1}"}</MathJax> and <MathJax inline>{"\\chi^2_{1-\\alpha/2, n-1}"}</MathJax> such that:
                        </Typography>
                        <MathJax>
                          {"$$P\\left(\\chi^2_{\\alpha/2, n-1} \\leq \\frac{(n-1)S^2}{\\sigma^2} \\leq \\chi^2_{1-\\alpha/2, n-1}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Multiplying all parts by <MathJax inline>{"\\frac{\\sigma^2}{(n-1)S^2}"}</MathJax> (which reverses the inequalities because we're dividing by a positive number):
                        </Typography>
                        <MathJax>
                          {"$$P\\left(\\frac{1}{\\chi^2_{1-\\alpha/2, n-1}} \\leq \\frac{\\sigma^2}{(n-1)S^2} \\leq \\frac{1}{\\chi^2_{\\alpha/2, n-1}}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Multiplying all parts by $(n-1)S^2$:
                        </Typography>
                        <MathJax>
                          {"$$P\\left(\\frac{(n-1)S^2}{\\chi^2_{1-\\alpha/2, n-1}} \\leq \\sigma^2 \\leq \\frac{(n-1)S^2}{\\chi^2_{\\alpha/2, n-1}}\\right) = 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Therefore, the $(1-\alpha)$ confidence interval for $\sigma^2$ is:
                        </Typography>
                        <MathJax>
                          {"$$\\left(\\frac{(n-1)S^2}{\\chi^2_{1-\\alpha/2, n-1}}, \\frac{(n-1)S^2}{\\chi^2_{\\alpha/2, n-1}}\\right)$$"}
                        </MathJax>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Derivation for Standard Deviation:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          To find a confidence interval for $\sigma$, we take the square root of the endpoints of the interval for $\sigma^2$:
                        </Typography>
                        <MathJax>
                          {"$$\\left(\\sqrt{\\frac{(n-1)S^2}{\\chi^2_{1-\\alpha/2, n-1}}}, \\sqrt{\\frac{(n-1)S^2}{\\chi^2_{\\alpha/2, n-1}}}\\right)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          This transformation is valid because the square root function is monotonically increasing.
                        </Typography>
                      </Box>
                      
                      <Alert severity="warning" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          <strong>Important Note:</strong> The chi-square-based intervals for variance and standard deviation are 
                          highly sensitive to the normality assumption. Non-normal data can lead to poor coverage properties.
                        </Typography>
                      </Alert>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Derivation for Binomial Proportion (Exact Method)
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Assumptions:
                      </Typography>
                      <ul>
                        <li>
                          <Typography variant="body2">
                            Random sample of size <MathJax inline>{"n"}</MathJax> from a Bernoulli distribution with parameter <MathJax inline>{"p"}</MathJax>
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Number of successes $X \sim Binomial(n, p)$
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Sample proportion $\hat{p} = X/n$
                          </Typography>
                        </li>
                      </ul>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Derivation of Clopper-Pearson (Exact) Interval:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          For the Clopper-Pearson interval, we invert the exact binomial test. The lower bound $p_L$ satisfies:
                        </Typography>
                        <MathJax>
                          {"$$P(X \\geq x; n, p_L) = \\frac{\\alpha}{2}$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          The upper bound $p_U$ satisfies:
                        </Typography>
                        <MathJax>
                          {"$$P(X \\leq x; n, p_U) = \\frac{\\alpha}{2}$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          These can be expressed using the beta distribution:
                        </Typography>
                        <MathJax>
                          {"$$p_L = B\\left(\\frac{\\alpha}{2}; x, n-x+1\\right)$$"}
                        </MathJax>
                        <MathJax>
                          {"$$p_U = B\\left(1-\\frac{\\alpha}{2}; x+1, n-x\\right)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Where $B(q; a, b)$ is the $q$-th quantile of the Beta distribution with parameters $a$ and $b$.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          For the special cases:
                        </Typography>
                        <ul>
                          <li>
                            <Typography variant="body2">
                              When $x = 0$, the lower bound is 0
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              When $x = n$, the upper bound is 1
                            </Typography>
                          </li>
                        </ul>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Key Properties:
                      </Typography>
                      <ul>
                        <li>
                          <Typography variant="body2">
                            The Clopper-Pearson interval guarantees at least $(1-\alpha)$ coverage for all values of $p$
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            It is often conservative (wider than necessary) because the discrete nature of the binomial distribution
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            As $n$ increases, it converges to the normal approximation (Wald) interval
                          </Typography>
                        </li>
                      </ul>
                      
                      <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          <strong>Historical Note:</strong> The Clopper-Pearson interval was developed in 1934 and is often called the "exact" 
                          confidence interval for a binomial proportion because it uses the exact binomial distribution rather than asymptotic approximations.
                        </Typography>
                      </Alert>
                    </AccordionDetails>
                  </Accordion>
                </Paper>
              </Box>
            )}
            
            {/* Nonparametric Methods */}
            {activeTab === 1 && (
              <Box>
                <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Nonparametric Confidence Interval Derivations
                  </Typography>
                  
                  <Alert severity="info" sx={{ mb: 3 }}>
                    <Typography variant="body2">
                      Nonparametric methods make minimal assumptions about the data-generating distribution, 
                      offering robustness at the cost of wider intervals when parametric assumptions would have been valid.
                    </Typography>
                  </Alert>
                  
                  <Accordion defaultExpanded>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Bootstrap Percentile Method
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Theoretical Foundation:
                      </Typography>
                      
                      <Typography variant="body2" paragraph>
                        The bootstrap method approximates the sampling distribution of a statistic by resampling with replacement 
                        from the observed data. Let's explore the theoretical justification.
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          Let <MathJax inline>{"X_1, X_2, \\ldots, X_n"}</MathJax> be independent and identically distributed (i.i.d.) random variables 
                          from an unknown distribution <MathJax inline>{"F"}</MathJax>, and let <MathJax inline>{"\\hat{\\theta} = s(X_1, X_2, \\ldots, X_n)"}</MathJax> be an estimator 
                          of a parameter <MathJax inline>{"\\theta = t(F)"}</MathJax>.
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          The sampling distribution of <MathJax inline>{String.raw`\hat{\theta}`}</MathJax> depends on the unknown <MathJax inline>{"F"}</MathJax>. The bootstrap approximates 
                          this by using the empirical distribution function <MathJax inline>{"\\hat{F}_n"}</MathJax>, which puts mass <MathJax inline>{"1/n"}</MathJax> on each observed 
                          value <MathJax inline>{"X_i"}</MathJax>.
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          For the bootstrap percentile method:
                        </Typography>
                        <ol>
                          <li>
                            <Typography variant="body2">
                              Generate <MathJax inline>{"B"}</MathJax> bootstrap samples <MathJax inline>{"X^*_1, X^*_2, \\ldots, X^*_n"}</MathJax> by sampling with replacement from the original data
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              Compute the bootstrap replicate <MathJax inline>{"\\hat{\\theta}^*_b = s(X^*_{b1}, X^*_{b2}, \\ldots, X^*_{bn})"}</MathJax> for each bootstrap sample <MathJax inline>{"b = 1, 2, \\ldots, B"}</MathJax>
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              Form the empirical distribution of the bootstrap replicates <MathJax inline>{"\\hat{\\theta}^*_1, \\hat{\\theta}^*_2, \\ldots, \\hat{\\theta}^*_B"}</MathJax>
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              The <MathJax inline>{"(1-\\alpha)"}</MathJax> confidence interval is <MathJax inline>{"[\\hat{\\theta}^*_{(\\alpha/2)}, \\hat{\\theta}^*_{(1-\\alpha/2)}]"}</MathJax>, where <MathJax inline>{"\\hat{\\theta}^*_{(q)}"}</MathJax> is the <MathJax inline>{"q"}</MathJax>-quantile of the bootstrap distribution
                            </Typography>
                          </li>
                        </ol>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Mathematical Justification:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          The percentile method works because, under certain conditions, the bootstrap distribution of <MathJax inline>{"\\hat{\\theta}^* - \\hat{\\theta}"}</MathJax> 
                          approximates the sampling distribution of <MathJax inline>{"\\hat{\\theta} - \\theta"}</MathJax>:
                        </Typography>
                        <MathJax>
                          {"$$P_{F}(\\hat{\\theta} - \\theta \\leq c) \\approx P_{\\hat{F}_n}(\\hat{\\theta}^* - \\hat{\\theta} \\leq c)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          This implies:
                        </Typography>
                        <MathJax>
                          {"$$P_{F}(\\hat{\\theta} - \\theta \\leq c) \\approx P_{\\hat{F}_n}(\\hat{\\theta}^* \\leq c + \\hat{\\theta})$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Which leads to:
                        </Typography>
                        <MathJax>
                          {"$$P_{F}(\\theta \\geq \\hat{\\theta} - c) \\approx P_{\\hat{F}_n}(\\hat{\\theta}^* \\leq c + \\hat{\\theta})$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Similarly:
                        </Typography>
                        <MathJax>
                          {"$$P_{F}(\\theta \\leq \\hat{\\theta} + d) \\approx P_{\\hat{F}_n}(\\hat{\\theta}^* \\geq \\hat{\\theta} - d)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          For suitable $c$ and $d$, we get a $(1-\alpha)$ confidence interval:
                        </Typography>
                        <MathJax>
                          {"$$P_{F}(\\hat{\\theta} - c \\leq \\theta \\leq \\hat{\\theta} + d) \\approx 1-\\alpha$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          The percentile method implicitly finds $c$ and $d$ from the bootstrap distribution.
                        </Typography>
                      </Box>
                      
                      <Alert severity="warning" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          <strong>Limitations:</strong> The bootstrap percentile method assumes that the bootstrap distribution is unbiased and symmetric.
                          It may perform poorly when these assumptions are violated, which motivates more sophisticated bootstrap methods like BCa.
                        </Typography>
                      </Alert>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Bias-Corrected and Accelerated (BCa) Bootstrap
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Theoretical Foundation:
                      </Typography>
                      
                      <Typography variant="body2" paragraph>
                        The BCa method improves on the percentile method by correcting for bias and skewness in the bootstrap distribution.
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          The BCa method adjusts the percentiles used in the confidence interval calculation:
                        </Typography>
                        <MathJax>
                          {"$$[\\hat{\\theta}^*_{(\\alpha_1)}, \\hat{\\theta}^*_{(\\alpha_2)}]$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Where $\alpha_1$ and $\alpha_2$ are adjusted percentiles:
                        </Typography>
                        <MathJax>
                          {"$$\\alpha_1 = \\Phi\\left(z_0 + \\frac{z_0 + z_{\\alpha/2}}{1 - a(z_0 + z_{\\alpha/2})}\\right)$$"}
                        </MathJax>
                        <MathJax>
                          {"$$\\alpha_2 = \\Phi\\left(z_0 + \\frac{z_0 + z_{1-\\alpha/2}}{1 - a(z_0 + z_{1-\\alpha/2})}\\right)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Here:
                        </Typography>
                        <ul>
                          <li>
                            <Typography variant="body2">
                              $\Phi$ is the standard normal CDF
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              $z_\alpha$ is the $\alpha$-quantile of the standard normal distribution
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              $z_0$ is the bias-correction parameter
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              $a$ is the acceleration parameter
                            </Typography>
                          </li>
                        </ul>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Parameter Estimation:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          The bias-correction parameter $z_0$ is estimated as:
                        </Typography>
                        <MathJax>
                          {"$$z_0 = \\Phi^{-1}\\left(\\frac{\\#\\{\\hat{\\theta}^*_b < \\hat{\\theta}\\}}{B}\\right)$$"}
                        </MathJax>
                        <Typography variant="body2" paragraph>
                          where <MathJax inline>{"\\#\\{\\hat{\\theta}^*_b < \\hat{\\theta}\\}"}</MathJax> is the number of bootstrap replicates less than the original estimate.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          The acceleration parameter <MathJax inline>{"a"}</MathJax> is estimated using jackknife resampling:
                        </Typography>
                        <MathJax>
                          {"$$a = \\frac{\\sum_{i=1}^n (\\hat{\\theta}_{(\\cdot)} - \\hat{\\theta}_{(i)})^3}{6\\left[\\sum_{i=1}^n (\\hat{\\theta}_{(\\cdot)} - \\hat{\\theta}_{(i)})^2\\right]^{3/2}}$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph>
                          where <MathJax inline>{"\\hat{\\theta}_{(i)}"}</MathJax> is the estimate calculated with the <MathJax inline>{"i"}</MathJax>-th observation removed, and <MathJax inline>{"\\hat{\\theta}_{(\\cdot)}"}</MathJax> is the average of the <MathJax inline>{"\\hat{\\theta}_{(i)}"}</MathJax> values.
                        </Typography>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Theoretical Properties:
                      </Typography>
                      <ul>
                        <li>
                          <Typography variant="body2">
                            <strong>Second-order accuracy:</strong> The BCa method has error rate $O(n^{-1})$ compared to $O(n^{-1/2})$ for the percentile method
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            <strong>Transformation invariance:</strong> If <MathJax inline>{"\\hat{\\theta}"}</MathJax> is transformed by a monotonic function <MathJax inline>{"g"}</MathJax>, the BCa interval for <MathJax inline>{"g(\\theta)"}</MathJax> is <MathJax inline>{"[g(\\hat{\\theta}^*_{(\\alpha_1)}), g(\\hat{\\theta}^*_{(\\alpha_2)})]"}</MathJax>
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            <strong>Range preservation:</strong> The BCa interval will never extend beyond the range of the parameter space
                          </Typography>
                        </li>
                      </ul>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Wilcoxon Signed-Rank Confidence Interval for Median
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Assumptions:
                      </Typography>
                      <ul>
                        <li>
                          <Typography variant="body2">
                            Random sample $X_1, X_2, \ldots, X_n$ from a continuous, symmetric distribution with median $\theta$, where <MathJax inline>{"n"}</MathJax> is the sample size
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            The sample is i.i.d. (independent and identically distributed)
                          </Typography>
                        </li>
                      </ul>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Derivation:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          The Wilcoxon signed-rank confidence interval for the median is based on the duality between confidence intervals and hypothesis tests.
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          For any value $\theta_0$, define the centered observations:
                        </Typography>
                        <MathJax>
                          {"$$Y_i = X_i - \\theta_0$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          The Wilcoxon signed-rank statistic is:
                        </Typography>
                        <MathJax>
                          {"$$W^+ = \\sum_{i=1}^n Rank(|Y_i|) \\cdot I(Y_i > 0)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph>
                          where $Rank(|Y_i|)$ is the rank of $|Y_i|$ among $|Y_1|, |Y_2|, \ldots, |Y_n|$, and $I(Y_i > 0)$ is the indicator function.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Under the null hypothesis $H_0: \theta = \theta_0$, the distribution of $W^+$ is symmetric about $\frac{n(n+1)}{4}$, where <MathJax inline>{"n"}</MathJax> is the sample size.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          We include $\theta_0$ in the confidence interval if we fail to reject $H_0$ at significance level $\alpha$. This happens when:
                        </Typography>
                        <MathJax>
                          {"$$W^+_{\\alpha/2} \\leq W^+ \\leq W^+_{1-\\alpha/2}$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph>
                          where $W^+_q$ is the <MathJax inline>{"q"}</MathJax>-quantile of the Wilcoxon signed-rank distribution.
                        </Typography>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Practical Implementation:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          The confidence interval consists of all values $\theta_0$ that satisfy the above condition. In practice:
                        </Typography>
                        <ol>
                          <li>
                            <Typography variant="body2">
                              Calculate all pairwise averages: $A_{ij} = \frac{X_i + X_j}{2}$ for $1 \leq i \leq j \leq n$, where <MathJax inline>{"n"}</MathJax> is the sample size
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              Sort these $\frac{n(n+1)}{2}$ averages
                            </Typography>
                          </li>
                          <li>
                            <Typography variant="body2">
                              The $(1-\alpha)$ confidence interval is $[A_{(k)}, A_{(N-k+1)}]$, where $N = \frac{n(n+1)}{2}$ and <MathJax inline>{"k"}</MathJax> is determined from the Wilcoxon distribution tables
                            </Typography>
                          </li>
                        </ol>
                      </Box>
                      
                      <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          <strong>Key Property:</strong> The Wilcoxon signed-rank confidence interval is distribution-free (valid for any continuous, symmetric distribution) 
                          and robust to outliers. It is optimal (minimum length) among all distribution-free procedures when the underlying distribution is Gaussian.
                        </Typography>
                      </Alert>
                    </AccordionDetails>
                  </Accordion>
                </Paper>
              </Box>
            )}
            
            {/* Asymptotic Theory */}
            {activeTab === 2 && (
              <Box>
                <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Asymptotic Theory for Confidence Intervals
                  </Typography>
                  
                  <Alert severity="info" sx={{ mb: 3 }}>
                    <Typography variant="body2">
                      Asymptotic theory provides approximations that become increasingly accurate as sample sizes grow larger, 
                      enabling confidence interval construction for complex situations where exact methods are unavailable.
                    </Typography>
                  </Alert>
                  
                  <Accordion defaultExpanded>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Central Limit Theorem and Delta Method
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Central Limit Theorem:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          The foundation of many asymptotic confidence intervals is the Central Limit Theorem (CLT), which states that for i.i.d. samples $X_1, X_2, \ldots, X_n$ with mean $\mu$ and finite variance $\sigma^2$:
                        </Typography>
                        <MathJax>
                          {"$$\\frac{\\sqrt{n}(\\bar{X}_n - \\mu)}{\\sigma} \\xrightarrow{\\text{d}} N(0, 1) \\quad \\text{as } n \\to \\infty$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          where <MathJax inline>{"$\\xrightarrow{\\text{d}}$"}</MathJax> denotes convergence in distribution.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          This means that for large <MathJax inline>{"$n$"}</MathJax>, we can approximate:
                        </Typography>
                        <MathJax>
                          {"$$\\bar{X}_n \\approx N\\left(\\mu, \\frac{\\sigma^2}{n}\\right)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Leading to the asymptotic <MathJax inline>{"$(1-\\alpha)$"}</MathJax> confidence interval for <MathJax inline>{"$\\mu$"}</MathJax>:
                        </Typography>
                        <MathJax>
                          {"$$\\bar{X}_n \\pm z_{\\alpha/2} \\frac{\\sigma}{\\sqrt{n}}$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph>
                          In practice, we usually replace $\sigma$ with its estimate $s$.
                        </Typography>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Delta Method:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          The Delta Method extends the CLT to functions of asymptotically normal estimators. If <MathJax inline>{"$\\sqrt{n}(\\hat{\\theta}_n - \\theta) \\xrightarrow{\\text{d}} N(0, \\sigma^2)$"}</MathJax> and <MathJax inline>{"$g$"}</MathJax> is differentiable at <MathJax inline>{"$\\theta$"}</MathJax> with <MathJax inline>{"$g'(\\theta) \\neq 0$"}</MathJax>, then:
                        </Typography>
                        <MathJax>
                          {"$$\\sqrt{n}(g(\\hat{\\theta}_n) - g(\\theta)) \\xrightarrow{\\text{d}} N(0, [g'(\\theta)]^2 \\sigma^2)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          This gives the asymptotic $(1-\alpha)$ confidence interval for $g(\theta)$:
                        </Typography>
                        <MathJax>
                          {"$$g(\\hat{\\theta}_n) \\pm z_{\\alpha/2} \\frac{|g'(\\hat{\\theta}_n)| \\hat{\\sigma}}{\\sqrt{n}}$$"}
                        </MathJax>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Example: Confidence Interval for Variance Using Delta Method:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          Suppose we want a confidence interval for the standard deviation $\sigma$ given the sample variance $s^2$.
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          For large $n$, $s^2$ is approximately normal:
                        </Typography>
                        <MathJax>
                          {"$$s^2 \\approx N\\left(\\sigma^2, \\frac{2\\sigma^4}{n}\\right)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Let <MathJax inline>{"g(x) = \\sqrt{x}"}</MathJax>, so <MathJax inline>{"g'(x) = \\frac{1}{2\\sqrt{x}}"}</MathJax> and <MathJax inline>{"g'(\\sigma^2) = \\frac{1}{2\\sigma}"}</MathJax>.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          By the Delta Method:
                        </Typography>
                        <MathJax>
                          {"$$s = \\sqrt{s^2} \\approx N\\left(\\sigma, \\frac{\\sigma^2}{2n}\\right)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          Leading to the asymptotic $(1-\alpha)$ confidence interval for $\sigma$:
                        </Typography>
                        <MathJax>
                          {"$$s \\pm z_{\\alpha/2} \\frac{s}{\\sqrt{2n}}$$"}
                        </MathJax>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Wald, Score, and Likelihood Ratio Intervals
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        General Theory:
                      </Typography>
                      
                      <Typography variant="body2" paragraph>
                        These three types of intervals are based on different approaches to constructing confidence regions from likelihood functions.
                        Let <MathJax inline>{"L(\\theta; \\mathbf{X})"}</MathJax> be the likelihood function for parameter <MathJax inline>{"\\theta"}</MathJax> given data <MathJax inline>{"\\mathbf{X}"}</MathJax>, and <MathJax inline>{"\\hat{\\theta}"}</MathJax> be the maximum likelihood estimator (MLE).
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          1. Wald Interval:
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          Based on the asymptotic normality of the MLE:
                        </Typography>
                        <MathJax>
                          {"$$\\hat{\\theta} \\approx N\\left(\\theta, \\frac{1}{\\mathcal{I}(\\theta)}\\right)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 1 }}>
                          where $\mathcal{I}(\theta)$ is the Fisher information.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 1 }}>
                          The Wald $(1-\alpha)$ confidence interval is:
                        </Typography>
                        <MathJax>
                          {"$$\\hat{\\theta} \\pm z_{\\alpha/2} \\sqrt{\\frac{1}{\\mathcal{I}(\\hat{\\theta})}}$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 1 }}>
                          Or equivalently:
                        </Typography>
                        <MathJax>
                          {"$$\\hat{\\theta} \\pm z_{\\alpha/2} \\sqrt{\\widehat{\\text{Var}}(\\hat{\\theta})}$$"}
                        </MathJax>
                        
                        <Divider sx={{ my: 2 }} />
                        
                        <Typography variant="subtitle2" gutterBottom>
                          2. Score Interval:
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          Based on the score function <MathJax inline>{"S(\\theta) = \\frac{\\partial}{\\partial\\theta} \\log L(\\theta; \\mathbf{X})"}</MathJax>:
                        </Typography>
                        <MathJax>
                          {"$$\\frac{S(\\theta)^2}{\\mathcal{I}(\\theta)} \\xrightarrow{\\text{d}} \\chi^2_1 \\quad \\text{as } n \\to \\infty$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 1 }}>
                          The Score <MathJax inline>{"(1-\\alpha)"}</MathJax> confidence interval consists of all values <MathJax inline>{"\\theta"}</MathJax> satisfying:
                        </Typography>
                        <MathJax>
                          {"$$\\frac{S(\\theta)^2}{\\mathcal{I}(\\theta)} \\leq \\chi^2_{1,1-\\alpha}$$"}
                        </MathJax>
                        
                        <Divider sx={{ my: 2 }} />
                        
                        <Typography variant="subtitle2" gutterBottom>
                          3. Likelihood Ratio Interval:
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          Based on the likelihood ratio statistic:
                        </Typography>
                        <MathJax>
                          {"$$-2\\log\\frac{L(\\theta; \\mathbf{X})}{L(\\hat{\\theta}; \\mathbf{X})} \\xrightarrow{\\text{d}} \\chi^2_1 \\quad \\text{as } n \\to \\infty$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 1 }}>
                          The Likelihood Ratio $(1-\alpha)$ confidence interval consists of all values $\theta$ satisfying:
                        </Typography>
                        <MathJax>
                          {"$$-2\\log\\frac{L(\\theta; \\mathbf{X})}{L(\\hat{\\theta}; \\mathbf{X})} \\leq \\chi^2_{1,1-\\alpha}$$"}
                        </MathJax>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Example: Binomial Proportion:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          For a binomial proportion with $X \sim Binomial(n, p)$ and $\hat{p} = X/n$:
                        </Typography>
                        
                        <Typography variant="subtitle2" gutterBottom>
                          Wald Interval (standard method):
                        </Typography>
                        <MathJax>
                          {"$$\\hat{p} \\pm z_{\\alpha/2} \\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n}}$$"}
                        </MathJax>
                        
                        <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                          Score Interval (Wilson):
                        </Typography>
                        <MathJax>
                          {"$$\\frac{\\hat{p} + \\frac{z_{\\alpha/2}^2}{2n} \\pm z_{\\alpha/2}\\sqrt{\\frac{\\hat{p}(1-\\hat{p})}{n} + \\frac{z_{\\alpha/2}^2}{4n^2}}}{1 + \\frac{z_{\\alpha/2}^2}{n}}$$"}
                        </MathJax>
                        
                        <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                          Likelihood Ratio Interval:
                        </Typography>
                        <Typography variant="body2">
                          All values of $p$ satisfying:
                        </Typography>
                        <MathJax>
                          {"$$2\\left[X\\log\\left(\\frac{X}{np}\\right) + (n-X)\\log\\left(\\frac{n-X}{n(1-p)}\\right)\\right] \\leq \\chi^2_{1,1-\\alpha}$$"}
                        </MathJax>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Relative Performance:
                      </Typography>
                      <ul>
                        <li>
                          <Typography variant="body2">
                            <strong>Wald:</strong> Simplest but can have poor coverage, especially for small samples or extreme parameter values
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            <strong>Score:</strong> Better coverage than Wald, especially for small samples
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            <strong>Likelihood Ratio:</strong> Often the most accurate, invariant to parameterization, but can be computationally intensive
                          </Typography>
                        </li>
                      </ul>
                    </AccordionDetails>
                  </Accordion>
                  
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Asymptotically Pivotal Statistics
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography variant="subtitle2" gutterBottom>
                        Definition and Properties:
                      </Typography>
                      
                      <Typography variant="body2" paragraph>
                        A statistic $T_n(X_1, \ldots, X_n; \theta)$ is asymptotically pivotal if its asymptotic distribution 
                        does not depend on any unknown parameters. This property is crucial for constructing valid confidence intervals.
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          For example, if <MathJax inline>{"\\hat{\\theta}_n"}</MathJax> is an estimator of <MathJax inline>{"\\theta"}</MathJax> with asymptotic variance <MathJax inline>{"v(\\theta)"}</MathJax>, then:
                        </Typography>
                        <MathJax>
                          {"$$\\frac{\\sqrt{n}(\\hat{\\theta}_n - \\theta)}{\\sqrt{v(\\theta)}} \\xrightarrow{\\text{d}} N(0, 1)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          This is asymptotically pivotal if we know <MathJax inline>{"v(\\theta)"}</MathJax> exactly. However, if we must estimate <MathJax inline>{"v(\\theta)"}</MathJax> with <MathJax inline>{"\\hat{v}(\\hat{\\theta}_n)"}</MathJax>, then:
                        </Typography>
                        <MathJax>
                          {"$$\\frac{\\sqrt{n}(\\hat{\\theta}_n - \\theta)}{\\sqrt{\\hat{v}(\\hat{\\theta}_n)}} \\xrightarrow{\\text{d}} N(0, 1)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          The resulting t-statistic is still asymptotically pivotal if <MathJax inline>{"\\hat{v}(\\hat{\\theta}_n) \\stackrel{p}{\\to} v(\\theta)"}</MathJax> (i.e., the variance estimator is consistent).
                        </Typography>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Studentization:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          Studentization is the process of dividing a statistic by a consistent estimate of its standard error to create an asymptotically pivotal quantity.
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          For example, the studentized mean is:
                        </Typography>
                        <MathJax>
                          {"$$T_n = \\frac{\\sqrt{n}(\\bar{X}_n - \\mu)}{S_n} \\xrightarrow{\\text{d}} N(0, 1)$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph>
                          where $S_n^2 = \frac{1}{n-1}\sum_{i=1}^n (X_i - \bar{X}_n)^2$ is the sample variance.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          For small samples from normal distributions, $T_n$ follows a t-distribution with <MathJax inline>{"n-1"}</MathJax> degrees of freedom.
                        </Typography>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Higher-Order Asymptotics:
                      </Typography>
                      
                      <Box sx={{ p: 2, bgcolor: 'background.paper', my: 2 }}>
                        <Typography variant="body2" paragraph>
                          Basic asymptotic methods have error rates of order $O(n^{-1/2})$. Higher-order methods can reduce this to $O(n^{-1})$ or even $O(n^{-3/2})$.
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          For instance, Bartlett correction adjusts the likelihood ratio statistic:
                        </Typography>
                        <MathJax>
                          {"$$-2\\log\\Lambda \\cdot (1 - b/n) \\xrightarrow{\\text{d}} \\chi^2_p$$"}
                        </MathJax>
                        
                        <Typography variant="body2" paragraph>
                          where <MathJax inline>{"b"}</MathJax> is a constant that depends on the model, <MathJax inline>{"\\Lambda"}</MathJax> is the likelihood ratio, and <MathJax inline>{"p"}</MathJax> is the dimension of the parameter space.
                        </Typography>
                        
                        <Typography variant="body2" paragraph sx={{ mt: 2 }}>
                          The resulting confidence region has coverage error of order <MathJax inline>{"O(n^{-2})"}</MathJax> instead of <MathJax inline>{"O(n^{-1})"}</MathJax>.
                        </Typography>
                      </Box>
                      
                      <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          <strong>Key Insight:</strong> Asymptotically pivotal statistics are the foundation of bootstrap calibration methods. 
                          The studentized bootstrap (t-bootstrap) typically outperforms the percentile bootstrap because it uses 
                          asymptotically pivotal quantities, reducing the coverage error rate from <MathJax inline>{"O(n^{-1/2})"}</MathJax> to <MathJax inline>{"O(n^{-1})"}</MathJax> or better.
                        </Typography>
                      </Alert>
                    </AccordionDetails>
                  </Accordion>
                </Paper>
              </Box>
            )}
            
            {/* Custom Mathematical Content */}
            {mathematicalContent && mathematicalContent.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Additional Mathematical Resources
                </Typography>
                {mathematicalContent.map((content) => (
                  <Paper key={content.id} elevation={2} sx={{ p: 3, mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      {content.title}
                    </Typography>
                    
                    {content.content && (
                      <MathJax>
                        {content.content}
                      </MathJax>
                    )}
                  </Paper>
                ))}
              </Box>
            )}
          </Box>
        )}
      </Box>
    </MathJaxContext>
  );
};

export default MathematicalProofs;