FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools to ensure proper package handling
RUN pip install --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "run_local.py"]