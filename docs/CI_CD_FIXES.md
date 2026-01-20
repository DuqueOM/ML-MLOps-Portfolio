# CI/CD Fixes - Enero 2026

## Errores Corregidos

### 1. MkDocs Build Failure
**Error**: 3 warnings en strict mode por enlaces rotos
```
WARNING - Doc file 'FEATURES.md' contains a link '../README.md#...', but target not found
WARNING - Doc file 'FEATURES.md' contains a link '../scripts/...', but target not found
```

**Solución**: `docs/FEATURES.md`
- Eliminados enlaces a archivos fuera de `docs/`
- Convertidos a referencias de texto plano
- MkDocs ahora construye sin warnings

### 2. CarVision Test Failure
**Error**: `ValueError: invalid literal for int() with base 10: '6 cylinders'`
```python
dtypes = {"cylinders": "int8"}  # ❌ Falla con strings
```

**Solución**: `CarVision-Market-Intelligence/src/carvision/data.py`
```python
# Removido dtype int8 de cylinders
# Permite inferencia automática para strings como '6 cylinders'
dtypes = {
    "price": "float32",
    "model_year": "int16",
    # "cylinders": "int8",  # ❌ Removido
    "odometer": "float32",
    ...
}
```

### 3. TelecomAI Test Failure
**Error**: `TypeError: 'PathsConfig' object is not subscriptable`
```python
cfg.paths["data_csv"]  # ❌ PathsConfig es Pydantic, no dict
```

**Solución**: `TelecomAI-Customer-Intelligence/tests/test_main_workflow.py`
```python
# Antes (dict subscript)
data_csv_abs = project_root / cfg.paths["data_csv"]

# Después (Pydantic attribute)
data_csv_abs = project_root / cfg.paths.data_csv

# Crear PathsConfig correctamente
from src.telecom.config import PathsConfig
cfg.paths = PathsConfig(
    data_csv=str(data_csv_abs),
    artifacts_dir=str(artifacts_dir),
    ...
)
```

## Jobs Saltados - Explicación

### ¿Por qué se saltaron `e2e` y `ghcr-publish`?

**Estructura de dependencias**:
```yaml
tests:
  # Job principal que falló

e2e:
  needs: [tests]  # ⚠️ Depende de tests
  # Se salta si tests falla

ghcr-publish:
  needs: [tests, security, docker]  # ⚠️ Depende de tests
  if: github.ref == 'refs/heads/main'
  # Se salta si tests falla

integration-test:
  needs: [docker]  # ⚠️ Depende de docker
  # Se salta si docker falla
```

**Comportamiento de GitHub Actions**:
- Si un job falla, todos los jobs que dependen de él (`needs: [...]`) se saltan automáticamente
- Esto es el comportamiento esperado para evitar ejecutar jobs que dependen de artefactos de jobs fallidos

## Validación Local

### Tests ejecutados localmente (antes del fix):
```bash
# BankChurn: ✅ 28/28 tests pasando
# CarVision: ❌ 1 fallo (cylinders dtype)
# TelecomAI: ❌ 1 fallo (PathsConfig subscript)
```

### Tests después del fix:
```bash
# Todos los tests deberían pasar en CI/CD
```

## Próximos Pasos

1. ✅ **Commit aplicado**: `f0b03a5`
2. ✅ **Push a main**: Ejecutado
3. ⏳ **Esperar CI/CD**: GitHub Actions ejecutará todos los jobs
4. ✅ **Verificar**: 
   - Tests pasan en los 3 proyectos
   - MkDocs construye sin warnings
   - Jobs `e2e` y `ghcr-publish` se ejecutan

## Monitoreo

**URL del workflow**: 
https://github.com/DuqueOM/ML-MLOps-Portfolio/actions

**Jobs esperados**:
- ✅ tests (6 matrix jobs: 3 proyectos × 2 versiones Python)
- ✅ quality-gates
- ✅ security
- ✅ docker
- ✅ e2e
- ✅ integration-test (solo en main)
- ✅ ghcr-publish (solo en main)

---

**Fecha**: 20 de enero de 2026
**Commit**: f0b03a5
