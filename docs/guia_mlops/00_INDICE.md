# 📚 Guía MLOps — Portfolio Edition

> **De Python Básico a Senior/Staff en MLOps**
> 
> Esta guía está diseñada para reproducir el portafolio ML completo desde cero, con todo el conocimiento técnico y práctico necesario.

---

## 🎯 Objetivo

Al completar esta guía serás capaz de:

- ✅ Construir los 3 proyectos ML del portafolio desde cero
- ✅ Implementar CI/CD con 80%+ de coverage
- ✅ Diseñar arquitecturas ML production-ready
- ✅ Pasar entrevistas técnicas nivel Senior/Staff

## 🧭 Cómo usar esta guía

Esta guía está pensada como un recorrido completo **de Python básico a perfil Senior/Staff en ML/MLOps** usando este mismo portafolio como proyecto integrador.

- **Perfil de entrada**: Python básico (funciones, clases, módulos), Git elemental y comodidad con la terminal.
- **Estructura didáctica**: 23 módulos en 6 fases, cada uno con teoría aplicada al portafolio, ejemplos reales y ejercicios prácticos.
- **Ruta sugerida**:
  - Usa el [SYLLABUS](SYLLABUS.md) y el [PLAN_ESTUDIOS](PLAN_ESTUDIOS.md) para seguir el programa de 8 semanas.
  - Para cada módulo: lee el `.md` correspondiente, replica los pasos en uno de los 3 proyectos y resuelve los ejercicios de [EJERCICIOS.md](EJERCICIOS.md).
  - Revisa [EJERCICIOS_SOLUCIONES.md](EJERCICIOS_SOLUCIONES.md) solo para contrastar o desbloquearte.
  - Anota los **errores que encuentres** y compáralos con las secciones de errores habituales de cada módulo.
- **Proyecto integrador**: al final, usa [20_PROYECTO_INTEGRADOR.md](20_PROYECTO_INTEGRADOR.md) y la [RÚBRICA_EVALUACION](RUBRICA_EVALUACION.md) para validar que tu portafolio reproduce el original de 0 a 100.
- **Presentación y demo**: apóyate en [GUIA_AUDIOVISUAL.md](GUIA_AUDIOVISUAL.md), [24_SPEECH_PORTAFOLIO_MLOPS.md](24_SPEECH_PORTAFOLIO_MLOPS.md) y [25_TALKING_POINTS_PORTAFOLIO_MLOPS.md](25_TALKING_POINTS_PORTAFOLIO_MLOPS.md) para grabar video, audio y preparar entrevistas.

---

## 📊 Roadmap Visual

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                        RUTA DE APRENDIZAJE                                  ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  FASE 1: FUNDAMENTOS         FASE 2: ML ENGINEERING      FASE 3: MLOps      ║
║  ──────────────────         ────────────────────        ─────────────       ║
║  [01] Python Moderno        [07] sklearn Pipelines      [11] Testing ML     ║
║  [02] Diseño de Sistemas    [08] Feature Engineering    [12] CI/CD          ║
║  [03] Estructura Proyecto   [09] Training Profesional   [13] Docker         ║
║  [04] Entornos              [10] Experiment Tracking    [14] APIs (FastAPI) ║
║  [05] Git Profesional                                   [15] Dashboards     ║
║  [06] Versionado Datos                                  [16] Observabilidad ║
║                                                                             ║
║  FASE 4: PRODUCCIÓN          FASE 5: ESPECIALIZACIÓN    FASE 6: MAESTRÍA    ║
║  ──────────────────         ────────────────────        ─────────────────   ║
║  [17] Despliegue            [19] Documentación          [22] Checklist Pro  ║
║  [18] Infraestructura       [20] Proyecto Integrador    [23] Recursos       ║
║                             [21] Glosario                                   ║
║                                                                             ║
║  ════════════════════════════════════════════════════════════════════════   ║
║                                                                             ║
║     🎯 MATERIAL COMPLEMENTARIO:                                            ║
║     • Ejercicios Prácticos (EJERCICIOS.md)                                  ║
║     • Soluciones Detalladas (EJERCICIOS_SOLUCIONES.md)                      ║
║     • Simulacros de Entrevista (SIMULACRO_*.md)                             ║
║     • Rúbrica de Evaluación (RUBRICA_EVALUACION.md)                         ║
║     • Guía Audiovisual (GUIA_AUDIOVISUAL.md)                                ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

