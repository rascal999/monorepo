FROM baseimage-python:latest

WORKDIR /app

# Copy application code
COPY app/ /app/

# Set Python to run unbuffered
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]