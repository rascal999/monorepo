FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install build dependencies
RUN pip install --no-cache-dir hatchling

# Copy dependency files first
COPY requirements.txt pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY smolagent/ smolagent/
COPY run.sh .

# Install package in editable mode
RUN pip install -e . && \
    chmod +x run.sh

# Default command (can be overridden)
CMD ["./run.sh"]