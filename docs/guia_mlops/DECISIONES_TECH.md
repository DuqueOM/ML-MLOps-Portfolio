# ⚖️ Decisiones Técnicas — ADRs del Portafolio

> **Por qué elegimos cada herramienta y tecnología**

*Última actualización: Diciembre 2025*

---

## 📋 Índice de ADRs

| # | Decisión | Alternativas | Módulo | Estado |
|:--|:---------|:-------------|:------:|:-------|
| 001 | Python 3.11+ | R, Julia | 01 | ✅ Aceptada |
| 002 | scikit-learn | XGBoost, LightGBM | 07 | ✅ Aceptada |
| 003 | Pydantic v2 | dataclasses, attrs | 01 | ✅ Aceptada |
| 004 | FastAPI | Flask, Django | 14 | ✅ Aceptada |
| 005 | pytest | unittest | 11 | ✅ Aceptada |
| 006 | GitHub Actions | Jenkins, GitLab CI | 12 | ✅ Aceptada |
| 007 | MLflow | W&B, Neptune | 10 | ✅ Aceptada |
| 008 | Docker | Conda, Poetry | 13, 17 | ✅ Aceptada |
| 009 | DVC | Git LFS, S3 directo | 06 | ✅ Aceptada |
| 010 | Streamlit | Gradio, Panel | 15 | ✅ Aceptada |
| 011 | Prometheus + Grafana | Datadog, New Relic | 16 | ✅ Aceptada |
| 012 | Kubernetes | Docker Swarm, ECS | 18 | ✅ Aceptada |
| 013 | Ruff | Flake8 + Black + isort | 01 | ✅ Aceptada |
| 014 | src/ Layout | Flat layout | 03 | ✅ Aceptada |

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

## ADR-009: DVC para Versionado de Datos

### Contexto
Necesitamos versionar datasets grandes sin guardarlos en Git.

### Decisión
Usar DVC (Data Version Control).

### Alternativas Consideradas
- **Git LFS**: Pago por storage, menos features
- **S3 directo**: Sin versionado semántico
- **Delta Lake**: Overkill para nuestro tamaño

### Consecuencias
- ✅ Versionado semántico de datos
- ✅ Pipelines reproducibles
- ✅ Integración con Git
- ❌ Curva de aprendizaje adicional

> 📖 Ver [Módulo 06](06_VERSIONADO_DATOS.md)

---

## ADR-010: Streamlit para Dashboards

### Contexto
Necesitamos crear dashboards interactivos para stakeholders.

### Decisión
Usar Streamlit para dashboards ML.

### Alternativas Consideradas
- **Gradio**: Más simple, menos personalizable
- **Panel**: Menos popular, más verboso
- **Dash**: Más complejo, mejor para apps empresariales

### Consecuencias
- ✅ Python puro, sin HTML/CSS/JS
- ✅ Reactivo por defecto
- ✅ Caching de modelos integrado
- ✅ Deploy fácil (Streamlit Cloud)
- ❌ Menos control sobre UI que frameworks web

> 📖 Ver [Módulo 15](15_STREAMLIT.md)

---

## ADR-011: Prometheus + Grafana para Observabilidad

### Contexto
Necesitamos monitorear modelos en producción y detectar drift.

### Decisión
Usar Prometheus para métricas y Grafana para dashboards.

### Alternativas Consideradas
- **Datadog**: Excelente pero costoso
- **New Relic**: Similar a Datadog
- **CloudWatch/Stackdriver**: Vendor lock-in

### Consecuencias
- ✅ Open source, sin costo
- ✅ Estándar de la industria
- ✅ Alertas configurables
- ✅ Integración con K8s nativa
- ❌ Más setup que SaaS

> 📖 Ver [Módulo 16](16_OBSERVABILIDAD.md)

---

## ADR-012: Kubernetes para Orquestación

### Contexto
Necesitamos orquestar contenedores en producción con auto-scaling.

### Decisión
Usar Kubernetes para deployment.

### Alternativas Consideradas
- **Docker Swarm**: Más simple, menos features
- **ECS/Fargate**: Vendor lock-in AWS
- **Nomad**: Menos adopción

### Consecuencias
- ✅ Estándar de la industria
- ✅ Auto-scaling (HPA)
- ✅ Self-healing (probes)
- ✅ Portable entre clouds
- ❌ Curva de aprendizaje alta

> 📖 Ver [Módulo 18](18_INFRAESTRUCTURA.md)

---

## ADR-013: Ruff para Linting

### Contexto
Necesitamos herramientas de calidad de código rápidas.

### Decisión
Usar Ruff como linter y formateador unificado.

### Alternativas Consideradas
- **Flake8 + Black + isort**: Múltiples herramientas, más lento
- **Pylint**: Muy lento, muchos false positives

### Consecuencias
- ✅ 10-100x más rápido que alternativas
- ✅ Una herramienta = una config
- ✅ Compatible con reglas de Flake8
- ✅ Formateador incluido
- ❌ Herramienta relativamente nueva

> 📖 Ver [Módulo 01](01_PYTHON_MODERNO.md) - Glosario: [Ruff](21_GLOSARIO.md#ruff)

---

## ADR-014: src/ Layout para Proyectos

### Contexto
Necesitamos una estructura de proyecto profesional e instalable.

### Decisión
Usar src/ layout en todos los proyectos.

### Alternativas Consideradas
- **Flat layout**: Más simple pero problemático con imports
- **Monorepo**: Más complejo para este tamaño

### Consecuencias
- ✅ Evita importar código local en vez del paquete
- ✅ Estructura profesional estándar
- ✅ Instalable con `pip install -e .`
- ❌ Un nivel más de directorios

> 📖 Ver [Módulo 03](03_ESTRUCTURA_PROYECTO.md)

---

## 📊 Matriz de Decisiones Resumen

| Área | Herramienta | Por qué | Módulo |
|:-----|:------------|:--------|:------:|
| Lenguaje | Python 3.11+ | Ecosistema ML | 01 |
| ML Framework | scikit-learn | Pipelines unificados | 07 |
| Config | Pydantic v2 | Validación + FastAPI | 01 |
| API | FastAPI | Async + docs auto | 14 |
| Dashboard | Streamlit | Python puro, reactivo | 15 |
| Testing | pytest | Fixtures + plugins | 11 |
| CI/CD | GitHub Actions | Integración nativa | 12 |
| Tracking | MLflow | Open source + local | 10 |
| Versionado datos | DVC | Git + datos grandes | 06 |
| Container | Docker | Reproducibilidad | 13, 17 |
| Orquestación | Kubernetes | Auto-scaling, probes | 18 |
| Monitoreo | Prometheus + Grafana | Open source, estándar | 16 |
| Linting | Ruff | Rápido, unificado | 01 |
| Estructura | src/ layout | Profesional, instalable | 03 |

---

## 🔗 Referencias

- [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) - Videos y cursos por herramienta
- [21_GLOSARIO.md](21_GLOSARIO.md) - Definiciones detalladas de cada herramienta

---

<div align="center">

[← Volver al Índice](00_INDICE.md) | [Recursos Externos](RECURSOS_POR_MODULO.md)

</div>
