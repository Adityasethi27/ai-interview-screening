FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install deps first for better layer caching.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Build the vector store at image build time so the container is ready to serve.
# (Requires GEMINI_API_KEY at build; alternatively run ingestion at container start.)
EXPOSE 8000

# Ingest KB on startup (idempotent) then launch the API.
CMD ["sh", "-c", "python -m scripts.ingest_kb && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
