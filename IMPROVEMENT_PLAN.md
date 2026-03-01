# Plan de Mejora del Portafolio ML/MLOps — v6.1 → v7.0

> **Baseline**: Tag v6.1 | **Objetivo**: Subir de percentil 75-80% → 90-95% entre juniors MLOps
> **Fecha inicio**: Febrero 2026

---

## FASE 1: Quick Fixes (Seguridad + Code Quality) — ~1 hora

### 1a. CORS Security Fix
**Problema**: `allow_origins=["*"]` + `allow_credentials=True` es un red flag de seguridad.
**Solución**: CORS configurable por variable de entorno, defaults restrictivos.

**Archivos a modificar**:
- `BankChurn-Predictor/app/fastapi_app.py`
- `CarVision-Market-Intelligence/app/fastapi_app.py`
- `TelecomAI-Customer-Intelligence/app/fastapi_app.py` (→ luego será NLP)
- `BankChurn-Predictor/configs/config.yaml`

### 1b. Eliminar sys.path.insert anti-pattern
**Problema**: Manipulación manual de `sys.path` es un anti-pattern de producción.
**Solución**: Usar `pip install -e .` en Dockerfiles y desarrollo. Los `pyproject.toml` ya existen.

**Archivos a modificar**:
- Todos los `main.py` y `app/fastapi_app.py`
- Todos los `Dockerfile` (agregar `pip install -e .`)
- `Makefile` (agregar install editable)

---

## FASE 2: BankChurn ML Upgrade — ~3-5 horas

### Objetivo: AUC 0.87 → 0.91+, demostrar ML depth

**NO cambiar dataset** — el dataset de Bank Churn (10K filas) es suficiente.
Lo que falta es **feature engineering avanzado** y **modeling sofisticado**.

### 2a. Feature Engineering Avanzado
Agregar a `src/bankchurn/features.py` (nuevo módulo):
- **Interaction features**: `Age × NumOfProducts`, `Balance × IsActiveMember`
- **Binning inteligente**: Age groups, Balance quartiles, Tenure bands
- **Statistical features**: `Balance/EstimatedSalary` ratio, `CreditScore` z-score
- **Risk scoring**: composite features basadas en dominio bancario
- **Polynomial features**: degree=2 para features numéricas clave

### 2b. Modeling Avanzado
- **Stacking Classifier**: LR + RF + XGBoost como base, LogReg como meta-learner
- **Calibration**: CalibratedClassifierCV para probabilidades calibradas
- **Threshold optimization**: Optimize F1/business metric en lugar de default 0.5
- **Feature selection**: SelectFromModel o recursive feature elimination

### 2c. Métricas de Negocio
- Profit curve analysis (costo de FP vs FN)
- Expected calibration error (ECE)
- Lift/gain charts automatizados

---

## FASE 3: CarVision ML Upgrade — ~3-5 horas

### Objetivo: R² 0.77 → 0.90+, demostrar data engineering real

### 3a. Dataset Upgrade (RECOMENDADO)
**Opción A (PREFERIDA)**: Usar el dataset de Craigslist Vehicles (~420K filas)
- Disponible en Kaggle: https://www.kaggle.com/datasets/austinreese/craigslist-carstrucks-data
- Datos reales, messy, con missings, outliers → demuestra manejo de datos de producción
- Licencia: CC0 (Public Domain)

**Opción B**: Mantener dataset actual pero con feature engineering agresivo.

### 3b. Feature Engineering Avanzado
- **Target encoding** para marcas de alto cardinalidad
- **Geospatial features**: region/state clustering
- **Market features**: precio promedio por marca/modelo/año
- **Text features**: extraer info de "model" field (trim, engine, transmission)
- **Temporal**: depreciación no-lineal (exponential decay por edad)

### 3c. Modeling Avanzado
- **LightGBM/XGBoost** con hyperparameter tuning (Optuna)
- **Quantile regression** para intervalos de predicción (uncertainty)
- **Feature importance** con permutation importance + SHAP

---

## FASE 4: Reemplazar TelecomAI → Proyecto NLP — ~8-12 horas

### ESTA ES LA MEJORA MÁS IMPACTANTE DEL PLAN

**Proyecto**: `NLPInsight-Analyzer` — Análisis de Sentimiento con Transformers
**Stack**: HuggingFace Transformers + PyTorch + FastAPI

### 4a. Concepto
- **Task**: Multi-class sentiment classification (positive/negative/neutral)
- **Model**: Fine-tuned DistilBERT (eficiente para deploy, demuestra transfer learning)
- **Dataset**: IMDB Reviews (50K) o Financial PhraseBank (4.8K frases financieras)
  - Financial PhraseBank es más "enterprise" y encaja con el tema financiero del portafolio
- **Diferenciador**: Demuestra NLP real, PyTorch, HuggingFace, GPU-awareness, ONNX export

