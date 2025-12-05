# 📊 Rúbrica de Evaluación — Portfolio MLOps

> **Criterios profesionales para evaluar proyectos ML**

---

## 🎯 Puntuación Total: 100 puntos

| Rango | Nivel | Descripción |
|:-----:|:------|:------------|
| 90-100 | **Staff/Principal** | Listo para liderar equipos ML |
| 80-89 | **Senior** | Production-ready, contratación inmediata |
| 70-79 | **Mid-Level** | Sólido, necesita pulir detalles |
| 60-69 | **Junior+** | Funcional, falta madurez |
| <60 | **En desarrollo** | Requiere más trabajo |

---

## 📋 Criterios de Evaluación

### 1. Calidad del Código (20 puntos)

| Aspecto | Puntos | Criterio |
|:--------|:------:|:---------|
| Type hints | 5 | 100% de funciones públicas tipadas |
| Docstrings | 3 | Todas las clases y funciones documentadas |
| Pydantic configs | 4 | Configuración validada, no dicts crudos |
| src/ layout | 4 | Estructura profesional instalable |
| SOLID principles | 4 | Código modular y extensible |

**Ejemplo 5/5 en type hints:**
```python
def predict(self, features: pd.DataFrame) -> np.ndarray:
    """Generate predictions for input features."""
    return self.model.predict(features)
```

---

### 2. Pipeline ML (20 puntos)

| Aspecto | Puntos | Criterio |
|:--------|:------:|:---------|
| sklearn Pipeline | 6 | Pipeline unificado (no pasos sueltos) |
| ColumnTransformer | 4 | Preprocessing organizado |
| Custom Transformer | 4 | Al menos 1 transformer propio |
| Data leakage prevention | 4 | drop_columns correcto, sin target leak |
| Reproducibilidad | 2 | random_state fijado |

**Ejemplo 6/6 en Pipeline:**
```python
pipe = Pipeline([
    ("features", FeatureEngineer()),
    ("preprocess", ColumnTransformer([...])),
    ("model", RandomForestClassifier())
])
```

---

### 3. Testing y CI/CD (20 puntos)

| Aspecto | Puntos | Criterio |
|:--------|:------:|:---------|
| Coverage ≥80% | 6 | Medido con pytest-cov |
| Unit tests | 4 | Tests de funciones individuales |
| Integration tests | 4 | Tests de pipeline completo |
| GitHub Actions | 4 | CI automático en cada push |
| Security scanning | 2 | Bandit, pip-audit, o similar |

**Ejemplo 6/6 en Coverage:**
```yaml
# ci.yml
- name: Test with coverage
  run: pytest --cov=src/ --cov-fail-under=80
```

---

### 4. Containerización y APIs (15 puntos)

| Aspecto | Puntos | Criterio |
|:--------|:------:|:---------|
| Dockerfile multi-stage | 4 | Build y runtime separados |
| Non-root user | 2 | Seguridad básica |
| FastAPI schemas | 4 | Pydantic request/response |
| Health endpoint | 2 | /health funcional |
| Error handling | 3 | Respuestas HTTP correctas |

---

### 5. Experiment Tracking (10 puntos)

| Aspecto | Puntos | Criterio |
|:--------|:------:|:---------|
| MLflow logging | 4 | Params, metrics, artifacts |
| Model Registry | 3 | Modelo registrado con versión |
| Comparación experimentos | 3 | Múltiples runs comparables |

---

### 6. Documentación (15 puntos)

| Aspecto | Puntos | Criterio |
|:--------|:------:|:---------|
| README profesional | 5 | Badges, quickstart, arquitectura |
| Model Card | 4 | Performance, limitaciones, uso |
| Docstrings | 3 | Código autodocumentado |
| ADRs | 3 | Decisiones técnicas explicadas |

---

## 📊 Checklist Rápido por Proyecto

### BankChurn-Predictor
- [ ] Pipeline con ResampleClassifier
- [ ] Coverage ≥79%
- [ ] MLflow tracking
- [ ] FastAPI /predict endpoint
- [ ] Dockerfile funcional

### CarVision-Market-Intelligence
- [ ] FeatureEngineer custom transformer
- [ ] Coverage ≥80%
- [ ] Streamlit dashboard
- [ ] drop_columns para evitar leakage

### TelecomAI-Customer-Intelligence
- [ ] Pipeline sklearn completo
- [ ] Coverage ≥80%
- [ ] Múltiples modelos comparados
- [ ] API funcional

---

## 🏆 Niveles de Certificación

