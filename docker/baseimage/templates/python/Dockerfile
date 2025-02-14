FROM baseimage-python:latest

WORKDIR /app

# Copy application code and tests
COPY app/ ./app/
COPY tests/ ./tests/

# Add app directory to Python path for test imports
ENV PYTHONPATH=/app/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "app/main.py"]