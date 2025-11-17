FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# SECURITY: Create non-root user for running the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
COPY . .

# SECURITY: Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Create directory for data files with proper permissions
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data && chmod 700 /app/data

# Expose port
EXPOSE 8000

# Health check - use curl or wget instead of Python requests
# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# SECURITY: Switch to non-root user
USER appuser

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

