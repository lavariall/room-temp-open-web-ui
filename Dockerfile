# Multi-stage build for minimal size
FROM python:3.11-alpine as builder

WORKDIR /app

# Install build dependencies for aiohttp (if needed for alpine)
RUN apk add --no-cache build-base

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final stage
FROM python:3.11-alpine

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "src/server.py"]
