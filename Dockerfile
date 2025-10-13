# Use official Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies (Tesseract + OpenCV requirements)
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Cloud Run's default port
EXPOSE 8080

# Start Gunicorn on port 8080 (Cloud Run requirement)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "2"]
