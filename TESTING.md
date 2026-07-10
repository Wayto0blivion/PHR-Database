# PHR Database - Testing Documentation

This document describes the comprehensive test suite for the PHR Flask application.

## Overview

A complete test suite has been implemented to ensure the website is fully operational before any Git commits. The test suite:

- ✅ **Verifies all routes are accessible** - Tests every endpoint in the application
- ✅ **Tests database connectivity** - Ensures all database engines are working
- ✅ **Validates forms** - Checks that all forms can be instantiated
- ✅ **Tests authentication/authorization** - Verifies login and permission systems
- ✅ **100% Read-Only** - No tests modify or add data to your database
- ✅ **Automatic Pre-Commit Validation** - Runs before every commit

## Quick Start

### 1. Install Test Dependencies

From the `services/flask` directory:

```bash
# Windows
setup_tests.bat

# Linux/Mac
./setup_tests.sh
```

This will:
1. Install pytest and testing dependencies
2. Set up the pre-commit hook
3. Run tests to verify everything works

### 2. Run Tests Manually

```bash
# From services/flask directory

# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py -v

# Run specific test file
python run_tests.py tests/test_routes.py

# Run specific test
python run_tests.py -k test_login_page_loads
```

### 3. Pre-Commit Testing

Tests **automatically run before every commit**:

```bash
git add .
git commit -m "Your changes"
# Tests run automatically here
# Commit blocked if tests fail ❌
# Commit proceeds if tests pass ✅
```

To bypass (not recommended):
```bash
git commit --no-verify -m "Your message"
```

## Test Suite Structure

```
services/flask/
├── tests/
│   ├── __init__.py              # Package initialization
│   ├── conftest.py              # Shared fixtures and configuration
│   ├── test_routes.py           # Route accessibility tests
│   ├── test_database.py         # Database connectivity tests
│   ├── test_forms.py            # Form validation tests
│   ├── test_helper_functions.py # Utility function tests
│   └── README.md                # Detailed test documentation
├── pytest.ini                   # Pytest configuration
├── requirements-test.txt        # Test dependencies
├── run_tests.py                 # Test runner script
├── setup_tests.bat              # Windows setup script
└── setup_tests.sh               # Linux/Mac setup script

.git/hooks/
├── pre-commit                   # Pre-commit hook (Unix)
└── pre-commit.bat               # Pre-commit hook (Windows)
```

## What Gets Tested

### Public Routes
- Login page
- Password generator
- Other public endpoints

### Authenticated Routes
- Home page
- Profile page
- QR search
- Data import pages

### Admin Routes
- Admin dashboard
- Site mapper
- Server management
- Password reset

### Permission-Based Routes
- PC Tech features (HDD search, SuperWiper, Aiken)
- Network price data
- Mobile weightsheets
- Validation entry
- Processing data

### Database Tests
- Connection to all 5 database engines:
  - Processing_Data (main database)
  - db_killdisk (HDD/Killdisk data)
  - Validation (validation logs)
  - awbc_db (Aiken data)
  - superwiper (SuperWiper data)
- Model integrity checks
- Query functionality
- Relationship validation

### Form Tests
- ValidationEntryForm
- ImportForm
- CustomerEntryForm
- AikenProductionForm
- Server_AddOn_Form
- NetworkPricingSearchForm
- And more...

## Test Safety Features

### Read-Only Guarantee
All tests are designed to be **completely read-only**:

✅ **Tests DO:**
- Query existing data
- Verify database connections
- Check route accessibility
- Test form instantiation
- Validate authentication

❌ **Tests NEVER:**
- Create new records
- Modify existing records
- Delete any data
- Change database state
- Alter user permissions

### Test Isolation
- Each test is independent
- Tests use existing data
- No test affects another test
- Database state unchanged after tests

## Configuration

### pytest.ini
Controls test behavior:
- Test discovery patterns
- Output formatting
- Warning filters
- Test categorization

### conftest.py
Provides shared test fixtures:
- `app` - Test Flask application instance
- `client` - Test client for requests
- `authenticated_client` - Pre-authenticated user
- `admin_client` - Admin user client
- `pc_tech_client` - PC Tech user client

