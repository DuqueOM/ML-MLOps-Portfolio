# 14. Docker Avanzado para ML

## 🎯 Objetivo del Módulo

Construir imágenes Docker optimizadas, seguras y pequeñas como las del portafolio.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  NIVEL 1: Funcional       NIVEL 2: Optimizado      NIVEL 3: Production       ║
║  ─────────────────        ──────────────────       ──────────────────        ║
║  FROM python:3.11         Multi-stage build        Distroless/Alpine         ║
║  COPY . .                 Slim base                Non-root user             ║
║  pip install              Layer caching            CVE scanning              ║
║                                                                              ║
║  ~1.2GB                   ~400MB                   ~150MB                    ║
║  ⚠️ Básica                 ✅ Mejor                  🛡️ Hardened            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Contenido

1. [Dockerfile Básico vs Optimizado](#141-dockerfile-básico-vs-optimizado)
2. [Multi-Stage Builds](#142-multi-stage-builds)
3. [Mejores Prácticas](#143-mejores-prácticas)
4. [Dockerfile Real del Portafolio](#144-dockerfile-real-del-portafolio)
5. [Docker Compose para ML](#145-docker-compose-para-ml)

---

## 14.1 Dockerfile Básico vs Optimizado

### ❌ Nivel 1: Básico (No usar en producción)

```dockerfile
# Dockerfile MALO - Solo para demos rápidas
FROM python:3.11

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]

# Problemas:
# - Imagen de ~1.2GB
# - Incluye herramientas de desarrollo innecesarias
# - Cache de pip no aprovechado
# - Corre como root (inseguro)
# - Copia archivos innecesarios (.git, tests, etc.)
```

### ✅ Nivel 2: Optimizado

```dockerfile
# Dockerfile MEJOR - Para staging/desarrollo

# 1. Usar slim para reducir tamaño
FROM python:3.11-slim

# 2. Establecer directorio de trabajo
WORKDIR /app

# 3. Copiar SOLO requirements primero (aprovecha cache)
COPY requirements.txt .

# 4. Instalar dependencias (capa cacheada si requirements no cambia)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar código fuente
COPY src/ ./src/
COPY app/ ./app/
COPY configs/ ./configs/

# 6. Usuario no-root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 7. Puerto y comando
EXPOSE 8000
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]

# Mejoras:
# - ~400MB (slim base)
# - Cache de layers optimizado
# - No corre como root
# - Solo archivos necesarios
```

---

## 14.2 Multi-Stage Builds

### El Concepto

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MULTI-STAGE BUILD                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STAGE 1: Builder                    STAGE 2: Runtime                       │
│  ────────────────                    ────────────────                       │
│  • Imagen completa                   • Imagen mínima                        │
│  • Compila código                    • Solo runtime                         │
│  • Instala dependencias              • Copia solo binarios                  │
│  • Genera wheels                     • Sin compiladores                     │
│                                                                             │
│  ┌─────────────────┐                 ┌──────────────────┐                   │
│  │ python:3.11     │                 │ python:3.11-slim │                   │
│  │ + gcc, make     │                 │                  │                   │
│  │ + pip wheel     │   ──COPY──►     │ + wheels only    │                   │
│  │ = 1.2GB         │                 │ = 150-400MB      │                   │
│  └─────────────────┘                 └──────────────────┘                   │
│                                                                             │
│  Se DESCARTA                         Se USA en producción                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Implementación

```dockerfile
# Dockerfile Multi-Stage - Nivel 3

# ══════════════════════════════════════════════════════════════════════════
# STAGE 1: Builder - Compila dependencias
# ══════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim AS builder

WORKDIR /build

# Instalar herramientas de compilación (temporales)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Crear wheels (binarios precompilados)
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ══════════════════════════════════════════════════════════════════════════
# STAGE 2: Runtime - Imagen final mínima
# ══════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copiar SOLO los wheels del builder
COPY --from=builder /wheels /wheels

# Instalar desde wheels (sin compilación)
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copiar código
COPY src/ ./src/
COPY app/ ./app/
COPY configs/ ./configs/

# Copiar modelo pre-entrenado si existe
COPY artifacts/model.joblib ./artifacts/model.joblib 2>/dev/null || true

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 14.3 Mejores Prácticas

### .dockerignore

```dockerignore
# .dockerignore - Excluir archivos innecesarios

# Git
.git
.gitignore

# Python
__pycache__
*.py[cod]
*.pyo
.pytest_cache
.mypy_cache
.coverage
htmlcov/
.venv/
venv/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# Tests (no necesarios en producción)
tests/
*_test.py
test_*.py
conftest.py

# Documentación
docs/
*.md
!README.md

# Datos (montar como volumen, no copiar)
data/
*.csv
*.parquet

# Notebooks
*.ipynb
notebooks/

# Logs y temporales
*.log
logs/
tmp/
```

### Layer Caching

```dockerfile
# ❌ MALO: Cualquier cambio en código invalida cache de pip
COPY . .
RUN pip install -r requirements.txt

# ✅ BUENO: requirements separado para aprovechar cache
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/  # Cambios aquí NO invalidan pip install
```

### Security: Non-Root User

```dockerfile
# Crear usuario con UID específico (evita conflictos de permisos)
RUN useradd -m -u 1000 appuser

# Dar permisos al directorio de trabajo
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root ANTES de CMD
USER appuser

# Ahora el proceso corre como appuser, no como root
```

---

## 14.4 Dockerfile Real del Portafolio

### BankChurn-Predictor/Dockerfile

```dockerfile
# BankChurn-Predictor Production Dockerfile
# Multi-stage build optimizado para ML

# ══════════════════════════════════════════════════════════════════════════
# Stage 1: Builder
# ══════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim AS builder

WORKDIR /build

# Dependencias de sistema para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Crear wheels
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ══════════════════════════════════════════════════════════════════════════
# Stage 2: Runtime
# ══════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim

# Labels para metadata
LABEL maintainer="duqueom@example.com"
LABEL version="1.0.0"
LABEL description="BankChurn Predictor API"

WORKDIR /app

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias desde wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copiar código fuente
COPY src/ ./src/
COPY app/ ./app/
COPY configs/ ./configs/

# Copiar modelo (si existe)
COPY models/ ./models/ 2>/dev/null || mkdir -p ./models

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=45s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 14.5 Docker Compose para ML

### docker-compose.demo.yml (Portafolio)

```yaml
# Docker Compose para demo completa del portafolio
version: "3.8"

services:
  # MLflow Server (central)
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.2
    container_name: mlflow-server
    ports:
      - "5000:5000"
    volumes:
      - mlflow-data:/mlflow
    command: >
      mlflow server
      --backend-store-uri sqlite:///mlflow/mlflow.db
      --default-artifact-root /mlflow/artifacts
      --host 0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - ml-network

  # BankChurn API
  bankchurn:
    build:
      context: ./BankChurn-Predictor
      dockerfile: Dockerfile
    container_name: bankchurn-api
    ports:
      - "8001:8000"
    volumes:
      - ./BankChurn-Predictor/models:/app/models:ro
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    depends_on:
      mlflow:
        condition: service_healthy
    networks:
      - ml-network

  # CarVision API
  carvision:
    build:
      context: ./CarVision-Market-Intelligence
      dockerfile: Dockerfile
    container_name: carvision-api
    ports:
      - "8002:8000"
    volumes:
      - ./CarVision-Market-Intelligence/artifacts:/app/artifacts:ro
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    depends_on:
      mlflow:
        condition: service_healthy
    networks:
      - ml-network

  # TelecomAI API
  telecom:
    build:
      context: ./TelecomAI-Customer-Intelligence
      dockerfile: Dockerfile
    container_name: telecom-api
    ports:
      - "8003:8000"
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    depends_on:
      mlflow:
        condition: service_healthy
    networks:
      - ml-network

volumes:
  mlflow-data:

networks:
  ml-network:
    driver: bridge
```

### Comandos Útiles

```bash
# Construir todas las imágenes
docker compose -f docker-compose.demo.yml build

# Iniciar todos los servicios
docker compose -f docker-compose.demo.yml up -d

# Ver logs
docker compose -f docker-compose.demo.yml logs -f bankchurn

# Parar todo
docker compose -f docker-compose.demo.yml down

# Limpiar volúmenes también
docker compose -f docker-compose.demo.yml down -v
```

---

## 🧨 Errores habituales y cómo depurarlos en Docker para ML

En ML es muy común tener imágenes gigantes, problemas de permisos o contenedores que “funcionan en mi máquina pero no en producción”.

### 1) Imágenes demasiado grandes

**Síntomas típicos**

- `docker images` muestra tamaños > 1GB.
- Push/pull al registry tarda mucho o falla por timeout.

**Cómo identificarlo**

- Compara tu Dockerfile con los ejemplos `python:3.11` vs `python:3.11-slim` del módulo.
- Revisa si estás copiando todo el repo (`COPY . .`) sin `.dockerignore`.

**Cómo corregirlo**

- Usa bases `slim` y **multi-stage builds**.
- Añade un `.dockerignore` que excluya datos, notebooks, tests y `.venv`.

---

### 2) Errores de permisos al correr como non-root

**Síntomas típicos**

- El contenedor arranca pero falla al leer modelos, logs o escribir en directorios.
- Mensajes tipo `Permission denied: '/app/models/model.joblib'`.

**Cómo identificarlo**

- Verifica que después de copiar archivos hagas `chown` al usuario de la app.
- Revisa que `USER appuser` aparezca **después** de ajustar permisos.

**Cómo corregirlo**

- Asegúrate de:
  ```dockerfile
  RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
  USER appuser
  ```
- Monta volúmenes con permisos compatibles (por ejemplo, propiedad UID 1000 en host).

---

### 3) Modelo o artefactos no encontrados dentro del contenedor

**Síntomas típicos**

- La API levanta pero responde 500 porque no encuentra el modelo (`FileNotFoundError`).

**Cómo identificarlo**

- Revisa las rutas de `COPY` en el Dockerfile y las rutas que tu código usa (`./models`, `./artifacts`).

**Cómo corregirlo**

- Copia los artefactos a la ruta esperada o monta un volumen de solo lectura:
  ```yaml
  volumes:
    - ./BankChurn-Predictor/models:/app/models:ro
  ```

---

### 4) Contenedores que arrancan pero el healthcheck falla

**Síntomas típicos**

- El servicio aparece como "unhealthy" en `docker ps`.

**Cómo identificarlo**

- Examina el `HEALTHCHECK` y verifica que la URL y puerto sean correctos.

**Cómo corregirlo**

- Asegúrate de que el endpoint `/health` exista y escuche en el mismo puerto que expones.
- Ajusta tiempos de `start-period` si el modelo tarda más en cargar.

---

### 5) Patrón general de debugging con Docker

1. Inspecciona el contenedor en ejecución con `docker exec -it <container> /bin/bash`.
2. Navega por `/app` para verificar que el código, modelos y configs estén donde esperas.
3. Comprueba permisos (`ls -l`) y usuario actual (`whoami`).
4. Si la imagen es muy grande, revisa el historial de capas con `docker history`.

Con este enfoque, tus imágenes Docker serán reproducibles, ligeras y listas para producción.

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **Multi-stage builds**: Explica cómo reducen tamaño de imagen.

2. **Layer caching**: Por qué el orden de instrucciones importa.

3. **Security**: No correr como root, no incluir secrets en imagen.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Imágenes grandes | Multi-stage + slim base images |
| Secrets | Usa build args o secrets mounting |
| Debugging | Usa `docker exec -it container bash` |
| Producción | Healthchecks obligatorios |

### Dockerfile Optimizado

```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder
COPY requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY src/ /app/src/
USER nobody
HEALTHCHECK CMD curl -f http://localhost:8000/health
```


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [Docker Tutorial - TechWorld Nana](https://www.youtube.com/watch?v=3c-iBn73dDE) | Video |
| 🟡 | [Multi-stage Builds](https://www.youtube.com/watch?v=zpkqNPwEzac) | Video |

**Documentación oficial:**
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **Multi-stage Build**: Separar build de runtime
- **Docker Compose**: Orquestar múltiples contenedores
- **Non-root user**: Seguridad en contenedores

---

## 📋 Plantillas Relacionadas

Ver [templates/](templates/index.md) para plantillas listas:
- [Dockerfile](templates/Dockerfile) — Multi-stage completo para ML APIs
- [Dockerfile_template](templates/Dockerfile_template) — Versión simplificada
- [docker-compose.yml](templates/docker-compose.yml) — Stack con servicios

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 13:
- **13.1**: Dockerfile multi-stage
- **13.2**: Docker Compose para stack ML

---

<div align="center">

[← CI/CD GitHub Actions](12_CI_CD.md) | [Siguiente: FastAPI Producción →](14_FASTAPI.md)

</div>
