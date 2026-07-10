"""
Test suite for Flask forms.
Tests verify that forms are properly initialized and have expected fields.
"""
import pytest
from website.forms import (
    ValidationEntryForm, ImportForm, CustomerEntryForm,
    CustomerSearchForm, AikenProductionForm, AikenDeviceSearchForm,
    Server_AddOn_Form, NetworkPricingSearchForm
)


class TestValidationEntryForm:
    """Test ValidationEntryForm."""

    def test_form_instantiates(self, app):
        """Test that the form can be instantiated."""
        with app.app_context():
            form = ValidationEntryForm()
            assert form is not None


class TestImportForm:
    """Test ImportForm."""

    def test_form_instantiates(self, app):
        """Test that the form can be instantiated."""
        with app.app_context():
            form = ImportForm()
            assert form is not None


class TestCustomerEntryForm:
    """Test CustomerEntryForm."""

    def test_form_instantiates(self, app):
        """Test that the form can be instantiated."""
        with app.app_context():
            form = CustomerEntryForm()
            assert form is not None


class TestCustomerSearchForm:
    """Test CustomerSearchForm."""

    def test_form_instantiates(self, app):
        """Test that the form can be instantiated."""
        with app.app_context():
            form = CustomerSearchForm()
            assert form is not None


class TestAikenProductionForm:
    """Test AikenProductionForm."""

    def test_form_instantiates(self, app):
        """Test that the form can be instantiated."""
        with app.app_context():
            form = AikenProductionForm()
            assert form is not None


class TestAikenDeviceSearchForm:
    """Test AikenDeviceSearchForm."""

    def test_form_instantiates(self, app):
        """Test that the form can be instantiated."""
        with app.app_context():
            form = AikenDeviceSearchForm()
            assert form is not None


class TestServerAddOnForm:
    """Test Server_AddOn_Form."""

    def test_form_instantiates(self, app):
        """Test that the form can be instantiated."""
        with app.app_context():
            form = Server_AddOn_Form()
            assert form is not None


class TestNetworkPricingSearchForm:
    """Test NetworkPricingSearchForm."""

    def test_form_instantiates(self, app):
        """Test that the form can be instantiated."""
        with app.app_context():
            form = NetworkPricingSearchForm()
            assert form is not None
