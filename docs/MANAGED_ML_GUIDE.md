# Managed ML Platforms — SageMaker (AWS) & Vertex AI (GCP)

> **Multi-paradigm portfolio**: Custom FastAPI + Kubernetes as the primary serving architecture,
> AND managed endpoints (SageMaker + Vertex AI) to demonstrate enterprise platform skills.
> See [ADR-017](decisions/017-custom-vs-managed-ml-platforms.md) for the full comparison.

## Architecture: Three Paradigms, One Portfolio

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           ML-MLOps-Portfolio                                     │
│                                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────────────┐ │
│  │  1. Custom FastAPI    │  │  2. AWS SageMaker    │  │  3. GCP Vertex AI     │ │
│  │  on K8s (GKE + EKS)  │  │  Managed Endpoint    │  │  Managed Endpoint     │ │
│  │  ── PRIMARY ──        │  │  ── COMPLEMENT ──    │  │  ── COMPLEMENT ──     │ │
│  │                       │  │                      │  │                       │ │
│  │  ✅ SHAP middleware   │  │  ✅ Built-in scaling │  │  ✅ Built-in scaling  │ │
│  │  ✅ Prometheus        │  │  ✅ CloudWatch       │  │  ✅ Cloud Monitoring  │ │
│  │  ✅ Multi-cloud       │  │  ✅ Model Monitor    │  │  ✅ Model Monitoring  │ │
│  │  ✅ Full control      │  │  ✅ 5-min deploy     │  │  ✅ 5-min deploy     │ │
│  │  ❌ More maintenance  │  │  ❌ AWS-only         │  │  ❌ GCP-only         │ │
│  └──────────────────────┘  └──────────────────────┘  └────────────────────────┘ │
│                                                                                  │
│  "I can build custom infrastructure AND use managed platforms —                  │
│   the right choice depends on team context, not personal preference."            │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: AWS SageMaker Endpoint

### Prerequisites (AWS)

```bash
# AWS CLI configured
export AWS_PROFILE=ml-portfolio
aws sts get-caller-identity  # Verify access

# Python packages
pip install sagemaker boto3

# SageMaker execution role (one-time setup)
bash scripts/sagemaker/setup-role.sh
```

### Quick Start (SageMaker)

```bash
# 1. Deploy endpoint (~5 minutes)
python scripts/sagemaker/deploy_endpoint.py

# 2. Test endpoint
python scripts/sagemaker/deploy_endpoint.py test

# 3. Check status
python scripts/sagemaker/deploy_endpoint.py status

# 4. DELETE when done (stops charges!)
python scripts/sagemaker/deploy_endpoint.py delete
```

### How SageMaker Works

#### Model Packaging

SageMaker requires a `model.tar.gz` containing:

```
model.tar.gz
├── model.joblib      ← trained BankChurn StackingClassifier
└── inference.py      ← SageMaker inference handler
```

The `inference.py` implements 4 functions that SageMaker calls automatically:

| Function | Purpose | Called When |
|----------|---------|------------|
| `model_fn(model_dir)` | Load model from disk | Container startup |
| `input_fn(body, content_type)` | Deserialize JSON → DataFrame | Each request |
| `predict_fn(data, model)` | Run `predict_proba()` | Each request |
| `output_fn(prediction, accept)` | Serialize dict → JSON | Each request |

#### SageMaker Deployment Flow

```
model.joblib + inference.py
        │
        ▼
    model.tar.gz ──▶ S3 bucket
        │
        ▼
    SageMaker Model (references S3 + sklearn container)
        │
        ▼
    Endpoint Config (instance type, count)
        │
        ▼
    Endpoint (InService) ──▶ HTTPS endpoint ready for invocations
```

#### SageMaker Auto-Scaling

```python
# Example: Configure SageMaker auto-scaling (not in portfolio scripts — for reference)
import boto3

client = boto3.client("application-autoscaling")

# Register scalable target
client.register_scalable_target(
    ServiceNamespace="sagemaker",
    ResourceId="endpoint/bankchurn-endpoint/variant/primary",
    ScalableDimension="sagemaker:variant:DesiredInstanceCount",
    MinCapacity=1,
    MaxCapacity=5,
)

# Target tracking policy — scale on invocations per instance
client.put_scaling_policy(
    PolicyName="bankchurn-scaling",
    ServiceNamespace="sagemaker",
    ResourceId="endpoint/bankchurn-endpoint/variant/primary",
    ScalableDimension="sagemaker:variant:DesiredInstanceCount",
    PolicyType="TargetTrackingScaling",
    TargetTrackingScalingPolicyConfiguration={
        "TargetValue": 100.0,  # 100 invocations per instance
        "PredefinedMetricSpecification": {
            "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
        },
        "ScaleInCooldown": 300,
        "ScaleOutCooldown": 60,
    },
)
```

