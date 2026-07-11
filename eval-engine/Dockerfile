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

RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

ENV DECISION_LOG_PATH=/app/data/decisions.jsonl
ENV STABLE_PREDICTION_LOG_PATH=/app/data/stable_predictions.jsonl
ENV CANARY_PREDICTION_LOG_PATH=/app/data/canary_predictions.jsonl

CMD ["python", "-m", "app.main"]