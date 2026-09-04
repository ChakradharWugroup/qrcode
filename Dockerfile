FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for OpenCV, PyZbar, and SSL
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Generate a self-signed certificate for HTTPS
RUN openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 3650 -subj "/CN=141.147.165.228"

# Run Uvicorn with SSL enabled
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860} --ssl-keyfile key.pem --ssl-certfile cert.pem
