"""Basic tests for the core module."""

from django.test import TestCase


class BasicTest(TestCase):
    """Basic test case to verify that the testing framework works."""
    
    def test_basic(self):
        """Basic test to verify that tests are working."""
        self.assertEqual(1 + 1, 2)