| Nivel | Puntuación | Badge |
|:------|:----------:|:-----:|
| MLOps Practitioner | 70-79 | 🥉 |
| MLOps Engineer | 80-89 | 🥈 |
| Senior MLOps Engineer | 90-94 | 🥇 |
| Staff MLOps Engineer | 95-100 | 💎 |

---

## 📚 Evaluación por Módulo

Sistema de autoevaluación para cada fase del programa.

### Fase 1: Fundamentos (Módulos 01-06)

| Módulo | Criterio de Aprobación | Ejercicio Requerido |
|:------:|:-----------------------|:--------------------|
| 01 | Type hints en 100% funciones, config Pydantic | 1.1, 1.2 |
| 02 | Diagrama C4 de un proyecto, ADR documentado | 2.1 |
| 03 | Proyecto con src/ layout instalable | 3.1 |
| 04 | requirements.txt + lockfile, .env funcional | 4.1 |
| 05 | pre-commit configurado, commits convencionales | 5.1 |
| 06 | DVC pipeline funcional, remote configurado | 6.1 |

**Checkpoint Fase 1**: Proyecto con estructura profesional, versionado con DVC

---

### Fase 2: ML Engineering (Módulos 07-10)

| Módulo | Criterio de Aprobación | Ejercicio Requerido |
|:------:|:-----------------------|:--------------------|
| 07 | Pipeline sklearn unificado, ColumnTransformer | 7.1, 7.2 |
| 08 | Custom Transformer (FeatureEngineer o similar) | 8.1 |
| 09 | Clase Trainer con fit/predict, cross-validation | 9.1 |
| 10 | MLflow tracking: params, metrics, artifacts | 10.1 |

**Checkpoint Fase 2**: Modelo entrenado con pipeline unificado, experimentos en MLflow

---

### Fase 3: MLOps Core (Módulos 11-16)

| Módulo | Criterio de Aprobación | Ejercicio Requerido |
|:------:|:-----------------------|:--------------------|
| 11 | Tests con ≥80% coverage, conftest.py | 11.1, 11.2 |
| 12 | GitHub Actions CI funcionando en cada push | 12.1 |
| 13 | Dockerfile multi-stage, non-root user | 13.1 (→17.1) |
| 14 | FastAPI /predict + /health, schemas Pydantic | 14.1, 14.2 |
| 15 | Dashboard Streamlit funcional | 15.1 |
| 16 | Logging JSON estructurado | 16.1 |

**Checkpoint Fase 3**: API dockerizada con CI/CD verde, ≥80% coverage

---

### Fase 4: Producción (Módulos 17-18)

| Módulo | Criterio de Aprobación | Ejercicio Requerido |
|:------:|:-----------------------|:--------------------|
| 17 | Docker Compose con API + MLflow + Prometheus | 17.2 |
| 18 | K8s Deployment con probes, HPA configurado | 18.1, 18.2 |

**Checkpoint Fase 4**: Stack completo desplegable en K8s local

---

### Fase 5: Especialización (Módulos 19-23)

| Módulo | Criterio de Aprobación | Ejercicio Requerido |
|:------:|:-----------------------|:--------------------|
| 19 | Model Card + Dataset Card completados | 19.1, 19.2 |
| 20 | Script E2E funcionando | 20.1 |
| 21 | Flashcards revisadas, términos dominados | 21.1 |
| 22 | Auditoría de proyecto completada | 22.1 |
| 23 | Plan de estudio personalizado | 23.1 |

**Checkpoint Fase 5**: Portafolio documentado, listo para entrevistas

---

## 🎯 Autoevaluación Rápida

Completa esta tabla honestamente para identificar tus gaps:

```markdown
| Competencia | 1-5 | Gap? | Recurso |
|-------------|:---:|:----:|---------|
| Type hints + Pydantic | _ | | Módulo 01 |
| sklearn Pipeline | _ | | Módulo 07 |
| Testing (pytest) | _ | | Módulo 11 |
| GitHub Actions | _ | | Módulo 12 |
| Docker | _ | | Módulo 13, 17 |
| FastAPI | _ | | Módulo 14 |
| MLflow | _ | | Módulo 10 |
| Observabilidad | _ | | Módulo 16 |
| Kubernetes | _ | | Módulo 18 |
```

> 📺 Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para videos y cursos según tus gaps

---

<div align="center">

[← Volver al Índice](00_INDICE.md) | [Ejercicios](EJERCICIOS.md) | [Recursos Externos](RECURSOS_POR_MODULO.md)

</div>
