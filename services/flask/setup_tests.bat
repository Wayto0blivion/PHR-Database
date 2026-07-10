@echo off
REM Setup script for test suite installation

echo ======================================
echo PHR Flask Test Suite Setup
echo ======================================
echo.

REM Get repository root
for /f "delims=" %%i in ('git rev-parse --show-toplevel 2^>nul') do set REPO_ROOT=%%i

if "%REPO_ROOT%"=="" (
    echo Error: Not in a git repository
    exit /b 1
)

echo Repository root: %REPO_ROOT%
echo.

REM Activate virtual environment
if exist "%REPO_ROOT%\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%REPO_ROOT%\.venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found at %REPO_ROOT%\.venv
    echo Continuing with system Python...
)

REM Install test dependencies
echo.
echo Installing test dependencies...
python -m pip install -r requirements-test.txt

if errorlevel 1 (
    echo.
    echo Error: Failed to install test dependencies
    exit /b 1
)

REM Setup pre-commit hook
echo.
echo Setting up pre-commit hook...

REM Copy the Windows batch version of the hook
copy /Y "%REPO_ROOT%\.git\hooks\pre-commit.bat" "%REPO_ROOT%\.git\hooks\pre-commit" >nul

if errorlevel 1 (
    echo Warning: Failed to setup pre-commit hook
) else (
    echo Pre-commit hook installed successfully
)

REM Run tests to verify setup
echo.
echo ======================================
echo Running tests to verify setup...
echo ======================================
echo.

cd /d "%REPO_ROOT%\services\flask"
python -m pytest tests/ -v

if errorlevel 1 (
    echo.
    echo ======================================
    echo Setup completed but some tests failed
    echo Please review the test output above
    echo ======================================
    exit /b 1
) else (
    echo.
    echo ======================================
    echo Setup completed successfully!
    echo All tests passed.
    echo ======================================
    echo.
    echo The pre-commit hook is now active and will run tests
    echo before each commit to ensure code quality.
    echo ======================================
)

exit /b 0
