/**
 * Tests for simulation calculations used in D3.js enhanced components
 */

// Import calculation functions from the components
// Note: In a real implementation, these would be extracted into separate utility files
import { poissonPMF, poissonCDF } from '../../../components/probability_distributions/simulations/EmailArrivalsD3';
import { normalPDF, normalCDF } from '../../../components/probability_distributions/simulations/QualityControlD3';
import { binomialPMF, binomialCDF } from '../../../components/probability_distributions/simulations/ClinicalTrialD3';
import { runNetworkSimulation } from '../../../components/probability_distributions/simulations/NetworkTrafficD3';
import { 
  calculateOC, 
  calculateAcceptanceProbability 
} from '../../../components/probability_distributions/simulations/ManufacturingDefectsD3';

describe('Poisson Distribution Calculations', () => {
  test('poissonPMF should calculate correct probabilities', () => {
    expect(poissonPMF(0, 1)).toBeCloseTo(0.368, 3);
    expect(poissonPMF(1, 1)).toBeCloseTo(0.368, 3);
    expect(poissonPMF(2, 1)).toBeCloseTo(0.184, 3);
    expect(poissonPMF(3, 1)).toBeCloseTo(0.061, 3);
  });

  test('poissonPMF should handle edge cases', () => {
    expect(poissonPMF(0, 0)).toBe(1);
    expect(poissonPMF(-1, 1)).toBe(0);
    expect(poissonPMF(1.5, 1)).toBe(0); // Non-integer k
  });

  test('poissonCDF should calculate correct cumulative probabilities', () => {
    expect(poissonCDF(0, 1)).toBeCloseTo(0.368, 3);
    expect(poissonCDF(1, 1)).toBeCloseTo(0.736, 3);
    expect(poissonCDF(2, 1)).toBeCloseTo(0.920, 3);
    expect(poissonCDF(10, 1)).toBeCloseTo(1.000, 3);
  });

  test('poissonCDF should handle edge cases', () => {
    expect(poissonCDF(-1, 1)).toBe(0);
    expect(poissonCDF(0, 0)).toBe(1);
  });

  test('poissonPMF should handle large lambda values', () => {
    // Using logarithms for numerical stability
    expect(poissonPMF(50, 50)).toBeCloseTo(0.056, 3);
    expect(poissonPMF(100, 100)).toBeCloseTo(0.040, 3);
  });
});

describe('Normal Distribution Calculations', () => {
  test('normalPDF should calculate correct density values', () => {
    expect(normalPDF(0, 0, 1)).toBeCloseTo(0.399, 3);
    expect(normalPDF(1, 0, 1)).toBeCloseTo(0.242, 3);
    expect(normalPDF(2, 0, 1)).toBeCloseTo(0.054, 3);
  });

  test('normalPDF should be symmetric around mean', () => {
    const mean = 5;
    const std = 2;
    expect(normalPDF(mean - 1, mean, std)).toBeCloseTo(normalPDF(mean + 1, mean, std), 10);
    expect(normalPDF(mean - 2, mean, std)).toBeCloseTo(normalPDF(mean + 2, mean, std), 10);
  });

  test('normalCDF should calculate correct cumulative probabilities', () => {
    expect(normalCDF(0, 0, 1)).toBeCloseTo(0.5, 3);
    expect(normalCDF(1, 0, 1)).toBeCloseTo(0.841, 3);
    expect(normalCDF(2, 0, 1)).toBeCloseTo(0.977, 3);
    expect(normalCDF(-1, 0, 1)).toBeCloseTo(0.159, 3);
  });

  test('normalCDF should handle extreme values', () => {
    expect(normalCDF(10, 0, 1)).toBeCloseTo(1, 10);
    expect(normalCDF(-10, 0, 1)).toBeCloseTo(0, 10);
  });
});

