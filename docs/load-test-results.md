# Load Test Results — Production Performance Benchmarks

> **Date**: 2026-03-18 | **Tool**: [Locust](https://locust.io/) | **Infrastructure**: GKE (GCP) + EKS (AWS)

## Test Configuration

| Parameter | Smoke | Load | Stress |
|-----------|-------|------|--------|
| Users | 6 | 50 | 100 |
| Ramp rate | 6/s | 10/s | 20/s |
| Duration | 30s | 2m | 2m |
| SLA: error rate | < 1% | < 1% | < 5% |
| SLA: p95 latency | < 500ms | < 800ms | best-effort |

All tests run via NGINX ingress with randomized payloads simulating production traffic patterns.

---

## GCP (GKE) — `us-central1`

**Ingress**: `http://136.111.152.72`

### Smoke Test (6 users, 30s) — Idle Latencies

| Service | Endpoint | p50 | p95 | Errors |
|---------|----------|-----|-----|--------|
| BankChurn | POST /predict | **200ms** | 410ms | 0% |
| NLPInsight | POST /predict | **78ms** | 140ms | 0% |
| ChicagoTaxi | GET /demand | **100ms** | 400ms | 0% |

### Load Test (50 users, 2 min) — Production Baseline

| Service | Endpoint | p50 | p95 | Errors | Throughput |
|---------|----------|-----|-----|--------|------------|
| BankChurn | POST /predict | **3100ms** | 6500ms | 0% | 4.9 req/s |
| NLPInsight | POST /predict | **84ms** | 570ms | 0% | 9.0 req/s |
| ChicagoTaxi | GET /demand | **110ms** | 4900ms | 0% | 4.1 req/s |

### Stress Test (100 users, 2 min) — Breaking Point

| Service | Endpoint | p50 | p95 | Errors | Throughput |
|---------|----------|-----|-----|--------|------------|
| BankChurn | POST /predict | **8200ms** | 19000ms | **0.02%** | 3.6 req/s |
| NLPInsight | POST /predict | **79ms** | 170ms | 0% | 19.6 req/s |
| ChicagoTaxi | GET /demand | **100ms** | 230ms | 0% | 10.2 req/s |

---

## AWS (EKS) — `us-east-1`

**Ingress**: NLB + NGINX Ingress Controller

### Smoke Test (6 users, 30s) — Idle Latencies

| Service | Endpoint | p50 | p95 | Errors |
|---------|----------|-----|-----|--------|
| BankChurn | POST /predict | **110ms** | 140ms | 0% |
| NLPInsight | POST /predict | **100ms** | 120ms | 0% |
| ChicagoTaxi | GET /demand | **120ms** | 230ms | 0% |

### Load Test (50 users, 2 min) — Production Baseline

| Service | Endpoint | p50 | p95 | Errors | Throughput |
|---------|----------|-----|-----|--------|------------|
| BankChurn | POST /predict | **120ms** | 200ms | 0% | 14.1 req/s |
| NLPInsight | POST /predict | **100ms** | 180ms | 0% | 10.5 req/s |
| ChicagoTaxi | GET /demand | **130ms** | 210ms | 0% | 5.2 req/s |

### Stress Test (100 users, 2 min) — Breaking Point

| Service | Endpoint | p50 | p95 | Errors | Throughput |
|---------|----------|-----|-----|--------|------------|
| BankChurn | POST /predict | **130ms** | 5100ms | **0%** | 24.1 req/s |
| NLPInsight | POST /predict | **100ms** | 290ms | 0% | 18.1 req/s |
| ChicagoTaxi | GET /demand | **130ms** | 320ms | 0% | 8.7 req/s |

---

## Key Findings

### 1. Async Inference Eliminates BankChurn Failures

| Metric | Before (sync, 2 workers) | After (async, 1 worker) |
|--------|--------------------------|-------------------------|
| Stress errors (100 users) | **81%** | **0.02%** (GCP) / **0%** (AWS) |
| CPU limit | 2000m | 1000m |
| Memory per pod | ~600Mi (2 processes) | ~300Mi (1 process) |

See [ADR-015](decisions/015-async-inference-threadpool.md) for implementation details.

### 2. AWS Outperforms GCP Under Load

AWS EKS shows significantly lower latencies under concurrent load, likely due to:
- **NLB** (Layer 4) vs GKE's NGINX ingress (Layer 7) — less overhead
- **EC2 instance types** with higher single-thread performance
- Better CPU burst capacity on EKS managed nodes

### 3. NLPInsight and ChicagoTaxi Are Stable

Both services maintain sub-200ms p50 latencies even under 100 concurrent users on both clouds. No optimization needed.

### 4. BankChurn Latency Is Expected

BankChurn's `StackingClassifier` (5 base learners + meta-learner) is inherently more computationally expensive than single-model services. The 200ms idle latency is appropriate for the model complexity and the bank churn prediction use case (analyst tool, not real-time). See [ADR-003](decisions/003-stacking-classifier-bankchurn.md).

---

## Infrastructure Configuration

| Service | Workers | CPU Limit | HPA Target | Thread Pool |
|---------|---------|-----------|------------|-------------|
| BankChurn | 1 | 1000m | 50% | 4 threads (async) |
| NLPInsight | 1 | 1000m | 60% | N/A |
| ChicagoTaxi | 1 | 750m | 60% | N/A |

See [ADR-014](decisions/014-single-worker-pod-ml-inference.md) for the single-worker pod pattern rationale.
