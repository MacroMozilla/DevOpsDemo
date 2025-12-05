FROM python:3.11-slim

# Author information
LABEL maintainer="harry"
LABEL description="Production-ready Django DevOps Demo"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy the entire Django project into the container
COPY --chown=appuser:appuser . .

# Run database migrations and collect static files
RUN python manage.py collectstatic --noinput || true

# Copy entrypoint script and fix line endings (CRLF -> LF)
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/')" || exit 1

# Start the Django application using Gunicorn with optimized settings
ENTRYPOINT ["/app/entrypoint.sh"]