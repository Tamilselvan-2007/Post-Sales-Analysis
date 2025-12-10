FROM python:3.10-slim

# Install system dependencies for OpenCV, numpy, YOLO
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

# Install PyTorch CPU
RUN pip install --no-cache-dir torch==2.2.2+cpu torchvision==0.17.2+cpu \
    -f https://download.pytorch.org/whl/torch_stable.html

# Install other Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 10000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--timeout", "120", "--bind", "0.0.0.0:$PORT", "app:app"]

