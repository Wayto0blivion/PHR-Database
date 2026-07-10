"""
Test suite for helper functions.
Tests verify utility functions work correctly.
"""
import pytest
from website import helper_functions as hf


class TestHelperFunctions:
    """Test helper function utilities."""

    def test_helper_functions_module_exists(self):
        """Test that helper functions module is importable."""
        assert hf is not None

    def test_user_permissions_decorator_exists(self):
        """Test that user_permissions decorator exists."""
        assert hasattr(hf, 'user_permissions')
        assert callable(hf.user_permissions)
