# Multi-stage build for BioCheAI Enhanced
FROM node:18-alpine AS frontend-builder

# Build frontend
WORKDIR /app/frontend
COPY biocheai-frontend/package*.json ./
RUN npm ci --only=production
COPY biocheai-frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./static

# Create necessary directories
RUN mkdir -p instance logs

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start command
CMD ["python", "run.py"]
