# ---- builder ----
FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml .
RUN pip install --no-cache-dir --target=/build/deps .

# ---- runtime ----
FROM python:3.12-slim AS runtime

RUN useradd --create-home --uid 1000 appuser
WORKDIR /app

COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages
COPY app/ ./app/

RUN mkdir -p /app/artifacts /app/logs && chown -R appuser:appuser /app

USER appuser

ENV MODEL_PATH=/app/artifacts/model.joblib
ENV PREDICTION_LOG_PATH=/app/logs/predictions.jsonl

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]