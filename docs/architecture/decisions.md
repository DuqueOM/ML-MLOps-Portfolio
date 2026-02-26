# Architectural Decision Records

> **Purpose**: This document captures the rationale behind every significant technical decision in this portfolio. Each decision is documented with its context, the choice made, alternatives considered, and the conditions under which the decision should be revisited. Written for technical reviewers, hiring managers, and future maintainers.
>
> **Last Updated**: February 2026 | **Portfolio Version**: 2.0.0

---

## Table of Contents

1. [Kubernetes Storage: emptyDir Ephemeral Volumes](#adr-001-kubernetes-storage-emptydir-ephemeral-volumes)
2. [Init Container Image: python:3.11-alpine with Pinned Dependencies](#adr-002-init-container-image-python311-alpine-with-pinned-dependencies)
3. [Model Versioning: ConfigMaps Separated from Deployments](#adr-003-model-versioning-configmaps-separated-from-deployments)
4. [Download Resilience: Retry with Fixed Backoff](#adr-004-download-resilience-retry-with-fixed-backoff)
5. [GKE Cluster: Single-Node e2-medium with Autoscaling](#adr-005-gke-cluster-single-node-e2-medium-with-autoscaling)
6. [Networking: Custom VPC with Private Subnets](#adr-006-networking-custom-vpc-with-private-subnets)
7. [Ingress: GCE-Native Load Balancer](#adr-007-ingress-gce-native-load-balancer)
8. [Container Images: Multi-Stage Docker Builds](#adr-008-container-images-multi-stage-docker-builds)
9. [Model Serialization: Joblib over Pickle](#adr-009-model-serialization-joblib-over-pickle)
10. [Model Selection: Auto-Selection Pipeline](#adr-010-model-selection-auto-selection-pipeline)
11. [Experiment Tracking: Self-Hosted MLflow on GKE](#adr-011-experiment-tracking-self-hosted-mlflow-on-gke)
12. [Monitoring: Self-Hosted Prometheus + Grafana](#adr-012-monitoring-self-hosted-prometheus-grafana)
13. [CI/CD: GitHub Actions with Matrix Testing](#adr-013-cicd-github-actions-with-matrix-testing)
14. [Container Registry: Dual Registry Strategy](#adr-014-container-registry-dual-registry-strategy)
15. [Storage: GCS with Lifecycle Policies](#adr-015-storage-gcs-with-lifecycle-policies)
16. [Infrastructure as Code: Terraform with Remote State](#adr-016-infrastructure-as-code-terraform-with-remote-state)
17. [Security: Defense in Depth](#adr-017-security-defense-in-depth)
18. [Cost Optimization Summary](#cost-optimization-summary)

---

## ADR-001: Kubernetes Storage — emptyDir Ephemeral Volumes

**Status**: Accepted | **Category**: Infrastructure

### Context

Each ML API pod needs access to a trained model file (~4MB) at startup. The model is stored in Google Cloud Storage and must be available at a local path inside the container.

### Decision

Use `emptyDir` volumes — ephemeral storage that exists for the lifetime of the pod.

### Rationale

- **Model size is negligible**: At ~4MB per model, downloading from GCS within the same region (us-central1 → us-central1) takes 2–5 seconds. The egress cost is $0.000048 per pod startup — literally five thousandths of a cent.
- **Pod stability is high**: With pods running 36+ hours without restarts, the download occurs once and the pod serves indefinitely. The emptyDir persists across container restarts within the same pod lifecycle.
- **Kubernetes lifecycle guarantees idempotency**: Init Containers execute once per pod lifecycle, not per container restart. If the main container (`bankchurn-api`) crashes and Kubernetes restarts it, the Init Container does not re-run — the emptyDir remains intact with the model already downloaded. The only scenario where the Init Container re-executes is when the entire pod is recreated, at which point the emptyDir is destroyed by definition — there is no file to check because the volume is new and empty. Adding an "if file exists, skip download" check would protect against an architecturally impossible scenario.

### Alternatives Considered

| Alternative | Why Not |
|---|---|
| **PersistentVolumeClaim (PVC)** | Adds cost (~$4/mo for 10GB SSD), operational complexity (StorageClass, provisioner), and solves a problem that doesn't exist at this scale. PVCs are warranted when models exceed ~500MB and startup latency becomes unacceptable. |
| **Baked into Docker image** | Couples model version to image version. Every model update requires a full Docker build + push + rollout instead of a ConfigMap patch + restart. Violates separation of concerns between code and data. |
| **hostPath volume** | Ties pods to specific nodes, breaks scheduling flexibility, and creates security risks (container can access host filesystem). Not portable across cloud providers. |
| **DaemonSet pre-loading** | Node-level caching is the correct solution for multi-GB models in enterprise systems with aggressive autoscaling. For 4MB models with 1 replica, it introduces unnecessary architectural complexity (DaemonSet lifecycle, node affinity, cache invalidation). |

### When to Revisit

- Models exceed ~500MB and startup latency becomes user-facing.
- Cluster autoscaling recreates pods more than once per hour sustained.
- Multiple replicas per service make redundant downloads a measurable cost.

---

## ADR-002: Init Container Image — python:3.11-alpine with Pinned Dependencies

**Status**: Accepted | **Category**: Infrastructure

### Context

The Init Container needs to download a file from Google Cloud Storage before the main application container starts.

### Decision

Use `python:3.11-alpine` (~50MB) with `google-cloud-storage==2.18.2` installed via pip at runtime.

### Rationale

**Why python:3.11-alpine, not google/cloud-sdk:**
The official Google Cloud SDK image includes gcloud, gsutil, bq, kubectl, and all their dependencies. Even the alpine variant weighs several hundred MB. For this use case — copying a single file from GCS — only the `google-cloud-storage` Python library is needed. The alpine image at ~50MB has exactly what's required. Smaller image means faster pull on uncached nodes and reduced attack surface from unused dependencies.

**Why pin the version `==2.18.2`:**
Without a pinned version, `pip install google-cloud-storage` installs whatever is latest on PyPI at pod startup time. If a breaking change ships six months later, every new pod fails non-deterministically — the Docker image hasn't changed, only the runtime environment. Pinning guarantees identical behavior today, tomorrow, and when the cluster is recreated in a year. This is standard mandatory practice in any production environment at zero cost.

**The known trade-off — pip install at runtime:**
Adds ~15–25 seconds to pod startup. For pods with low recreation frequency (this project), it's completely irrelevant. For clusters with aggressive autoscaling recreating dozens of pods per minute, the cumulative overhead and PyPI runtime dependency become problematic.

### The Elite Alternative (Deliberately Not Implemented)

Build a custom Docker image with `google-cloud-storage==2.18.2` pre-installed, push it to Artifact Registry, and use it directly as the Init Container image. This eliminates `pip install` entirely — instant startup, no PyPI dependency.

**Why not**: Adding a fourth Docker image (bankchurn, carvision, telecom + downloader) requires an additional CI/CD pipeline, independent versioning, image testing, and security update maintenance. For a service with 1 stable replica and pods that rarely recreate, that maintenance cost far exceeds the benefit of eliminating 20 seconds of pip install. The custom image becomes the correct choice if pods recreate more than once per hour sustained.

### Why NOT Implement SHA256 Hash Verification

GCS is not a generic HTTP server without integrity guarantees. Every download through `google-cloud-storage` travels over HTTPS with TLS (transit integrity guaranteed by the cryptographic protocol). Additionally, every blob in GCS has an MD5 checksum stored alongside the object, and the library verifies it automatically upon download completion — if the downloaded file doesn't match the stored checksum, `blob.download_to_filename()` raises an exception, caught by the retry loop.

Adding manual SHA256 in the ConfigMap would introduce concrete operational cost: every time a new model is trained and uploaded to GCS, the hash must be computed locally and the ConfigMap updated manually. Forgetting that step means the pod won't start even though the model is perfectly valid. This adds a new failure class (forgotten hash update) to protect against a risk (in-transit corruption) that GCS already mitigates internally with greater reliability.

Manual SHA256 verification is warranted when downloading from sources without transit verification (plain HTTP, untrusted public mirrors). It does not apply to GCS.

---

## ADR-003: Model Versioning — ConfigMaps Separated from Deployments

**Status**: Accepted | **Category**: Infrastructure

### Context

Model updates should be deployable without modifying infrastructure manifests.

### Decision

GCS paths (`GCS_BUCKET`, `GCS_MODEL_PATH`, `MODEL_VERSION`) live in per-project ConfigMaps (`bankchurn-model-config`, `carvision-model-config`, `telecom-model-config`), independent of the Deployment manifests.

### Rationale

Updating the production model should be an administrative data operation, not an infrastructure change. Without ConfigMaps, switching from `model_v1.joblib` to `model_v2.joblib` requires editing the Deployment YAML, running `kubectl apply`, waiting for rollout, and managing rollback with `kubectl rollout undo` if something fails — touching infrastructure for what is fundamentally a configuration change.

With ConfigMaps, the process is:

```bash
kubectl patch configmap bankchurn-model-config -n ml-portfolio \
  -p '{"data":{"GCS_MODEL_PATH":"bankchurn/model-v2.joblib"}}'
kubectl rollout restart deployment/bankchurn-predictor -n ml-portfolio
```

The Deployment itself never changes. Version history is preserved in the ConfigMap, and rollback is a patch back to the previous path.

### The Natural Next Evolution (Not Implemented)

In mature MLOps systems, the source of truth for the active model version is the **MLflow Model Registry** — a centralized registry where models have formal stages (Staging, Production, Archived) and complete history. The Init Container would query the MLflow API at startup: "give me the artifact URI for the Production stage of bankchurn-predictor" and download that specific version. This enables promoting models from Staging to Production with a single click in the MLflow UI, with zero infrastructure changes.

This project already has MLflow deployed in the same cluster — integration with the Model Registry is the direct evolutionary step from the current ConfigMap approach.

---

## ADR-004: Download Resilience — Retry with Fixed Backoff

**Status**: Accepted | **Category**: Infrastructure

### Context

GCS, like any distributed service, can experience transient latency spikes, rate limiting, or brief outages lasting seconds to minutes.

### Decision

The download script retries up to 3 times with 10-second intervals between attempts.

### Rationale

**Without retry**: If GCS returns a 503 at the exact moment the Init Container runs, the pod enters `Init:Error`. Kubernetes applies its own exponential backoff (10s, 20s, 40s...) before retrying the entire pod. Time from failure to successful startup can be several minutes, and logs show errors that appear critical without being so — difficult to distinguish from a real failure.

**With explicit retry**: The script handles transient failures internally — 3 attempts with 10 seconds between them cover the vast majority of GCS transient incidents. If all 3 attempts fail, the script exits with code 1, the Init Container dies with an error, and Kubernetes applies its normal CrashLoopBackOff — correct behavior, because if GCS is sustainedly inaccessible, it's better to not start the pod and alert visibly than to operate in a degraded state.

**Multiple replicas scenario (e.g., 20 simultaneous pods)**: Each pod downloads its own copy independently. With 4MB per download and 20 replicas, that's 80MB total from GCS. At same-region egress rate ($0.12/GB), the total cost is $0.0096 — less than a cent. The real concern appears with multi-GB models where parallel downloads can saturate node bandwidth or generate significant egress costs. Mitigation in that case is node-level caching (DaemonSet) or a ReadWriteMany shared volume.

---

## ADR-005: GKE Cluster — Single-Node e2-medium with Autoscaling

**Status**: Accepted | **Category**: Infrastructure / Cost

### Context

The portfolio runs 6 services: 3 ML APIs (BankChurn ~384Mi, CarVision ~640Mi+256Mi sidecar, TelecomAI ~384Mi), MLflow, Prometheus, and Grafana. Total memory footprint is approximately 3–3.5GB under normal operation.

### Decision

- **Machine type**: `e2-medium` (1 shared vCPU, 4GB RAM) — ~$25/month per node
- **Node count**: 1 (handles full workload)
- **Autoscaling**: 1–5 nodes (HPA on CPU/memory for ML APIs)

### Rationale

| Configuration | Monthly Cost | Justification |
|---|---|---|
| `e2-medium` × 1 node | ~$25 | 4GB RAM fits all 6 pods with headroom. Shared vCPU is sufficient — ML inference is not CPU-bound for these model sizes. |
| `e2-standard-2` × 1 | ~$49 | 2× cost for dedicated vCPUs that these workloads don't need. |
| `e2-standard-4` × 2 | ~$196 | Enterprise-grade overkill. 8 vCPUs and 32GB RAM for pods using 3.5GB total. |

**Why not preemptible/spot instances for production**: Preemptible VMs save 60–80% but can be terminated with 30 seconds notice. For a portfolio demonstration that needs to be reliably accessible for recruiters and reviewers, availability takes priority over the ~$15/month savings. The Terraform configuration correctly sets `preemptible = false` for production while enabling it for dev/staging environments.

**Autoscaling design**: All 3 ML services have standardized HPA with dual metrics (CPU + memory). BankChurn/CarVision target 70% CPU and 80% memory; TelecomAI targets 75% CPU and 80% memory. Conservative scale-down (300s stabilization, max 50% reduction/min) prevents thrashing, while scale-up uses 60s stabilization to filter transient spikes. Memory requests are calibrated to `kubectl top pods` steady-state usage + headroom, ensuring the HPA scales down to 1 replica when idle.

### Cost Impact

Optimizing from the initial `variables.tf` defaults (`e2-standard-4` × 3 nodes) to actual deployment (`e2-medium` × 1 node):

| Resource | Before | After | Savings |
|---|---|---|---|
| Compute | ~$294/mo | ~$25/mo | **91%** |
| Total cluster cost | ~$400/mo | ~$120/mo | **70%** |

---

## ADR-006: Networking — Custom VPC with Private Subnets

**Status**: Accepted | **Category**: Security / Infrastructure

### Context

GKE clusters need network isolation. The default VPC auto-creates subnets in every region — wasteful and harder to manage.

### Decision

Custom VPC with a single subnet in `us-central1`, secondary IP ranges for pods (`10.30.0.0/16`) and services (`10.20.0.0/16`), and private Cloud SQL access via VPC peering.

### Rationale

- **Single-region deployment**: All resources in `us-central1` minimizes inter-region latency and egress costs. The subnet CIDR (`10.10.0.0/24`) provides 254 host addresses — more than sufficient.
- **Secondary IP ranges**: Required by GKE for VPC-native clusters (alias IP mode). `/16` ranges provide 65,534 addresses each — generous but standard for GKE.
- **Private Cloud SQL**: Database accessible only through VPC peering, not exposed to the internet. Even if `db-f1-micro` is the smallest tier, private networking is a security baseline.
- **No NAT gateway**: Not needed because pods access GCS and Artifact Registry through Google's internal network (same project, same region). External egress is minimal.

### Alternatives Considered

| Alternative | Why Not |
|---|---|
| **Default VPC** | Auto-creates subnets globally, harder to audit, less control over CIDR ranges. Not suitable for IaC-managed infrastructure. |
| **Multi-region** | Adds complexity and cost with no benefit. All users access via a single Ingress IP. |
| **Private GKE cluster** | Restricts API server access to VPC only. Useful for enterprise security but complicates development access and CI/CD. Overkill for a portfolio project. |

---

## ADR-007: Ingress — GCE-Native Load Balancer

**Status**: Accepted | **Category**: Networking

### Context

Three ML APIs need to be accessible on a single public IP with path-based routing.

### Decision

GCE-native Ingress (`kubernetes.io/ingress.class: "gce"`) with `ImplementationSpecific` path matching and `defaultBackend` pointing to BankChurn.

### Rationale

- **GCE-native**: Uses Google's global HTTP(S) load balancer — fully managed, no additional software to deploy or maintain. Automatic SSL termination, DDoS protection, and CDN integration available.
- **Path-based routing**: `/bankchurn/*` → BankChurn, `/carvision/*` → CarVision, `/telecom/*` → TelecomAI. Clean URL structure with a single IP (`34.120.120.57`).
- **defaultBackend**: Ensures requests to `/` or unmatched paths return a valid response (BankChurn) instead of a 404. Important for health checks and discovery.
- **NodePort services**: Required by GCE Ingress (it communicates with backends via node ports, not ClusterIP).

### Alternatives Considered

| Alternative | Why Not |
|---|---|
| **NGINX Ingress Controller** | Requires deploying and maintaining an additional pod. More flexible but unnecessary for simple path-based routing. Adds memory/CPU overhead. |
| **Istio service mesh** | Enterprise-grade service mesh with mTLS, traffic shaping, observability. Massive overhead (~2GB RAM, sidecar per pod) for features not needed at this scale. |
| **Individual LoadBalancers** | One GCE LB per service ($18/mo × 3 = $54/mo vs single LB at $18/mo). Tripled cost with no benefit. |

---

## ADR-008: Container Images — Multi-Stage Docker Builds

**Status**: Accepted | **Category**: CI/CD / Security

### Context

ML applications have heavy build dependencies (gcc, g++, build-essential) for compiling C extensions (numpy, scipy, scikit-learn, xgboost) that are not needed at runtime.

### Decision

Two-stage builds: `builder` stage compiles dependencies in a virtualenv, `runtime` stage copies only the compiled venv into a clean `python:3.11-slim-bookworm` base.

### Rationale

- **Image size reduction**: Builder stage includes ~800MB of build tools. Runtime image contains only the compiled Python packages + application code. Typical reduction: 1.2GB → 400–500MB.
- **Attack surface reduction**: No compiler, no build tools, no package manager caches in the production image. Fewer CVEs to remediate.
- **Layer caching**: Configs copied before source code (`COPY configs/ → COPY src/`). Most builds only invalidate the last 2–3 layers, making rebuilds fast.
- **Non-root user**: `appuser` (UID 1000) with minimal permissions. Containers never run as root.
- **Docker HEALTHCHECK**: Built-in health monitoring independent of Kubernetes probes. Useful for local development with `docker run`.
- **Virtualenv isolation**: Dependencies in `/opt/venv` are fully isolated from system Python — prevents conflicts and makes the venv layer independently cacheable.

### Image Size Comparison

| Approach | Estimated Size |
|---|---|
| Single-stage `python:3.11` | ~1.5GB |
| Single-stage `python:3.11-slim` | ~900MB |
| **Multi-stage (current)** | **~450MB** |
| Multi-stage with distroless | ~350MB (but harder to debug) |

---

## ADR-009: Model Serialization — Joblib over Pickle

**Status**: Accepted | **Category**: ML Engineering

### Context

Trained scikit-learn pipelines need to be persisted to disk for serving.

### Decision

Use `joblib.dump(pipeline, path, compress=3)` with `.joblib` extension.

### Rationale

- **NumPy optimization**: Joblib is specifically optimized for objects containing large NumPy arrays (common in ML pipelines). It memory-maps arrays during loading, reducing peak memory usage.
- **Compression**: `compress=3` (zlib) reduces model file size by ~40–60% with negligible load time impact. BankChurn model: ~1.7MB, CarVision: ~4MB, TelecomAI: ~0.8MB.
- **Standardization**: All 3 projects use `models/model.joblib` — uniform path, uniform serialization format, uniform Init Container download logic.
- **Scikit-learn recommendation**: The official scikit-learn documentation recommends joblib over pickle for scikit-learn models specifically because of the NumPy array handling.

### Alternatives Considered

| Alternative | Why Not |
|---|---|
| **pickle** | No compression, no NumPy optimization. Larger files, higher memory during deserialization. |
| **ONNX** | Framework-agnostic format, excellent for serving. But scikit-learn ONNX export is lossy for complex pipelines (custom transformers, FeatureEngineer). Adds `skl2onnx` dependency and conversion step. |
| **MLflow model format** | Wraps joblib/pickle with metadata. Good for registry integration but adds MLflow as a runtime dependency for model loading. The current approach uses joblib directly — simpler, no MLflow dependency at inference time. |

---

## ADR-010: Model Selection — Auto-Selection Pipeline

**Status**: Accepted | **Category**: ML Engineering

### Context

CarVision compares multiple model architectures (RandomForest, XGBoost, Neural Network) during training. The best model should be automatically selected for production.

### Decision

Training pipeline trains the primary model plus all models listed in `compare_models`, evaluates each on the validation set, and auto-selects the model with the highest R² score.

### Rationale

- **Data-driven selection**: CarVision's config defaults to RandomForest, but the auto-selection pipeline discovered that XGBoost achieves R²=0.705 vs RandomForest's R²=0.675 — a 4.4% improvement selected automatically without manual intervention.
- **Reproducibility**: The comparison results are persisted to `models/model_comparison.json` and the selected model name is recorded in `models/metrics_val.json` with `auto_selected: true` and `original_model: random_forest`.
- **Config-driven**: The `compare_models` list in `config.yaml` controls which models are evaluated. Adding a new model is a one-line config change.

### Production Models

| Project | Model Type | Selection Method | Key Metric |
|---|---|---|---|
| **BankChurn** | VotingClassifier (LR + RF) | Manual ensemble design | AUC 0.87 |
| **CarVision** | XGBRegressor | Auto-selected over RF | R² 0.705 |
| **TelecomAI** | VotingClassifier (LR + GB + RF) | Manual ensemble design | Accuracy 82% |

---

## ADR-011: Experiment Tracking — Self-Hosted MLflow on GKE

**Status**: Accepted | **Category**: MLOps

### Context

ML experiment tracking requires a centralized server to compare runs across projects.

### Decision

MLflow server deployed as a pod in the same GKE cluster, with SQLite backend and ephemeral storage.

### Rationale

- **Zero additional cost**: Runs on the same node as the ML APIs. No separate compute instance needed.
- **Cluster-internal access**: Services reach MLflow at `http://mlflow-service:5000` via Kubernetes DNS — no external network calls.
- **Terraform provisions Cloud SQL**: The infrastructure includes a PostgreSQL instance (`db-f1-micro`) for MLflow's production backend. The current SQLite deployment demonstrates the concept while avoiding the ~$7–10/month Cloud SQL cost during portfolio demonstration phase.

### When to Upgrade to Cloud SQL Backend

When experiment history must survive pod restarts, or when multiple concurrent users need write access. The Terraform infrastructure is already provisioned — switching requires only updating the MLflow deployment's `--backend-store-uri` to the Cloud SQL connection string.

---

## ADR-012: Monitoring — Self-Hosted Prometheus + Grafana

**Status**: Accepted | **Category**: Observability

### Context

Production ML services need observability: request rates, latency distributions, error rates, and model-specific metrics.

### Decision

- **Prometheus** (v2.48.0): Scrapes `/metrics` endpoints from all 3 ML APIs via Kubernetes service discovery.
- **Grafana** (v10.2.2): Dashboards for ML Services Overview (request rate, error rate, p95 latency).
- Both deployed as pods with `emptyDir` storage and proper `securityContext`.

### Rationale

- **Prometheus annotations**: ML API pods are annotated with `prometheus.io/scrape: "true"`, `prometheus.io/port: "8000"`. Prometheus auto-discovers targets via Kubernetes SD — no manual target configuration needed when new services are added.
- **RBAC**: Prometheus has a dedicated ServiceAccount with ClusterRole permissions to discover pods, services, and endpoints across the namespace.
- **30-day retention**: `--storage.tsdb.retention.time=30d` balances observability depth with storage. Sufficient for trend analysis and incident investigation.
- **Alert rules**: `ServiceDown` alert fires after 2 minutes of a service being unreachable — catches real outages without alerting on transient pod restarts.
- **Security context**: Both Prometheus and Grafana run as non-root users (UID 65534 and 472 respectively) with appropriate fsGroup settings.

### Alternatives Considered

| Alternative | Why Not |
|---|---|
| **GCP Managed Prometheus** | Already enabled in GKE config (`managed_prometheus.enabled = true`). Coexists with self-hosted Prometheus. The self-hosted stack demonstrates MLOps monitoring skills explicitly. |
| **Cloud Monitoring + Cloud Logging** | Fully managed but less customizable. Doesn't demonstrate hands-on Prometheus/Grafana experience valued in MLOps roles. |
| **Datadog / New Relic** | SaaS monitoring with excellent ML features. But adds vendor dependency and cost ($15+/host/month) for capabilities not needed at this scale. |

---

## ADR-013: CI/CD — GitHub Actions with Matrix Testing

**Status**: Accepted | **Category**: CI/CD

### Context

Three ML projects share a monorepo and need automated testing, security scanning, Docker builds, and image publishing.

### Decision

Single workflow (`ci-mlops.yml`) with 8 parallel jobs:

1. **Tests & Coverage** — Matrix: 3 projects × 2 Python versions (3.11, 3.12)
2. **Quality Gates** — Black formatting, Flake8 critical errors
3. **Security Scanning** — Gitleaks (secrets), Bandit (code), pip-audit (dependencies)
4. **Docker Build & Scan** — Build + Trivy vulnerability scan (CRITICAL/HIGH)
5. **E2E Test** — Full pipeline execution (BankChurn)
6. **Cross-Project Integration** — Docker Compose with all 3 services (main branch only)
7. **Performance Benchmarks** — Automated benchmarks (main branch only)
8. **GHCR Publish** — Push images to GitHub Container Registry (main branch only)

### Rationale

- **Matrix strategy**: `fail-fast: false` ensures all project/version combinations are tested even if one fails. Catches Python version-specific issues early.
- **Coverage thresholds enforced in CI**: BankChurn 79%, CarVision 80%, TelecomAI 80%. Pipeline fails if coverage drops below these gates.
- **Security as first-class citizen**: Gitleaks prevents accidental secret commits. Bandit catches Python security anti-patterns. pip-audit flags vulnerable dependencies. Trivy scans Docker images for OS and library CVEs.
- **Docker build caching**: `type=gha` (GitHub Actions cache) avoids rebuilding unchanged layers. Scoped per project (`scope=${{ matrix.project }}-v2`).
- **Conditional jobs**: Integration tests, benchmarks, and image publishing only run on `main` branch pushes — saves CI minutes on feature branches while maintaining thorough validation on merge.
- **PostgreSQL service container**: Provides a real database for MLflow-dependent tests without mocking.

### Alternatives Considered

| Alternative | Why Not |
|---|---|
| **Separate workflow per project** | Duplicates pipeline logic. Harder to enforce consistent quality gates across projects. |
| **Jenkins** | Self-hosted CI requires a dedicated server. GitHub Actions is free for public repos and integrates natively with GitHub. |
| **GitLab CI** | Strong CI/CD but would require migrating the repository. GitHub Actions meets all requirements. |
| **ArgoCD / GitOps** | Declarative deployment from Git. Excellent for enterprise K8s but adds another component to manage. The current `kubectl apply` approach is simpler and sufficient. |

---

## ADR-014: Container Registry — Dual Registry Strategy

**Status**: Accepted | **Category**: Infrastructure

### Context

Docker images need to be stored and accessible from both GKE (for production) and GitHub (for CI/CD and open-source distribution).

### Decision

- **GCP Artifact Registry**: Primary registry for GKE deployments. Images pushed via Cloud Build or `docker push`.
- **GitHub Container Registry (GHCR)**: Secondary registry for open-source visibility. Images published automatically on `main` branch pushes.

### Rationale

- **Artifact Registry for GKE**: Same-region pulls are free and fast. GKE nodes authenticate automatically via Workload Identity. Versioned with `latest` + semantic version tags.
- **GHCR for portability**: Anyone can `docker pull ghcr.io/duqueom/bankchurn-predictor:latest` without GCP credentials. Demonstrates open-source distribution practice.
- **Automated tagging**: GHCR images tagged with `{branch}-{sha}` and `latest` via `docker/metadata-action`. Full traceability from image to commit.

---

## ADR-015: Storage — GCS with Lifecycle Policies

**Status**: Accepted | **Category**: Cost / Infrastructure

### Context

ML models and MLflow artifacts need durable, versioned storage.

### Decision

Two GCS buckets with uniform bucket-level access:
- `ml-models-production`: Trained models with versioning + 90-day Nearline lifecycle rule.
- `mlflow-artifacts-production`: MLflow experiment artifacts with versioning.

### Rationale

- **Versioning enabled**: Every model upload creates a new version. Previous versions are retained, enabling instant rollback without re-training.
- **Lifecycle rule (90 → Nearline)**: Models older than 90 days are automatically moved to Nearline storage ($0.01/GB/mo vs $0.02/GB/mo). At current model sizes (~12MB total), the savings are negligible in absolute terms but demonstrate production storage management.
- **Uniform bucket-level access**: Simplifies IAM by applying permissions at the bucket level rather than per-object ACLs. Required for organizational security policies.
- **force_destroy protection**: Disabled for production (`var.environment != "production"` evaluates to false), preventing accidental `terraform destroy` from deleting model storage.

---

## ADR-016: Infrastructure as Code — Terraform with Remote State

**Status**: Accepted | **Category**: Infrastructure

### Context

GCP resources must be reproducible, version-controlled, and auditable.

### Decision

Terraform with GCS backend for remote state, modular resource definitions, and environment-parameterized variables.

### Rationale

- **Remote state in GCS**: State file stored in `ml-portfolio-duque-om-202602-terraform-state` bucket. Enables team collaboration (state locking with GCS), prevents local state file accidents, and survives workstation loss.
- **Environment parameterization**: Single `main.tf` supports dev, staging, and production via `var.environment`. Naming convention (`${project_name}-${resource}-${environment}`) ensures resource isolation.
- **Secret Manager integration**: Optional path for database passwords — if `var.db_password` is empty, Terraform reads from GCP Secret Manager. Prevents plaintext secrets in tfvars for team environments.
- **Deletion protection**: Cloud SQL has `deletion_protection = true` in production. GKE has `deletion_protection = false` for easier teardown — trade-off documented, cluster can be reproduced from Terraform in minutes.

### Resources Managed (10+)

| Resource | Purpose |
|---|---|
| GKE Cluster + Node Pool | Compute for all services |
| VPC + Subnet | Network isolation |
| Cloud SQL (PostgreSQL 15) | MLflow backend (provisioned) |
| 2× GCS Buckets | ML models + MLflow artifacts |
| Artifact Registry | Docker image storage |
| Service Account + IAM | GKE workload permissions |
| VPC Peering | Private Cloud SQL access |

---

## ADR-017: Security — Defense in Depth

**Status**: Accepted | **Category**: Security

### Context

A production ML system handling predictions needs security at every layer.

### Decision

Multi-layer security approach:

### Container Level
- **Non-root users**: All containers run as UID 1000 (`appuser`) or service-specific UIDs (Prometheus: 65534, Grafana: 472).
- **Read-only capabilities**: No privileged containers, no host network access.
- **Minimal base images**: `python:3.11-slim-bookworm` — no unnecessary tools or libraries.

### Network Level
- **Private Cloud SQL**: No public IP, accessible only via VPC peering.
- **ClusterIP services**: Prometheus and Grafana are internal-only (`ClusterIP`). Not exposed to the internet.
- **NodePort for Ingress**: Only ML APIs exposed through the GCE load balancer.
- **Workload Identity**: GKE pods authenticate to GCP services via Kubernetes service accounts mapped to GCP service accounts — no JSON key files in pods.

### CI/CD Level
- **Gitleaks**: Scans Git history for accidentally committed secrets.
- **Bandit**: Static analysis for Python security anti-patterns (SQL injection, hardcoded passwords, unsafe deserialization).
- **pip-audit**: Checks all Python dependencies against known vulnerability databases.
- **Trivy**: Scans Docker images for OS package and library CVEs at CRITICAL and HIGH severity.

### Credential Management
- **GitHub Secrets**: `GCP_PROJECT_ID`, `GCP_SA_KEY`, `GCP_REGION`, `GKE_CLUSTER_NAME` stored in GitHub encrypted secrets.
- **Grafana credentials**: Kubernetes Secret (`grafana-credentials`) with optional injection — falls back to defaults if secret doesn't exist.
- **terraform.tfvars**: Gitignored. Example file provided without sensitive values.

---

## Cost Optimization Summary

### Monthly Cost Breakdown (Estimated)

| Resource | Configuration | Monthly Cost |
|---|---|---|
| GKE Management Fee | 1 zonal cluster | $0 (free tier) |
| Compute (e2-medium × 1) | Shared vCPU, 4GB | ~$25 |
| GCE Load Balancer | 1 forwarding rule | ~$18 |
| Cloud SQL (db-f1-micro) | Provisioned, minimal usage | ~$8 |
| GCS Storage | ~12MB models + state | ~$0.05 |
| Artifact Registry | 3 images × ~450MB | ~$0.50 |
| Network Egress | Minimal (same-region) | ~$0.10 |
| **Total** | | **~$52/month** |

### Optimizations Applied

| Optimization | Savings | Rationale |
|---|---|---|
| `e2-medium` vs `e2-standard-4` | **~$70/node/mo** | Shared vCPU sufficient for inference workloads |
| 1 node vs 3 nodes | **~$50/mo** | All 6 pods fit on single node |
| Single Ingress vs 3 LBs | **~$36/mo** | Path-based routing consolidates cost |
| emptyDir vs PVC | **~$4/mo** | No persistent disk needed for 4MB models |
| GCS lifecycle (Nearline) | **~$0.01/mo** | Automatic tier transition for old models |
| Same-region deployment | **~$5/mo egress** | Zero inter-region transfer fees |

### Scaling Cost Projections

| Scale | Configuration | Estimated Monthly |
|---|---|---|
| **Current** (portfolio demo) | 1 node, 6 pods | ~$52 |
| **Light production** (10 RPS) | 2 nodes, 6 pods | ~$77 |
| **Medium production** (100 RPS) | 3 nodes, 9 pods (3 replicas) | ~$127 |
| **Heavy production** (1000 RPS) | 5 nodes, 15 pods + Redis cache | ~$250+ |

---

!!! info "Document Status"
    This document reflects the current production architecture as of February 2026.
    Decisions should be revisited when the workload profile changes significantly
    (model sizes, traffic patterns, team size, or compliance requirements).
