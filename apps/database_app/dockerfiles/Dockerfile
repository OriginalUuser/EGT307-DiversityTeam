FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY scripts/ ./scripts/

CMD ["/bin/bash", "./scripts/dataset_download.sh"]