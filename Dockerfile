FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    BRAVE_BIN=/usr/bin/brave-browser \
    DISPLAY=:99

WORKDIR /app

# SO + librerías gráficas + Xvfb
RUN apt-get update && apt-get install -y \
    curl wget gnupg apt-transport-https ca-certificates unzip \
    xvfb xauth x11-apps \
    fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 \
    libxext6 libxfixes3 libxrandr2 libxshmfence1 libxss1 libxtst6 xdg-utils \
    libxkbcommon0 libatspi2.0-0 libpango-1.0-0 libpangocairo-1.0-0 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Brave
RUN curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" \
    > /etc/apt/sources.list.d/brave-browser-release.list && \
    apt-get update && apt-get install -y brave-browser && \
    rm -rf /var/lib/apt/lists/*

# Poetry + deps (sin venv)
COPY pyproject.toml /app/
RUN pip install --no-cache-dir "poetry==1.7.1" && \
    poetry install --no-interaction --no-ansi --no-root

# Código
COPY . /app

# Script de arranque: Xvfb en background + uvicorn en foreground
RUN printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -euo pipefail' \
  'echo "[start] Xvfb en $DISPLAY..."' \
  'Xvfb :99 -screen 0 1280x800x24 -nolisten tcp &' \
  'sleep 0.5' \
  'echo "[start] Lanzando uvicorn..."' \
  'exec uvicorn main:app --host 0.0.0.0 --port 8000' \
  > /usr/local/bin/start-with-xvfb.sh && chmod +x /usr/local/bin/start-with-xvfb.sh

EXPOSE 8000
CMD ["/usr/local/bin/start-with-xvfb.sh"]