Compare to the custom K8s HPA approach:
```yaml
# k8s/bankchurn-hpa.yaml (portfolio's custom approach)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1
  maxReplicas: 3
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

**Key difference**: SageMaker scales on *invocations per instance* (business metric), K8s HPA scales on *CPU utilization* (infrastructure metric). SageMaker's approach is more ML-native; K8s gives more infrastructure control.

#### SageMaker Model Monitor

```python
# Example: Set up data quality monitoring (reference — not in portfolio scripts)
from sagemaker.model_monitor import DefaultModelMonitor
from sagemaker.model_monitor.dataset_format import DatasetFormat

monitor = DefaultModelMonitor(
    role=role_arn,
    instance_count=1,
    instance_type="ml.m5.xlarge",
    volume_size_in_gb=20,
)

# Create baseline from training data
monitor.suggest_baseline(
    baseline_dataset="s3://bucket/training-data.csv",
    dataset_format=DatasetFormat.csv(header=True),
)

# Schedule hourly monitoring
monitor.create_monitoring_schedule(
    monitor_schedule_name="bankchurn-monitor",
    endpoint_input=endpoint_name,
    output_s3_uri="s3://bucket/monitoring-output",
    schedule_cron_expression="cron(0 * ? * * *)",
)
```

Compare to the portfolio's custom drift detection:
```bash
# k8s/drift-detection-cronjob.yaml (portfolio's custom approach)
# Runs daily at 06:00 UTC — KS test + PSI + Evidently report
kubectl get cronjobs -n ml-portfolio
```

**Key difference**: SageMaker Model Monitor gives you out-of-the-box data quality checks with CloudWatch alerts. Custom drift detection (KS + PSI + Evidently) gives full control over statistical tests and thresholds.

#### SageMaker Infrastructure Created

| Resource | Name | Cost |
|----------|------|------|
| SageMaker Model | `bankchurn-model` | Free |
| Endpoint Config | `bankchurn-endpoint-config` | Free |
| Endpoint | `bankchurn-endpoint` | **~$0.065/hr** (~$47/mo if 24/7) |
| S3 artifact | `s3://ml-portfolio-ml-models-production/sagemaker/bankchurn/model.tar.gz` | ~$0.001/mo |

> ⚠️ **Cost control**: Only keep the endpoint alive during demos. Deploy → test → delete.
> Recreating takes ~5 minutes.

### SageMaker Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `NoSuchEntityException` on role | IAM role not created | Run `bash scripts/sagemaker/setup-role.sh` |
| Endpoint stuck in `Creating` | Large model or cold region | Wait up to 10 minutes; check CloudWatch logs |
| `ModelError` on invoke | inference.py error | Check `aws logs` for `/aws/sagemaker/Endpoints/bankchurn-endpoint` |
| `AccessDeniedException` | Role missing S3 or SageMaker perms | Re-run `setup-role.sh` |
| High latency on first call | Cold start | Second call will be ~150ms |
| `ValidationException` | Wrong sklearn framework version | Verify `1.2-1` matches your model's sklearn version |

---

## Part 2: GCP Vertex AI Endpoint

### Prerequisites (GCP)

```bash
# GCP CLI configured
export GCP_PROJECT=ml-portfolio-duque-om-202602
export GCP_REGION=us-central1
gcloud auth application-default login

# Python packages
pip install google-cloud-aiplatform google-cloud-storage

# Vertex AI service account (one-time setup)
bash scripts/vertex_ai/setup-service-account.sh

# Enable Vertex AI API (if not already)
gcloud services enable aiplatform.googleapis.com --project=$GCP_PROJECT
```

### Quick Start (Vertex AI)

```bash
# 1. Deploy endpoint (~5-10 minutes)
python scripts/vertex_ai/deploy_endpoint.py

# 2. Test endpoint
python scripts/vertex_ai/deploy_endpoint.py test

# 3. Check status
python scripts/vertex_ai/deploy_endpoint.py status

# 4. DELETE when done (stops charges!)
python scripts/vertex_ai/deploy_endpoint.py delete
```

