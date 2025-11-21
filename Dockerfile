FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create backend directory
RUN mkdir -p /app/backend

# Copy requirements first for better caching (requirements.txt is in root)
COPY requirements.txt /app/backend/requirements.txt

# Create virtual environment and install dependencies
# Use absolute paths to avoid activation issues
WORKDIR /app/backend
RUN python3 -m venv venv && \
    /app/backend/venv/bin/pip install --upgrade pip && \
    /app/backend/venv/bin/pip install -r /app/backend/requirements.txt

# Copy application code
WORKDIR /app
COPY backend/ /app/backend/

# Copy CSV data file
COPY BO_reprints_rows_2.csv /app/BO_reprints_rows_2.csv

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/data && chown -R appuser:appuser /app/data && chmod 700 /app/data

# Health check (uses default port 8000, Railway will override PORT at runtime)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Set PYTHONPATH so Python can find modules
ENV PYTHONPATH=/app/backend

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Start command using venv
# Use $PORT environment variable (Railway provides this)
# Use absolute paths to avoid cd issues
CMD ["/bin/bash", "-c", "cd /app/backend && /app/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

