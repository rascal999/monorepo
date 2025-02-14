FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install nginx for the nginx -s reload command
RUN apt-get update && \
    apt-get install -y nginx-common && \
    rm -rf /var/lib/apt/lists/*

# Copy source code
COPY src/monitor.py .

# Make script executable
RUN chmod +x monitor.py

# Set Python to unbuffered mode
ENV PYTHONUNBUFFERED=1

# Run with Python explicitly
CMD ["python", "-u", "monitor.py"]