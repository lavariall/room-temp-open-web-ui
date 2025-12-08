FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any (Open WebUI might need some)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the default FastMCP port (can be overridden)
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# Run the Web App (FastAPI + Frontend)
CMD ["python", "src/web_app.py"]
