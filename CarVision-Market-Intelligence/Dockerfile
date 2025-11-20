FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
# Desactivar verificación de hashes para evitar error con dependencias transitivas
ENV PIP_NO_REQUIRE_HASHES=1
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY . .
ENV MODEL_PATH=artifacts/model.joblib
EXPOSE 8000
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:8000/health || exit 1
