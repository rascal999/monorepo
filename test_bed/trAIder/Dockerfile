FROM baseimage-python:latest

WORKDIR /app

# Copy entire project
COPY . .

# Install project dependencies
RUN pip install -r requirements.txt

# Install the package in development mode
RUN pip install -e .

# Set Python to run unbuffered
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run using the installed package module
ENTRYPOINT ["python"]
CMD ["-m", "app.main"]