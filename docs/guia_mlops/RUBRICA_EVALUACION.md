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

<div align="center">

[← Volver al Índice](00_INDICE.md)

</div>
