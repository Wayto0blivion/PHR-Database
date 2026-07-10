# PHR Flask Application Test Suite

This test suite ensures that all functions on the website are operational before commits are made to the repository.

## Overview

The test suite is designed to:
- ✅ Verify all routes are accessible and return expected status codes
- ✅ Test database connectivity without modifying data
- ✅ Validate form instantiation and structure
- ✅ Test helper functions and utilities
- ✅ Ensure authentication and authorization work correctly
- ✅ **READ-ONLY**: No tests modify or add data to the database

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_routes.py           # Route accessibility tests
├── test_database.py         # Database connectivity and model tests
├── test_forms.py            # Form validation tests
└── test_helper_functions.py # Utility function tests
```

## Running Tests

### Manual Test Execution

From the `services/flask` directory:

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py -v

# Run specific test file
python run_tests.py tests/test_routes.py

# Run specific test class or function
python run_tests.py -k test_login_page_loads

# Run tests matching a pattern
python run_tests.py -k "test_admin"
```

Or using pytest directly:

```bash
pytest tests/
pytest tests/test_routes.py -v
pytest tests/ -k "admin" -v
```

### Automatic Pre-Commit Testing

Tests automatically run before every Git commit. The commit will be **blocked** if any tests fail.

To bypass the pre-commit hook (not recommended):
```bash
git commit --no-verify -m "Your message"
```

## Test Categories

### Public Routes (`test_routes.py::TestPublicRoutes`)
Tests routes that don't require authentication:
- Login page
- Password generator page

### Authenticated Routes (`test_routes.py::TestAuthenticatedRoutes`)
Tests routes that require user login:
- Home page
- Profile page
- QR search

### Admin Routes (`test_routes.py::TestAdminRoutes`)
Tests routes requiring admin permissions:
- Admin dashboard
- Site map
- Server management

### PC Tech Routes (`test_routes.py::TestPCTechRoutes`)
Tests routes for PC Tech users:
- Data import
- HDD search
- SuperWiper search

### Database Tests (`test_database.py`)
Tests database connectivity and model integrity:
- Connection verification for all database engines
- Model query capabilities
- Model relationships
- Field existence validation

### Form Tests (`test_forms.py`)
Tests form instantiation and structure:
- Validation forms
- Import forms
- Search forms
- Customer entry forms

## Configuration

### pytest.ini
Configuration file for pytest behavior:
- Test discovery patterns
- Output formatting
- Warning filters
- Test markers

### conftest.py
Shared fixtures for all tests:
- `app`: Flask application instance with test config
- `client`: Test client for making requests
- `authenticated_client`: Pre-authenticated test client
- `admin_client`: Admin user test client
- `pc_tech_client`: PC Tech user test client

## Important Notes

### Read-Only Testing
All tests are **READ-ONLY**. They:
- ✅ Query existing data
- ✅ Verify connections
- ✅ Test route accessibility
- ❌ **Never** create new records
- ❌ **Never** modify existing records
- ❌ **Never** delete records

### Test Requirements
Tests require:
1. Active database connections
2. At least one active user in the database
3. Python virtual environment with all dependencies
4. Proper database credentials in `website/__init__.py`

### Expected Test Behavior
- Tests check for status codes: `200` (success), `302` (redirect), or `403` (forbidden)
- Missing permissions result in redirects, not failures
- Some tests may be skipped if specific user types don't exist

## Troubleshooting

### Tests Fail Due to Missing User
If tests fail because no users exist:
1. Create at least one active user in the database
2. For full test coverage, create users with different permission levels

### Database Connection Errors
If database tests fail:
1. Verify database servers are running
2. Check credentials in `website/__init__.py`
3. Ensure network connectivity to database servers

### Import Errors
If import errors occur:
1. Ensure you're in the correct directory: `services/flask`
2. Activate the virtual environment
3. Install test dependencies: `pip install pytest`

## Adding New Tests

When adding new functionality to the website:

1. Add route tests to `test_routes.py`
2. Add model tests to `test_database.py` if new models are created
3. Add form tests to `test_forms.py` if new forms are created
4. Ensure tests are read-only and don't modify database

Example test:
```python
def test_new_feature_accessible(self, authenticated_client):
    """Test that new feature is accessible."""
    response = authenticated_client.get('/new-feature')
    assert response.status_code in [200, 302, 403]
```

## CI/CD Integration

The pre-commit hook can be extended for CI/CD:
- GitHub Actions
- GitLab CI
- Jenkins
- Azure DevOps

Example GitHub Actions workflow would run:
```yaml
- name: Run Tests
  run: |
    cd services/flask
    python -m pytest tests/ -v
```

## Contact

For issues with the test suite, please contact the development team or open an issue in the repository.
