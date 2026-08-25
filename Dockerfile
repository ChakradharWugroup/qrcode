FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for OpenCV and PyZbar
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run Uvicorn (Hugging Face Spaces uses port 7860 by default)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}