## 📖 Índice de Módulos

### FASE 1: Fundamentos de Ingeniería (Semanas 1-2)

| # | Módulo | Descripción | Proyecto Relacionado |
|---|--------|-------------|---------------------|
| 01 | [Python Moderno](01_PYTHON_MODERNO.md) | Type hints, Pydantic, src/ layout, SOLID | Todos |
| 02 | [Diseño de Sistemas ML](02_DISENO_SISTEMAS.md) | ML Canvas, C4 Model, ADRs | Todos |
| 03 | [Estructura de Proyecto](03_ESTRUCTURA_PROYECTO.md) | pyproject.toml, Makefile, organización | Todos |
| 04 | [Entornos Reproducibles](04_ENTORNOS.md) | venv, Poetry, Docker, dependencias | Todos |
| 05 | [Git Profesional](05_GIT_PROFESIONAL.md) | Conventional Commits, pre-commit, branching | Todos |
| 06 | [Versionado de Datos](06_VERSIONADO_DATOS.md) | DVC, pipelines de datos, artifacts | Todos |

### FASE 2: ML Engineering (Semanas 3-4)

| # | Módulo | Descripción | Proyecto Relacionado |
|---|--------|-------------|---------------------|
| 07 | [sklearn Pipelines](07_SKLEARN_PIPELINES.md) | Pipeline, ColumnTransformer, Custom Transformers | Todos |
| 08 | [Ingeniería de Features](08_INGENIERIA_FEATURES.md) | Data leakage, feature engineering seguro | CarVision, BankChurn |
| 09 | [Training Profesional](09_TRAINING_PROFESIONAL.md) | ChurnTrainer, CV, gestión de artefactos | BankChurn |
| 10 | [Experiment Tracking](10_EXPERIMENT_TRACKING.md) | MLflow, Registry, Signatures | Todos |

### FASE 3: MLOps Core (Semanas 5-6)

| # | Módulo | Descripción | Proyecto Relacionado |
|---|--------|-------------|---------------------|
| 11 | [Testing para ML](11_TESTING_ML.md) | Pirámide de testing, fixtures, 80% coverage | Todos |
| 12 | [CI/CD con GitHub Actions](12_CI_CD.md) | Matrix testing, coverage, security scanning | Todos |
| 13 | [Docker Avanzado](13_DOCKER.md) | Multi-stage, non-root, docker-compose | Todos |
| 14 | [FastAPI para ML](14_FASTAPI.md) | Schemas, endpoints, error handling | Todos |
| 15 | [Streamlit Dashboards](15_STREAMLIT.md) | Caching, tabs, visualizaciones | CarVision |
| 16 | [Observabilidad](16_OBSERVABILIDAD.md) | Prometheus, logging, drift detection | Todos |

### FASE 4: Producción (Semana 7)

| # | Módulo | Descripción | Proyecto Relacionado |
|---|--------|-------------|---------------------|
| 17 | [Despliegue](17_DESPLIEGUE.md) | Lambda vs ECS vs K8s, estrategias | Todos |
| 18 | [Infraestructura como Código](18_INFRAESTRUCTURA.md) | Terraform, Kubernetes basics | Avanzado |

### FASE 5: Especialización (Semana 8)

| # | Módulo | Descripción | Proyecto Relacionado |
|---|--------|-------------|---------------------|
| 19 | [Documentación y Ética](19_DOCUMENTACION.md) | Model Cards, Data Cards, MkDocs | Todos |
| 20 | [Proyecto Integrador](20_PROYECTO_INTEGRADOR.md) | Rúbrica 100 puntos, checklist completo | Nuevo proyecto |
| 21 | [Glosario MLOps](21_GLOSARIO.md) | Términos y definiciones | Referencia |

### FASE 6: Maestría

