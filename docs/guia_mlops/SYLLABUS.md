# 📅 SYLLABUS — Guía MLOps v2 (Portfolio Edition)

> **Programa completo de 6-8 semanas para construir un portafolio ML/MLOps profesional desde cero**

---

## 🎯 Objetivo del Programa

Al completar este programa serás capaz de:

- ✅ **Reproducir 100%** de los artefactos clave del portafolio (modelos, APIs, dashboards)
- ✅ Implementar **CI/CD profesional** con 80%+ coverage
- ✅ Diseñar **arquitecturas ML production-ready**
- ✅ **Pasar entrevistas técnicas** nivel Senior/Staff
- ✅ Crear **Model Cards y Dataset Cards** completos
- ✅ Implementar **observabilidad y monitoreo** básico

---

## 📊 Estructura del Programa (12 Módulos)

| Módulo | Nombre | Duración | Mini-Proyecto |
|:------:|:-------|:--------:|:--------------|
| 00 | Introducción | 0.5 días | Setup inicial |
| 01 | Python Moderno | 2 días | Librería `utils/` |
| 02 | Ingeniería de Datos | 4 días | ETL reproducible |
| 03 | Feature Engineering | 3 días | Transformadores `.pkl` |
| 04 | Modelado | 6 días | Scripts de entrenamiento |
| 05 | MLflow & DVC | 3 días | Tracking local |
| 06 | Despliegue API | 3 días | FastAPI `/predict` |
| 07 | Dashboard | 2 días | Streamlit app |
| 08 | CI/CD & Testing | 3 días | GitHub Actions |
| 09 | Model & Dataset Cards | 1.5 días | Documentación ML |
| 10 | Observabilidad | 2 días | Logging + alertas |
| 11 | Mantenimiento & Auditoría | 2 días | Runbooks |

**Tiempo total estimado**: 32 días (~6-8 semanas a ritmo moderado)

---

## 📚 Detalle por Módulo

### Módulo 00 — Introducción (0.5 días)

| Contenido | Entregable |
|:----------|:-----------|
| Objetivos del curso | ✅ Entender el roadmap |
| Cómo leer la guía | ✅ Setup de herramientas |
| Requerimientos mínimos | ✅ Entorno listo |
| Mapa guía → repo | ✅ Comprensión de estructura |

**Output**: Entorno de desarrollo listo, comprensión clara del objetivo final.

---

### Módulo 01 — Python Moderno (2 días)

| Contenido | Entregable |
|:----------|:-----------|
| Type hints y tipado estático | Código tipado |
| Dataclasses y Pydantic | Config validado |
| OOP y SOLID básico | Clases bien diseñadas |
| Estructura de paquete | `utils/` funcional |

**Mini-Proyecto**: Crear librería `utils/` con `config.py` (Pydantic) y `mathops.py` (funciones tipadas).

**Validar**: `make check-01`

---

### Módulo 02 — Ingeniería de Datos (4 días)

| Contenido | Entregable |
|:----------|:-----------|
| Lectura/escritura de datos | Loaders reutilizables |
| Validación con schemas | Contratos de datos |
| Transformaciones básicas | ETL reproducible |
| Tests de integridad | Datos validados |

**Mini-Proyecto**: ETL que produce CSV/Parquet reproducible + tests de integridad.

**Validar**: `make check-02`

---

### Módulo 03 — Feature Engineering (3 días)

| Contenido | Entregable |
|:----------|:-----------|
| Pipelines serializables | Pipeline persistido |
| Custom encoders | Transformadores `.pkl` |
| Prevención de data leakage | Código seguro |
| Persistencia de artefactos | Artefactos reutilizables |

**Mini-Proyecto**: `FeatureEngineer` class con transformadores serializados.

**Validar**: `make check-03`

---

### Módulo 04 — Modelado (6 días)

| Contenido | Entregable |
|:----------|:-----------|
| Pipelines sklearn completos | Pipeline unificado |
| Validación temporal/cruzada | CV implementado |
| Hyperparameter tuning | Búsqueda de hiperparámetros |
| Experimentación reproducible | Scripts de entrenamiento |

**Mini-Proyecto**: Scripts que generan modelos y reportes en `outputs/`.

**Validar**: `make check-04`

---

### Módulo 05 — MLflow & DVC (3 días)

| Contenido | Entregable |
|:----------|:-----------|
| MLflow server local | `mlflow ui` funcionando |
| Tracking de experimentos | Métricas registradas |
| DVC init y pipelines | `dvc.yaml` configurado |
| Versionado de artefactos | Datos versionados |

**Mini-Proyecto**: `mlruns/` y `dvc/` que emulan el flujo del repo.

**Validar**: `make check-05`

---

### Módulo 06 — Despliegue API (3 días)

