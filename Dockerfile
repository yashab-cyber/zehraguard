# ZehraGuard InsightX Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        postgresql-client \
        redis-tools \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY core/ ./core/
COPY integrations/ ./integrations/
COPY ml/ ./ml/
COPY api/ ./api/
COPY agents/processors/ ./agents/processors/

# Create necessary directories
RUN mkdir -p /app/logs /app/models /app/data

# Copy configuration files
COPY deployment/supervisor/ /etc/supervisor/conf.d/
COPY deployment/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user
RUN groupadd -r zehraguard && useradd -r -g zehraguard zehraguard
RUN chown -R zehraguard:zehraguard /app
USER zehraguard

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start supervisor
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
