#!/bin/bash

# Finance Tracker Installation Script

echo "Installing Finance Tracker dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment (optional)
echo "Do you want to create a virtual environment? (y/n)"
read -r create_venv

if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "Virtual environment activated."
    else
        echo "Failed to create virtual environment. Continuing with system Python."
    fi
fi

# Install dependencies
echo "Installing required packages..."
pip3 install -r "$(dirname "$0")/requirements.txt"

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully!"
    echo ""
    echo "To run the Finance Tracker:"
    if [ "$create_venv" = "y" ] || [ "$create_venv" = "Y" ]; then
        echo "1. Activate the virtual environment: source venv/bin/activate"
    fi
    echo "2. Run the application: python3 run.py"
    echo ""
    echo "Or simply: streamlit run app.py"
else
    echo "Error installing dependencies. Please check the error message above."
    exit 1
fi