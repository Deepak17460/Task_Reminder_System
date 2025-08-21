# Use official Python slim image for a smaller footprint
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY templates/ ./templates/
COPY run_application/ ./run_application/

# Ensure data directory exists
RUN mkdir -p /app/data

# Expose port 5000 for Flask
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=run_application/run_app.py

# Command to run the application
CMD ["python", "run_application/run_app.py"]