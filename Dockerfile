FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps required by some wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libffi-dev \
       libssl-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Add a non-root user
RUN useradd -m appuser || true

# Copy project files
COPY . .
RUN chown -R appuser:appuser /app || true
USER appuser

# Expose port used by uvicorn
EXPOSE 8000

# Default command: run the etapa4 FastAPI service
CMD ["uvicorn", "backend.etapa4_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
