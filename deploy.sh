#!/bin/bash
set -euo pipefail
# Deployment script for Finance Tracker

echo "🚀 Deploying Finance Tracker..."

# Run tests first (gracefully skip if no test suite is available)
echo "1. Running tests..."
if command -v python3 >/dev/null 2>&1; then
    if [ -f "run_tests.py" ]; then
        python3 run_tests.py || TEST_EXIT=$?
    elif command -v pytest >/dev/null 2>&1 && [ -d "tests" ]; then
        pytest || TEST_EXIT=$?
    else
        echo "ℹ️ No automated tests detected. Skipping test step."
        TEST_EXIT=0
    fi
else
    echo "⚠️ python3 is not available. Skipping tests."
    TEST_EXIT=0
fi

if [ "${TEST_EXIT:-0}" -ne 0 ]; then
    echo "❌ Tests failed. Deployment aborted."
    exit 1
fi

# Install dependencies
echo "2. Installing dependencies..."
pip install -r requirements.txt
echo "   Installing dev dependencies..."
pip install -r requirements-dev.txt

# Initialize database
echo "3. Initializing database..."
python3 -c "
from services.database_service import DatabaseService
from services.auth_service import AuthService
DatabaseService.initialize_database()
AuthService.initialize_auth_database()
print('✅ Database initialized')
"

# Start the application
echo "4. Starting Finance Tracker..."
streamlit run finance_tracker.py --server.headless false --server.port 8501
