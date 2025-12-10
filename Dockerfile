FROM python:3.10-slim

# Install required system packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy ONLY the backend folder
COPY PCB_BACK_END /app/

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Expose Render $PORT
EXPOSE 10000

# Start Gunicorn (pointing to PCB_BACK_END/app.py)
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "--bind", "0.0.0.0:10000", "app:app"]
