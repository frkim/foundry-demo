# syntax=docker/dockerfile:1
# Build context: src/   ->   docker build -t foundry-demo:local src
# All packages resolve through the Microsoft Central Feed Services (CFS) protected feeds.

ARG NODE_IMAGE=node:24-alpine
ARG PYTHON_IMAGE=python:3.13-slim
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.11.6

FROM ${UV_IMAGE} AS uv

# ---------- Stage 1: build the Vue/Vuetify SPA ----------
FROM ${NODE_IMAGE} AS web
WORKDIR /web
COPY web/.npmrc web/package.json web/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY web/ ./
RUN npm run build

# ---------- Stage 2: Python runtime (FastAPI + static SPA) ----------
FROM ${PYTHON_IMAGE} AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_DEFAULT_INDEX=https://packagefeedproxy.microsoft.io/pypi/simple \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv
COPY --from=uv /uv /usr/local/bin/uv
# Build-time only: modest download parallelism + retries make restores resilient to flaky DNS in local builders.
ARG UV_CONCURRENT_DOWNLOADS=4
ARG UV_HTTP_RETRIES=5
WORKDIR /app

# Dependencies first for better layer caching.
COPY api/pyproject.toml api/uv.lock api/README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY api/src ./src
RUN uv sync --frozen --no-dev --no-editable \
    && rm -rf /root/.cache

COPY --from=web /web/dist /app/static

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app
USER 10001:10001

ENV PATH="/app/.venv/bin:${PATH}" \
    STATIC_DIR=/app/static
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=4)"]

CMD ["uvicorn", "foundry_demo.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log", "--proxy-headers", "--forwarded-allow-ips", "*"]
