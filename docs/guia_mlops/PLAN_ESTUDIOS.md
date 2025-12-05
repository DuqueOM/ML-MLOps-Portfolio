# 📅 Plan de Estudios — 8 Semanas

> **Roadmap detallado para completar el portafolio MLOps**

---

## 📊 Vista General

```
┌──────────────────────────────────────────────────────────────────────┐
│                    PLAN DE 8 SEMANAS                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Semana 1-2:  FUNDAMENTOS                                            │
│               Python moderno, estructura, Git, entornos              │
│                                                                      │
│  Semana 3-4:  ML ENGINEERING                                         │
│               Pipelines sklearn, feature engineering, MLflow         │
│                                                                      │
│  Semana 5-6:  MLOps CORE                                             │
│               Testing, CI/CD, Docker, APIs                           │
│                                                                      │
│  Semana 7:    PRODUCCIÓN                                             │
│               Deploy, observabilidad, infraestructura                │
│                                                                      │
│  Semana 8:    PROYECTO FINAL                                         │
│               Documentación, demo, preparación entrevistas           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

> **Consejo didáctico**: En cada módulo, antes de marcar el checkpoint como completado, revisa también la sección de **"Errores habituales y cómo depurarlos"** para consolidar patrones de debugging.
>
> **Ruta 0 → Senior/Staff**: Usa la sección **"Ruta 0 → Senior/Staff (macro-módulos)"** del [SYLLABUS](SYLLABUS.md) como mapa de alto nivel, y este plan de 8 semanas como cronograma concreto.

---

## 📚 Semana 1: Python Moderno + Estructura

### Objetivos
- [ ] Dominar type hints y Pydantic
- [ ] Crear estructura src/ layout
- [ ] Configurar pyproject.toml

### Actividades Diarias

| Día | Actividad | Tiempo | Entregable |
|:---:|:----------|:------:|:-----------|
| 1 | Leer [01_PYTHON_MODERNO](01_PYTHON_MODERNO.md) | 2h | Notas |
| 2 | Ejercicios type hints | 3h | Código tipado |
| 3 | Leer [02_DISENO_SISTEMAS](02_DISENO_SISTEMAS.md) | 2h | ML Canvas |
| 4 | Leer [03_ESTRUCTURA_PROYECTO](03_ESTRUCTURA_PROYECTO.md) | 2h | Estructura base |
| 5 | Crear proyecto BankChurn base | 3h | Repo inicial |

### Recursos
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Python Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

---

## 📚 Semana 2: Git + Entornos + DVC

### Objetivos
- [ ] Configurar pre-commit hooks
- [ ] Dominar Conventional Commits
- [ ] Inicializar DVC

### Actividades Diarias

| Día | Actividad | Tiempo | Entregable |
|:---:|:----------|:------:|:-----------|
| 1 | Leer [04_ENTORNOS](04_ENTORNOS.md) | 2h | requirements.txt |
| 2 | Leer [05_GIT_PROFESIONAL](05_GIT_PROFESIONAL.md) | 2h | pre-commit.yaml |
| 3 | Configurar pre-commit en proyecto | 2h | Hooks funcionando |
| 4 | Leer [06_VERSIONADO_DATOS](06_VERSIONADO_DATOS.md) | 2h | DVC init |
| 5 | Versionar datos de BankChurn | 3h | .dvc files |

---

## 📚 Semana 3: Pipelines sklearn

### Objetivos
- [ ] Crear Pipeline unificado
- [ ] Implementar ColumnTransformer
- [ ] Crear Custom Transformer

### Actividades Diarias

| Día | Actividad | Tiempo | Entregable |
|:---:|:----------|:------:|:-----------|
| 1-2 | Leer [07_SKLEARN_PIPELINES](07_SKLEARN_PIPELINES.md) | 4h | Pipeline básico |
| 3 | Implementar ColumnTransformer | 3h | Preprocessing |
| 4-5 | Leer [08_INGENIERIA_FEATURES](08_INGENIERIA_FEATURES.md) | 4h | FeatureEngineer class |

### Proyecto
Crear `src/bankchurn/training.py` con pipeline completo.

---

## 📚 Semana 4: Training + MLflow

### Objetivos
- [ ] Crear clase Trainer profesional
- [ ] Implementar cross-validation
- [ ] Integrar MLflow tracking

### Actividades Diarias

| Día | Actividad | Tiempo | Entregable |
|:---:|:----------|:------:|:-----------|
| 1-2 | Leer [09_TRAINING_PROFESIONAL](09_TRAINING_PROFESIONAL.md) | 4h | ChurnTrainer class |
| 3-5 | Leer [10_EXPERIMENT_TRACKING](10_EXPERIMENT_TRACKING.md) | 6h | MLflow integrado |

### Proyecto
Entrenar modelo con métricas en MLflow UI.

---

## 📚 Semana 5: Testing

### Objetivos
- [ ] Escribir tests unitarios
- [ ] Alcanzar 80% coverage
- [ ] Crear fixtures reutilizables

### Actividades Diarias

| Día | Actividad | Tiempo | Entregable |
|:---:|:----------|:------:|:-----------|
| 1-2 | Leer [11_TESTING_ML](11_TESTING_ML.md) | 4h | conftest.py |
| 3-5 | Escribir tests para BankChurn | 6h | 80% coverage |

---

## 📚 Semana 6: CI/CD + Docker + APIs

### Objetivos
- [ ] Crear GitHub Actions workflow
- [ ] Dockerfile multi-stage
- [ ] API FastAPI funcional

### Actividades Diarias

| Día | Actividad | Tiempo | Entregable |
|:---:|:----------|:------:|:-----------|
| 1 | Leer [12_CI_CD](12_CI_CD.md) | 2h | ci.yml |
| 2 | Leer [13_DOCKER](13_DOCKER.md) | 2h | Dockerfile |
| 3-4 | Leer [14_FASTAPI](14_FASTAPI.md) | 4h | /predict endpoint |
| 5 | Leer [15_STREAMLIT](15_STREAMLIT.md) | 2h | Dashboard básico |

---

## 📚 Semana 7: Producción

### Objetivos
- [ ] Implementar logging estructurado
- [ ] Entender estrategias de deploy
- [ ] Conocer Terraform/K8s básico

### Actividades Diarias

| Día | Actividad | Tiempo | Entregable |
|:---:|:----------|:------:|:-----------|
| 1-2 | Leer [16_OBSERVABILIDAD](16_OBSERVABILIDAD.md) | 4h | Logging JSON |
| 3-4 | Leer [17_DESPLIEGUE](17_DESPLIEGUE.md) | 4h | Estrategia elegida |
| 5 | Leer [18_INFRAESTRUCTURA](18_INFRAESTRUCTURA.md) | 2h | Conceptos IaC |

---

## 📚 Semana 8: Proyecto Final

### Objetivos
- [ ] Completar documentación
- [ ] Pasar rúbrica de evaluación
- [ ] Preparar para entrevistas

### Actividades Diarias

| Día | Actividad | Tiempo | Entregable |
|:---:|:----------|:------:|:-----------|
| 1 | Leer [19_DOCUMENTACION](19_DOCUMENTACION.md) | 2h | Model Card |
| 2-3 | [20_PROYECTO_INTEGRADOR](20_PROYECTO_INTEGRADOR.md) | 6h | Self-assessment |
| 4 | Revisar [21_GLOSARIO](21_GLOSARIO.md) | 2h | Términos dominados |
| 5 | Simulacros de entrevista | 3h | Preparación lista |

---

## ⏱️ Tiempo Total Estimado

| Componente | Horas |
|:-----------|------:|
| Lectura de módulos | 40h |
| Ejercicios prácticos | 30h |
| Proyecto BankChurn | 20h |
| Proyectos adicionales | 20h |
| **TOTAL** | **110h** |

**Dedicación sugerida**: 15-20 horas/semana

---

## ✅ Checklist de Finalización

- [ ] 3 proyectos funcionando (BankChurn, CarVision, TelecomAI)
- [ ] CI/CD pasando en los 3
- [ ] Coverage ≥80% en todos
- [ ] APIs dockerizadas
- [ ] READMEs profesionales
- [ ] Model Cards completos

---

<div align="center">

[← Volver al Índice](00_INDICE.md)

</div>
