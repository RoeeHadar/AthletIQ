# Implements: FR-012, CON-003, ADR-004, ADR-009
# FastAPI prediction service image (sync /v1).
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY api ./api
COPY database ./database

RUN pip install --no-cache-dir .

ENV PYTHONPATH=/app
ENV ATHLETIQ_ARTIFACTS_PATH=/artifacts
ENV ATHLETIQ_RAW_PATH=/data/raw

EXPOSE 8000
# Listen on all interfaces inside the container; Compose publishes 127.0.0.1:8000 (ADR-009).
CMD ["uvicorn", "api.app.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
