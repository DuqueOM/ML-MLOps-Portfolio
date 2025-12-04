# 🎬 Guía de Material Audiovisual — ML-MLOps Portfolio

> **Guía completa para crear demos profesionales de tu portafolio**

**Última actualización**: Diciembre 2025  
**Versión**: 5.1 — Portfolio Edition  
**Repositorio**: [github.com/DuqueOM/ML-MLOps-Portfolio](https://github.com/DuqueOM/ML-MLOps-Portfolio)

---

## 📋 Índice

1. [Estado Actual del Portafolio](#-estado-actual-del-portafolio)
2. [Servicios del Stack Demo](#-servicios-del-stack-demo)
3. [Material Audiovisual Requerido](#-material-audiovisual-requerido)
4. [Herramientas Recomendadas](#-herramientas-recomendadas)
5. [Guía de GIFs Demostrativos](#-guía-de-gifs-demostrativos)
6. [Guía de Screenshots](#-guía-de-screenshots)
7. [Guía de Video Principal](#-guía-de-video-principal)
8. [Comandos y Scripts Útiles](#-comandos-y-scripts-útiles)
9. [Checklist Final](#-checklist-final)

---

## 🎯 Estado Actual del Portafolio

### Proyectos del Portafolio

| Proyecto | Descripción | Tecnologías Clave |
|----------|-------------|-------------------|
| **BankChurn-Predictor** | Predicción de abandono bancario | sklearn Pipeline, ResampleClassifier, MLflow |
| **CarVision-Market-Intelligence** | Predicción de precios de vehículos | FeatureEngineer transformer, Streamlit dashboard |
| **TelecomAI-Customer-Intelligence** | Clasificación de planes móviles | Pipeline ML unificado |

### Métricas Actuales

| Proyecto | Coverage | Métrica Principal | CI Status |
|----------|:--------:|:-----------------:|:---------:|
| BankChurn | 79% | 86% AUC | ✅ Passing |
| CarVision | 80% | 0.87 R² | ✅ Passing |
| TelecomAI | 80% | 82% Accuracy | ✅ Passing |

---

## 🖥 Servicios del Stack Demo

### Comando para Levantar

```bash
docker-compose -f docker-compose.demo.yml up -d
```

### 5 Servicios Principales

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SERVICIOS DEL STACK DEMO                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🔹 MLFLOW TRACKING SERVER                                              │
│     URL: http://localhost:5000                                          │
│     Función: Tracking de experimentos, Model Registry                   │
│     Mostrar: Lista de experimentos, métricas, modelos registrados       │
│                                                                         │
│  🔹 BANKCHURN API (FastAPI)                                             │
│     URL: http://localhost:8001/docs                                     │
│     Función: Predicción de abandono de clientes                         │
│     Mostrar: Swagger UI, endpoint /predict, respuesta JSON              │
│                                                                         │
│  🔹 CARVISION API (FastAPI)                                             │
│     URL: http://localhost:8002/docs                                     │
│     Función: Predicción de precios de vehículos                         │
│     Mostrar: Swagger UI, endpoint /predict                              │
│                                                                         │
│  🔹 CARVISION STREAMLIT DASHBOARD                                       │
│     URL: http://localhost:8501                                          │
│     Función: Dashboard interactivo para análisis y predicción           │
│     Mostrar: Gráficos, formulario de predicción, resultados             │
│                                                                         │
│  🔹 TELECOMAI API (FastAPI)                                             │
│     URL: http://localhost:8003/docs                                     │
│     Función: Clasificación de planes móviles                            │
│     Mostrar: Swagger UI, endpoint /predict                              │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  SERVICIOS OPCIONALES (con --profile monitoring)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🔸 PROMETHEUS: http://localhost:9090                                   │
│  🔸 GRAFANA:    http://localhost:3000 (admin/admin)                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Resumen de URLs

| Servicio | Puerto | URL Completa | Tipo |
|----------|:------:|--------------|:----:|
| MLflow UI | 5000 | http://localhost:5000 | Dashboard |
| BankChurn API | 8001 | http://localhost:8001/docs | Swagger |
| CarVision API | 8002 | http://localhost:8002/docs | Swagger |
| **CarVision Dashboard** | **8501** | **http://localhost:8501** | **Streamlit** |
| TelecomAI API | 8003 | http://localhost:8003/docs | Swagger |
| Prometheus | 9090 | http://localhost:9090 | Monitoring |
| Grafana | 3000 | http://localhost:3000 | Dashboards |

---

## 📊 Material Audiovisual Requerido

### Resumen de Elementos

| Categoría | Cantidad | Prioridad | Descripción |
|-----------|:--------:|:---------:|-------------|
| GIFs Demostrativos | 5 | 🔴 Alta | Portfolio, 3 APIs, Streamlit |
| Screenshots | 8 | 🟡 Media | UIs, dashboards, CI |
| Video Demo Principal | 1 | 🔴 Alta | 3-5 min completo |
| Thumbnails | 4 | 🟢 Baja | Para YouTube/docs |

### Mapa de Archivos → Referencias

| Archivo | Ubicación | Se usa en |
|---------|-----------|-----------|
| `portfolio-demo.gif` | `media/gifs/` | README.md principal |
| `bankchurn-preview.gif` | `media/gifs/` | README.md, BankChurn/README.md |
| `carvision-preview.gif` | `media/gifs/` | README.md, CarVision/README.md |
| `streamlit-carvision.gif` | `media/gifs/` | CarVision/README.md |
| `telecom-preview.gif` | `media/gifs/` | README.md, TelecomAI/README.md |
| `mlflow-experiments.png` | `media/screenshots/` | docs/, READMEs |
| `mlflow-model-registry.png` | `media/screenshots/` | docs/ |
| `swagger-bankchurn.png` | `media/screenshots/` | BankChurn/README.md |
| `swagger-carvision.png` | `media/screenshots/` | CarVision/README.md |
| `swagger-telecom.png` | `media/screenshots/` | TelecomAI/README.md |
| `streamlit-dashboard.png` | `media/screenshots/` | CarVision/README.md |
| `github-actions-ci.png` | `media/screenshots/` | README.md principal |

---

## 🛠 Herramientas Recomendadas

### Para Windows

| Herramienta | Uso | Instalación |
|-------------|-----|-------------|
| **OBS Studio** | Grabar pantalla | `winget install OBSProject.OBSStudio` |
| **Greenshot** | Screenshots | `winget install Greenshot.Greenshot` |
| **ffmpeg** | Convertir video→GIF | `winget install ffmpeg` |
| **ShareX** | GIFs directos | `winget install ShareX.ShareX` |

### Para Linux

| Herramienta | Uso | Instalación |
|-------------|-----|-------------|
| **OBS Studio** | Grabar pantalla | `sudo apt install obs-studio` |
| **Flameshot** | Screenshots | `sudo apt install flameshot` |
| **ffmpeg** | Convertir video→GIF | `sudo apt install ffmpeg` |
| **Peek** | GIFs directos | `sudo apt install peek` |

### Para macOS

| Herramienta | Uso | Instalación |
|-------------|-----|-------------|
| **OBS Studio** | Grabar pantalla | `brew install obs` |
| **Screenshot nativo** | Screenshots | Cmd+Shift+4 |
| **ffmpeg** | Convertir video→GIF | `brew install ffmpeg` |
| **Gifski** | GIFs de alta calidad | `brew install gifski` |

---

## 🎞 Guía de GIFs Demostrativos

### GIF 1: Portfolio Demo Principal (TODOS los servicios)

**Archivo**: `media/gifs/portfolio-demo.gif`  
**Duración**: 20-25 segundos  
**Resolución**: 800x600

#### Guion Detallado

```
┌─────────────────────────────────────────────────────────────────────────┐
│              PORTFOLIO DEMO PRINCIPAL (20-25 segundos)                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  0:00-0:03  ESCENA 1: Levantar servicios                               │
│  ───────────────────────────────────────────────────────────────────── │
│  • Terminal con comando:                                                │
│    docker-compose -f docker-compose.demo.yml up -d                      │
│  • Mostrar output: "Creating mlflow-server...",                         │
│    "Creating bankchurn-api...", "Creating carvision-api...",            │
│    "Creating carvision-dashboard...", "Creating telecom-api..."         │
│                                                                         │
│  0:03-0:08  ESCENA 2: Los 5 servicios funcionando                      │
│  ───────────────────────────────────────────────────────────────────── │
│  • Abrir 5 pestañas del navegador (split screen o en secuencia):       │
│    1. http://localhost:5000 (MLflow)                                    │
│    2. http://localhost:8001/docs (BankChurn Swagger)                    │
│    3. http://localhost:8002/docs (CarVision Swagger)                    │
│    4. http://localhost:8501 (CarVision Streamlit) ← IMPORTANTE         │
│    5. http://localhost:8003/docs (TelecomAI Swagger)                    │
│  • Pausar 2 segundos en cada una                                        │
│                                                                         │
│  0:08-0:13  ESCENA 3: Demo Streamlit Dashboard                         │
│  ───────────────────────────────────────────────────────────────────── │
│  • Enfocar en localhost:8501                                            │
│  • Mostrar gráficos de análisis de datos                                │
│  • Llenar formulario de predicción rápido                               │
│  • Mostrar resultado de precio estimado                                 │
│                                                                         │
│  0:13-0:18  ESCENA 4: Predicción en API                                │
│  ───────────────────────────────────────────────────────────────────── │
│  • Cambiar a BankChurn Swagger (localhost:8001/docs)                    │
│  • Click en POST /predict → "Try it out"                                │
│  • Ejecutar y mostrar respuesta JSON                                    │
│                                                                         │
│  0:18-0:22  ESCENA 5: MLflow Experiments                               │
│  ───────────────────────────────────────────────────────────────────── │
│  • Cambiar a MLflow (localhost:5000)                                    │
│  • Mostrar lista de experimentos                                        │
│  • Click en un experimento para ver métricas                            │
│                                                                         │
│  0:22-0:25  ESCENA 6: Cierre                                           │
│  ───────────────────────────────────────────────────────────────────── │
│  • Volver a vista general con las 5 pestañas                            │
│  • O mostrar terminal con "docker-compose ps" (5 running)               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Preparación Completa

```bash
# 1. Levantar todos los servicios
cd /path/to/ML-MLOps-Portfolio
docker-compose -f docker-compose.demo.yml up -d

# 2. Esperar a que estén listos (importante!)
echo "Esperando 45 segundos para que todos los servicios inicien..."
sleep 45

# 3. Verificar TODOS los servicios
echo "=== Verificando 5 servicios ==="
echo "MLflow:" && curl -s http://localhost:5000/health 2>/dev/null || echo "OK"
echo "BankChurn:" && curl -s http://localhost:8001/health
echo "CarVision API:" && curl -s http://localhost:8002/health
echo "CarVision Streamlit:" && curl -s http://localhost:8501 >/dev/null && echo '{"status":"healthy"}'
echo "TelecomAI:" && curl -s http://localhost:8003/health

# 4. Ver estado de contenedores
docker-compose -f docker-compose.demo.yml ps

# 5. Abrir TODAS las pestañas
# Linux:
xdg-open http://localhost:5000      # MLflow
xdg-open http://localhost:8001/docs # BankChurn
xdg-open http://localhost:8002/docs # CarVision API
xdg-open http://localhost:8501      # CarVision Streamlit ← NO OLVIDAR
xdg-open http://localhost:8003/docs # TelecomAI

# Windows (PowerShell):
# Start-Process http://localhost:5000
# Start-Process http://localhost:8001/docs
# Start-Process http://localhost:8002/docs
# Start-Process http://localhost:8501
# Start-Process http://localhost:8003/docs
```

---

### GIF 2: BankChurn API Demo

**Archivo**: `media/gifs/bankchurn-preview.gif`  
**Duración**: 8-10 segundos  
**Resolución**: 800x600

#### Guion

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BANKCHURN DEMO (8-10 segundos)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  0:00-0:02  Swagger UI de BankChurn                                    │
│  • Mostrar http://localhost:8001/docs                                   │
│  • Título visible: "BankChurn Predictor API"                            │
│                                                                         │
│  0:02-0:05  Expandir /predict                                          │
│  • Click en POST /predict                                               │
│  • Click "Try it out"                                                   │
│  • Llenar con datos de ejemplo (ver abajo)                              │
│                                                                         │
│  0:05-0:08  Ejecutar y ver resultado                                   │
│  • Click "Execute"                                                      │
│  • Scroll para ver respuesta:                                           │
│    {                                                                    │
│      "prediction": 0,                                                   │
│      "probability": 0.23,                                               │
│      "label": "No Churn"                                                │
│    }                                                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Datos de Ejemplo para BankChurn

```json
{
  "credit_score": 650,
  "age": 45,
  "tenure": 5,
  "balance": 50000,
  "num_of_products": 2,
  "has_cr_card": 1,
  "is_active_member": 1,
  "estimated_salary": 75000,
  "geography": "France",
  "gender": "Male"
}
```

---

### GIF 3: CarVision API Demo

**Archivo**: `media/gifs/carvision-preview.gif`  
**Duración**: 8-10 segundos  
**Resolución**: 800x600

#### Guion

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CARVISION API DEMO (8-10 segundos)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  0:00-0:02  Swagger UI de CarVision                                    │
│  • Mostrar http://localhost:8002/docs                                   │
│  • Título: "CarVision Market Intelligence API"                          │
│                                                                         │
│  0:02-0:05  Expandir /predict                                          │
│  • Click en POST /predict                                               │
│  • "Try it out"                                                         │
│  • Llenar datos de vehículo                                             │
│                                                                         │
│  0:05-0:08  Resultado                                                  │
│  • Ejecutar predicción                                                  │
│  • Mostrar precio estimado: {"predicted_price": 25430.50}               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### Datos de Ejemplo para CarVision

```json
{
  "model_year": 2020,
  "model": "toyota camry",
  "condition": "good",
  "odometer": 35000,
  "fuel": "gas",
  "transmission": "automatic",
  "type": "sedan",
  "paint_color": "white"
}
```

---

### GIF 4: CarVision Streamlit Dashboard (NUEVO - IMPORTANTE)

**Archivo**: `media/gifs/streamlit-carvision.gif`  
**Duración**: 12-15 segundos  
**Resolución**: 800x600

#### Guion Detallado

```
┌─────────────────────────────────────────────────────────────────────────┐
│              CARVISION STREAMLIT DEMO (12-15 segundos)                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  0:00-0:03  Dashboard Principal                                        │
│  ───────────────────────────────────────────────────────────────────── │
│  • Mostrar http://localhost:8501                                        │
│  • Vista inicial del dashboard con título                               │
│  • Sidebar visible con opciones                                         │
│                                                                         │
│  0:03-0:06  Sección de Análisis de Datos                               │
│  ───────────────────────────────────────────────────────────────────── │
│  • Mostrar gráficos de distribución de precios                          │
│  • Gráfico de precios por marca/año                                     │
│  • Estadísticas descriptivas                                            │
│                                                                         │
│  0:06-0:10  Formulario de Predicción                                   │
│  ───────────────────────────────────────────────────────────────────── │
│  • Navegar a sección de predicción                                      │
│  • Seleccionar marca: Toyota                                            │
│  • Seleccionar modelo: Camry                                            │
│  • Año: 2020                                                            │
│  • Kilometraje: 35,000                                                  │
│  • Condición: Good                                                      │
│                                                                         │
│  0:10-0:13  Resultado de Predicción                                    │
│  ───────────────────────────────────────────────────────────────────── │
│  • Click en botón "Predecir Precio"                                     │
│  • Mostrar resultado: "$25,430" (grande, visible)                       │
│  • Mostrar intervalo de confianza si existe                             │
│                                                                         │
│  0:13-0:15  Vista Final                                                │
│  ───────────────────────────────────────────────────────────────────── │
│  • Scroll up para mostrar todo el dashboard                             │
│  • O cambiar a otra sección brevemente                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### GIF 5: TelecomAI API Demo

**Archivo**: `media/gifs/telecom-preview.gif`  
**Duración**: 8 segundos  
**Resolución**: 800x600

#### Guion

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    TELECOMAI DEMO (8 segundos)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  0:00-0:02  Swagger UI de TelecomAI                                    │
│  • Mostrar http://localhost:8003/docs                                   │
│  • Título: "TelecomAI Customer Intelligence API"                        │
│                                                                         │
│  0:02-0:05  Expandir /predict                                          │
│  • Llenar datos de uso del cliente                                      │
│                                                                         │
│  0:05-0:08  Resultado                                                  │
│  • Ejecutar predicción                                                  │
│  • Mostrar plan recomendado                                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### GIF 6: MLflow Dashboard (NUEVO - Recomendado)

**Archivo**: `media/gifs/mlflow-demo.gif`  
**Duración**: 10-12 segundos  
**Resolución**: 800x600

#### Guion

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    MLFLOW DEMO (10-12 segundos)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  0:00-0:03  MLflow UI Principal                                        │
│  • Mostrar http://localhost:5000                                        │
│  • Lista de experimentos visible                                        │
│                                                                         │
│  0:03-0:06  Seleccionar Experimento                                    │
│  • Click en experimento "bankchurn" o "carvision"                       │
│  • Mostrar lista de runs                                                │
│                                                                         │
│  0:06-0:09  Ver Métricas                                               │
│  • Click en un run específico                                           │
│  • Mostrar métricas: AUC, F1, Accuracy                                  │
│  • Mostrar parámetros logueados                                         │
│                                                                         │
│  0:09-0:12  Model Artifacts                                            │
│  • Mostrar sección de artifacts                                         │
│  • Modelo guardado visible                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📸 Guía de Screenshots

### Screenshots Requeridos (8 total)

| # | Nombre | Qué capturar | URL |
|:-:|--------|--------------|-----|
| 1 | `mlflow-experiments.png` | Lista de experimentos en MLflow | localhost:5000 |
| 2 | `mlflow-metrics.png` | Gráficos de métricas de un run | localhost:5000 |
| 3 | `swagger-bankchurn.png` | Swagger UI de BankChurn | localhost:8001/docs |
| 4 | `swagger-carvision.png` | Swagger UI de CarVision | localhost:8002/docs |
| 5 | `swagger-telecom.png` | Swagger UI de TelecomAI | localhost:8003/docs |
| 6 | `streamlit-dashboard.png` | Dashboard Streamlit completo | localhost:8501 |
| 7 | `streamlit-prediction.png` | Resultado de predicción en Streamlit | localhost:8501 |
| 8 | `github-actions-ci.png` | CI pipeline pasando | GitHub |

### Cómo Tomar Buenos Screenshots

1. **Usa zoom al 100%** en el navegador
2. **Limpia la URL bar** (quita extensiones visibles)
3. **Usa modo claro** para mejor legibilidad en docs
4. **Resolución mínima**: 1200x800
5. **Comprime** después con `pngquant`

```bash
# Comprimir todos los screenshots
for f in media/screenshots/*.png; do
  pngquant --quality=65-80 "$f" --output "${f%.png}-opt.png"
done
```

---

## 🎥 Guía de Video Principal

### Especificaciones

| Campo | Valor |
|-------|-------|
| **Duración** | 4-6 minutos |
| **Resolución** | 1080p (1920x1080) |
| **Formato** | MP4 |
| **Audio** | Narración clara |
| **Plataforma** | YouTube (unlisted) o Google Drive |

### Estructura del Video (Actualizada)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  VIDEO DEMO PRINCIPAL (4-6 min)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  0:00-0:30  INTRODUCCIÓN                                               │
│  ───────────────────────────────────────────────────────────────────── │
│  • "Hola, soy [nombre] y este es mi portafolio MLOps"                   │
│  • Mostrar GitHub repo                                                  │
│  • "3 proyectos ML end-to-end con CI/CD y 5 servicios dockerizados"     │
│                                                                         │
│  0:30-1:00  LEVANTAR EL STACK                                          │
│  ───────────────────────────────────────────────────────────────────── │
│  • Mostrar terminal: docker-compose up                                  │
│  • Explicar: "Con un solo comando levanto 5 servicios"                  │
│  • Mostrar docker ps con los 5 contenedores                             │
│                                                                         │
│  1:00-2:00  TOUR POR LOS 5 SERVICIOS                                   │
│  ───────────────────────────────────────────────────────────────────── │
│  • MLflow (5000): "Aquí trackeo todos los experimentos"                 │
│  • BankChurn API (8001): "API de predicción de churn"                   │
│  • CarVision API (8002): "API de precios de vehículos"                  │
│  • Streamlit (8501): "Dashboard interactivo para CarVision"             │
│  • TelecomAI API (8003): "Clasificación de planes móviles"              │
│                                                                         │
│  2:00-3:00  DEMO BANKCHURN                                             │
│  ───────────────────────────────────────────────────────────────────── │
│  • Mostrar código del pipeline sklearn                                  │
│  • Ejecutar predicción en Swagger UI                                    │
│  • Mostrar métricas en MLflow                                           │
│                                                                         │
│  3:00-4:00  DEMO CARVISION + STREAMLIT                                 │
│  ───────────────────────────────────────────────────────────────────── │
│  • Mostrar FeatureEngineer custom transformer                           │
│  • Demo en Streamlit Dashboard (gráficos + predicción)                  │
│  • Mostrar API también funcionando                                      │
│                                                                         │
│  4:00-4:30  CI/CD Y TESTING                                            │
│  ───────────────────────────────────────────────────────────────────── │
│  • Mostrar GitHub Actions                                               │
│  • Tests con 80%+ coverage                                              │
│  • Badge de CI passing                                                  │
│                                                                         │
│  4:30-5:00  ARQUITECTURA                                               │
│  ───────────────────────────────────────────────────────────────────── │
│  • Mostrar diagrama de arquitectura                                     │
│  • Stack: sklearn, MLflow, FastAPI, Streamlit, Docker                   │
│  • Configuración con Pydantic                                           │
│                                                                         │
│  5:00-5:30  CIERRE                                                     │
│  ───────────────────────────────────────────────────────────────────── │
│  • Resumen: "3 proyectos, 5 servicios, 80%+ coverage"                   │
│  • "Todo el código está en GitHub"                                      │
│  • Mostrar URL del repositorio                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Script de Narración

> **INTRO**: "Hola, soy [nombre]. Este es mi portafolio de Machine Learning y MLOps. Incluye tres proyectos completos que se ejecutan como cinco servicios dockerizados: tres APIs con FastAPI, un dashboard con Streamlit, y tracking centralizado con MLflow."

> **STACK**: "Con docker-compose levanto todo el stack. Mira, aquí puedes ver los cinco contenedores corriendo: el servidor de MLflow, las tres APIs de predicción, y el dashboard de Streamlit para CarVision."

> **TOUR**: "Déjame mostrarte cada servicio. En el puerto 5000 tenemos MLflow donde trackeo todos los experimentos. En 8001 está BankChurn para predicción de abandono de clientes. En 8002 CarVision para precios de vehículos. En 8501, que es muy importante, tenemos el dashboard de Streamlit con visualizaciones interactivas. Y en 8003 TelecomAI para clasificación de planes."

> **BANKCHURN**: "Veamos BankChurn. El modelo usa un pipeline unificado de sklearn con ColumnTransformer para preprocesamiento. Aquí hago una predicción en la API... y mira, el cliente tiene 23% de probabilidad de abandonar."

> **CARVISION**: "CarVision tiene algo especial: un custom transformer llamado FeatureEngineer que calcula features como la edad del vehículo. Pero lo mejor es el dashboard de Streamlit... aquí puedo ver análisis de datos y hacer predicciones de forma interactiva. Mira, este Toyota Camry 2020 tiene un precio estimado de $25,000."

> **CIERRE**: "Todo pasa por CI con GitHub Actions y tiene más de 80% de coverage. El código completo está en GitHub. Gracias por ver."

---

## 💻 Comandos y Scripts Útiles

### Levantar el Stack Completo

```bash
# Clonar repositorio
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Levantar los 5 servicios principales
docker-compose -f docker-compose.demo.yml up -d

# Esperar a que estén listos
sleep 45

# Verificar TODOS los servicios (5)
echo "=== Estado de los 5 servicios ==="
echo "1. MLflow (5000):"
curl -s http://localhost:5000 >/dev/null && echo "   ✅ Running" || echo "   ❌ Down"

echo "2. BankChurn API (8001):"
curl -s http://localhost:8001/health && echo ""

echo "3. CarVision API (8002):"
curl -s http://localhost:8002/health && echo ""

echo "4. CarVision Streamlit (8501):"
curl -s http://localhost:8501 >/dev/null && echo '   ✅ {"status":"healthy"}' || echo "   ❌ Down"

echo "5. TelecomAI API (8003):"
curl -s http://localhost:8003/health && echo ""

# Ver contenedores
docker-compose -f docker-compose.demo.yml ps
```

### Abrir Todas las URLs

```bash
# Linux
xdg-open http://localhost:5000 &      # MLflow
xdg-open http://localhost:8001/docs & # BankChurn
xdg-open http://localhost:8002/docs & # CarVision API
xdg-open http://localhost:8501 &      # CarVision Streamlit
xdg-open http://localhost:8003/docs & # TelecomAI

# macOS
open http://localhost:5000
open http://localhost:8001/docs
open http://localhost:8002/docs
open http://localhost:8501
open http://localhost:8003/docs
```

### PowerShell (Windows)

```powershell
# Abrir todas las URLs
Start-Process "http://localhost:5000"      # MLflow
Start-Process "http://localhost:8001/docs" # BankChurn
Start-Process "http://localhost:8002/docs" # CarVision API
Start-Process "http://localhost:8501"      # CarVision Streamlit
Start-Process "http://localhost:8003/docs" # TelecomAI
```

### Convertir Video a GIF

```bash
# Método con paleta (mejor calidad)
ffmpeg -i video.mp4 -vf "fps=12,scale=800:-1:flags=lanczos,palettegen" palette.png
ffmpeg -i video.mp4 -i palette.png -filter_complex "fps=12,scale=800:-1:flags=lanczos[x];[x][1:v]paletteuse" output.gif
rm palette.png

# Optimizar tamaño
gifsicle -O3 --colors 128 output.gif -o output-optimized.gif
```

### Ejemplos de Predicción para Demo

```bash
# BankChurn - Cliente que NO abandonará
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "credit_score": 750,
    "age": 35,
    "tenure": 8,
    "balance": 125000,
    "num_of_products": 2,
    "has_cr_card": 1,
    "is_active_member": 1,
    "estimated_salary": 95000,
    "geography": "France",
    "gender": "Female"
  }' | jq

# CarVision - Predecir precio
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "model_year": 2020,
    "model": "toyota camry",
    "condition": "good",
    "odometer": 35000,
    "fuel": "gas",
    "transmission": "automatic",
    "type": "sedan"
  }' | jq
```

---

## ✅ Checklist Final

### Material de Alta Prioridad (5 GIFs)

- [ ] `media/gifs/portfolio-demo.gif` — Demo completo (5 servicios)
- [ ] `media/gifs/bankchurn-preview.gif` — Demo API BankChurn
- [ ] `media/gifs/carvision-preview.gif` — Demo API CarVision
- [ ] `media/gifs/streamlit-carvision.gif` — Demo Streamlit Dashboard ← NUEVO
- [ ] `media/gifs/telecom-preview.gif` — Demo API TelecomAI

### Material de Alta Prioridad (Video)

- [ ] Video principal grabado (4-6 min)
- [ ] Video subido a YouTube/Drive
- [ ] Link actualizado en README.md

### Material de Media Prioridad (Screenshots)

- [ ] `mlflow-experiments.png` — Lista de experimentos
- [ ] `mlflow-metrics.png` — Métricas de un run
- [ ] `swagger-bankchurn.png` — Swagger BankChurn
- [ ] `swagger-carvision.png` — Swagger CarVision
- [ ] `swagger-telecom.png` — Swagger TelecomAI
- [ ] `streamlit-dashboard.png` — Dashboard completo
- [ ] `streamlit-prediction.png` — Resultado de predicción
- [ ] `github-actions-ci.png` — CI pasando

### Verificación Final

- [ ] Todos los GIFs pesan < 5MB
- [ ] Screenshots optimizados
- [ ] Video tiene audio claro
- [ ] READMEs actualizados con GIFs
- [ ] Links funcionan correctamente
- [ ] Git push realizado

---

## 📚 Recursos Adicionales

### Tutoriales Recomendados

- [OBS Studio Quickstart](https://obsproject.com/wiki/OBS-Studio-Quickstart)
- [ffmpeg GIF Guide](https://engineering.giphy.com/how-to-make-gifs-with-ffmpeg/)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)

### Ejemplos de Portafolios con Buenos Demos

- [made-with-ml](https://github.com/GokuMohandas/made-with-ml)
- [mlops-zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp)

---

## 🔗 Links del Portafolio

| Recurso | URL |
|---------|-----|
| **Repositorio** | https://github.com/DuqueOM/ML-MLOps-Portfolio |
| **BankChurn** | /BankChurn-Predictor |
| **CarVision** | /CarVision-Market-Intelligence |
| **TelecomAI** | /TelecomAI-Customer-Intelligence |

### URLs Locales (con Docker)

| Servicio | URL |
|----------|-----|
| MLflow | http://localhost:5000 |
| BankChurn API | http://localhost:8001/docs |
| CarVision API | http://localhost:8002/docs |
| CarVision Streamlit | http://localhost:8501 |
| TelecomAI API | http://localhost:8003/docs |

---

<div align="center">

**¡Tu portafolio tiene 5 servicios listos para demostrar!** 🚀

[← Volver al Índice](00_INDICE.md)

</div>
