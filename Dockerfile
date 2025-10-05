# Use official Python 3.11 slim image
FROM python:3.11-slim

# Install Tesseract OCR and dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Start Gunicorn server
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers", "2"]
