##############################
# FLL-Sim API Service Dockerfile
# FastAPI-based educational platform API
##############################

FROM python:3.12-slim AS base

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for API service
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
COPY requirements-api.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-api.txt

# Install package
COPY pyproject.toml setup.py README.md ./
COPY src/ ./src/
RUN pip install -e .

# Copy API application
COPY api/ ./api/

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash apiuser
USER apiuser

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
