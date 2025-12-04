---
title: "SYLLABUS — Guía MLOps v3"
module: "01"
order: 0
tags:
  - "syllabus"
  - "overview"
  - "roadmap"
status: "ready"
---

# 📚 SYLLABUS — Guía MLOps v3 (Portfolio Edition)

> **Versión**: 3.0 | **Duración total**: 10-12 semanas | **Nivel**: Junior → Staff

---

## 🎯 Objetivo

Transformar a un desarrollador Python en un **ML/MLOps Engineer nivel Staff** capaz de:

1. Diseñar y desplegar sistemas ML end-to-end
2. Implementar CI/CD con 80%+ coverage
3. Gestionar riesgos, fairness y governance
4. Responder incidentes y mantener sistemas en producción
5. Comunicar y presentar portafolio profesionalmente

---

## 📊 Estructura del Programa (31 Módulos + Apéndice)

### Fase 1: Fundamentos (Semanas 1-2)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 01 | **Introducción y Setup** | 4 | Entorno configurado |
| 02 | **Python Moderno** | 16 | Librería utils/ con tests |
| 03 | **Entornos y Reproducibilidad** | 8 | pyproject.toml funcional |
| 04 | **Git Profesional** | 8 | Repo con pre-commit hooks |

### Fase 2: Ingeniería de Datos (Semanas 3-4)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 05 | **Ingeniería de Datos** | 16 | ETL pipeline con tests |
| 06 | **Versionado de Datos (DVC)** | 12 | Pipeline DVC reproducible |
| 07 | **Data Lineage & Governance** 🆕 | 8 | Sistema de lineage + contratos |

### Fase 3: Feature Engineering (Semana 5)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 08 | **EDA y Calidad de Datos** | 8 | Reporte de calidad |
| 09 | **Feature Engineering** | 12 | FeatureEngineer serializable |

### Fase 4: Modelado (Semanas 6-7)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 10 | **Sklearn Pipelines** | 12 | Pipeline unificado |
| 11 | **Training Profesional** | 16 | Clase Trainer completa |
| 12 | **Tuning y Validación** | 8 | Reporte de tuning |

### Fase 5: Experiment Tracking (Semana 8)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 13 | **MLflow & DVC** | 12 | Experimentos rastreados |
| 14 | **Versionado de Modelos** | 8 | Modelo en registry |

### Fase 6: Despliegue (Semanas 9-10)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 15 | **Docker para ML** | 12 | Dockerfile multi-stage |
| 16 | **APIs con FastAPI** | 12 | API con tests |
| 17 | **Dashboards con Streamlit** | 8 | Dashboard funcional |
| 18 | **Infraestructura y Despliegue** | 8 | Documentación de infra |

### Fase 7: CI/CD & Testing (Semana 11)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 19 | **Testing para ML** | 16 | Suite de tests 80%+ coverage |
| 20 | **CI/CD con GitHub Actions** | 12 | Pipeline CI funcionando |
| 21 | **Seguridad y Testing Adversarial** 🆕 | 8 | Tests de seguridad |

### Fase 8: Producción (Semana 12)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 22 | **Observabilidad y Monitoring** | 12 | Dashboards de métricas |
| 23 | **Performance y Optimización** 🆕 | 8 | Reporte de benchmark |
| 24 | **Model Risk Management** 🆕 | 8 | Risk assessment |

### Fase 9: Mantenimiento (Semana 13)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 25 | **Mantenimiento y Runbooks** | 8 | Runbooks documentados |
| 26 | **On-call e Incidentes** 🆕 | 8 | Simulacro completado |

### Fase 10: Documentación (Semana 14)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 27 | **Model & Dataset Cards** | 6 | Cards completos |
| 28 | **Proyecto Integrador** | 16 | Portafolio validado |

### Fase 11: Habilidades Profesionales (Semana 15)

| # | Módulo | Horas | Entregable |
|:-:|:-------|:-----:|:-----------|
| 29 | **Habilidades Profesionales** | 8 | README y comunicación |
| 30 | **Simulacros de Entrevista** | 8 | Respuestas preparadas |
| 31 | **Speech y Pitch de Portafolio** | 4 | Pitch de 5-7 min |

