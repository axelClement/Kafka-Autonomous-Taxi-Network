# Use Python 3.11 as base image (compatible with kafka-python)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/

# Default command (can be overridden in docker-compose)
CMD ["python", "src/producer_taxi.py"]