| # | Módulo | Descripción | Proyecto Relacionado |
|---|--------|-------------|---------------------|
| 22 | [Checklist Profesional](22_CHECKLIST.md) | Verificación pre-deploy | Todos |
| 23 | [Recursos y Referencias](23_RECURSOS.md) | Libros, cursos, papers | Aprendizaje continuo |

---

## 📚 Material Complementario

| Recurso | Descripción |
|---------|-------------|
| [Ejercicios Prácticos](EJERCICIOS.md) | Ejercicios por módulo |
| [Soluciones Detalladas](EJERCICIOS_SOLUCIONES.md) | Soluciones con explicaciones |
| [Simulacro Entrevista Senior](SIMULACRO_ENTREVISTA_LEAD_SENIOR.md) | Preguntas nivel senior |
| [Simulacro Entrevista Parte 2](SIMULACRO_ENTREVISTA_PARTE2.md) | Más preguntas avanzadas |
| [Rúbrica de Evaluación](RUBRICA_EVALUACION.md) | Criterios de evaluación |
| [Guía Audiovisual](GUIA_AUDIOVISUAL.md) | Videos y recursos multimedia |
| [Speech Portafolio MLOps](24_SPEECH_PORTAFOLIO_MLOPS.md) | Guion largo para narrar todo el portafolio en formato charla o audio |
| [Talking Points Portafolio](25_TALKING_POINTS_PORTAFOLIO_MLOPS.md) | Puntos clave breves para entrevistas técnicas y revisiones de código |
| [Syllabus](SYLLABUS.md) | Programa detallado del curso |
| [Plan de Estudios](PLAN_ESTUDIOS.md) | Cronograma sugerido |
| [Decisiones Técnicas](DECISIONES_TECH.md) | ADRs del portafolio |
| [Plantillas](PLANTILLAS.md) | Templates reutilizables |
| Scripts PDF/Audio | `generate_pdfs.py` y `generate_audio.py` para exportar la guía a PDF y MP3 |

---

## 🏗️ Proyectos del Portafolio

Esta guía te prepara para construir:

### 1. BankChurn-Predictor
- **Problema**: Clasificación binaria (churn/no-churn)
- **Técnicas**: RandomForest, SMOTE, Class Weighting
- **Coverage**: 79%+

### 2. CarVision-Market-Intelligence
- **Problema**: Regresión (predicción de precios)
- **Técnicas**: Custom FeatureEngineer, RandomForest
- **Coverage**: 97%

### 3. TelecomAI-Customer-Intelligence
- **Problema**: Clasificación multiclase
- **Técnicas**: LogisticRegression, GradientBoosting
- **Coverage**: 97%

---

## ⚡ Quick Start

```bash
# Clonar el portafolio
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Empezar con BankChurn
cd BankChurn-Predictor
pip install -e ".[dev]"
make train
make test
make serve
```

---

## 📈 Progreso Sugerido

```
Semana 1-2: Módulos 01-06 (Fundamentos)
Semana 3-4: Módulos 07-10 (ML Engineering)
Semana 5-6: Módulos 11-16 (MLOps)
Semana 7:   Módulos 17-18 (Producción)
Semana 8:   Módulos 19-23 + Proyecto Integrador
```

---

## ✅ Convenciones de la Guía

| Símbolo | Significado |
|---------|-------------|
| 💡 | Tip o consejo práctico |
| ⚠️ | Advertencia importante |
| ❌ | Anti-patrón o error común |
| ✅ | Buena práctica |
| 🔧 | Ejercicio práctico |
| 📝 | Nota o aclaración |
| 🎯 | Objetivo de aprendizaje |

---

<div align="center">

**¡Empieza ahora!** → [01. Python Moderno](01_PYTHON_MODERNO.md)

</div>

---

## 📚 Material Complementario Adicional

| Recurso | Descripción |
|---------|-------------|
| [Plantillas](PLANTILLAS.md) | Templates README, pyproject.toml, Dockerfile |
| [Decisiones Técnicas](DECISIONES_TECH.md) | ADRs: Por qué elegimos cada herramienta |
| [Plan de Estudios](PLAN_ESTUDIOS.md) | Roadmap detallado de 10 semanas |
