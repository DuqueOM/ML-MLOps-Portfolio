---
trigger: glob
globs: ["**/schemas.py", "**/validate*.py", "**/pandera*"]
description: Data validation with Pandera — schema definitions, validation points
---

# Data Validation Rules

## Why Pandera (Not Great Expectations)

- Great Expectations: 100+ dependencies, data store contracts, team documentation
- Pandera: ~12 dependencies, DataFrame validation, Prometheus-compatible

Use Pandera when:
- Models use in-memory DataFrames from sklearn pipelines
- Team is small (< 5 ML engineers)
- No external data store contracts to validate

Use Great Expectations when:
- Multiple data sources (SQL + S3 + Kafka)
- Shared data contracts between teams
- Spark or Databricks pipelines

## Schema Definition

```python
import pandera.pandas as pa

class ServiceInputSchema(pa.DataFrameModel):
    """One schema per service. Document type, range, nullability."""
    feature_name: float = pa.Field(ge=0, le=100, description="Feature description")
    category: str = pa.Field(isin=["A", "B", "C"], description="Category type")

    class Config:
        coerce = True   # Auto-convert types where possible
        strict = False  # Allow extra columns
```

## Validation Points (ALL THREE MANDATORY)

### Point 1: Before Training
```python
# data/validate_data.py
@pa.check_types
def validate_training_data(df: pa.typing.DataFrame[ServiceInputSchema]) -> pd.DataFrame:
    return df
# Fail fast: training does not start with invalid data
```

### Point 2: API Endpoint
```python
# app/fastapi_app.py — /predict endpoint
# Pydantic validates request structure
# Pandera validates DataFrame before inference
# SchemaError → HTTP 422 with descriptive message
```

### Point 3: Drift Detection
```python
# monitoring/drift_detection.py
# Schema validation of production batch before calculating PSI
# Schema mismatch = immediate alert (features added/removed upstream)
```

## Rules

- ALWAYS define one Pandera schema per service
- ALWAYS validate at all three points (training, serving, drift)
- ALWAYS use `coerce = True` to handle type mismatches gracefully
- NEVER skip validation in production — SchemaError is better than silent wrong predictions
- ALWAYS include a leakage check: features that shouldn't exist at prediction time
