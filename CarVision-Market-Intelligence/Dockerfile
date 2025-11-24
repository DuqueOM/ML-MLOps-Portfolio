FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Remover hashes y backslashes de continuación de requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    && sed -e '/--hash=/d' -e 's/ \\$//' -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' requirements.txt > requirements_no_hash.txt \
    && pip install --no-cache-dir -r requirements_no_hash.txt

COPY . .

# Ensure src package is in python path
ENV PYTHONPATH=/app
ENV MODEL_PATH=artifacts/model.joblib

EXPOSE 8000

# Use explicit uvicorn call
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:8000/health || exit 1
