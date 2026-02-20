#!/bin/bash
echo "Stopping Streamlit..."
pkill -f "streamlit run" 2>/dev/null
sleep 1

echo "Clearing all caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
rm -rf .streamlit/cache 2>/dev/null
rm -rf ~/.streamlit/cache 2>/dev/null

echo "Starting Streamlit..."
streamlit run finance_tracker.py --server.port 8501 --server.headless true
