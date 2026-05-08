FROM python:3.11-slim

WORKDIR /app

# System dependencies (including OpenCV libs for PaddleOCR)
RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev curl \
    libgl1 libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to avoid resolver issues
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch CPU-only FIRST (200MB instead of 2GB CUDA version)
RUN pip install --no-cache-dir torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# Install PaddlePaddle separately (large, can timeout)
RUN pip install --no-cache-dir paddlepaddle>=2.6.2 || \
    pip install --no-cache-dir paddlepaddle>=2.6.2

# Install remaining Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000", \
     "--log-level", "warning"]
