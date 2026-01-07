# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY conflict_api/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY conflict_api /app

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]