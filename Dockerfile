FROM python:3.10-slim

# Install required system packages for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend folder only
COPY PCB_BACK_END /app/

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

# Start server
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]

