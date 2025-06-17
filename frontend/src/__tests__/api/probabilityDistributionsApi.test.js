import axios from 'axios';
import * as api from '../../api/probabilityDistributionsApi';

// Mock axios
jest.mock('axios');

describe('Probability Distributions API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('fetchDistributionProjects calls the correct endpoint', async () => {
    const mockData = [{ id: 1, name: 'Test Project' }];
    axios.get.mockResolvedValueOnce({ data: mockData });

    const result = await api.fetchDistributionProjects();
    
    expect(axios.get).toHaveBeenCalledWith('/api/probability-distributions/projects/');
    expect(result).toEqual(mockData);
  });

  test('fetchDistributions calls the correct endpoint with project ID', async () => {
    const mockData = [{ id: 1, name: 'Test Distribution' }];
    axios.get.mockResolvedValueOnce({ data: mockData });

    const projectId = 123;
    const result = await api.fetchDistributions(projectId);
    
    expect(axios.get).toHaveBeenCalledWith('/api/probability-distributions/distributions/', {
      params: { project: projectId }
    });
    expect(result).toEqual(mockData);
  });

  test('createDistribution calls the correct endpoint with data', async () => {
    const mockData = { id: 1, name: 'New Distribution' };
    axios.post.mockResolvedValueOnce({ data: mockData });

    const distributionData = { 
      name: 'New Distribution', 
      distribution_type: 'NORMAL',
      parameters: { mean: 0, std: 1 } 
    };
    
    const result = await api.createDistribution(distributionData);
    
    expect(axios.post).toHaveBeenCalledWith('/api/probability-distributions/distributions/', distributionData);
    expect(result).toEqual(mockData);
  });

  test('calculatePmfPdf calls the correct endpoint with parameters', async () => {
    const mockData = { 
      x_values: [0, 1, 2], 
      pmf_pdf_values: [0.1, 0.2, 0.1] 
    };
    axios.post.mockResolvedValueOnce({ data: mockData });

    const distributionType = 'NORMAL';
    const parameters = { mean: 0, std: 1 };
    const xValues = [0, 1, 2];
    
    const result = await api.calculatePmfPdf(distributionType, parameters, xValues);
    
    expect(axios.post).toHaveBeenCalledWith('/api/probability-distributions/utilities/calculate-pmf-pdf/', {
      distribution_type: distributionType,
      parameters,
      x_values: xValues
    });
    expect(result).toEqual(mockData);
  });

  test('calculateCdf calls the correct endpoint with parameters', async () => {
    const mockData = { 
      x_values: [0, 1, 2], 
      cdf_values: [0.1, 0.3, 0.6] 
    };
    axios.post.mockResolvedValueOnce({ data: mockData });

    const distributionType = 'NORMAL';
    const parameters = { mean: 0, std: 1 };
    const xValues = [0, 1, 2];
    
    const result = await api.calculateCdf(distributionType, parameters, xValues);
    
    expect(axios.post).toHaveBeenCalledWith('/api/probability-distributions/utilities/calculate-cdf/', {
      distribution_type: distributionType,
      parameters,
      x_values: xValues
    });
    expect(result).toEqual(mockData);
  });

  test('generateRandomSample calls the correct endpoint with parameters', async () => {
    const mockData = { sample: [1, 2, 3, 4, 5] };
    axios.post.mockResolvedValueOnce({ data: mockData });

    const distributionType = 'NORMAL';
    const parameters = { mean: 0, std: 1 };
    const sampleSize = 5;
    const seed = 123;
    
    const result = await api.generateRandomSample(distributionType, parameters, sampleSize, seed);
    
    expect(axios.post).toHaveBeenCalledWith('/api/probability-distributions/utilities/generate-random-sample/', {
      distribution_type: distributionType,
      parameters,
      sample_size: sampleSize,
      seed
    });
    expect(result).toEqual(mockData);
  });

  test('compareBinomialApproximations calls the correct endpoint with parameters', async () => {
    const mockData = { 
      binomial: [0.1, 0.2, 0.3],
      normal_approx: [0.09, 0.19, 0.31],
      poisson_approx: [0.11, 0.21, 0.28]
    };
    axios.post.mockResolvedValueOnce({ data: mockData });

    const n = 10;
    const p = 0.3;
    const approximationTypes = ['NORMAL', 'POISSON'];
    const save = true;
    const projectId = 123;
    
    const result = await api.compareBinomialApproximations(n, p, approximationTypes, save, projectId);
    
    expect(axios.post).toHaveBeenCalledWith('/api/probability-distributions/utilities/binomial-approximation/', {
      n,
      p,
      approximation_types: approximationTypes,
      save,
      project_id: projectId
    });
    expect(result).toEqual(mockData);
  });

  test('simulateNetworkTraffic calls the correct endpoint with parameters', async () => {
    const mockData = { 
      simulation_results: {
        queue_sizes: [0, 1, 2, 1, 0],
        arrivals: [1, 1, 0, 0, 1],
        departures: [0, 0, 1, 1, 0]
      },
      metrics: {
        average_queue_size: 0.8,
        blocking_probability: 0.05
      }
    };
    axios.post.mockResolvedValueOnce({ data: mockData });

    const params = {
      arrivalRate: 5,
      serviceRate: 6,
      simulationTime: 100,
      bufferSize: 10,
      seed: 123,
      save: true,
      projectId: 456
    };
    
    const result = await api.simulateNetworkTraffic(params);
    
    expect(axios.post).toHaveBeenCalledWith('/api/probability-distributions/utilities/network-traffic-simulation/', {
      arrival_rate: params.arrivalRate,
      service_rate: params.serviceRate,
      simulation_time: params.simulationTime,
      buffer_size: params.bufferSize,
      seed: params.seed,
      save: params.save,
      project_id: params.projectId
    });
    expect(result).toEqual(mockData);
  });

  test('handles API errors correctly', async () => {
    const errorMessage = 'Network Error';
    axios.get.mockRejectedValueOnce(new Error(errorMessage));

    // We expect the function to throw an error
    await expect(api.fetchDistributionProjects()).rejects.toThrow();
    
    // The console.error should have been called with an error message
    // Note: This is assuming the implementation logs errors to console
    expect(console.error).toHaveBeenCalled;
  });
});