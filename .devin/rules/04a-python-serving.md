---
trigger: glob
globs: ["**/app/*.py", "**/api/*.py"]
description: Python ML serving — async inference, SHAP wrappers, Prometheus metrics, FastAPI conventions
---

# Python ML Serving Rules

## Template Contract (MANDATORY)

The scaffolded FastAPI service is a first-class template contract, not a
placeholder. Keep `docs/FASTAPI_TEMPLATE_CONTRACT.md` aligned with the
actual code whenever changing the serving surface.

Canonical ownership:

- `app/main.py`: FastAPI app, lifespan, CORS, stable error envelope,
  tracing, `/health`, `/ready`, `/model/info`, `/model/reload`.
- `app/fastapi_app.py`: inference router, `ThreadPoolExecutor`,
  model loading, feature parity, SHAP wrapper, Prometheus metrics, and
  prediction logging.
- `app/schemas.py`: public Pydantic API contract.
- `src/<service>/training/features.py`: reusable `FeatureEngineer`
  used by both training and inference.

Run or update `tests/test_fastapi_template_contract.py` for every
serving-surface change.

## Async Inference (MANDATORY)

`sklearn.predict()` and most ML frameworks are synchronous — they block asyncio's event loop.

ALWAYS use `asyncio.run_in_executor()`:
```python
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import asyncio

_inference_executor = ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="ml-infer"
)

def _sync_predict(input_dict: dict, explain: bool) -> dict:
    """CPU-bound — runs in thread pool, does not block event loop."""
    df = pd.DataFrame([input_dict])
    prob = float(model_pipeline.predict_proba(df)[:, 1][0])
    # ... build response
    return response

@app.post("/predict")
async def predict(input_data: InputSchema, explain: bool = False):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _inference_executor,
        partial(_sync_predict, input_data.model_dump(), explain)
    )
```

Why this works: sklearn, XGBoost, LightGBM release the GIL during C extensions → real parallelism with threads.

## SHAP KernelExplainer (MANDATORY for complex models)

NEVER use `TreeExplainer` with StackingClassifier, pipelines, or complex ensembles.

ALWAYS use `KernelExplainer` with a `predict_proba_wrapper`:
```python
def predict_proba_wrapper(X_array: np.ndarray) -> np.ndarray:
    """SHAP in ORIGINAL feature space, not transformed space."""
    X_df = pd.DataFrame(X_array, columns=original_feature_names)
    return pipeline.predict_proba(X_df)[:, 1]

explainer = shap.KernelExplainer(
    model=predict_proba_wrapper,
    data=X_background.values[:50],  # 50 samples: precision/speed balance
)
```

ALWAYS verify the consistency property:
```
base_value + sum(shap_values) ≈ predict_proba(input)  (tolerance < 0.01)
```

## Model Warm-up (MANDATORY — D-23)

The first call to `model.predict()` and `explainer.shap_values()` pays
JIT/cache-warming costs that often push the first real request past the
P95 SLO. ALWAYS execute a throwaway inference in the FastAPI `lifespan`
after loading artifacts:

```python
@asynccontextmanager
async def lifespan(app):
    load_model_artifacts()
    warm_up_model()      # dummy predict + dummy SHAP
    _warmed_up = True    # gate /ready on this flag
    yield
    _warmed_up = False   # drain traffic during shutdown
```

The warm-up MUST be best-effort — it catches exceptions and reports them
but never raises. A failed warm-up leaves `_warmed_up = False` so the
readiness probe keeps the pod out of the load balancer until an operator
acts.

## SHAP explainer caching (MANDATORY — D-24)

Build the `KernelExplainer` ONCE at startup and reuse it across requests.
Recomputing `shap.KernelExplainer(...)` per-request (a) rebuilds the
background summary and (b) re-samples — typically adds 100-500 ms to each
request for no value:

```python
# In load_model_artifacts() — at startup, not in the endpoint
_explainer = shap.KernelExplainer(
    model=predict_proba_wrapper,
    data=X_background.values[:50],
)
```

## ThreadPoolExecutor sizing (MANDATORY)

Size the inference executor to match K8s CPU limits:

```python
import os
_CPU_LIMIT = int(os.getenv("INFERENCE_CPU_LIMIT", str(os.cpu_count() or 1)))
_inference_executor = ThreadPoolExecutor(
    max_workers=min(_CPU_LIMIT, os.cpu_count() or 1),
    thread_name_prefix="ml-infer",
)
```

Over-sizing `max_workers` when K8s limits are tight produces context-
switching overhead; under-sizing limits concurrency unnecessarily. The
service README MUST document the chosen value with the profiling data
that justifies it.

## FastAPI Conventions

- `/predict` — main inference endpoint
- `/predict?explain=true` — SHAP explanation (opt-in)
- `/predict_batch` — batch inference endpoint (underscore, not slash)
- `/health` — **liveness** only (always 200 if event loop is alive)
- `/ready` — **readiness** (503 until model loaded AND warmed up; D-23)
- `/metrics` — Prometheus metrics
- `/model/info` — model metadata; protected by API auth when enabled
- `/model/reload` — admin-only hot reload; hidden unless explicitly enabled
- Model loaded ONCE at startup (lifespan handler), never per-request
- Warm-up runs ONCE in lifespan before `_warmed_up` flips true
- CORS default is no middleware; origins are explicit through
  `CORS_ORIGINS`
- Non-2xx responses use the stable error envelope unless an adopter is
  in a documented migration
- `ALLOW_MODELLESS_STARTUP=true` is dev/CI only and MUST fail in
  staging/production

## Graceful shutdown (MANDATORY — D-25)

`uvicorn` MUST run with `--timeout-graceful-shutdown=20` (or less) so
in-flight requests complete on SIGTERM. Coordinate with K8s
`terminationGracePeriodSeconds: 30` (must be strictly greater than
uvicorn's timeout to leave SIGKILL headroom).

## Prometheus Metrics (MANDATORY per service)

```python
from prometheus_client import Counter, Histogram, Gauge

predictions_total = Counter('{service}_predictions_total', '...', ['risk_level', 'model_version'])
prediction_latency = Histogram('{service}_request_duration_seconds', '...', ['endpoint'])
prediction_score_distribution = Histogram('{service}_prediction_score', '...')
```

## Type Hints

Required on all public functions. Use Pydantic for config and API schemas:
```python
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    feature_a: float = Field(..., ge=0, le=100, description="Feature A value")
    feature_b: str = Field(..., description="Category")
```

## When NOT to Apply
- Test files (`test_*.py`) — test conventions are different
- Training scripts — use `04b-python-training` rules instead
- One-off scripts, migrations, CLI tools
