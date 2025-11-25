# Reporte de Auditoría — BankChurn-Predictor

**Fecha**: 2025-11-25  
**Proyecto**: BankChurn-Predictor  
**Tipo**: Clasificación binaria (predicción de abandono bancario)

---

## 1) Resumen Ejecutivo

BankChurn-Predictor es un sistema de predicción de abandono de clientes bancarios que utiliza un pipeline unificado de sklearn con MLflow para tracking de experimentos. El proyecto presenta una arquitectura sólida con:

- **87 tests pasando** con **78% de cobertura**
- **Sin vulnerabilidades de seguridad** detectadas (Bandit/pip-audit)
- **Complejidad promedio A (3.76)** — código mantenible
- **Linting 100% passing** (Black, Flake8)

**Áreas de mejora identificadas**: Algunos errores menores de mypy en config.py y funciones con complejidad C que podrían refactorizarse.

---

## 2) Objetivos de Este Reporte

- ✅ Verificar calidad de código (formato, estilo, complejidad)
- ✅ Ejecutar pruebas y medir cobertura
- ✅ Auditar seguridad y dependencias
- ✅ Evaluar mantenibilidad y deuda técnica
- ✅ Documentar pasos reproducibles para auditorías futuras

---

## 3) Requisitos Previos

Para reproducir esta auditoría, necesitas:

- Python 3.11 o 3.12
- Docker (opcional, para tests de integración)
- Acceso a DVC remote (opcional, para datos)

### Comandos para Replicar

```bash
# Clonar y navegar al proyecto
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio/BankChurn-Predictor

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.in

# Instalar herramientas de auditoría
pip install black flake8 mypy bandit radon pytest pytest-cov coverage
```

---

## 4) Pasos Ejecutados (Comandos con Salida)

### 4.1 Formateo y Linting

**¿Por qué?** Verificar que el código sigue un estilo consistente facilita la colaboración y reduce errores.

```bash
black --check src/ app/ tests/
```

**Output:**
```
All done! ✨ 🍰 ✨
20 files would be left unchanged.
```

✅ **Resultado**: Todo el código está correctamente formateado.

```bash
flake8 src/ app/ --max-line-length=120 --statistics
```

**Output:**
```
(sin errores)
```

✅ **Resultado**: No hay violaciones de estilo.

---

### 4.2 Tipado Estático (mypy)

**¿Por qué?** El tipado estático detecta errores antes de ejecutar el código y mejora la documentación.

```bash
mypy src/ --ignore-missing-imports
```

**Output:**
```
src/bankchurn/config.py:12: error: Library stubs not installed for "yaml"
src/bankchurn/config.py:55: error: Missing named argument "voting" for "EnsembleConfig"
src/bankchurn/config.py:123: error: Missing named argument "test_size" for "ModelConfig"
src/bankchurn/config.py:123: error: Missing named argument "cv_folds" for "ModelConfig"
```

⚠️ **Resultado**: 4 errores de tipado a corregir.

**Interpretación**:
- El error de `yaml` se resuelve instalando `types-PyYAML`
- Los errores de argumentos faltantes indican que las dataclasses `EnsembleConfig` y `ModelConfig` tienen campos requeridos sin valores por defecto

---

### 4.3 Análisis de Complejidad (Radon)

**¿Por qué?** Alta complejidad ciclomática dificulta el testing y mantenimiento.

```bash
radon cc src/ -s -a
```

**Output (extracto):**
```
src/bankchurn/prediction.py
    M 78:4 ChurnPredictor.predict - C (13)
    C 19:0 ChurnPredictor - B (6)
    M 213:4 ChurnPredictor.explain_prediction - A (5)

src/bankchurn/training.py
    M 136:4 ChurnTrainer.build_preprocessor - C (11)
    M 244:4 ChurnTrainer.train - B (7)

src/bankchurn/evaluation.py
    M 195:4 ModelEvaluator.compute_fairness_metrics - B (10)
    M 91:4 ModelEvaluator.evaluate - B (9)

Average complexity: A (3.76)
```

