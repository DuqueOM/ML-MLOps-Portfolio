# ⚖️ Decisiones Técnicas — ADRs del Portafolio

> **Por qué elegimos cada herramienta y tecnología**

---

## 📋 Índice de ADRs

| # | Decisión | Alternativas | Estado |
|:--|:---------|:-------------|:-------|
| 001 | Python 3.11+ | R, Julia | ✅ Aceptada |
| 002 | scikit-learn | XGBoost, LightGBM | ✅ Aceptada |
| 003 | Pydantic v2 | dataclasses, attrs | ✅ Aceptada |
| 004 | FastAPI | Flask, Django | ✅ Aceptada |
| 005 | pytest | unittest | ✅ Aceptada |
| 006 | GitHub Actions | Jenkins, GitLab CI | ✅ Aceptada |
| 007 | MLflow | W&B, Neptune | ✅ Aceptada |
| 008 | Docker | Conda, Poetry | ✅ Aceptada |

---

## ADR-001: Python 3.11+

### Contexto
Necesitamos un lenguaje para todo el stack ML.

### Decisión
Usar Python 3.11+ como lenguaje principal.

### Alternativas Consideradas
- **R**: Mejor para estadística, peor para APIs y producción
- **Julia**: Más rápido, ecosistema menos maduro

### Consecuencias
- ✅ Ecosistema ML más completo
- ✅ FastAPI, Pydantic nativos
- ✅ Mayor pool de talento
- ❌ Más lento que lenguajes compilados

---

## ADR-002: scikit-learn para Modelos

### Contexto
Necesitamos un framework ML para clasificación/regresión tabular.

### Decisión
Usar scikit-learn como framework principal.

### Alternativas Consideradas
- **XGBoost/LightGBM**: Más performance, menos integración con pipelines
- **PyTorch**: Overkill para datos tabulares

### Consecuencias
- ✅ Pipelines unificados con `Pipeline` y `ColumnTransformer`
- ✅ Fácil de testear y serializar
- ✅ Documentación excelente
- ❌ Menos performance que gradient boosting dedicado

---

## ADR-003: Pydantic v2 para Configuración

### Contexto
Necesitamos validar configuración de forma robusta.

### Decisión
Usar Pydantic v2 para todas las configuraciones.

### Alternativas Consideradas
- **dataclasses**: Sin validación built-in
- **attrs**: Menos popular, similar funcionalidad
- **Dict/YAML directo**: Sin validación

### Consecuencias
- ✅ Validación automática de tipos
- ✅ Errores claros en config inválida
- ✅ Integración perfecta con FastAPI
- ❌ Dependencia adicional

**Ejemplo:**
```python
class ModelConfig(BaseModel):
    n_estimators: int = Field(ge=10, le=500)
    max_depth: int | None = Field(default=None, ge=1)
```

---

## ADR-004: FastAPI para APIs

### Contexto
Necesitamos servir modelos via HTTP.

### Decisión
Usar FastAPI para todas las APIs.

### Alternativas Consideradas
- **Flask**: Más simple, sin async, sin docs automáticas
- **Django**: Overkill para APIs ML
- **gRPC**: Más complejo, mejor para microservicios internos

### Consecuencias
- ✅ Async por defecto
- ✅ Docs OpenAPI automáticas
- ✅ Validación con Pydantic integrada
- ✅ Rendimiento excelente
- ❌ Menos tutoriales que Flask

---

## ADR-005: pytest para Testing

### Contexto
Necesitamos un framework de testing.

### Decisión
Usar pytest con pytest-cov.

### Alternativas Consideradas
- **unittest**: Más verboso, menos features
- **nose2**: Abandonado

### Consecuencias
- ✅ Fixtures potentes
- ✅ Plugins (pytest-cov, pytest-mock)
- ✅ Sintaxis simple con assert
- ✅ Parametrización fácil

---

## ADR-006: GitHub Actions para CI/CD

### Contexto
Necesitamos CI/CD automatizado.

### Decisión
Usar GitHub Actions.

### Alternativas Consideradas
- **Jenkins**: Self-hosted, más mantenimiento
- **GitLab CI**: Requiere migrar repos
- **CircleCI**: Costo adicional

### Consecuencias
- ✅ Integrado con GitHub
- ✅ Gratis para repos públicos
- ✅ Matrix testing fácil
- ✅ Marketplace de actions
- ❌ Vendor lock-in con GitHub

---

## ADR-007: MLflow para Tracking

### Contexto
Necesitamos tracking de experimentos y registry de modelos.

### Decisión
Usar MLflow (local + server).

### Alternativas Consideradas
- **W&B (Weights & Biases)**: Mejor UI, costo para equipos
- **Neptune**: Similar a W&B
- **DVC**: Más para datos que experimentos

### Consecuencias
- ✅ Open source, sin vendor lock-in
- ✅ Model Registry integrado
- ✅ Funciona local sin servidor
- ❌ UI menos moderna que W&B

---

## ADR-008: Docker para Empaquetado

### Contexto
Necesitamos empaquetar aplicaciones para deploy.

### Decisión
Usar Docker con multi-stage builds.

### Alternativas Consideradas
- **Conda pack**: Solo Python, sin proceso completo
- **Poetry**: Solo dependencias, no containerización

### Consecuencias
- ✅ Reproducibilidad total
- ✅ Funciona en cualquier cloud
- ✅ Compose para desarrollo local
- ❌ Overhead de imagen

---

## 📊 Matriz de Decisiones Resumen

| Área | Herramienta | Por qué |
|:-----|:------------|:--------|
| Lenguaje | Python 3.11+ | Ecosistema ML |
| ML Framework | scikit-learn | Pipelines unificados |
| Config | Pydantic v2 | Validación + FastAPI |
| API | FastAPI | Async + docs auto |
| Testing | pytest | Fixtures + plugins |
| CI/CD | GitHub Actions | Integración nativa |
| Tracking | MLflow | Open source + local |
| Container | Docker | Reproducibilidad |

---

<div align="center">

[← Volver al Índice](00_INDICE.md)

</div>
