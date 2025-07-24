#!/bin/bash

# Run the Finance Tracker application
echo "Starting Finance Tracker..."

# Try running with streamlit command first
if command -v streamlit &> /dev/null; then
    echo "Running with streamlit command..."
    streamlit run finance_tracker.py
    exit $?
fi

# If streamlit command not found, try with python3
if command -v python3 &> /dev/null; then
    echo "Running with python3..."
    python3 -m streamlit run finance_tracker.py
    exit $?
fi

# If python3 not found, try with python
if command -v python &> /dev/null; then
    echo "Running with python..."
    python -m streamlit run finance_tracker.py
    exit $?
fi

echo "Error: Could not find python3, python, or streamlit commands."
echo "Please install Python 3 and Streamlit:"
echo "  brew install python3  # Install Python 3"
echo "  pip3 install streamlit  # Install Streamlit"
exit 1