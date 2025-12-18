# Use Python 3.11 (Required for latest yt-dlp)
FROM python:3.11-slim

# Install system dependencies
# - ffmpeg: for audio conversion
# - git: required to pip install yt-dlp directly from GitHub
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app.py .

# Command to run the application using Gunicorn for better performance
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]