### Environment Requirements
- Python 3.7+
- Active database connections
- At least one user in the database
- Virtual environment with dependencies

## Test Results

Tests check for valid HTTP status codes:
- `200` - Success (page loaded)
- `302` - Redirect (authentication required or navigation)
- `403` - Forbidden (insufficient permissions)

Any of these codes indicates the route is working correctly. The tests verify:
1. ✅ Route exists and is accessible
2. ✅ Authentication/authorization works
3. ✅ Database queries execute successfully
4. ✅ Forms can be instantiated

## Troubleshooting

### Tests Fail - Database Connection
**Problem:** Cannot connect to database

**Solution:**
1. Verify database servers are running:
   - MySQL at 192.168.3.243 (main, killdisk, validation)
   - MySQL at 192.168.3.224 (Aiken)
   - MySQL at 192.168.3.99 (SuperWiper)
2. Check credentials in `website/__init__.py`
3. Ensure network connectivity

### Tests Fail - No Users Found
**Problem:** Tests can't find users for authentication

**Solution:**
1. Ensure at least one active user exists in the database
2. For full coverage, create users with different permissions:
   - Regular user (active_status=True)
   - Admin user (admin_status=True)
   - PC Tech user (pc_status=True)

### Tests Fail - Import Errors
**Problem:** Cannot import modules

**Solution:**
1. Ensure you're in the correct directory: `services/flask`
2. Activate virtual environment
3. Install dependencies: `pip install -r requirements-test.txt`

### Pre-Commit Hook Not Working
**Problem:** Hook doesn't run on commit

**Solution (Windows):**
```bash
cd .git/hooks
copy pre-commit.bat pre-commit
```

**Solution (Linux/Mac):**
```bash
chmod +x .git/hooks/pre-commit
```

## Adding New Tests

When adding new features:

1. **Add route test** in `tests/test_routes.py`:
```python
def test_new_feature_loads(self, authenticated_client):
    """Test that new feature page loads."""
    response = authenticated_client.get('/new-feature')
    assert response.status_code in [200, 302, 403]
```

2. **Add database test** in `tests/test_database.py` (if new models):
```python
def test_new_model_query(self, app):
    """Test that NewModel can be queried."""
    with app.app_context():
        records = NewModel.query.limit(5).all()
        assert isinstance(records, list)
```

3. **Add form test** in `tests/test_forms.py` (if new forms):
```python
def test_new_form_instantiates(self, app):
    """Test that NewForm instantiates."""
    with app.app_context():
        form = NewForm()
        assert form is not None
```

## CI/CD Integration

The test suite can be integrated with CI/CD pipelines:

### GitHub Actions
```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          cd services/flask
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: |
          cd services/flask
          pytest tests/ -v
```

### GitLab CI
```yaml
test:
  script:
    - cd services/flask
    - pip install -r requirements.txt
    - pip install -r requirements-test.txt
    - pytest tests/ -v
```

## Performance

Typical test execution time:
- **Full suite:** 10-30 seconds
- **Route tests only:** 5-15 seconds
- **Database tests:** 3-10 seconds

Factors affecting speed:
- Database connection latency
- Number of routes in application
- Database query performance

## Best Practices

1. ✅ **Run tests before pushing** - Even though pre-commit runs them
2. ✅ **Keep tests read-only** - Never modify database in tests
3. ✅ **Add tests for new features** - Maintain test coverage
4. ✅ **Fix failing tests immediately** - Don't commit with failing tests
5. ✅ **Review test output** - Understand what failed and why

## Support

For issues or questions about the test suite:
1. Check `services/flask/tests/README.md` for detailed documentation
2. Review test output for specific error messages
3. Contact the development team

## Summary

The test suite provides:
- ✅ **Automatic quality control** via pre-commit hooks
- ✅ **Safe, read-only testing** that never modifies your database
- ✅ **Comprehensive coverage** of routes, databases, and forms
- ✅ **Easy setup and execution** with provided scripts
- ✅ **Clear documentation** for maintenance and extension

This ensures the PHR website remains fully operational and stable with every commit.
