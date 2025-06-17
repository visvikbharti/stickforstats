import io
import json
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from datetime import datetime
from uuid import uuid4

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from stickforstats.mainapp.services.report.report_generator_service import ReportGeneratorService
from stickforstats.mainapp.models.analysis import AnalysisResult

User = get_user_model()


class ReportGeneratorServiceTestCase(TestCase):
    """
    Test cases for the ReportGeneratorService.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create mock analysis results
        self.mock_analyses = [
            AnalysisResult(
                id=uuid4(),
                user=self.test_user,
                title="Test Analysis 1",
                analysis_type="descriptive_statistics",
                results=json.dumps({
                    "mean": 10.5,
                    "median": 9.8,
                    "std": 2.3
                }),
                created_at=datetime.now()
            ),
            AnalysisResult(
                id=uuid4(),
                user=self.test_user,
                title="Test Analysis 2",
                analysis_type="hypothesis_test",
                results=json.dumps({
                    "p_value": 0.032,
                    "t_statistic": 2.15,
                    "degrees_of_freedom": 28
                }),
                created_at=datetime.now()
            )
        ]
        
        # Initialize the service
        self.report_service = ReportGeneratorService()
    
    @patch('stickforstats.mainapp.services.report.report_generator_service.html_to_pdf')
    def test_generate_pdf_report(self, mock_html_to_pdf):
        """Test generating a PDF report."""
        # Mock the PDF conversion
        mock_pdf_data = b"PDF_DATA"
        mock_pdf_buffer = io.BytesIO(mock_pdf_data)
        mock_html_to_pdf.return_value = mock_pdf_buffer
        
        # Call the service
        report_info, report_buffer = self.report_service.generate_report_from_analyses(
            user_id=str(self.test_user.id),
            analyses=self.mock_analyses,
            title="Test Report",
            description="Test report description",
            report_format='pdf',
            include_visualizations=True,
            include_raw_data=False
        )
        
        # Verify results
        self.assertEqual(report_info['title'], "Test Report")
        self.assertEqual(report_info['format'], "pdf")
        self.assertEqual(report_info['analysis_count'], 2)
        self.assertEqual(report_buffer.getvalue(), mock_pdf_data)
        
        # Verify HTML was generated and converted to PDF
        mock_html_to_pdf.assert_called_once()
    
    def test_generate_html_report(self):
        """Test generating an HTML report."""
        # Call the service
        report_info, report_buffer = self.report_service.generate_report_from_analyses(
            user_id=str(self.test_user.id),
            analyses=self.mock_analyses,
            title="HTML Report",
            report_format='html',
            include_visualizations=True,
            include_raw_data=True
        )
        
        # Verify results
        self.assertEqual(report_info['title'], "HTML Report")
        self.assertEqual(report_info['format'], "html")
        self.assertEqual(report_info['analysis_count'], 2)
        
        # Verify HTML content
        html_content = report_buffer.getvalue().decode('utf-8')
        self.assertIn("HTML Report", html_content)
        self.assertIn("Test Analysis 1", html_content)
        self.assertIn("Test Analysis 2", html_content)
        self.assertIn("descriptive_statistics", html_content)
        self.assertIn("hypothesis_test", html_content)
    
    @patch('stickforstats.mainapp.services.report.report_generator_service.convert_html_to_docx')
    def test_generate_docx_report(self, mock_convert_html_to_docx):
        """Test generating a DOCX report."""
        # Mock the DOCX conversion
        mock_docx_data = b"DOCX_DATA"
        mock_docx_buffer = io.BytesIO(mock_docx_data)
        mock_convert_html_to_docx.return_value = mock_docx_buffer
        
        # Call the service
        report_info, report_buffer = self.report_service.generate_report_from_analyses(
            user_id=str(self.test_user.id),
            analyses=self.mock_analyses,
            title="DOCX Report",
            report_format='docx',
            include_visualizations=False,
            include_raw_data=False
        )
        
        # Verify results
        self.assertEqual(report_info['title'], "DOCX Report")
        self.assertEqual(report_info['format'], "docx")
        self.assertEqual(report_info['analysis_count'], 2)
        self.assertEqual(report_buffer.getvalue(), mock_docx_data)
        
        # Verify HTML was generated and converted to DOCX
        mock_convert_html_to_docx.assert_called_once()
    
    def test_unsupported_format(self):
        """Test handling of unsupported report formats."""
        with self.assertRaises(ValueError):
            self.report_service.generate_report_from_analyses(
                user_id=str(self.test_user.id),
                analyses=self.mock_analyses,
                title="Invalid Format Report",
                report_format='excel',  # Unsupported format
                include_visualizations=True,
                include_raw_data=False
            )
    
    @patch('stickforstats.mainapp.services.report.report_generator_service.ReportGeneratorService._generate_html_content')
    def test_empty_analyses(self, mock_generate_html):
        """Test handling of empty analyses list."""
        # Call the service with empty analyses
        with self.assertRaises(ValueError):
            self.report_service.generate_report_from_analyses(
                user_id=str(self.test_user.id),
                analyses=[],  # Empty list
                title="Empty Analyses Report",
                report_format='pdf',
                include_visualizations=True,
                include_raw_data=False
            )
        
        # Verify HTML generation was not called
        mock_generate_html.assert_not_called()
    
    def test_report_customization(self):
        """Test report customization options."""
        # Test with custom title and description
        report_info, _ = self.report_service.generate_report_from_analyses(
            user_id=str(self.test_user.id),
            analyses=self.mock_analyses,
            title="Custom Title",
            description="Custom description for testing",
            report_format='html',
            include_visualizations=True,
            include_raw_data=False
        )
        
        self.assertEqual(report_info['title'], "Custom Title")
        self.assertEqual(report_info['description'], "Custom description for testing")
        
        # Test with default title (no description)
        report_info, _ = self.report_service.generate_report_from_analyses(
            user_id=str(self.test_user.id),
            analyses=self.mock_analyses,
            report_format='html',
            include_visualizations=True,
            include_raw_data=False
        )
        
        self.assertEqual(report_info['title'], "Statistical Analysis Report")
        self.assertIsNone(report_info['description'])


if __name__ == '__main__':
    unittest.main()