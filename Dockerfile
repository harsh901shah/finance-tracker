# Finance Tracker – production-ready Docker image for hosting
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (exclude dev/test artifacts via .dockerignore if present)
COPY . .

# Create logs directory; /data is the default volume mount for persistent DB
RUN mkdir -p logs

# Override at run time: -e FINANCE_TRACKER_DB_PATH=/data/finance_tracker.db
ENV FINANCE_TRACKER_DB_PATH=/data/finance_tracker.db

EXPOSE 8501

# Bind to 0.0.0.0 so the app is reachable from outside the container
CMD ["streamlit", "run", "finance_tracker.py", "--server.port=8501", "--server.address=0.0.0.0"]