| Grado | Significado | Cantidad en Proyecto |
|-------|-------------|---------------------|
| A (1-5) | Excelente | 36 funciones |
| B (6-10) | Bueno | 4 funciones |
| C (11-20) | Moderado | 2 funciones |
| D-F (>20) | Refactorizar | 0 funciones |

⚠️ **Funciones a considerar refactorizar**:
- `ChurnPredictor.predict` (C=13)
- `ChurnTrainer.build_preprocessor` (C=11)

---

### 4.4 Tests y Cobertura

**¿Por qué?** Los tests aseguran que el código funciona como se espera y la cobertura mide qué tan bien están probadas las funciones.

```bash
pytest tests/ -q --tb=short -m "not slow" --cov=src --cov-report=term-missing
```

**Output:**
```
87 passed, 1 skipped, 28 warnings in 34.99s

Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
app/fastapi_app.py              176     40    77%   21, 40-66, 72-75, ...
src/bankchurn/cli.py            115     28    76%   96-98, 148-150, ...
src/bankchurn/config.py          64      4    94%   62, 123, 125, 127
src/bankchurn/evaluation.py     106     16    85%   59-60, 85-86, ...
src/bankchurn/models.py          56      6    89%   173-175, 184-186
src/bankchurn/prediction.py      92     41    55%   45-46, 72-73, ...
src/bankchurn/training.py       136     27    80%   70-71, 96, ...
-----------------------------------------------------------
TOTAL                           762    171    78%
```

✅ **Resultado**: 87 tests pasando, 78% cobertura (umbral: 65%)

**Módulos con menor cobertura**:
- `prediction.py` (55%) — funciones de explicabilidad sin tests
- `cli.py` (76%) — algunos comandos no testeados
- `fastapi_app.py` (77%) — endpoints de error handling

---

### 4.5 Seguridad (Bandit)

**¿Por qué?** Bandit detecta patrones de código inseguros como inyección SQL, uso de pickle sin validación, etc.

```bash
bandit -r src/ -f json -o reports/audit/bandit-bankchurn.json -ll
```

**Output (resumen):**
```json
{
  "metrics": {
    "_totals": {
      "SEVERITY.HIGH": 0,
      "SEVERITY.MEDIUM": 0,
      "SEVERITY.LOW": 2
    }
  },
  "results": []
}
```

✅ **Resultado**: Sin issues de severidad media o alta.

Los 2 issues LOW en `training.py` son falsos positivos relacionados con logging.

---

### 4.6 Dependencias (pip-audit)

**¿Por qué?** Las dependencias desactualizadas pueden contener vulnerabilidades conocidas.

```bash
pip-audit
```

**Output:**
```
No known vulnerabilities found
```

✅ **Resultado**: Todas las dependencias están libres de vulnerabilidades conocidas.

---

## 5) Resultados & Interpretación

### Issues Priorizados

#### P2 — Importantes

| ID | Issue | Archivo | Línea | Descripción |
|----|-------|---------|-------|-------------|
| P2-01 | Missing argument "voting" | `config.py` | 55 | EnsembleConfig no tiene default para `voting` |
| P2-02 | Missing argument "test_size" | `config.py` | 123 | ModelConfig requires default |
| P2-03 | Library stubs for yaml | `config.py` | 12 | Instalar types-PyYAML |

**Ejemplo del problema P2-01:**

```python
# Actual (línea ~55 en config.py)
@dataclass
class EnsembleConfig:
    voting: str  # Sin default - requiere valor siempre

# Corregido
@dataclass
class EnsembleConfig:
    voting: str = "soft"  # Con default
```

#### P3 — Deuda Técnica

| ID | Issue | Archivo | Descripción |
|----|-------|---------|-------------|
| P3-01 | Complejidad C (13) | `prediction.py:78` | `ChurnPredictor.predict` muy complejo |
| P3-02 | Complejidad C (11) | `training.py:136` | `build_preprocessor` muy complejo |
| P3-03 | Baja cobertura | `prediction.py` | 55% cobertura en módulo de predicción |

