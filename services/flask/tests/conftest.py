"""
Test configuration and fixtures for Flask application tests.
This file provides shared fixtures and test configurations.
"""
import pytest
from website import create_app, db
from website.models import User


@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application instance."""
    app = create_app()

    # Override database configuration for testing
    # Using the same database but in read-only mode to prevent modifications
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'LOGIN_DISABLED': False,
    })

    yield app


@pytest.fixture(scope='session')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope='session')
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def authenticated_client(client, app):
    """
    Create an authenticated test client.
    This fixture logs in a test user for protected routes.
    """
    with app.app_context():
        # Query for an existing user (don't create new ones to avoid DB modifications)
        user = User.query.filter_by(active_status=True).first()

        if user:
            # Simulate login by setting up the session
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

    return client


@pytest.fixture(scope='function')
def admin_client(client, app):
    """
    Create an authenticated admin test client.
    This fixture logs in an admin user for admin-only routes.
    """
    with app.app_context():
        # Query for an existing admin user
        user = User.query.filter_by(admin_status=True, active_status=True).first()

        if user:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

    return client


@pytest.fixture(scope='function')
def pc_tech_client(client, app):
    """
    Create an authenticated PC Tech user test client.
    """
    with app.app_context():
        user = User.query.filter_by(pc_status=True, active_status=True).first()

        if user:
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True

    return client
