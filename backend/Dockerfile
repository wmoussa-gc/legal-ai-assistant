FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies including SWI-Prolog
RUN apt-get update && apt-get install -y \
    software-properties-common \
    apt-transport-https \
    curl \
    wget \
    git \
    build-essential \
    cmake \
    pkg-config \
    && apt-add-repository ppa:swi-prolog/stable \
    && apt-get update \
    && apt-get install -y swi-prolog \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for scasp (using SWI-Prolog as base)
RUN ln -sf /usr/bin/swipl /usr/local/bin/scasp

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/temp

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]