---

## 6) Remediación Paso a Paso

### Fix P2-01: Añadir defaults a EnsembleConfig

```bash
# Abrir archivo
vim src/bankchurn/config.py
```

**Antes:**
```python
@dataclass
class EnsembleConfig:
    voting: str
```

**Después:**
```python
@dataclass
class EnsembleConfig:
    voting: str = "soft"
```

### Fix P2-03: Instalar type stubs

```bash
pip install types-PyYAML
```

Añadir a `requirements.in`:
```
types-PyYAML>=2024.0.0
```

### Fix P3-01: Refactorizar ChurnPredictor.predict

El método `predict` tiene complejidad 13 porque maneja múltiples casos. Sugerencia de refactor:

```python
# Antes (simplificado)
def predict(self, data):
    # validación
    # conversión
    # preprocessing
    # predicción
    # postprocessing
    # formateo resultado
    return result

# Después (extraer métodos)
def predict(self, data):
    validated = self._validate_input(data)
    preprocessed = self._preprocess(validated)
    raw_prediction = self._make_prediction(preprocessed)
    return self._format_result(raw_prediction)

def _validate_input(self, data):
    ...

def _preprocess(self, data):
    ...
```

---

## 7) Checklist Final

- [x] **Linting passing** — Black y Flake8 sin errores
- [x] **Cobertura >= 65%** — 78% alcanzado
- [x] **Bandit: no medium/critical** — Solo 2 LOW (falsos positivos)
- [x] **pip-audit: no vulnerabilities** — Verificado
- [x] **No secrets in repo** — Gitleaks limpio
- [ ] **mypy <= warnings allowed** — 4 errores a corregir
- [ ] **Complejidad <= B** — 2 funciones con C

---

## 8) Recursos y Referencias

### Archivos de CI/CD

- `.github/workflows/ci-mlops.yml` — Pipeline principal
- `BankChurn-Predictor/Makefile` — Comandos locales

### Documentación

- `README.md` — Descripción general del proyecto
- `ARCHITECTURE.md` — Arquitectura del sistema
- `model_card.md` — Documentación del modelo
- `data_card.md` — Documentación de los datos

### Comandos Útiles

```bash
# Entrenar modelo
make train

# Servir API
make serve

# Correr todos los tests
make test

# Generar reporte de cobertura HTML
pytest --cov=src --cov-report=html
```

---

## 9) Apéndice: Outputs Crudos

### Ubicación de archivos

```
reports/audit/
├── bandit-bankchurn.json    # SAST completo
├── bankchurn-pytest.txt     # Output de pytest
└── pip-audit.json           # Audit de dependencias
```

### Extracto de pytest

```
tests/test_api_coverage.py ......                 [  6%]
tests/test_cli.py .............                   [ 21%]
tests/test_config.py ...............              [ 38%]
tests/test_data.py ..                             [ 40%]
tests/test_evaluation.py .........                [ 51%]
tests/test_integration.py ......                  [ 57%]
tests/test_models.py .........s.......            [ 77%]
tests/test_prediction.py .......                  [ 85%]
tests/test_training.py .............              [100%]

87 passed, 1 skipped
```

---

## 10) Qué Haría a Continuación

### Prioridad Alta (Esta Semana)
1. Corregir los 4 errores de mypy en `config.py`
2. Instalar `types-PyYAML` y actualizar requirements

### Prioridad Media (2 Semanas)
3. Aumentar cobertura de `prediction.py` de 55% a 75%
4. Añadir tests para endpoints de error en FastAPI

### Prioridad Baja (1 Mes)
5. Refactorizar `ChurnPredictor.predict` para reducir complejidad
6. Documentar decisiones arquitectónicas en ADRs

---

*Reporte generado como parte del proceso de auditoría del portafolio ML-MLOps.*
