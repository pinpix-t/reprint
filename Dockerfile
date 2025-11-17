FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/backend/requirements.txt

# Create virtual environment and install dependencies
# Use absolute paths to avoid activation issues
RUN cd /app/backend && \
    python3 -m venv venv && \
    /app/backend/venv/bin/pip install --upgrade pip && \
    /app/backend/venv/bin/pip install -r /app/backend/requirements.txt && \
    /app/backend/venv/bin/python -m spacy download en_core_web_sm

# Copy application code
COPY backend/ /app/backend/

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app && \
    mkdir -p /app/data && chown -R appuser:appuser /app/data && chmod 700 /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Start command using venv
CMD ["/bin/bash", "-c", "cd /app/backend && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000"]