describe('Binomial Distribution Calculations', () => {
  test('binomialPMF should calculate correct probabilities', () => {
    expect(binomialPMF(0, 10, 0.5)).toBeCloseTo(0.001, 3);
    expect(binomialPMF(5, 10, 0.5)).toBeCloseTo(0.246, 3);
    expect(binomialPMF(10, 10, 0.5)).toBeCloseTo(0.001, 3);
  });

  test('binomialPMF should handle edge cases', () => {
    expect(binomialPMF(0, 10, 0)).toBeCloseTo(1, 10);
    expect(binomialPMF(10, 10, 1)).toBeCloseTo(1, 10);
    expect(binomialPMF(5, 10, 0)).toBeCloseTo(0, 10);
    expect(binomialPMF(-1, 10, 0.5)).toBe(0);
    expect(binomialPMF(11, 10, 0.5)).toBe(0);
  });

  test('binomialCDF should calculate correct cumulative probabilities', () => {
    expect(binomialCDF(0, 10, 0.5)).toBeCloseTo(0.001, 3);
    expect(binomialCDF(5, 10, 0.5)).toBeCloseTo(0.623, 3);
    expect(binomialCDF(10, 10, 0.5)).toBeCloseTo(1, 10);
  });

  test('binomialCDF should handle edge cases', () => {
    expect(binomialCDF(-1, 10, 0.5)).toBe(0);
    expect(binomialCDF(10, 10, 0)).toBeCloseTo(1, 10);
  });
});

describe('Network Simulation Calculations', () => {
  test('runNetworkSimulation should return expected structure', () => {
    const result = runNetworkSimulation({
      arrivalRate: 5,
      serviceRate: 10,
      bufferSize: 5,
      simulationTime: 10,
    });

    // Check result structure
    expect(result).toHaveProperty('simulationData');
    expect(result).toHaveProperty('metrics');
    expect(result).toHaveProperty('queueSizeDistribution');
    expect(result).toHaveProperty('theoreticalMetrics');
    expect(result).toHaveProperty('parameters');

    // Check metrics
    expect(result.metrics).toHaveProperty('utilization');
    expect(result.metrics).toHaveProperty('avgQueueSize');
    expect(result.metrics).toHaveProperty('avgWaitTime');
    expect(result.metrics).toHaveProperty('packetLossRate');

    // Validate values are in reasonable ranges
    expect(result.metrics.utilization).toBeGreaterThanOrEqual(0);
    expect(result.metrics.utilization).toBeLessThanOrEqual(1);
    expect(result.metrics.avgQueueSize).toBeGreaterThanOrEqual(0);
    expect(result.metrics.packetLossRate).toBeGreaterThanOrEqual(0);
    expect(result.metrics.packetLossRate).toBeLessThanOrEqual(1);
  });

  test('runNetworkSimulation should calculate metrics correctly for stable system', () => {
    const result = runNetworkSimulation({
      arrivalRate: 2,
      serviceRate: 10,
      bufferSize: 10,
      simulationTime: 100,
    });

    // For a stable system with arrival << service rate:
    // - Utilization should be low
    // - Queue size should be small
    // - Packet loss should be near 0
    expect(result.metrics.utilization).toBeLessThan(0.5);
    expect(result.metrics.avgQueueSize).toBeLessThan(1);
    expect(result.metrics.packetLossRate).toBeCloseTo(0, 1);
  });

  test('runNetworkSimulation should show congestion for unstable system', () => {
    const result = runNetworkSimulation({
      arrivalRate: 15,
      serviceRate: 10,
      bufferSize: 5,
      simulationTime: 100,
    });

    // For an unstable system with arrival > service rate:
    // - Utilization should be high
    // - Queue should be mostly full
    // - Packet loss should be significant
    expect(result.metrics.utilization).toBeGreaterThan(0.8);
    expect(result.metrics.avgQueueSize).toBeGreaterThan(1);
    expect(result.metrics.packetLossRate).toBeGreaterThan(0.1);
  });
});

describe('Manufacturing Quality Calculations', () => {
  test('calculateAcceptanceProbability should calculate correct probabilities', () => {
    expect(calculateAcceptanceProbability(0.01, 100, 2)).toBeGreaterThan(0.9);
    expect(calculateAcceptanceProbability(0.05, 100, 2)).toBeLessThan(0.5);
    expect(calculateAcceptanceProbability(0.1, 100, 2)).toBeLessThan(0.1);
  });

  test('calculateOC should generate correct operating characteristic curve', () => {
    const ocCurve = calculateOC(100, 2, [0.01, 0.02, 0.05, 0.1, 0.15]);

    // OC curve should be monotonically decreasing
    for (let i = 1; i < ocCurve.length; i++) {
      expect(ocCurve[i].acceptanceProbability).toBeLessThanOrEqual(ocCurve[i-1].acceptanceProbability);
    }

    // Check specific points
    expect(ocCurve[0].acceptanceProbability).toBeGreaterThan(0.9); // Low defect rate
    expect(ocCurve[ocCurve.length - 1].acceptanceProbability).toBeLessThan(0.1); // High defect rate
  });
});