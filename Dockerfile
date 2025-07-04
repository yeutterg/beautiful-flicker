# Beautiful Flicker Flask App Dockerfile

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgfortran5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY flask_app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application
COPY flask_app/ /app/flask_app/

# Copy the original source code (needed for analysis modules)
COPY src/ /app/src/

# Set environment variables
ENV FLASK_APP=flask_app/app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the application with gunicorn
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 4 --timeout 120 flask_app.app:app