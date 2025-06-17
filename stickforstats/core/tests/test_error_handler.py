import unittest
from unittest.mock import patch, MagicMock, mock_open
import logging
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response

from stickforstats.core.services.error_handler import (
    ErrorHandler, safe_operation, try_except, ApiErrorResponse
)

class TestErrorHandler(TestCase):
    """Test cases for the ErrorHandler class."""
    
    def test_handle_exception_decorator(self):
        """Test that the handle_exception decorator works correctly."""
        # Create a function that will raise an exception
        @ErrorHandler.handle_exception
        def test_func():
            raise ValueError("Test error")
        
        # Mock the log_error method to avoid side effects
        with patch.object(ErrorHandler, 'log_error') as mock_log:
            # Call the function, it should return None instead of raising
            result = test_func()
            
            # Check that log_error was called with the exception
            mock_log.assert_called_once()
            self.assertIsInstance(mock_log.call_args[0][0], ValueError)
            
            # Check that the function returned None
            self.assertIsNone(result)
    
    def test_log_error(self):
        """Test that errors are logged correctly."""
        error = ValueError("Test error")
        additional_info = {"test_key": "test_value"}
        
        # Mock the logger
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Mock the file operations
            with patch('os.makedirs') as mock_makedirs, \
                 patch('builtins.open', mock_open()) as mock_file, \
                 patch('os.path.join', return_value='logs/stickforstats.log'):
                
                # Call the method
                ErrorHandler.log_error(error, additional_info)
                
                # Verify logger was called
                mock_logger.error.assert_called_once()
                
                # Verify directory was created
                mock_makedirs.assert_called_once()
                
                # Verify file was written to
                mock_file.assert_called_once_with('logs/stickforstats.log', 'a')
                handle = mock_file()
                self.assertTrue(handle.write.called)
    
    def test_get_user_friendly_message(self):
        """Test that user-friendly messages are generated correctly."""
        # Test with different error types
        tests = [
            (ValueError("Bad value"), "Invalid value"),
            (FileNotFoundError("missing.txt"), "File not found"),
            (KeyError("config"), "Missing key"),
            (Exception("Generic error"), "An error occurred")
        ]
        
        for error, expected_substring in tests:
            message = ErrorHandler.get_user_friendly_message(error)
            self.assertIn(expected_substring, message)
            self.assertIn(str(error), message)

class TestSafeOperation(TestCase):
    """Test cases for the safe_operation decorator."""
    
    def test_safe_operation(self):
        """Test that safe_operation works correctly."""
        # Create test functions
        @safe_operation
        def successful_func():
            return "Success"
        
        @safe_operation
        def failing_func():
            raise ValueError("Test error")
        
        # Test the successful function
        self.assertEqual(successful_func(), "Success")
        
        # Test the failing function
        with patch.object(ErrorHandler, 'log_error'):
            self.assertIsNone(failing_func())

class TestTryExcept(TestCase):
    """Test cases for the try_except function."""
    
    def test_try_except_success(self):
        """Test try_except with a successful function."""
        result = try_except(lambda: "Success")
        self.assertEqual(result, "Success")
    
    def test_try_except_failure(self):
        """Test try_except with a failing function."""
        default = "Default"
        
        with patch.object(ErrorHandler, 'log_error'):
            result = try_except(lambda: 1/0, default)
            self.assertEqual(result, default)
    
    def test_try_except_with_message(self):
        """Test try_except with a custom error message."""
        default = "Default"
        message = "Custom error message"
        
        with patch.object(ErrorHandler, 'log_error') as mock_log:
            result = try_except(lambda: 1/0, default, message)
            
            # Check that log_error was called with additional info
            self.assertEqual(result, default)
            mock_log.assert_called_once()
            self.assertEqual(mock_log.call_args[0][1], {'custom_message': message})

class TestApiErrorResponse(TestCase):
    """Test cases for the ApiErrorResponse class."""
    
    def test_bad_request(self):
        """Test generating a bad request response."""
        message = "Invalid input"
        response = ApiErrorResponse.bad_request(message)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], message)
    
    def test_not_found(self):
        """Test generating a not found response."""
        message = "Resource not found"
        response = ApiErrorResponse.not_found(message)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error'], message)
    
    def test_server_error(self):
        """Test generating a server error response."""
        message = "Internal server error"
        response = ApiErrorResponse.server_error(message)
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error'], message)
    
    @override_settings(DEBUG=True)
    def test_server_error_with_exception_in_debug(self):
        """Test server error with exception details in debug mode."""
        message = "Internal server error"
        exc = ValueError("Test error")
        
        with patch.object(ErrorHandler, 'log_error'):
            response = ApiErrorResponse.server_error(message, exc)
            
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json()['error'], message)
            self.assertEqual(response.json()['exception'], str(exc))
            self.assertIn('traceback', response.json())
    
    def test_validation_error(self):
        """Test generating a validation error response."""
        errors = {"field1": ["This field is required"], "field2": ["Invalid value"]}
        response = ApiErrorResponse.validation_error(errors)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Validation failed')
        self.assertEqual(response.json()['validation_errors'], errors)

class MockAPIView(APIView):
    """Mock API view for testing the API exception handler."""
    
    def get(self, request):
        # Raise an exception
        raise ValueError("Test error")

class TestApiExceptionHandler(TestCase):
    """Test the API exception handler."""
    
    def test_api_exception_handler(self):
        """Test that the API exception handler works correctly."""
        factory = APIRequestFactory()
        request = factory.get('/test/')
        view = MockAPIView.as_view()
        
        # Mock the drf_exception_handler
        with patch('stickforstats.core.services.error_handler.drf_exception_handler', 
                  return_value=None), \
             patch.object(ErrorHandler, 'log_error'):
            
            # This should use our exception handler
            response = view(request)
            
            # Check the response
            self.assertEqual(response.status_code, 500)
            self.assertIn('error', response.data)
            self.assertIn('detail', response.data)
            self.assertIn('type', response.data)