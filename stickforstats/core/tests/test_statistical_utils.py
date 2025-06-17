import unittest
import numpy as np
import pandas as pd
from django.test import TestCase

from stickforstats.core.services.data_processing.statistical_utils import StatisticalUtilsService

class TestStatisticalUtilsService(TestCase):
    """Test cases for the StatisticalUtilsService."""
    
    def setUp(self):
        """Set up test data."""
        # Create a sample DataFrame for testing
        self.test_data = pd.DataFrame({
            'numeric1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'numeric2': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.0],
            'categorical': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
            'with_nulls': [1, 2, None, 4, None, 6, 7, None, 9, 10]
        })
        
        # Data with outliers
        self.outlier_data = pd.DataFrame({
            'with_outliers': [1, 2, 3, 4, 5, 50, 6, 7, 8, 9]
        })
        
        # Normal distribution data
        np.random.seed(42)
        self.normal_data = pd.DataFrame({
            'normal_dist': np.random.normal(0, 1, 100)
        })
        
        # Non-normal distribution data
        self.non_normal_data = pd.DataFrame({
            'non_normal': np.random.exponential(1, 100)
        })
    
    def test_compute_descriptive_stats(self):
        """Test computing descriptive statistics."""
        result = StatisticalUtilsService.compute_descriptive_stats(self.test_data)
        
        # Check that we got results for each numeric column
        self.assertIn('numeric1', result)
        self.assertIn('numeric2', result)
        self.assertNotIn('categorical', result)
        self.assertIn('with_nulls', result)
        
        # Check specific statistics for a column
        self.assertEqual(result['numeric1']['mean'], 5.5)
        self.assertEqual(result['numeric1']['min'], 1.0)
        self.assertEqual(result['numeric1']['max'], 10.0)
        
        # Check that nulls are handled correctly
        self.assertEqual(result['with_nulls']['count'], 7)
        self.assertEqual(result['with_nulls']['missing'], 3)
    
    def test_perform_inferential_tests(self):
        """Test performing inferential tests."""
        # Test with normal distribution
        normal_result = StatisticalUtilsService.perform_inferential_tests(self.normal_data)
        self.assertIn('normal_dist', normal_result)
        self.assertIn('normality_tests', normal_result['normal_dist'])
        
        # Test with non-normal distribution
        non_normal_result = StatisticalUtilsService.perform_inferential_tests(self.non_normal_data)
        self.assertIn('non_normal', non_normal_result)
        
        # Regular test data
        result = StatisticalUtilsService.perform_inferential_tests(self.test_data)
        self.assertIn('numeric1', result)
        self.assertIn('numeric2', result)
    
    def test_analyze_distributions(self):
        """Test analyzing distributions."""
        result = StatisticalUtilsService.analyze_distributions(self.test_data)
        
        # Check that we got results for each numeric column
        self.assertIn('numeric1', result)
        self.assertIn('numeric2', result)
        self.assertNotIn('categorical', result)
        
        # Check that the histogram and kde data are present
        self.assertIn('histogram_data', result['numeric1'])
        self.assertIn('kde_data', result['numeric1'])
        
        # Check the structure of the histogram data
        self.assertIn('counts', result['numeric1']['histogram_data'])
        self.assertIn('bins', result['numeric1']['histogram_data'])
        
        # Check the structure of the kde data
        self.assertIn('x', result['numeric1']['kde_data'])
        self.assertIn('y', result['numeric1']['kde_data'])
    
    def test_check_outliers(self):
        """Test outlier detection."""
        # IQR method
        iqr_result = StatisticalUtilsService.check_outliers(self.outlier_data, method='iqr')
        self.assertIn('with_outliers', iqr_result)
        self.assertEqual(iqr_result['with_outliers']['method'], 'IQR')
        self.assertTrue(iqr_result['with_outliers']['outlier_count'] > 0)
        
        # Z-score method
        z_result = StatisticalUtilsService.check_outliers(self.outlier_data, method='zscore')
        self.assertIn('with_outliers', z_result)
        self.assertEqual(z_result['with_outliers']['method'], 'Z-Score')
        self.assertTrue(z_result['with_outliers']['outlier_count'] > 0)
    
    def test_compute_correlation_matrix(self):
        """Test computing correlation matrix."""
        result = StatisticalUtilsService.compute_correlation_matrix(self.test_data)
        
        # Check that we got results
        self.assertIn('matrix', result)
        self.assertIn('columns', result)
        self.assertIn('method', result)
        
        # Check that the method is correct
        self.assertEqual(result['method'], 'pearson')
        
        # Check that the columns are correct
        self.assertIn('numeric1', result['columns'])
        self.assertIn('numeric2', result['columns'])
        self.assertNotIn('categorical', result['columns'])
        
        # Test with Spearman method
        spearman_result = StatisticalUtilsService.compute_correlation_matrix(
            self.test_data, method='spearman'
        )
        self.assertEqual(spearman_result['method'], 'spearman')