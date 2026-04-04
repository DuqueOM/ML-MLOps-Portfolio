# ADR-017: Custom FastAPI + K8s vs Managed ML Platforms (SageMaker / Vertex AI)

## Status

**Accepted** — April 2026

## Context

The portfolio deploys 3 ML services (BankChurn, NLPInsight, ChicagoTaxi) as custom FastAPI applications on Kubernetes (GKE + EKS). Major cloud providers offer managed ML serving platforms:

- **AWS SageMaker** — upload model → create endpoint (auto-scaling, monitoring built-in)
- **GCP Vertex AI** — same pattern, Google's equivalent
- **Databricks Model Serving** — integrated with MLflow, Spark-native

The question: should the portfolio use managed platforms instead of (or in addition to) custom infrastructure?

## Decision

**Use custom FastAPI + K8s as the primary architecture, AND deploy BankChurn as a SageMaker Endpoint as a complementary demonstration.**

This "multi-paradigm" approach demonstrates:
1. Deep infrastructure knowledge (custom)
2. Pragmatism with enterprise tools (managed)
3. Ability to articulate trade-offs (this ADR)

## Comparison

| Dimension | Custom (FastAPI + K8s) | Managed (SageMaker/Vertex AI) |
|-----------|----------------------|-------------------------------|
| **Control** | Total — custom probes, metrics, middleware | Limited — provider defaults |
| **Cost (demo)** | ~$50/mo (included in K8s cluster) | ~$47/mo per endpoint (ml.t2.medium) |
| **Cost (production 100+ RPS)** | Scales with K8s nodes ($$$$) | Auto-scaling managed ($$$) |
| **Time-to-deploy** | ~15 min (build + push + rollout) | ~5 min (upload + create) |
| **Customization** | Infinite (SHAP middleware, custom metrics) | Limited (inference scripts only) |
| **Vendor lock-in** | Low (K8s is portable) | High (SageMaker SDK ≠ Vertex AI SDK) |
| **Observability** | Prometheus + Grafana (full control) | CloudWatch / Cloud Monitoring (built-in) |
| **Multi-cloud** | ✅ Kustomize overlays | ❌ Cloud-specific |
| **SHAP explainability** | ✅ `?explain=true` as query param | ❌ Requires custom container |

## Why Custom as Primary

1. **SHAP middleware**: `?explain=true` adds live feature contributions — impossible with standard SageMaker containers
2. **Prometheus metrics**: Custom `bankchurn_requests_total`, `bankchurn_prediction_latency_seconds` — CloudWatch doesn't expose these
3. **Multi-cloud portability**: Same Kustomize base deploys to GKE and EKS — SageMaker is AWS-only
4. **Interview differentiation**: Building custom infra from scratch demonstrates deeper understanding than clicking "Deploy" in a console

## Why SageMaker as Complement

1. **Enterprise relevance**: ~60% of ML teams in enterprise use SageMaker (2025 MLOps survey)
2. **Demonstrates versatility**: "I can build custom AND use managed" > "I only know one way"
3. **Low effort, high signal**: One endpoint for BankChurn adds significant portfolio value for ~2 hours of work
4. **Real comparison data**: Latency, cost, deploy-time comparisons with actual numbers

## Implementation

### AWS (SageMaker)
- `scripts/sagemaker/inference.py` — SageMaker inference handler (model_fn, input_fn, predict_fn, output_fn)
- `scripts/sagemaker/deploy_endpoint.py` — Deploy, test, and delete endpoint
- `scripts/sagemaker/setup-role.sh` — Create SageMaker execution IAM role
- Model artifact: `s3://ml-portfolio-ml-models-production/sagemaker/bankchurn/model.tar.gz`
- Instance: `ml.t2.medium` (~$0.065/hr) — deploy only during demos, delete after

### GCP (Vertex AI) — Implemented
- `scripts/vertex_ai/predictor.py` — Vertex AI Custom Prediction Routine (Predictor class pattern)
- `scripts/vertex_ai/deploy_endpoint.py` — Deploy, test, and delete endpoint
- `scripts/vertex_ai/setup-service-account.sh` — Create GCP service account + IAM roles
- Model artifact: `gs://ml-portfolio-duque-om-202602-ml-models-production/vertex-ai/bankchurn/model.joblib`
- Machine: `n1-standard-2` (~$0.095/hr) — deploy only during demos, delete after
- Key difference vs SageMaker: no `model.tar.gz` needed, Predictor class vs 4 functions, batch-native `instances` list

## Measured Results

| Metric | Custom FastAPI (EKS) | SageMaker Endpoint |
|--------|---------------------|-------------------|
| **Latency p50** | ~103ms | ~150-200ms |
| **Cold start** | ~3s (pod startup) | ~5s (container startup) |
| **Deploy time** | ~15 min (full CI/CD) | ~5 min (model upload) |
| **SHAP support** | ✅ Native (`?explain=true`) | ❌ Not available |
| **Auto-scaling** | HPA (CPU 70%) | Built-in (target invocations) |
| **Cost (idle)** | Included in cluster | ~$47/mo per endpoint |

## When to Use Each (Production Guidance)

| Scenario | Recommendation |
|----------|---------------|
| Small team, no K8s expertise | **SageMaker/Vertex AI** — faster to production |
| Existing K8s platform | **Custom FastAPI** — leverages existing infra |
| Need custom metrics/middleware | **Custom** — full control |
| Need rapid experimentation | **Managed** — deploy in minutes |
| Regulated industry (explainability required) | **Custom** — SHAP middleware |
| Multi-cloud requirement | **Custom + K8s** — portable |
| Portfolio/interview | **Both** — demonstrates versatility |

## Alternatives Considered

### Databricks Model Serving
- **Pros**: Integrated with MLflow, Spark-native, excellent for feature engineering
- **Cons**: Requires Databricks workspace (~$300+/mo), overkill for 3 sklearn models
- **Decision**: Not included — cost prohibitive for portfolio, and the portfolio already demonstrates MLflow on K8s

### BentoML / Seldon Core
- **Pros**: Open-source ML serving frameworks, K8s-native
- **Cons**: Additional abstraction layer over what we already have with FastAPI
- **Decision**: Not included — FastAPI gives us more control and is more widely understood

## References

- [SageMaker sklearn container](https://github.com/aws/sagemaker-scikit-learn-container)
- [Vertex AI prediction](https://cloud.google.com/vertex-ai/docs/predictions/overview)
- [MLOps Community Survey 2025](https://mlops.community/surveys/)
