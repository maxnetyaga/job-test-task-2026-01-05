FROM debian:trixie-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 DEBUG=False

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc nginx \
    && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./uv.lock ./.python-version .

RUN uv sync
ENV PATH="/app/.venv/bin:$PATH"

COPY nginx.conf /etc/nginx/nginx.conf

COPY . .

RUN mkdir -p /app/data

RUN chmod +x /app/entrypoint.sh

EXPOSE 8100

ENTRYPOINT ["/app/entrypoint.sh"]
