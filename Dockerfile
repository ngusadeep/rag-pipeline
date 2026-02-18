# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV UV_CACHE_DIR=/tmp/uv-cache
ENV VIRTUAL_ENV=/tmp/venv

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Install uvicorn system-wide
RUN pip install --no-cache-dir "uvicorn[standard]>=0.24.0"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Copy application code
COPY app/ ./app/
COPY main.py ./

# Install Python dependencies using uv (excluding uvicorn which is system-wide)
RUN UV_CACHE_DIR=/tmp/uv-cache VIRTUAL_ENV=/tmp/venv uv sync --no-dev

# Create data directories
RUN mkdir -p data/zvec data/documents

# Expose port
EXPOSE 8000

# Run the application using system uvicorn but with venv Python path
ENV PATH="/tmp/venv/bin:$PATH"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]