# ════════════════════════════════════════════════════════════════════════════════
# MÓDULO 17: PROYECTO INTEGRADOR
# Demo, Pitch y Preparación para Entrevistas
# Guía MLOps v5.0: Senior Edition | DuqueOM | Noviembre 2025
# ════════════════════════════════════════════════════════════════════════════════

<div align="center">

# 🎓 MÓDULO 17: Proyecto Integrador

### El Artefacto que Te Conseguirá el Trabajo

*"Tu portafolio es tu mejor carta de presentación."*

| Duración             | Teoría               | Práctica             |
| :------------------: | :------------------: | :------------------: |
| **4-5 horas**        | 20%                  | 80%                  |

</div>

---

## 🎯 Lo Que Lograrás

1. **Integrar** todo lo aprendido en un proyecto cohesivo
2. **Crear** una demo profesional
3. **Preparar** el pitch para entrevistas
4. **Publicar** el portafolio

---

## 17.1 Checklist Final del Proyecto

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    CHECKLIST PROYECTO COMPLETO                                ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   CÓDIGO:                                                                     ║
║   [x] Estructura profesional (src/ layout)                                    ║
║   [x] Tipado completo (mypy pasa)                                             ║
║   [x] Configuración Pydantic                                                  ║
║   [x] Pipeline sklearn unificado                                              ║
║   [x] Tests > 80% coverage                                                    ║
║                                                                               ║
║   VERSIONADO:                                                                 ║
║   [x] Git con Conventional Commits                                            ║
║   [x] Pre-commit hooks                                                        ║
║   [x] DVC para datos                                                          ║
║   [x] MLflow para experimentos                                                ║
║                                                                               ║
║   CI/CD:                                                                      ║
║   [x] GitHub Actions (lint, test, build)                                      ║
║   [x] Docker multi-stage                                                      ║
║   [x] Imagen < 500MB                                                          ║
║                                                                               ║
║   API:                                                                        ║
║   [x] FastAPI profesional                                                     ║
║   [x] Validación Pydantic                                                     ║
║   [x] Health check                                                            ║
║   [x] Error handling                                                          ║
║                                                                               ║
║   DOCUMENTACIÓN:                                                              ║
║   [x] README con badges                                                       ║
║   [x] MkDocs publicado                                                        ║
║   [x] Model Card completo                                                     ║
║   [x] ADRs documentados                                                       ║
║                                                                               ║
║   DEMO:                                                                       ║
║   [x] Video 3-5 minutos                                                       ║
║   [x] Script de demo funcional                                                ║
║   [x] Slides de presentación                                                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 17.2 Script de Demo

```bash
#!/bin/bash
# scripts/demo.sh - Demo completa del proyecto

set -e

echo "🚀 BankChurn Predictor - Demo"
echo "=============================="

# 1. Mostrar estructura
echo ""
echo "📁 Estructura del proyecto:"
tree -L 2 --dirsfirst -I '__pycache__|*.pyc|.git|.venv'

# 2. Ejecutar tests
echo ""
echo "🧪 Ejecutando tests..."
pytest tests/ -v --cov=src/bankchurn --cov-report=term-missing | head -50

# 3. Entrenar modelo
echo ""
echo "🤖 Entrenando modelo..."
python -m bankchurn.main --config configs/config.yaml

# 4. Mostrar MLflow
echo ""
echo "📊 Experimentos en MLflow:"
echo "Abrir: http://localhost:5000"

# 5. Iniciar API
echo ""
echo "🌐 Iniciando API..."
uvicorn app.main:app --port 8000 &
API_PID=$!
sleep 3

# 6. Test de predicción
echo ""
echo "🔮 Probando predicción..."
curl -s -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "credit_score": 650,
    "age": 35,
    "tenure": 5,
    "balance": 50000,
    "num_of_products": 2,
    "has_cr_card": true,
    "is_active_member": true,
    "estimated_salary": 75000,
    "geography": "France",
    "gender": "Female"
  }' | jq .

# 7. Health check
echo ""
echo "💚 Health check:"
curl -s http://localhost:8000/health | jq .

# Cleanup
kill $API_PID 2>/dev/null || true

echo ""
echo "✅ Demo completada!"
```

---

## 17.3 Video Demo (Guión)

### Estructura del Video (3-5 min)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    GUIÓN VIDEO DEMO (3-5 minutos)                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   0:00 - 0:30  INTRO                                                          ║
║   "Hola, soy [Nombre]. Les presento BankChurn Predictor, un sistema           ║
║    MLOps completo para predecir abandono de clientes bancarios."              ║
║                                                                               ║
║   0:30 - 1:00  PROBLEMA DE NEGOCIO                                            ║
║   "El banco pierde $2M/año por clientes que abandonan. Este sistema           ║
║    identifica el top 10% en riesgo, generando $400K de ahorro."               ║
║                                                                               ║
║   1:00 - 2:00  ARQUITECTURA (mostrar diagrama)                                ║
║   "El sistema tiene: Pipeline ML reproducible con DVC, tracking en            ║
║    MLflow, API FastAPI, contenedor Docker, y monitoreo con Prometheus."       ║
║                                                                               ║
║   2:00 - 3:30  DEMO EN VIVO                                                   ║
║   • Mostrar código (estructura, tipado, tests)                                ║
║   • Ejecutar pipeline de entrenamiento                                        ║
║   • Mostrar MLflow UI                                                         ║
║   • Probar API con curl                                                       ║
║   • Mostrar dashboard Grafana                                                 ║
║                                                                               ║
║   3:30 - 4:00  RESULTADOS                                                     ║
║   "El modelo logra AUC 0.87, latencia P99 de 45ms, y 85% coverage."           ║
║                                                                               ║
║   4:00 - 4:30  CIERRE                                                         ║
║   "El código está en GitHub. Gracias por ver. ¿Preguntas?"                    ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Tips para el Video