### 4b. Arquitectura
```
src/nlpinsight/
├── config.py          # Pydantic config
├── data.py            # Data loading, tokenization
├── training.py        # Fine-tuning pipeline
├── models.py          # Model definitions
├── inference.py       # Optimized inference (ONNX optional)
├── evaluation.py      # Metrics, confusion matrix
└── __init__.py

app/
├── fastapi_app.py     # API con /predict, /batch, /health, /metrics
└── __init__.py

configs/config.yaml
tests/
├── test_data.py
├── test_training.py
├── test_api.py
├── test_inference.py
└── conftest.py
```

### 4c. Features que demuestran ML avanzado
- **Transfer Learning**: Fine-tuning de modelo pre-entrenado
- **Tokenization pipeline**: Manejo de texto, padding, truncation
- **GPU-aware training**: `device = "cuda" if torch.cuda.is_available() else "cpu"`
- **Model optimization**: ONNX export para inference rápida
- **Batch inference**: Procesamiento eficiente de múltiples textos
- **Prometheus metrics**: Latencia de tokenización + inferencia separadas

### 4d. Integración con infraestructura existente
- Dockerfile con soporte GPU (base `pytorch/pytorch` o `python:3.11-slim` + torch CPU)
- K8s deployment con resource limits para GPU-optional
- CI/CD: tests sin GPU, build con torch CPU
- Mantener el patrón de API: FastAPI + Pydantic + Prometheus

---

## FASE 5: GitHub Fixes — ~2 horas

### 5a. GHCR Packages
- Verificar permisos del workflow `ghcr-publish`
- Asegurar que `packages: write` está en los permisos
- Hacer un push a main que trigger el publish
- Verificar que aparecen los packages en GitHub

### 5b. Git Practices
- Desde ahora: feature branches + squash merges
- Crear branch `feature/ml-upgrade-v7` para todo este trabajo
- PR con description clara al hacer merge
- Agregar `.github/PULL_REQUEST_TEMPLATE.md` mejorado

---

## FASE 6: Documentación y Justificación — ~2 horas

### 6a. Over-engineering Justification
Agregar a `docs/architecture/decisions.md` un ADR:
```
ADR-015: Why Full K8s Stack for Simple Models

Context: The models are intentionally simple (tabular sklearn) because 
the portfolio's PRIMARY goal is demonstrating MLOps infrastructure capabilities.

Decision: Use production-grade infrastructure (K8s, Terraform, multi-cloud)
to showcase the deployment pipeline, not the model complexity.

Rationale:
- "The value of MLOps is independent of model complexity"
- The same pipeline serves a linear regression or a 100B parameter LLM
- Infrastructure skills are evaluated separately from ML skills
- After FASE 4 (NLP project), both infrastructure AND ML depth are demonstrated
```

### 6b. Actualizar toda la documentación
- README.md: métricas actualizadas, nuevo proyecto NLP
- Model cards: actualizadas para BankChurn y CarVision
- ARCHITECTURE_PORTFOLIO.md: nuevo diagrama con NLP
- mkdocs.yml: nueva sección para NLP project

---

## Impacto Esperado en Perfil (Pregunta 6)

### Antes (v6.1)
| Dimensión | Score | Percentil |
|-----------|-------|-----------|
| Infra/Cloud | 8.5/10 | Top 10-15% |
| ML/DS | 6.5/10 | 40-50% |
| CI/CD | 8.0/10 | Top 15% |
| Testing | 7.5/10 | Top 10% |
| Docs | 9.0/10 | Top 5% |
| **TOTAL** | **7.7/10** | **Top 20-25%** |

### Después (v7.0)
| Dimensión | Score | Percentil | Cambio |
|-----------|-------|-----------|--------|
| Infra/Cloud | 8.5/10 | Top 10-15% | = |
| ML/DS | **8.5/10** | **Top 10-15%** | +2.0 ↑↑ |
| CI/CD | 8.5/10 | Top 10% | +0.5 ↑ |
| Testing | 8.0/10 | Top 10% | +0.5 ↑ |
| Docs | 9.0/10 | Top 5% | = |
| Security | **8.0/10** | **Top 15%** | NEW |
| **TOTAL** | **8.5/10** | **Top 10-15%** | +0.8 ↑↑ |

### Impacto en contratabilidad
| Mercado | Antes | Después |
|---------|-------|---------|
| México | 35-45% | **50-60%** |
| LATAM remoto | 25-35% | **40-50%** |
| USA remoto (startups) | 10-20% | **25-35%** |
| Europa remoto | 10-15% | **20-30%** |

### Roles adicionales que se desbloquean
- ✅ **Junior ML Engineer** — el proyecto NLP demuestra versatilidad ML real
- ✅ **AI Engineer** — HuggingFace + PyTorch + deployment = AI Engineering moderno
- ⬆️ **MLOps Mid-level** — con este portafolio + 6 meses de experiencia laboral

---

## Orden de Ejecución

1. ✅ Tag v6.1
2. ⏳ FASE 1: Quick fixes (CORS + sys.path)
3. ⏳ FASE 2: BankChurn ML upgrade
4. ⏳ FASE 3: CarVision ML upgrade  
5. ⏳ FASE 4: NLP Project (mayor esfuerzo)
6. ⏳ FASE 5: GitHub fixes
7. ⏳ FASE 6: Documentación
8. ⏳ Tag v7.0

