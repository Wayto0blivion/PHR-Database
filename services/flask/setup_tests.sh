#!/bin/bash
# Setup script for test suite installation

echo "======================================"
echo "PHR Flask Test Suite Setup"
echo "======================================"
echo ""

# Get repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$REPO_ROOT" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

echo "Repository root: $REPO_ROOT"
echo ""

# Activate virtual environment
if [ -f "$REPO_ROOT/.venv/Scripts/activate" ]; then
    echo "Activating virtual environment (Windows)..."
    source "$REPO_ROOT/.venv/Scripts/activate"
elif [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
    echo "Activating virtual environment (Unix)..."
    source "$REPO_ROOT/.venv/bin/activate"
else
    echo "Warning: Virtual environment not found at $REPO_ROOT/.venv"
    echo "Continuing with system Python..."
fi

# Install test dependencies
echo ""
echo "Installing test dependencies..."
python -m pip install -r requirements-test.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Failed to install test dependencies"
    exit 1
fi

# Setup pre-commit hook
echo ""
echo "Setting up pre-commit hook..."

# Make the hook executable
chmod +x "$REPO_ROOT/.git/hooks/pre-commit"

if [ $? -eq 0 ]; then
    echo "Pre-commit hook installed successfully"
else
    echo "Warning: Failed to setup pre-commit hook"
fi

# Run tests to verify setup
echo ""
echo "======================================"
echo "Running tests to verify setup..."
echo "======================================"
echo ""

cd "$REPO_ROOT/services/flask"
python -m pytest tests/ -v

if [ $? -ne 0 ]; then
    echo ""
    echo "======================================"
    echo "Setup completed but some tests failed"
    echo "Please review the test output above"
    echo "======================================"
    exit 1
else
    echo ""
    echo "======================================"
    echo "Setup completed successfully!"
    echo "All tests passed."
    echo "======================================"
    echo ""
    echo "The pre-commit hook is now active and will run tests"
    echo "before each commit to ensure code quality."
    echo "======================================"
fi

exit 0