### Apéndice

| Recurso | Descripción |
|:--------|:------------|
| Glosario | Términos MLOps |
| Recursos | Referencias y links |
| Ejercicios | Problemas adicionales |
| Plantillas | Model Card, Dataset Card, CI templates |
| Guía Audiovisual | Cómo crear demos y videos |

---

## ⏱️ Tiempo Total

| Concepto | Horas |
|:---------|------:|
| Módulos core (01-28) | ~200 |
| Módulos staff (07, 21, 23, 24, 26) | ~40 |
| Habilidades profesionales (29-31) | ~20 |
| **Total** | **~260** |

**Equivalente**: 10-12 semanas a tiempo parcial (20-25h/semana)

---

## 📋 Rúbrica de Evaluación (100 puntos)

### Código y Arquitectura (40 pts)
- [ ] **10 pts** — Pipeline sklearn unificado y serializable
- [ ] **10 pts** — Tests con ≥80% coverage
- [ ] **10 pts** — CI/CD funcionando (lint + test + build)
- [ ] **10 pts** — Docker multi-stage, non-root

### MLOps (30 pts)
- [ ] **10 pts** — MLflow tracking con métricas y artefactos
- [ ] **10 pts** — DVC pipeline reproducible
- [ ] **10 pts** — API FastAPI con validación y tests

### Documentación (15 pts)
- [ ] **5 pts** — Model Card completo
- [ ] **5 pts** — Dataset Card completo
- [ ] **5 pts** — README profesional con instrucciones

### Profesionalismo (15 pts)
- [ ] **5 pts** — Commits convencionales y PR templates
- [ ] **5 pts** — Risk assessment documentado
- [ ] **5 pts** — Pitch de portafolio preparado

---

## 🗺️ Mapa Guía → Repo

| Módulo | Archivos del Repo |
|:-------|:------------------|
| 02 Python | `src/*/config.py`, `pyproject.toml` |
| 05 ETL | `src/*/data.py`, `data/` |
| 09 Features | `src/*/features.py` |
| 10-11 Modelado | `src/*/pipeline.py`, `src/*/trainer.py` |
| 13 MLflow | `mlruns/`, `main.py --track` |
| 16 FastAPI | `app/fastapi_app.py`, `app/schemas.py` |
| 17 Streamlit | `app/streamlit_app.py` |
| 19-20 Testing | `tests/`, `.github/workflows/` |
| 27 Cards | `docs/model_card.md`, `docs/dataset_card.md` |

---

## 🚀 Quick Start

```bash
# 1. Clonar repo
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio/docs/guia_mlops

# 2. Setup entorno
make setup

# 3. Servir documentación
make serve-docs

# 4. Empezar módulo 01
open http://localhost:8000/docs/01_introduccion/
```

---

## 📆 Progreso Sugerido

```
Semana 1-2:   ████████ Módulos 01-04 (Fundamentos)
Semana 3-4:   ████████ Módulos 05-07 (Datos)
Semana 5:     ████     Módulos 08-09 (Features)
Semana 6-7:   ████████ Módulos 10-12 (Modelado)
Semana 8:     ████     Módulos 13-14 (Tracking)
Semana 9-10:  ████████ Módulos 15-18 (Despliegue)
Semana 11:    ██████   Módulos 19-21 (Testing)
Semana 12:    ██████   Módulos 22-24 (Producción)
Semana 13:    ████     Módulos 25-26 (Mantenimiento)
Semana 14:    ████     Módulos 27-28 (Documentación)
Semana 15:    ████     Módulos 29-31 (Profesional)
```

---

## ✅ Checklist Final

Antes de considerar el portafolio completo:

- [ ] `make check-all` pasa sin errores
- [ ] CI/CD verde en GitHub
- [ ] Coverage ≥ 80%
- [ ] Model Card y Dataset Card completos
- [ ] README con instrucciones de reproducción
- [ ] Pitch de 5-7 min preparado y practicado
- [ ] Risk assessment documentado
- [ ] Runbook de mantenimiento escrito

---

*Última actualización: 2024-12*
