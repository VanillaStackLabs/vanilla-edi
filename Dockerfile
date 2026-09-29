FROM python:3.14-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build tools in case C-extensions (pydantic-core, etc.) build from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a temporary directory
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.14-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
COPY . .

EXPOSE 8000

# Run Uvicorn with standard production flags
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]