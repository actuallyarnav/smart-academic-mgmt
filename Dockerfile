FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.6.8 /uv /uvx /bin/

COPY pyproject.toml README.md ./
RUN uv sync --no-dev

COPY . .
RUN uv sync --no-dev

EXPOSE 8080

CMD ["uv", "run", "app.py"]