| Contenido | Entregable |
|:----------|:-----------|
| FastAPI básico | API funcional |
| Schemas Pydantic | Request/Response tipados |
| Tests de integración | Tests pasando |
| Dockerfile | Contenedor listo |

**Mini-Proyecto**: API local con endpoint `/predict` funcional.

**Validar**: `make check-06`

---

### Módulo 07 — Dashboard (2 días)

| Contenido | Entregable |
|:----------|:-----------|
| Streamlit básico | App funcionando |
| Consumo de API | Integración con backend |
| Caching y optimización | Performance aceptable |
| Ejemplo desplegable | Ready to deploy |

**Mini-Proyecto**: Dashboard Streamlit que consume la API local.

**Validar**: `make check-07`

---

### Módulo 08 — CI/CD & Testing (3 días)

| Contenido | Entregable |
|:----------|:-----------|
| GitHub Actions | Workflow configurado |
| Matrix testing | Tests multi-versión |
| Coverage reports | 80%+ coverage |
| Security scanning | gitleaks local |

**Mini-Proyecto**: `ci_template.yml` funcional, simulación local con `act`.

**Validar**: `make check-08`

---

### Módulo 09 — Model & Dataset Cards (1.5 días)

| Contenido | Entregable |
|:----------|:-----------|
| Plantilla Model Card | Template relleno |
| Plantilla Dataset Card | Template relleno |
| Buenas prácticas de documentación | Docs completos |
| Ejemplos del portafolio | Cards reales |

**Mini-Proyecto**: Model Card y Dataset Card completados para un mini-proyecto.

**Validar**: `make check-09`

---

### Módulo 10 — Observabilidad & Monitoring (2 días)

| Contenido | Entregable |
|:----------|:-----------|
| Logging estructurado | Logs configurados |
| Métricas básicas | Latencia, error rate |
| Simulación de alertas | Scripts de alerta |
| Drift detection básico | Checks implementados |

**Mini-Proyecto**: Sistema con logging estructurado y scripts de alerta.

**Validar**: `make check-10`

---

### Módulo 11 — Mantenimiento & Auditoría (2 días)

| Contenido | Entregable |
|:----------|:-----------|
| Playbooks de mantenimiento | Runbooks documentados |
| Tests de regresión | Regression tests |
| Actualización de dependencias | Proceso documentado |
| Calendario de revisiones | Plan de mantenimiento |

**Mini-Proyecto**: MAINTENANCE_GUIDE.md y scripts de validación.

**Validar**: `make check-11`

---

## 📊 Rúbrica de Evaluación (100 puntos por módulo)

| Criterio | Puntos | Descripción |
|:---------|:------:|:------------|
| **Funcionalidad** | 40 | Pasa tests mínimos, produce outputs esperados |
| **Calidad del código** | 20 | Linters, type hints, modularidad |
| **Documentación** | 15 | README, Model/Dataset Cards |
| **Reproducibilidad** | 15 | Instrucciones make, lockfile, ejecución local |
| **Tests y cobertura** | 10 | Pruebas unitarias/integración mínimas |

**Nota mínima aprobatoria**: 70/100 por módulo

---

## 📈 Progreso Sugerido

```
Semana 1:   Módulos 00-01 (Fundamentos Python)
Semana 2:   Módulos 02-03 (Datos y Features)
Semana 3:   Módulo 04 (Modelado completo)
Semana 4:   Módulos 05-06 (Tracking + API)
Semana 5:   Módulos 07-08 (Dashboard + CI/CD)
Semana 6:   Módulos 09-11 (Docs + Mantenimiento)
```

---

## ✅ Prerrequisitos

- **Python 3.10+** instalado
- **Git** básico (clone, commit, push)
- **Línea de comandos** básica (bash/zsh)
- **Cuenta GitHub** activa
- **Editor/IDE** (VS Code recomendado)
- **8GB RAM** mínimo, 16GB recomendado

---

## 🛠️ Cómo usar la guía

1. **Clonar** el repositorio guía
2. **Ejecutar** `make setup` para preparar el entorno
3. **Seguir** cada módulo en orden
4. **Completar** el mini-proyecto de cada módulo
5. **Validar** con `make check-XX` correspondiente
6. **Revisar** soluciones en `solutions/` si necesitas ayuda

---

## 📦 Entregables Finales

Al completar la guía tendrás:

- [ ] Portafolio ML reproducido localmente
- [ ] 3 proyectos con CI/CD funcionando
- [ ] Model Cards y Dataset Cards completos
- [ ] APIs y dashboards desplegables
- [ ] Sistema de observabilidad básico
- [ ] Runbooks de mantenimiento

---

<div align="center">

**¡Empieza ahora!** → [00_INDICE.md](00_INDICE.md)

</div>
