import unittest
from unittest.mock import patch, MagicMock
import os
import json
import pandas as pd
from pathlib import Path
from django.test import TestCase
from django.conf import settings

from stickforstats.core.services.session.session_service import SessionService

class TestSessionService(TestCase):
    """Test cases for the SessionService."""
    
    def setUp(self):
        """Set up test data."""
        self.session_service = SessionService()
        self.test_username = "test_user"
        self.test_data = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        self.test_params = {'param1': 'value1', 'param2': 'value2'}
        self.test_results = {'metric1': 0.95, 'metric2': 0.85}
        self.test_plots = [
            {
                'title': 'Test Plot',
                'description': 'A test plot',
                'type': 'scatter',
                'plot_data': {'data': [{'x': [1, 2, 3], 'y': [4, 5, 6]}]}
            }
        ]
        
    def tearDown(self):
        """Clean up test data."""
        # Remove test directories if they exist
        test_dirs = [
            os.path.join(settings.BASE_DIR, "data", "analysis_history", self.test_username),
            os.path.join(settings.BASE_DIR, "data", "plots", self.test_username)
        ]
        for directory in test_dirs:
            if os.path.exists(directory):
                import shutil
                shutil.rmtree(directory)
    
    def test_ensure_storage_directories(self):
        """Test that storage directories are created correctly."""
        # Check that directories exist
        directories = [
            os.path.join(settings.BASE_DIR, "data", "user_sessions"),
            os.path.join(settings.BASE_DIR, "data", "analysis_history"),
            os.path.join(settings.BASE_DIR, "data", "plots"),
            os.path.join(settings.BASE_DIR, "data", "reports")
        ]
        
        for directory in directories:
            self.assertTrue(os.path.exists(directory))
    
    def test_save_and_get_analysis_result(self):
        """Test saving and retrieving analysis results."""
        # Save analysis result
        result = self.session_service.save_analysis_result(
            username=self.test_username,
            analysis_type="test_analysis",
            data=self.test_data,
            parameters=self.test_params,
            results=self.test_results,
            plots=self.test_plots
        )
        self.assertTrue(result)
        
        # Check that history file exists
        history_file = os.path.join(
            settings.BASE_DIR, "data", "analysis_history", 
            self.test_username, "history.json"
        )
        self.assertTrue(os.path.exists(history_file))
        
        # Get history
        history = self.session_service.get_user_history(self.test_username)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['analysis_type'], "test_analysis")
        self.assertEqual(history[0]['parameters'], self.test_params)
        
        # Check plots
        self.assertEqual(len(history[0]['plots']), 1)
        self.assertEqual(history[0]['plots'][0]['title'], 'Test Plot')
        
    def test_clear_user_history(self):
        """Test clearing user history."""
        # Save analysis result first
        self.session_service.save_analysis_result(
            username=self.test_username,
            analysis_type="test_analysis",
            data=self.test_data,
            parameters=self.test_params,
            results=self.test_results
        )
        
        # Verify history exists
        history = self.session_service.get_user_history(self.test_username)
        self.assertEqual(len(history), 1)
        
        # Clear history
        result = self.session_service.clear_user_history(self.test_username)
        self.assertTrue(result)
        
        # Verify history is cleared
        history = self.session_service.get_user_history(self.test_username)
        self.assertEqual(len(history), 0)
        
    def test_get_analysis_statistics(self):
        """Test getting analysis statistics."""
        # Save multiple analysis results
        self.session_service.save_analysis_result(
            username=self.test_username,
            analysis_type="test_analysis1",
            data=self.test_data,
            parameters=self.test_params,
            results=self.test_results,
            plots=self.test_plots
        )
        
        self.session_service.save_analysis_result(
            username=self.test_username,
            analysis_type="test_analysis2",
            data=self.test_data,
            parameters=self.test_params,
            results=self.test_results
        )
        
        # Get statistics
        stats = self.session_service.get_analysis_statistics(self.test_username)
        
        # Verify statistics
        self.assertEqual(stats['total_analyses'], 2)
        self.assertEqual(set(stats['unique_analysis_types']), {'test_analysis1', 'test_analysis2'})
        self.assertEqual(stats['total_plots'], 1)
        self.assertIsNotNone(stats['latest_analysis'])
        
    def test_prepare_results_for_storage(self):
        """Test preparing results for storage."""
        # Create results with non-serializable objects
        results = {
            'model': MagicMock(),  # Non-serializable object
            'metric': 0.95,  # Serializable
            'nested': {
                'trace': MagicMock(),  # Non-serializable object
                'value': 42  # Serializable
            },
            'array': pd.Series([1, 2, 3])  # Pandas object
        }
        
        # Prepare results
        clean_results = self.session_service._prepare_results_for_storage(results)
        
        # Verify serializable fields
        self.assertIn('metric', clean_results)
        self.assertEqual(clean_results['metric'], 0.95)
        
        # Verify nested serializable fields
        self.assertIn('nested', clean_results)
        self.assertIn('value', clean_results['nested'])
        self.assertEqual(clean_results['nested']['value'], 42)
        
        # Verify non-serializable fields are removed
        self.assertNotIn('model', clean_results)
        self.assertNotIn('trace', clean_results['nested'])
        
        # Verify pandas objects are converted
        self.assertIn('array', clean_results)
        self.assertIsInstance(clean_results['array'], list)
        
    def test_export_analysis_data(self):
        """Test exporting analysis data."""
        # Save analysis result
        self.session_service.save_analysis_result(
            username=self.test_username,
            analysis_type="test_analysis",
            data=self.test_data,
            parameters=self.test_params,
            results=self.test_results,
            plots=self.test_plots
        )
        
        # Get history to extract analysis ID
        history = self.session_service.get_user_history(self.test_username)
        analysis_id = history[0]['id']
        
        # Test JSON export
        data, filename = self.session_service.export_analysis_data(
            self.test_username, analysis_id, format='json'
        )
        self.assertIsNotNone(data)
        self.assertTrue(filename.endswith('.json'))
        
        # Test CSV export
        data, filename = self.session_service.export_analysis_data(
            self.test_username, analysis_id, format='csv'
        )
        self.assertIsNotNone(data)
        self.assertTrue(filename.endswith('.csv'))
        
        # Test with non-existent analysis
        data, filename = self.session_service.export_analysis_data(
            self.test_username, 'non-existent-id'
        )
        self.assertIsNone(data)
        self.assertEqual(filename, '')