#!/bin/bash
# Automated smoke test runner script

echo "🚀 Finance Tracker - Automated Smoke Tests"
echo "=========================================="

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3."
    exit 1
fi

# Run the smoke tests
echo "Running smoke tests..."
python3 tests/smoke_test.py

# Capture exit code
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! Your application is ready to deploy."
    echo ""
    echo "Next steps:"
    echo "1. Start the app: streamlit run app.py"
    echo "2. Test manually if needed"
    echo "3. Deploy with confidence!"
else
    echo ""
    echo "⚠️  Some tests failed. Please fix the issues before deploying."
    echo ""
    echo "To debug:"
    echo "1. Check the error messages above"
    echo "2. Fix the failing components"
    echo "3. Run tests again: ./run_tests.sh"
fi

exit $exit_code