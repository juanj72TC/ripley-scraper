FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Instala la librería playwright en el entorno Python
RUN pip install --no-cache-dir playwright

# Instala solo Chromium (no WebKit ni Firefox)
RUN python -m playwright install chromium

# Copia tu código
COPY . /app
WORKDIR /app

# Ejecuta el script
CMD ["python", "main.py"]
