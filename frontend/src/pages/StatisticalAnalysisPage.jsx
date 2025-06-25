import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Checkbox,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Upload as UploadIcon,
  Calculate as CalculateIcon,
  Assessment as AssessmentIcon,
  Science as ScienceIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  PlayArrow as PlayArrowIcon,
  Description as DescriptionIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { useSnackbar } from 'notistack';
import Papa from 'papaparse';
import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  ScatterChart,
  Scatter,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as ChartTooltip, 
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import jStat from 'jstat';
import { confidenceIntervalCalculations, advancedProbabilityCalculations } from '../utils/advancedStatistics';

const StatisticalAnalysisPage = () => {
  const { enqueueSnackbar } = useSnackbar();
  const [activeTab, setActiveTab] = useState(0);
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [analysisType, setAnalysisType] = useState('descriptive');
  const [results, setResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [rawData, setRawData] = useState('');

  // Handle file upload
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      Papa.parse(file, {
        complete: (result) => {
          if (result.data && result.data.length > 0) {
            const headers = result.data[0];
            const dataRows = result.data.slice(1).filter(row => row.some(cell => cell !== ''));
            
            setColumns(headers);
            setData(dataRows);
            enqueueSnackbar('Data uploaded successfully', { variant: 'success' });
            setUploadDialogOpen(false);
          }
        },
        header: false,
        skipEmptyLines: true
      });
    }
  };

  // Handle raw data input
  const handleRawDataSubmit = () => {
    try {
      const lines = rawData.trim().split('\n');
      if (lines.length > 0) {
        const headers = lines[0].split(/[,\t]/).map(h => h.trim());
        const dataRows = lines.slice(1).map(line => 
          line.split(/[,\t]/).map(cell => cell.trim())
        );
        
        setColumns(headers);
        setData(dataRows);
        enqueueSnackbar('Data loaded successfully', { variant: 'success' });
        setUploadDialogOpen(false);
        setRawData('');
      }
    } catch (error) {
      enqueueSnackbar('Error parsing data', { variant: 'error' });
    }
  };

  // Generate sample data
  const generateSampleData = () => {
    const sampleHeaders = ['Group', 'Value1', 'Value2', 'Category'];
    const sampleData = [];
    
    for (let i = 0; i < 50; i++) {
      const group = Math.random() > 0.5 ? 'A' : 'B';
      const value1 = (Math.random() * 100).toFixed(2);
      const value2 = (Math.random() * 50 + 25).toFixed(2);
      const category = ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)];
      sampleData.push([group, value1, value2, category]);
    }
    
    setColumns(sampleHeaders);
    setData(sampleData);
    enqueueSnackbar('Sample data generated', { variant: 'info' });
  };

  // Perform statistical analysis
  const performAnalysis = () => {
    if (selectedColumns.length === 0) {
      enqueueSnackbar('Please select columns for analysis', { variant: 'warning' });
      return;
    }

    setIsAnalyzing(true);
    const analysisResults = {};

    try {
      switch (analysisType) {
        case 'descriptive':
          analysisResults.descriptive = performDescriptiveAnalysis();
          break;
        case 'correlation':
          analysisResults.correlation = performCorrelationAnalysis();
          break;
        case 'regression':
          analysisResults.regression = performRegressionAnalysis();
          break;
        case 'hypothesis':
          analysisResults.hypothesis = performHypothesisTests();
          break;
        case 'anova':
          analysisResults.anova = performANOVA();
          break;
        case 'time-series':
          analysisResults.timeSeries = performTimeSeriesAnalysis();
          break;
      }

      setResults(analysisResults);
      enqueueSnackbar('Analysis completed', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('Error during analysis: ' + error.message, { variant: 'error' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Descriptive statistics
  const performDescriptiveAnalysis = () => {
    const results = {};
    
    selectedColumns.forEach(colIndex => {
      const columnData = data.map(row => parseFloat(row[colIndex])).filter(val => !isNaN(val));
      
      if (columnData.length > 0) {
        results[columns[colIndex]] = {
          count: columnData.length,
          mean: jStat.mean(columnData),
          median: jStat.median(columnData),
          mode: jStat.mode(columnData),
          std: jStat.stdev(columnData, true),
          variance: jStat.variance(columnData, true),
          min: jStat.min(columnData),
          max: jStat.max(columnData),
          range: jStat.range(columnData),
          q1: jStat.quartiles(columnData)[0],
          q3: jStat.quartiles(columnData)[2],
          iqr: jStat.quartiles(columnData)[2] - jStat.quartiles(columnData)[0],
          skewness: calculateSkewness(columnData),
          kurtosis: calculateKurtosis(columnData),
          cv: jStat.stdev(columnData, true) / jStat.mean(columnData),
          confidenceInterval: confidenceIntervalCalculations.tDistributionCI(columnData, 0.95)
        };
      }
    });
    
    return results;
  };

  // Correlation analysis
  const performCorrelationAnalysis = () => {
    if (selectedColumns.length < 2) {
      throw new Error('Select at least 2 columns for correlation analysis');
    }

    const correlationMatrix = [];
    const pValueMatrix = [];
    
    for (let i = 0; i < selectedColumns.length; i++) {
      correlationMatrix[i] = [];
      pValueMatrix[i] = [];
      
      for (let j = 0; j < selectedColumns.length; j++) {
        const data1 = data.map(row => parseFloat(row[selectedColumns[i]])).filter(val => !isNaN(val));
        const data2 = data.map(row => parseFloat(row[selectedColumns[j]])).filter(val => !isNaN(val));
        
        if (data1.length === data2.length && data1.length > 2) {
          const correlation = jStat.corrcoeff(data1, data2);
          correlationMatrix[i][j] = correlation;
          
          // Calculate p-value for correlation
          const n = data1.length;
          const t = correlation * Math.sqrt((n - 2) / (1 - correlation * correlation));
          const pValue = 2 * (1 - jStat.studentt.cdf(Math.abs(t), n - 2));
          pValueMatrix[i][j] = pValue;
        } else {
          correlationMatrix[i][j] = null;
          pValueMatrix[i][j] = null;
        }
      }
    }
    
    return {
      matrix: correlationMatrix,
      pValues: pValueMatrix,
      columns: selectedColumns.map(i => columns[i])
    };
  };

  // Simple linear regression
  const performRegressionAnalysis = () => {
    if (selectedColumns.length !== 2) {
      throw new Error('Select exactly 2 columns for regression analysis');
    }

    const xData = data.map(row => parseFloat(row[selectedColumns[0]])).filter(val => !isNaN(val));
    const yData = data.map(row => parseFloat(row[selectedColumns[1]])).filter(val => !isNaN(val));
    
    if (xData.length !== yData.length) {
      throw new Error('Selected columns must have the same number of valid values');
    }

    // Calculate regression coefficients
    const n = xData.length;
    const sumX = jStat.sum(xData);
    const sumY = jStat.sum(yData);
    const sumXY = jStat.sum(xData.map((x, i) => x * yData[i]));
    const sumX2 = jStat.sum(xData.map(x => x * x));
    const sumY2 = jStat.sum(yData.map(y => y * y));
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // Calculate R-squared
    const yMean = jStat.mean(yData);
    const ssTotal = jStat.sum(yData.map(y => Math.pow(y - yMean, 2)));
    const ssResidual = jStat.sum(yData.map((y, i) => Math.pow(y - (slope * xData[i] + intercept), 2)));
    const rSquared = 1 - (ssResidual / ssTotal);
    
    // Calculate standard errors
    const seResidual = Math.sqrt(ssResidual / (n - 2));
    const seSlope = seResidual / Math.sqrt(jStat.sum(xData.map(x => Math.pow(x - jStat.mean(xData), 2))));
    const seIntercept = seResidual * Math.sqrt(sumX2 / (n * jStat.sum(xData.map(x => Math.pow(x - jStat.mean(xData), 2)))));
    
    // Calculate t-statistics and p-values
    const tSlope = slope / seSlope;
    const tIntercept = intercept / seIntercept;
    const pSlope = 2 * (1 - jStat.studentt.cdf(Math.abs(tSlope), n - 2));
    const pIntercept = 2 * (1 - jStat.studentt.cdf(Math.abs(tIntercept), n - 2));
    
    return {
      equation: `y = ${slope.toFixed(4)}x + ${intercept.toFixed(4)}`,
      slope,
      intercept,
      rSquared,
      adjustedRSquared: 1 - (1 - rSquared) * (n - 1) / (n - 2),
      standardError: seResidual,
      slopeError: seSlope,
      interceptError: seIntercept,
      tStatistics: { slope: tSlope, intercept: tIntercept },
      pValues: { slope: pSlope, intercept: pIntercept },
      n: n,
      predictions: xData.map(x => ({ x, y: slope * x + intercept }))
    };
  };

  // Hypothesis tests
  const performHypothesisTests = () => {
    const tests = {};
    
    // Normality test (Jarque-Bera)
    selectedColumns.forEach(colIndex => {
      const columnData = data.map(row => parseFloat(row[colIndex])).filter(val => !isNaN(val));
      
      if (columnData.length > 3) {
        const n = columnData.length;
        const skewness = calculateSkewness(columnData);
        const kurtosis = calculateKurtosis(columnData);
        const jb = (n / 6) * (skewness * skewness + 0.25 * Math.pow(kurtosis - 3, 2));
        const pValue = 1 - jStat.chisquare.cdf(jb, 2);
        
        tests[columns[colIndex]] = {
          test: 'Jarque-Bera Normality Test',
          statistic: jb,
          pValue,
          isNormal: pValue > 0.05
        };
      }
    });
    
    return tests;
  };

  // One-way ANOVA
  const performANOVA = () => {
    // For ANOVA, we need one categorical column and one numeric column
    const categoricalCol = selectedColumns.find(col => {
      const uniqueValues = [...new Set(data.map(row => row[col]))];
      return uniqueValues.length < 10; // Assume categorical if less than 10 unique values
    });
    
    const numericCol = selectedColumns.find(col => col !== categoricalCol);
    
    if (!categoricalCol || !numericCol) {
      throw new Error('Select one categorical and one numeric column for ANOVA');
    }
    
    // Group data by category
    const groups = {};
    data.forEach(row => {
      const category = row[categoricalCol];
      const value = parseFloat(row[numericCol]);
      
      if (!isNaN(value)) {
        if (!groups[category]) groups[category] = [];
        groups[category].push(value);
      }
    });
    
    const groupNames = Object.keys(groups);
    const groupData = groupNames.map(name => groups[name]);
    
    // Perform ANOVA calculations
    const k = groupData.length;
    const N = groupData.reduce((sum, group) => sum + group.length, 0);
    const grandMean = groupData.flat().reduce((sum, x) => sum + x, 0) / N;
    
    const SSB = groupData.reduce((sum, group) => {
      const groupMean = jStat.mean(group);
      return sum + group.length * Math.pow(groupMean - grandMean, 2);
    }, 0);
    
    const SSW = groupData.reduce((sum, group) => {
      const groupMean = jStat.mean(group);
      return sum + group.reduce((groupSum, x) => groupSum + Math.pow(x - groupMean, 2), 0);
    }, 0);
    
    const dfBetween = k - 1;
    const dfWithin = N - k;
    const MSB = SSB / dfBetween;
    const MSW = SSW / dfWithin;
    const F = MSB / MSW;
    const pValue = 1 - jStat.centralF.cdf(F, dfBetween, dfWithin);
    
    return {
      groups: groupNames.map((name, i) => ({
        name,
        n: groups[name].length,
        mean: jStat.mean(groups[name]),
        std: jStat.stdev(groups[name], true)
      })),
      fStatistic: F,
      pValue,
      dfBetween,
      dfWithin,
      meanSquareBetween: MSB,
      meanSquareWithin: MSW,
      significant: pValue < 0.05
    };
  };

  // Time series analysis (basic)
  const performTimeSeriesAnalysis = () => {
    if (selectedColumns.length !== 1) {
      throw new Error('Select exactly 1 column for time series analysis');
    }
    
    const tsData = data.map(row => parseFloat(row[selectedColumns[0]])).filter(val => !isNaN(val));
    
    // Calculate moving averages
    const ma3 = [];
    const ma5 = [];
    
    for (let i = 0; i < tsData.length; i++) {
      if (i >= 2) {
        ma3.push(jStat.mean(tsData.slice(i - 2, i + 1)));
      }
      if (i >= 4) {
        ma5.push(jStat.mean(tsData.slice(i - 4, i + 1)));
      }
    }
    
    // Simple trend analysis
    const x = Array.from({ length: tsData.length }, (_, i) => i);
    const trend = performSimpleRegression(x, tsData);
    
    return {
      data: tsData,
      movingAverage3: ma3,
      movingAverage5: ma5,
      trend: trend,
      seasonality: detectSeasonality(tsData)
    };
  };

  // Helper functions
  const calculateSkewness = (data) => {
    const n = data.length;
    const mean = jStat.mean(data);
    const std = jStat.stdev(data, true);
    const sum = data.reduce((acc, x) => acc + Math.pow((x - mean) / std, 3), 0);
    return (n / ((n - 1) * (n - 2))) * sum;
  };

  const calculateKurtosis = (data) => {
    const n = data.length;
    const mean = jStat.mean(data);
    const std = jStat.stdev(data, true);
    const sum = data.reduce((acc, x) => acc + Math.pow((x - mean) / std, 4), 0);
    return ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * sum - (3 * Math.pow(n - 1, 2)) / ((n - 2) * (n - 3));
  };

  const performSimpleRegression = (x, y) => {
    const n = x.length;
    const sumX = jStat.sum(x);
    const sumY = jStat.sum(y);
    const sumXY = jStat.sum(x.map((xi, i) => xi * y[i]));
    const sumX2 = jStat.sum(x.map(xi => xi * xi));
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    return { slope, intercept };
  };

  const detectSeasonality = (data) => {
    // Simple seasonality detection (placeholder)
    return {
      detected: false,
      period: null,
      strength: null
    };
  };

  // Render results based on analysis type
  const renderResults = () => {
    if (!results) return null;

    switch (analysisType) {
      case 'descriptive':
        return renderDescriptiveResults();
      case 'correlation':
        return renderCorrelationResults();
      case 'regression':
        return renderRegressionResults();
      case 'hypothesis':
        return renderHypothesisResults();
      case 'anova':
        return renderANOVAResults();
      case 'time-series':
        return renderTimeSeriesResults();
      default:
        return null;
    }
  };

  const renderDescriptiveResults = () => {
    const descriptiveData = results.descriptive;
    
    return (
      <Grid container spacing={3}>
        {Object.entries(descriptiveData).map(([column, stats]) => (
          <Grid item xs={12} md={6} key={column}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {column}
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell>Count</TableCell>
                        <TableCell align="right">{stats.count}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Mean</TableCell>
                        <TableCell align="right">{stats.mean.toFixed(3)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Median</TableCell>
                        <TableCell align="right">{stats.median.toFixed(3)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Std Dev</TableCell>
                        <TableCell align="right">{stats.std.toFixed(3)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Min / Max</TableCell>
                        <TableCell align="right">{stats.min.toFixed(3)} / {stats.max.toFixed(3)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Q1 / Q3</TableCell>
                        <TableCell align="right">{stats.q1.toFixed(3)} / {stats.q3.toFixed(3)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Skewness</TableCell>
                        <TableCell align="right">{stats.skewness.toFixed(3)}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>95% CI</TableCell>
                        <TableCell align="right">
                          [{stats.confidenceInterval.lowerBound.toFixed(3)}, {stats.confidenceInterval.upperBound.toFixed(3)}]
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  const renderCorrelationResults = () => {
    const { matrix, pValues, columns } = results.correlation;
    
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Correlation Matrix
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell></TableCell>
                  {columns.map(col => (
                    <TableCell key={col} align="center">{col}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {matrix.map((row, i) => (
                  <TableRow key={i}>
                    <TableCell>{columns[i]}</TableCell>
                    {row.map((corr, j) => (
                      <TableCell key={j} align="center">
                        {corr !== null ? (
                          <Tooltip title={`p-value: ${pValues[i][j]?.toFixed(4)}`}>
                            <span style={{ 
                              color: Math.abs(corr) > 0.7 ? '#f44336' : 
                                     Math.abs(corr) > 0.4 ? '#ff9800' : '#4caf50'
                            }}>
                              {corr.toFixed(3)}
                            </span>
                          </Tooltip>
                        ) : '-'}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    );
  };

  const renderRegressionResults = () => {
    const reg = results.regression;
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Regression Results
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                {reg.equation}
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>R²</TableCell>
                      <TableCell align="right">{reg.rSquared.toFixed(4)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Adjusted R²</TableCell>
                      <TableCell align="right">{reg.adjustedRSquared.toFixed(4)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Standard Error</TableCell>
                      <TableCell align="right">{reg.standardError.toFixed(4)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Slope</TableCell>
                      <TableCell align="right">
                        {reg.slope.toFixed(4)} ± {reg.slopeError.toFixed(4)}
                        <Chip 
                          size="small" 
                          label={`p=${reg.pValues.slope.toFixed(4)}`}
                          color={reg.pValues.slope < 0.05 ? 'error' : 'default'}
                          sx={{ ml: 1 }}
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Intercept</TableCell>
                      <TableCell align="right">
                        {reg.intercept.toFixed(4)} ± {reg.interceptError.toFixed(4)}
                        <Chip 
                          size="small" 
                          label={`p=${reg.pValues.intercept.toFixed(4)}`}
                          color={reg.pValues.intercept < 0.05 ? 'error' : 'default'}
                          sx={{ ml: 1 }}
                        />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Regression Plot
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="x" />
                  <YAxis />
                  <ChartTooltip />
                  <Scatter 
                    name="Data" 
                    data={data.map((row, i) => ({
                      x: parseFloat(row[selectedColumns[0]]),
                      y: parseFloat(row[selectedColumns[1]])
                    })).filter(d => !isNaN(d.x) && !isNaN(d.y))}
                    fill="#8884d8" 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="y" 
                    data={reg.predictions}
                    stroke="#ff7300" 
                    strokeWidth={2}
                    dot={false}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderHypothesisResults = () => {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Normality Tests
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Column</TableCell>
                  <TableCell>Test</TableCell>
                  <TableCell align="right">Statistic</TableCell>
                  <TableCell align="right">p-value</TableCell>
                  <TableCell>Result</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(results.hypothesis).map(([column, test]) => (
                  <TableRow key={column}>
                    <TableCell>{column}</TableCell>
                    <TableCell>{test.test}</TableCell>
                    <TableCell align="right">{test.statistic.toFixed(4)}</TableCell>
                    <TableCell align="right">{test.pValue.toFixed(4)}</TableCell>
                    <TableCell>
                      <Chip 
                        label={test.isNormal ? 'Normal' : 'Not Normal'}
                        color={test.isNormal ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    );
  };

  const renderANOVAResults = () => {
    const anova = results.anova;
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ANOVA Results
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>F-Statistic</TableCell>
                      <TableCell align="right">{anova.fStatistic.toFixed(4)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>p-value</TableCell>
                      <TableCell align="right">
                        <Chip 
                          label={anova.pValue.toFixed(4)}
                          color={anova.significant ? 'error' : 'success'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>df (Between)</TableCell>
                      <TableCell align="right">{anova.dfBetween}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>df (Within)</TableCell>
                      <TableCell align="right">{anova.dfWithin}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>MS (Between)</TableCell>
                      <TableCell align="right">{anova.meanSquareBetween.toFixed(4)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>MS (Within)</TableCell>
                      <TableCell align="right">{anova.meanSquareWithin.toFixed(4)}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Group Statistics
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Group</TableCell>
                      <TableCell align="right">n</TableCell>
                      <TableCell align="right">Mean</TableCell>
                      <TableCell align="right">Std Dev</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {anova.groups.map(group => (
                      <TableRow key={group.name}>
                        <TableCell>{group.name}</TableCell>
                        <TableCell align="right">{group.n}</TableCell>
                        <TableCell align="right">{group.mean.toFixed(3)}</TableCell>
                        <TableCell align="right">{group.std.toFixed(3)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderTimeSeriesResults = () => {
    const ts = results.timeSeries;
    const chartData = ts.data.map((value, index) => ({
      index,
      value,
      ma3: index >= 2 ? ts.movingAverage3[index - 2] : null,
      ma5: index >= 4 ? ts.movingAverage5[index - 4] : null,
      trend: ts.trend.intercept + ts.trend.slope * index
    }));
    
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Time Series Analysis
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="index" />
              <YAxis />
              <ChartTooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" name="Original" strokeWidth={1} dot={false} />
              <Line type="monotone" dataKey="ma3" stroke="#82ca9d" name="MA(3)" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="ma5" stroke="#ffc658" name="MA(5)" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="trend" stroke="#ff7300" name="Trend" strokeWidth={2} strokeDasharray="5 5" dot={false} />
            </LineChart>
          </ResponsiveContainer>
          <Typography variant="body2" sx={{ mt: 2 }}>
            Trend: y = {ts.trend.intercept.toFixed(4)} + {ts.trend.slope.toFixed(4)}x
          </Typography>
        </CardContent>
      </Card>
    );
  };

  const exportResults = () => {
    if (!results) return;
    
    const resultsText = JSON.stringify(results, null, 2);
    const blob = new Blob([resultsText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `statistical_analysis_${analysisType}_${new Date().toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    enqueueSnackbar('Results exported successfully', { variant: 'success' });
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom align="center">
        Statistical Analysis Center
      </Typography>
      <Typography variant="subtitle1" gutterBottom align="center" color="text.secondary">
        Comprehensive statistical analysis tools for data exploration and hypothesis testing
      </Typography>

      <Paper sx={{ mt: 3, mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
          <Tab label="Data Input" icon={<UploadIcon />} />
          <Tab label="Analysis" icon={<CalculateIcon />} />
          <Tab label="Results" icon={<AssessmentIcon />} disabled={!results} />
          <Tab label="Export" icon={<DownloadIcon />} disabled={!results} />
        </Tabs>
      </Paper>

      {activeTab === 0 && (
        <Box sx={{ p: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Data Upload
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                    <Button
                      variant="contained"
                      startIcon={<UploadIcon />}
                      onClick={() => setUploadDialogOpen(true)}
                    >
                      Upload Data
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<ScienceIcon />}
                      onClick={generateSampleData}
                    >
                      Generate Sample Data
                    </Button>
                  </Box>

                  {data.length > 0 && (
                    <>
                      <Alert severity="success" sx={{ mb: 2 }}>
                        Data loaded: {data.length} rows × {columns.length} columns
                      </Alert>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Data Preview
                      </Typography>
                      <TableContainer sx={{ maxHeight: 400 }}>
                        <Table stickyHeader size="small">
                          <TableHead>
                            <TableRow>
                              {columns.map((col, index) => (
                                <TableCell key={index}>{col}</TableCell>
                              ))}
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {data.slice(0, 10).map((row, rowIndex) => (
                              <TableRow key={rowIndex}>
                                {row.map((cell, cellIndex) => (
                                  <TableCell key={cellIndex}>{cell}</TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                      {data.length > 10 && (
                        <Typography variant="caption" sx={{ mt: 1 }}>
                          Showing first 10 of {data.length} rows
                        </Typography>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {activeTab === 1 && (
        <Box sx={{ p: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Analysis Configuration
                  </Typography>
                  
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Analysis Type</InputLabel>
                    <Select
                      value={analysisType}
                      onChange={(e) => setAnalysisType(e.target.value)}
                    >
                      <MenuItem value="descriptive">Descriptive Statistics</MenuItem>
                      <MenuItem value="correlation">Correlation Analysis</MenuItem>
                      <MenuItem value="regression">Linear Regression</MenuItem>
                      <MenuItem value="hypothesis">Hypothesis Tests</MenuItem>
                      <MenuItem value="anova">ANOVA</MenuItem>
                      <MenuItem value="time-series">Time Series Analysis</MenuItem>
                    </Select>
                  </FormControl>

                  <Typography variant="subtitle2" gutterBottom>
                    Select Columns for Analysis
                  </Typography>
                  <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                    {columns.map((col, index) => (
                      <FormControlLabel
                        key={index}
                        control={
                          <Checkbox
                            checked={selectedColumns.includes(index)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedColumns([...selectedColumns, index]);
                              } else {
                                setSelectedColumns(selectedColumns.filter(i => i !== index));
                              }
                            }}
                          />
                        }
                        label={col}
                      />
                    ))}
                  </Box>

                  <Button
                    variant="contained"
                    fullWidth
                    startIcon={isAnalyzing ? <CircularProgress size={20} /> : <PlayArrowIcon />}
                    onClick={performAnalysis}
                    disabled={isAnalyzing || data.length === 0 || selectedColumns.length === 0}
                    sx={{ mt: 2 }}
                  >
                    {isAnalyzing ? 'Analyzing...' : 'Perform Analysis'}
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Analysis Description
                  </Typography>
                  {analysisType === 'descriptive' && (
                    <Box>
                      <Typography paragraph>
                        <strong>Descriptive Statistics</strong> provides a summary of your data including:
                      </Typography>
                      <ul>
                        <li>Measures of central tendency (mean, median, mode)</li>
                        <li>Measures of dispersion (variance, standard deviation, range)</li>
                        <li>Distribution shape (skewness, kurtosis)</li>
                        <li>Confidence intervals for the mean</li>
                      </ul>
                    </Box>
                  )}
                  {analysisType === 'correlation' && (
                    <Box>
                      <Typography paragraph>
                        <strong>Correlation Analysis</strong> examines relationships between variables:
                      </Typography>
                      <ul>
                        <li>Pearson correlation coefficients</li>
                        <li>Statistical significance (p-values)</li>
                        <li>Correlation matrix visualization</li>
                      </ul>
                      <Alert severity="info" sx={{ mt: 2 }}>
                        Select at least 2 numeric columns for correlation analysis
                      </Alert>
                    </Box>
                  )}
                  {analysisType === 'regression' && (
                    <Box>
                      <Typography paragraph>
                        <strong>Linear Regression</strong> models the relationship between variables:
                      </Typography>
                      <ul>
                        <li>Regression equation (y = mx + b)</li>
                        <li>R-squared and adjusted R-squared</li>
                        <li>Parameter estimates with standard errors</li>
                        <li>Statistical significance tests</li>
                      </ul>
                      <Alert severity="info" sx={{ mt: 2 }}>
                        Select exactly 2 columns: first as X (independent), second as Y (dependent)
                      </Alert>
                    </Box>
                  )}
                  {analysisType === 'hypothesis' && (
                    <Box>
                      <Typography paragraph>
                        <strong>Hypothesis Tests</strong> for data assumptions:
                      </Typography>
                      <ul>
                        <li>Normality test (Jarque-Bera)</li>
                        <li>Test statistics and p-values</li>
                        <li>Decision at α = 0.05</li>
                      </ul>
                    </Box>
                  )}
                  {analysisType === 'anova' && (
                    <Box>
                      <Typography paragraph>
                        <strong>One-Way ANOVA</strong> compares means across groups:
                      </Typography>
                      <ul>
                        <li>F-statistic and p-value</li>
                        <li>Between and within group variability</li>
                        <li>Group means and standard deviations</li>
                      </ul>
                      <Alert severity="info" sx={{ mt: 2 }}>
                        Select one categorical and one numeric column
                      </Alert>
                    </Box>
                  )}
                  {analysisType === 'time-series' && (
                    <Box>
                      <Typography paragraph>
                        <strong>Time Series Analysis</strong> for temporal data:
                      </Typography>
                      <ul>
                        <li>Moving averages (3 and 5 period)</li>
                        <li>Trend analysis</li>
                        <li>Basic seasonality detection</li>
                      </ul>
                      <Alert severity="info" sx={{ mt: 2 }}>
                        Select exactly 1 column with time-ordered data
                      </Alert>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {activeTab === 2 && results && (
        <Box sx={{ p: 3 }}>
          {renderResults()}
        </Box>
      )}

      {activeTab === 3 && results && (
        <Box sx={{ p: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Export Results
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={exportResults}
                >
                  Export as JSON
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DescriptionIcon />}
                  disabled
                >
                  Generate Report (Coming Soon)
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload Data</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Option 1: Upload CSV File
            </Typography>
            <input
              type="file"
              accept=".csv,.txt"
              onChange={handleFileUpload}
              style={{ marginBottom: 20 }}
            />
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle2" gutterBottom>
              Option 2: Paste Data
            </Typography>
            <TextField
              multiline
              rows={10}
              fullWidth
              placeholder="Paste comma or tab-separated data here. First row should be column headers."
              value={rawData}
              onChange={(e) => setRawData(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRawDataSubmit} variant="contained" disabled={!rawData}>
            Load Data
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default StatisticalAnalysisPage;