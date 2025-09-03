FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de requisitos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY migrations/ ./migrations/
COPY alembic.ini .
COPY run.py .

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Copiar y dar permisos al entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Entrypoint para ejecutar la aplicación
ENTRYPOINT ["/app/entrypoint.sh"]
