#!/bin/bash
# Deployment script for Finance Tracker

echo "🚀 Deploying Finance Tracker..."

# Run tests first
echo "1. Running tests..."
python3 run_tests.py
if [ $? -ne 0 ]; then
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