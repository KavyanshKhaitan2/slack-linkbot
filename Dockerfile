### Build ###
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS build

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY . .

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV HOME=/tmp
ENV XDG_CACHE_HOME=/tmp/.cache
ENV UV_CACHE_DIR=/tmp/uv-cache

RUN --mount=type=cache,target=/root/.cache/uv \
--mount=type=bind,source=uv.lock,target=uv.lock \
--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
uv sync --locked --no-install-project

RUN mkdir -p /tmp/uv-cache /tmp/.cache \
 && chown -R 999:999 /tmp/uv-cache /tmp/.cache
RUN  chown -R 999:999 /app


### Deployment ###

EXPOSE 8000
USER 999:999

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]