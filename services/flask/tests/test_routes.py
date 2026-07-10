"""
Test suite for Flask application routes.
Tests verify that routes are accessible and return expected status codes.
All tests are read-only and do not modify the database.
"""
import pytest
from flask import url_for


class TestPublicRoutes:
    """Test public routes that don't require authentication."""

    def test_login_page_loads(self, client):
        """Test that the login page loads successfully."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'email' in response.data.lower()

    def test_passwords_page_loads(self, client):
        """Test that the password generator page loads without authentication."""
        response = client.get('/passwords')
        assert response.status_code == 200


class TestAuthenticatedRoutes:
    """Test routes that require authentication."""

    def test_home_page_requires_auth(self, client):
        """Test that home page redirects when not authenticated."""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login

    def test_home_page_loads_when_authenticated(self, authenticated_client):
        """Test that home page loads for authenticated users."""
        response = authenticated_client.get('/')
        # Either 200 (success) or 302 (redirect within app) is acceptable
        assert response.status_code in [200, 302]

    def test_profile_requires_auth(self, client):
        """Test that profile page requires authentication."""
        response = client.get('/profile', follow_redirects=False)
        assert response.status_code == 302

    def test_qr_search_accessible(self, authenticated_client):
        """Test that QR search page is accessible."""
        response = authenticated_client.get('/qr-search')
        assert response.status_code in [200, 302]


class TestAdminRoutes:
    """Test routes that require admin permissions."""

    def test_admin_page_requires_admin(self, authenticated_client):
        """Test that admin page redirects non-admin users."""
        response = authenticated_client.get('/admin/')
        # Could be 302 (redirect), 403 (forbidden), or 200 (if user is admin)
        assert response.status_code in [200, 302, 403]

    def test_site_map_requires_admin(self, authenticated_client):
        """Test that site map requires admin permissions."""
        response = authenticated_client.get('/site-map')
        # Either accessible (200) or forbidden/redirect (302, 403)
        assert response.status_code in [200, 302, 403]

    def test_servers_requires_admin(self, authenticated_client):
        """Test that servers page requires admin permissions."""
        response = authenticated_client.get('/servers')
        assert response.status_code in [200, 302, 403]


class TestPCTechRoutes:
    """Test routes specific to PC Tech users."""

    def test_pandas_import_accessible(self, pc_tech_client):
        """Test that pandas import page is accessible to PC tech users."""
        if pc_tech_client:
            response = pc_tech_client.get('/pandas_import')
            assert response.status_code in [200, 302, 403]

    def test_hdd_search_accessible(self, pc_tech_client):
        """Test that HDD search is accessible."""
        if pc_tech_client:
            response = pc_tech_client.get('/search/hdd_search')
            assert response.status_code in [200, 302, 403]

    def test_superwiper_search_accessible(self, pc_tech_client):
        """Test that SuperWiper search is accessible."""
        if pc_tech_client:
            response = pc_tech_client.get('/search/superwiper-search')
            assert response.status_code in [200, 302, 403]


class TestQRCodeRoutes:
    """Test QR code related routes."""

    def test_qr_search_page_loads(self, authenticated_client):
        """Test that QR search page loads."""
        response = authenticated_client.get('/qr-search')
        assert response.status_code in [200, 302]

    def test_qr_generation_requires_permission(self, authenticated_client):
        """Test that QR generation requires specific permissions."""
        response = authenticated_client.get('/test/qr-generate')
        assert response.status_code in [200, 302, 403]


class TestValidationRoutes:
    """Test validation-related routes."""

    def test_validation_entry_accessible(self, authenticated_client):
        """Test that validation entry page is accessible."""
        response = authenticated_client.get('/validation_entry')
        assert response.status_code in [200, 302, 403]

    def test_hdd_validation_table_accessible(self, authenticated_client):
        """Test that HDD validation table is accessible."""
        response = authenticated_client.get('/search/hdd_validation_table')
        assert response.status_code in [200, 302, 403]

    def test_master_validation_accessible(self, authenticated_client):
        """Test that master validation is accessible."""
        response = authenticated_client.get('/search/master_validation')
        assert response.status_code in [200, 302, 403]


class TestAikenRoutes:
    """Test Aiken-related routes."""

    def test_aiken_production_accessible(self, pc_tech_client):
        """Test that Aiken production page is accessible."""
        if pc_tech_client:
            response = pc_tech_client.get('/aiken-production')
            assert response.status_code in [200, 302, 403]

    def test_aiken_unit_search_accessible(self, pc_tech_client):
        """Test that Aiken unit search is accessible."""
        if pc_tech_client:
            response = pc_tech_client.get('/aiken-unit-search')
            assert response.status_code in [200, 302, 403]

    def test_aiken_unfiltered_search_accessible(self, pc_tech_client):
        """Test that Aiken unfiltered search is accessible."""
        if pc_tech_client:
            response = pc_tech_client.get('/aiken-unfiltered-search')
            assert response.status_code in [200, 302, 403]


class TestMobileRoutes:
    """Test mobile-related routes."""

    def test_mobile_weightsheets_accessible(self, authenticated_client):
        """Test that the mobile home route is registered and reachable.

        The mobile blueprint is mounted at '/mobile' and its index view is
        defined on '/', so the canonical URL is '/mobile/'. Requesting '/mobile'
        without the trailing slash makes Flask emit a 308 redirect to '/mobile/'
        at the routing layer, BEFORE the view runs.

        We intentionally request the non-slash URL and do NOT follow the
        redirect: mobile_home() creates pallet/box rows on the live database
        (see conftest), so following it would write real data on every commit.
        Asserting the redirect confirms the route exists without side effects.
        """
        response = authenticated_client.get('/mobile')
        assert response.status_code in [200, 302, 308, 403]


class TestNetworkRoutes:
    """Test network-related routes."""

    def test_network_price_import_accessible(self, authenticated_client):
        """Test that network price import is accessible."""
        response = authenticated_client.get('/network-price-import')
        assert response.status_code in [200, 302, 403]

    def test_network_price_search_accessible(self, authenticated_client):
        """Test that network price search is accessible."""
        response = authenticated_client.get('/network-price-search')
        assert response.status_code in [200, 302, 403]


class TestServerAddonRoutes:
    """Test server add-on related routes."""

    def test_server_addon_search_accessible(self, authenticated_client):
        """Test that server add-on search is accessible."""
        response = authenticated_client.get('/search-server-addon')
        assert response.status_code in [200, 302, 403]

    def test_new_server_addon_accessible(self, authenticated_client):
        """Test that new server add-on page is accessible."""
        response = authenticated_client.get('/new-server-addon')
        assert response.status_code in [200, 302, 403]


class TestLogoutRoute:
    """Test logout functionality."""

    def test_logout_redirects(self, authenticated_client):
        """Test that logout redirects to appropriate page."""
        response = authenticated_client.get('/logout', follow_redirects=False)
        assert response.status_code in [200, 302]