- **Herramienta**: Loom, OBS, o QuickTime
- **Resolución**: 1080p mínimo
- **Audio**: Micrófono externo si es posible
- **Edición**: Cortar silencios, agregar zooms

---

## 17.4 Preparación para Entrevistas

### Preguntas Técnicas Frecuentes

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    PREGUNTAS FRECUENTES EN ENTREVISTAS                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   MLOPS GENERAL:                                                              ║
║   Q: ¿Qué es MLOps y por qué es importante?                                   ║
║   A: Es la práctica de llevar modelos ML a producción de forma confiable...   ║
║                                                                               ║
║   Q: ¿Cómo manejas data drift?                                                ║
║   A: Monitoreo con Evidently, alertas si drift > 10%, retraining trigger...   ║
║                                                                               ║
║   Q: ¿Cómo aseguras reproducibilidad?                                         ║
║   A: DVC para datos, MLflow para experimentos, Docker para ambiente...        ║
║                                                                               ║
║   SOBRE TU PROYECTO:                                                          ║
║   Q: ¿Por qué elegiste Random Forest sobre XGBoost?                           ║
║   A: [ADR documentado] Baseline interpretable, performance similar...         ║
║                                                                               ║
║   Q: ¿Cómo manejas el desbalanceo de clases?                                  ║
║   A: class_weight='balanced' + métricas apropiadas (AUC, Precision@K)...      ║
║                                                                               ║
║   Q: ¿Qué harías diferente si tuvieras más tiempo?                            ║
║   A: Feature store, A/B testing framework, modelo más interpretable...        ║
║                                                                               ║
║   SISTEMA DESIGN:                                                             ║
║   Q: ¿Cómo escalarías a 10x tráfico?                                          ║
║   A: HPA en K8s, caching de predicciones, batch async para grandes vols...    ║
║                                                                               ║
║   Q: ¿Cómo manejarías un modelo que se degrada?                               ║
║   A: Rollback automático, monitoreo de métricas, champion/challenger...       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Tu Pitch (30 segundos)

```
"Soy [Nombre], ML Engineer con experiencia en sistemas end-to-end.

Mi proyecto BankChurn Predictor demuestra MLOps completo: pipeline 
reproducible con DVC y MLflow, API FastAPI containerizada, CI/CD con 
GitHub Actions, y monitoreo con Prometheus.

El sistema logra AUC 0.87 con latencia P99 de 45ms, y tiene 85% 
test coverage. Todo el código está documentado y disponible en GitHub."
```

---

## 17.5 Publicación del Portafolio

### GitHub Profile README

```markdown
# 👋 Hola, soy [Tu Nombre]

## 🚀 ML Engineer | MLOps Practitioner

Especializado en llevar modelos de Machine Learning a producción.

### 📂 Proyectos Destacados

| Proyecto | Descripción | Stack |
|----------|-------------|-------|
| [BankChurn Predictor](link) | Sistema MLOps end-to-end | Python, FastAPI, Docker, K8s |
| [CarVision](link) | Predicción de precios de vehículos | Sklearn, DVC, MLflow |

### 🛠️ Tech Stack

![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/-Kubernetes-326CE5?logo=kubernetes&logoColor=white)

### 📊 GitHub Stats

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=username)
```

---

## 17.6 Certificación de Completitud

### Auto-Evaluación Final

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    CERTIFICACIÓN DE COMPLETITUD                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   CONFIRMO QUE:                                                               ║
║                                                                               ║
║   [ ] He completado los 17 módulos de la guía                                 ║
║   [ ] Mi proyecto tiene todos los componentes del checklist                   ║
║   [ ] Los tests pasan y coverage > 80%                                        ║
║   [ ] La documentación está completa y publicada                              ║
║   [ ] El video demo está grabado                                              ║
║   [ ] El código está en un repositorio público                                ║
║   [ ] Puedo explicar cada decisión técnica                                    ║
║   [ ] Estoy preparado para entrevistas técnicas                               ║
║                                                                               ║
║   Nombre: _______________________                                              ║
║   Fecha:  _______________________                                              ║
║   GitHub: _______________________                                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 🎉 ¡Felicitaciones!

Has completado la **Guía MLOps v5.0: Senior Edition**.

Ahora tienes:
- ✅ Un portafolio profesional
- ✅ Conocimientos de nivel Senior
- ✅ Habilidades prácticas comprobables
- ✅ Material para entrevistas

**El siguiente paso es tuyo: aplica a roles MLOps, ML Engineer, o Data Engineer.**

---

<div align="center">

# 🚀 ¡A Conquistar el Mundo!

*"El viaje de mil deploys comenzó con un solo git commit."*

*© 2025 DuqueOM - Guía MLOps v5.0: Senior Edition*

</div>
