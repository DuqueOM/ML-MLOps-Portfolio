# Dependency Conflicts Analysis

## Overview

This document analyzes dependency conflicts across the portfolio projects and provides remediation plans.

## Identified Conflicts

### 1. Pydantic Version Conflict — ✅ RESOLVED

**Projects Affected:**
- All 3 projects

**Issue (was):**
- Mixed `pydantic>=1.9.0` and `pydantic>=2.0.0` across requirements files
- Breaking changes between Pydantic v1 and v2

**Resolution (completed):**
- ✅ All 3 projects standardized on **Pydantic v2**
- ✅ All config classes migrated to v2 syntax (`model_dump`, `field_validator`)
- ✅ `requirements.txt` locked to `pydantic==2.12.4`
- ✅ All tests pass with Pydantic v2

### 2. PyArrow Dependency Scope

**Projects Affected:**
- CarVision-Market-Intelligence

**Issue:**
- Uses `pyarrow>=8.0.0` for data processing
- Heavy dependency for simple CSV operations

**Impact:**
- Large installation size (~200MB)
- Longer build times
- Potential version conflicts with other tools

**Remediation Plan:**
1. **Evaluate alternatives:**
   - Use pandas built-in CSV/Parquet readers
   - Consider `fastparquet` instead of `pyarrow`
   - Keep `pyarrow` only if Arrow format is required

2. **Optimization Steps:**
   ```bash
   # Test without pyarrow
   pip uninstall pyarrow
   python -c "import pandas as pd; pd.read_parquet('test.parquet')"
   
   # If fails, install minimal alternative
   pip install fastparquet
   ```

## Cross-Project Dependencies

### Shared Dependencies Matrix

| Dependency | BankChurn | CarVision | TelecomAI | Notes |
|------------|-----------|-----------|-----------|-------|
| pydantic | >=2.0.0 | >=2.0.0 | >=2.0.0 | ✅ Standardized on v2 |
| pyarrow | - | >=8.0.0 | 22.0.0 | Evaluate necessity |
| fastapi | >=0.78.0 | >=0.78.0 | >=0.78 | Consistent version |
| scikit-learn | Latest | Latest | >=1.0 | No conflicts |

### 3. TelecomAI Dependencies Analysis — ✅ RESOLVED

**Projects Affected:**
- TelecomAI-Customer-Intelligence

**Current State:**
- ✅ Uses `pydantic>=2.0.0` (migrated)
- Uses `pyarrow==22.0.0` (via mlflow dependencies)
- Uses `fastapi>=0.78` (consistent)
- Uses `scikit-learn>=1.0` (latest)

**Resolution:**
- ✅ Pydantic v2 migration completed
- PyArrow remains as transitive dependency via MLflow (acceptable)

## Resolution Priority

1. ~~**High Priority**: Pydantic version standardization~~ — ✅ DONE
2. **Medium Priority**: PyArrow dependency evaluation (CarVision)
3. **Low Priority**: Minor version mismatches

## Testing Strategy

After resolving conflicts:

```bash
# 1. Clean environment
python -m venv test_env
source test_env/bin/activate

# 2. Install each project separately
cd BankChurn-Predictor && pip install -r requirements.txt
cd ../CarVision-Market-Intelligence && pip install -r requirements.txt
cd ../TelecomAI-Customer-Intelligence && pip install -r requirements.txt

# 3. Run tests
python -m pytest tests/ --cov=src/

# 4. Test integration
python scripts/run_experiments.py
```

## Prevention Measures

1. **Dependency Locking**: Use `pip-tools` for consistent dependency resolution
2. **Version Constraints**: Pin critical dependencies in `pyproject.toml`
3. **Regular Audits**: Monthly dependency conflict checks
4. **CI/CD Integration**: Add conflict detection to pipeline

## Tools for Dependency Management

- `pip-audit`: Security vulnerability scanning
- `pipdeptree`: Dependency tree visualization
- `pip-check`: Conflicts detection
- `safety`: Security checking

## Monitoring

Regular dependency updates check:
```bash
# Check for outdated packages
pip list --outdated

# Check for security issues
pip-audit

# Visualize dependency tree
pipdeptree
```

---

**Last Updated**: February 2026
