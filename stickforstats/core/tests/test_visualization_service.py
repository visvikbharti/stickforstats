import unittest
import numpy as np
import pandas as pd
from django.test import TestCase

from stickforstats.core.services.visualization.visualization_service import VisualizationService

class TestVisualizationService(TestCase):
    """Test cases for the VisualizationService."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample DataFrame for testing
        np.random.seed(42)
        self.test_data = pd.DataFrame({
            'numeric1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'numeric2': [1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.0],
            'categorical': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
            'date': pd.date_range(start='2023-01-01', periods=10, freq='D')
        })
        
        # Initialize visualization service
        self.viz_service = VisualizationService()
    
    def test_create_distribution_plots(self):
        """Test creating distribution plots."""
        plot_types = ["histogram", "boxplot", "kdeplot"]
        result = self.viz_service.create_distribution_plots(
            self.test_data, 'numeric1', plot_types
        )
        
        # Check result structure
        self.assertEqual(result['type'], 'distribution')
        self.assertIn('plots', result)
        self.assertIn('statistics', result)
        
        # Check that we got the correct number of plots
        self.assertEqual(len(result['plots']), len(plot_types))
        
        # Check that each plot has the necessary attributes
        for plot in result['plots']:
            self.assertIn('id', plot)
            self.assertIn('type', plot)
            self.assertIn('plot_data', plot)
            self.assertIn('title', plot)
            self.assertIn('description', plot)
            self.assertIn(plot['type'], plot_types)
    
    def test_create_relationship_plots(self):
        """Test creating relationship plots."""
        plot_types = ["scatter", "line"]
        result = self.viz_service.create_relationship_plots(
            self.test_data, 'numeric1', 'numeric2', plot_types
        )
        
        # Check result structure
        self.assertEqual(result['type'], 'relationship')
        self.assertIn('plots', result)
        
        # Check that we got the correct number of plots
        self.assertEqual(len(result['plots']), len(plot_types))
        
        # Test with color column
        result_with_color = self.viz_service.create_relationship_plots(
            self.test_data, 'numeric1', 'numeric2', ["scatter"], 'categorical'
        )
        self.assertEqual(len(result_with_color['plots']), 1)
    
    def test_create_comparison_plots(self):
        """Test creating comparison plots."""
        # Test bar plot
        bar_result = self.viz_service.create_comparison_plots(
            self.test_data, 'categorical', 'numeric1', 'bar', agg_func='mean'
        )
        self.assertEqual(bar_result['type'], 'comparison')
        self.assertEqual(len(bar_result['plots']), 1)
        self.assertEqual(bar_result['plots'][0]['type'], 'bar')
        
        # Test box plot
        box_result = self.viz_service.create_comparison_plots(
            self.test_data, 'categorical', 'numeric1', 'box'
        )
        self.assertEqual(box_result['type'], 'comparison')
        self.assertEqual(len(box_result['plots']), 1)
        self.assertEqual(box_result['plots'][0]['type'], 'box')
    
    def test_create_time_series_plots(self):
        """Test creating time series plots."""
        plot_types = ["line", "area"]
        result = self.viz_service.create_time_series_plots(
            self.test_data, 'date', 'numeric1', plot_types
        )
        
        # Check result structure
        self.assertEqual(result['type'], 'time_series')
        self.assertIn('plots', result)
        
        # Check that we got the correct number of plots
        self.assertEqual(len(result['plots']), len(plot_types))
        
        # Test with rolling window
        rolling_result = self.viz_service.create_time_series_plots(
            self.test_data, 'date', 'numeric1', ["rolling"], window=3
        )
        self.assertEqual(rolling_result['type'], 'time_series')
        self.assertEqual(len(rolling_result['plots']), 1)
    
    def test_create_composition_plots(self):
        """Test creating composition plots."""
        # Test pie chart
        pie_result = self.viz_service.create_composition_plots(
            self.test_data, 'categorical', 'pie'
        )
        self.assertEqual(pie_result['type'], 'composition')
        self.assertEqual(len(pie_result['plots']), 1)
        self.assertEqual(pie_result['plots'][0]['type'], 'pie')
        
        # Test treemap with value column
        treemap_result = self.viz_service.create_composition_plots(
            self.test_data, 'categorical', 'treemap', value_col='numeric1'
        )
        self.assertEqual(treemap_result['type'], 'composition')
        self.assertEqual(len(treemap_result['plots']), 1)
        self.assertEqual(treemap_result['plots'][0]['type'], 'treemap')
    
    def test_describe_correlation(self):
        """Test correlation description helper."""
        # Test positive correlations
        self.assertIn("Very strong positive", self.viz_service._describe_correlation(0.9))
        self.assertIn("Strong positive", self.viz_service._describe_correlation(0.6))
        self.assertIn("Moderate positive", self.viz_service._describe_correlation(0.4))
        self.assertIn("Weak positive", self.viz_service._describe_correlation(0.2))
        self.assertIn("Negligible", self.viz_service._describe_correlation(0.05))
        
        # Test negative correlations
        self.assertIn("Very strong negative", self.viz_service._describe_correlation(-0.9))
        self.assertIn("Strong negative", self.viz_service._describe_correlation(-0.6))
        self.assertIn("Moderate negative", self.viz_service._describe_correlation(-0.4))
        self.assertIn("Weak negative", self.viz_service._describe_correlation(-0.2))
        self.assertIn("Negligible", self.viz_service._describe_correlation(-0.05))
    
    def test_interpret_regression(self):
        """Test regression interpretation helper."""
        # Test different R² values
        self.assertIn("Excellent fit", self.viz_service._interpret_regression(0.8, 0.01))
        self.assertIn("Good fit", self.viz_service._interpret_regression(0.6, 0.01))
        self.assertIn("Moderate fit", self.viz_service._interpret_regression(0.4, 0.01))
        self.assertIn("Poor fit", self.viz_service._interpret_regression(0.2, 0.01))
        self.assertIn("Very poor fit", self.viz_service._interpret_regression(0.05, 0.01))
        
        # Test significance
        self.assertIn("Statistically significant", 
                      self.viz_service._interpret_regression(0.8, 0.01))
        self.assertIn("Not statistically significant", 
                      self.viz_service._interpret_regression(0.8, 0.06))