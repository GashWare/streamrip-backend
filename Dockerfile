# Use a lightweight Python image
FROM python:3.9-slim

# 1. Install System Dependencies (FFmpeg is critical here)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

# 2. Set working directory
WORKDIR /app

# 3. Copy files
COPY requirements.txt .
COPY app.py .

# 4. Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Command to run the app
CMD ["python", "app.py"]