### How Vertex AI Works

#### Model Upload

Vertex AI does NOT require `model.tar.gz` — it reads directly from a GCS directory:

```
gs://bucket/vertex-ai/bankchurn/
└── model.joblib      ← trained BankChurn StackingClassifier
```

For custom preprocessing, Vertex AI uses a **Predictor class** (vs SageMaker's 4 functions):

```python
# scripts/vertex_ai/predictor.py — Vertex AI Custom Prediction Routine
class BankChurnPredictor:
    def __init__(self):
        """Load model (called once at container startup)."""
        model_path = os.path.join(os.environ["AIP_STORAGE_URI"], "model.joblib")
        self._model = joblib.load(model_path)

    def predict(self, instances: List[Dict]) -> List[Dict]:
        """Run prediction (called for each request)."""
        df = pd.DataFrame(instances)
        proba = self._model.predict_proba(df)
        return [{"churn_probability": round(float(p[1]), 4)} for p in proba]
```

Compare the inference contracts:

| Aspect | SageMaker (`inference.py`) | Vertex AI (`predictor.py`) |
|--------|--------------------------|---------------------------|
| **Pattern** | 4 standalone functions | 1 class with methods |
| **Model loading** | `model_fn(model_dir)` | `__init__(self)` |
| **Input parsing** | `input_fn(body, content_type)` | SDK handles JSON automatically |
| **Prediction** | `predict_fn(data, model)` | `predict(self, instances)` |
| **Output** | `output_fn(prediction, accept)` | `postprocess(self, prediction)` (optional) |
| **Batch support** | Must handle in `predict_fn` | `instances` is always a list |

#### Vertex AI Deployment Flow

```
model.joblib
     │
     ▼
  GCS bucket (gs://bucket/vertex-ai/bankchurn/)
     │
     ▼
  Vertex AI Model (references GCS + sklearn container)
     │
     ▼
  Vertex AI Endpoint (display name, region)
     │
     ▼
  Deploy Model to Endpoint (machine type, replicas)
     │
     ▼
  Endpoint (ready) ──▶ HTTPS endpoint for predictions
```

#### Vertex AI Auto-Scaling

```python
# Vertex AI auto-scaling is configured during deploy
model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-2",
    min_replica_count=1,      # Minimum instances
    max_replica_count=5,      # Maximum instances
    traffic_percentage=100,
    # Auto-scaling is automatic based on CPU utilization
    # No separate scaling policy needed (unlike SageMaker)
)
```

**Key difference**: Vertex AI auto-scaling is simpler — it's built into the `deploy()` call. SageMaker requires a separate Application Auto Scaling policy. Vertex AI scales based on CPU/GPU utilization automatically.

#### Vertex AI Model Monitoring

```python
# Example: Set up model monitoring on Vertex AI (reference)
from google.cloud import aiplatform

# Create monitoring job
job = aiplatform.ModelDeploymentMonitoringJob.create(
    display_name="bankchurn-monitoring",
    endpoint=endpoint,
    logging_sampling_strategy={"random_sample_config": {"sample_rate": 0.8}},
    log_ttl="7776000s",  # 90 days
    # Skew detection (training vs serving data)
    model_deployment_monitoring_objective_configs=[{
        "deployed_model_id": deployed_model_id,
        "objective_config": {
            "training_dataset": {
                "gcs_source": {"uris": ["gs://bucket/training-data.csv"]},
                "data_format": "csv",
                "target_field": "Exited",
            },
            "training_prediction_skew_detection_config": {
                "skew_thresholds": {
                    "Age": {"value": 0.3},
                    "Balance": {"value": 0.3},
                }
            },
        },
    }],
    schedule_config={"monitor_interval": {"seconds": 3600}},  # Hourly
)
```

#### Vertex AI Infrastructure Created

| Resource | Name | Cost |
|----------|------|------|
| Vertex AI Model | `bankchurn-model` | Free |
| Vertex AI Endpoint | `bankchurn-endpoint` | **~$0.095/hr** (~$68/mo if 24/7) |
| GCS artifact | `gs://...ml-models-production/vertex-ai/bankchurn/model.joblib` | ~$0.001/mo |

> ⚠️ **Cost control**: Same as SageMaker — deploy only during demos. Delete immediately after.

### Vertex AI Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `PermissionDenied` | Missing Vertex AI roles | Run `bash scripts/vertex_ai/setup-service-account.sh` |
| `RESOURCE_EXHAUSTED` | Region quota exceeded | Try `us-central1` or request quota increase |
| Model upload fails | GCS permissions | Verify `storage.objectViewer` role on service account |
| Endpoint stuck deploying | Container pull or health check failure | Check Vertex AI console logs |
| `InvalidArgument` on predict | Wrong input format | Vertex AI expects `{"instances": [...]}` |
| Slow first request | Container cold start | ~5-10s on first request, then ~150ms |

---

## Part 3: Full Comparison — Custom vs SageMaker vs Vertex AI

### Latency Comparison

| Metric | Custom FastAPI (K8s) | SageMaker (AWS) | Vertex AI (GCP) |
|--------|---------------------|-----------------|-----------------|
| **p50 latency** | ~103ms | ~150-200ms | ~150-200ms |
| **p95 latency** | ~150ms | ~300ms | ~300ms |
| **Cold start** | ~3s (pod) | ~5s (container) | ~5-10s (container) |
| **Deploy time** | ~15 min (CI/CD) | ~5 min | ~5-10 min |

### Feature Matrix

| Feature | Custom FastAPI | SageMaker | Vertex AI |
|---------|---------------|-----------|-----------|
| SHAP explainability (`?explain=true`) | ✅ | ❌ | ❌ |
| Custom Prometheus metrics | ✅ | ❌ | ❌ |
| Multi-cloud portable | ✅ (GKE + EKS) | ❌ (AWS) | ❌ (GCP) |
| Auto-scaling | HPA (CPU-based) | Built-in (invocations) | Built-in (CPU) |
| A/B testing | Argo Rollouts | Built-in variants | Built-in traffic split |
| Model monitoring | Custom (Prometheus + Evidently) | Model Monitor | Model Monitoring |
| Data quality checks | Custom (Pandera + CronJob) | Baseline + scheduled | Skew detection |
| Canary deployments | Argo Rollouts manifests | Endpoint variants | Traffic split % |
| Cost (idle, portfolio) | Included in K8s cluster | ~$47/mo per endpoint | ~$68/mo per endpoint |
| Inference script pattern | FastAPI route + Pydantic | 4 functions (model/input/predict/output) | Predictor class |
| SDK lock-in | None (HTTP + OpenAPI) | `sagemaker` SDK | `google-cloud-aiplatform` SDK |

### When to Use Each (Decision Guide)

| Scenario | Best Choice | Why |
|----------|-------------|-----|
| **Small team, no K8s** | SageMaker / Vertex AI | Zero infra management |
| **Existing K8s platform** | Custom FastAPI | Leverage existing infra |
| **Need SHAP/custom middleware** | Custom FastAPI | Full control over request pipeline |
| **Rapid prototyping** | SageMaker / Vertex AI | 5-min deploys |
| **Regulated industry** | Custom FastAPI | SHAP middleware + audit trail |
| **Multi-cloud required** | Custom + K8s | Kustomize overlays portable |
| **AWS-only shop** | SageMaker | Native integration + Model Monitor |
| **GCP-only shop** | Vertex AI | Native integration + BigQuery ML |
| **Portfolio / interviews** | **All three** | Demonstrates versatility |
| **Cost-sensitive startup** | Custom on K8s | No per-endpoint charges |
| **Enterprise with ML team** | SageMaker / Vertex AI | Focus on models, not infra |

---

## Files

### SageMaker (AWS)

| File | Purpose |
|------|---------|
| `scripts/sagemaker/inference.py` | SageMaker inference handler (4 functions) |
| `scripts/sagemaker/deploy_endpoint.py` | Deploy, test, delete, status, package |
| `scripts/sagemaker/setup-role.sh` | Create IAM execution role |

### Vertex AI (GCP)

| File | Purpose |
|------|---------|
| `scripts/vertex_ai/predictor.py` | Vertex AI Custom Prediction Routine (Predictor class) |
| `scripts/vertex_ai/deploy_endpoint.py` | Deploy, test, delete, upload, status |
| `scripts/vertex_ai/setup-service-account.sh` | Create GCP service account + IAM roles |

### Documentation

| File | Purpose |
|------|---------|
| `docs/decisions/017-custom-vs-managed-ml-platforms.md` | ADR with full comparison |
| `docs/MANAGED_ML_GUIDE.md` | This guide |
| `docs/MULTI_CLOUD_COMPARISON.md` | Cross-cloud comparison including managed platforms |
