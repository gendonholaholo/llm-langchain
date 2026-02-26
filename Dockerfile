# ---- builder ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Layer-cache: install deps before copying source
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy source and sync again (installs the project itself)
COPY src/ src/
COPY main.py alembic.ini ./
COPY alembic/ alembic/
COPY scripts/ scripts/
COPY data/ data/
COPY tests/ tests/
RUN uv sync --frozen

# ---- runtime ----
FROM python:3.12-slim-bookworm AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual-env and application code from builder
COPY --from=builder /app/.venv .venv
COPY --from=builder /app/src src
COPY --from=builder /app/alembic alembic
COPY --from=builder /app/alembic.ini alembic.ini
COPY --from=builder /app/scripts scripts
COPY --from=builder /app/data data
COPY --from=builder /app/tests tests
COPY --from=builder /app/pyproject.toml pyproject.toml
COPY --from=builder /app/main.py main.py

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
