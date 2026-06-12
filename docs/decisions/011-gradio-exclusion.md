<div class="portfolio-page" markdown="1">

# ADR-011: Gradio Demo — Not Deployed to Production

- **Status**: Accepted
- **Date**: 2026-03-10
- **Authors**: Duque Ortega Mutis
- **Related**: [ADR-009](009-simplification-when-not-to-build.md) (simplification philosophy)

> **TL;DR**: Kept Gradio as a local development tool only. Deploying it to K8s would create architectural inconsistency (1 of 3 services with a UI), duplicate Swagger UI functionality, and consume cluster resources for a component that doesn't serve the portfolio's MLOps thesis.

## Decision

**Do NOT deploy Gradio to the Kubernetes cluster.** Keep it as a local development tool only.

## Context

After removing CarVision (and its Streamlit dashboard) from the portfolio in v3.5.0, the three remaining services (BankChurn, NLPInsight, ChicagoTaxi) are all API-only FastAPI applications. The question arose whether BankChurn's Gradio demo should be deployed to fill the "interactive UI" gap.

## Evaluation

### Arguments FOR deploying Gradio

| Argument | Weight |
|----------|--------|
| Visual demo impresses non-technical reviewers | Medium |
| Shows ability to build user-facing ML interfaces | Low (not the portfolio's focus) |
| Fills gap left by CarVision Streamlit removal | Low |

### Arguments AGAINST deploying Gradio

| Argument | Weight |
|----------|--------|
| **Inconsistency**: Only 1 of 3 projects would have a UI → asymmetric architecture | High |
| **Not suited for a hardened service**: No auth, no RBAC, limited scaling, no production hardening | High |
| **Redundant**: Swagger UI already provides interactive API testing for all 3 services | High |
| **Resource impact**: Additional pod on an e2-medium cluster (shared vCPU, 4GB RAM) | Medium |
| **Scope creep**: Portfolio demonstrates MLOps (CI/CD, K8s, monitoring), not UI/UX | Medium |
| **Over-engineering**: Adding infrastructure that doesn't serve the portfolio's thesis | Medium |

### What mature teams actually do

In production ML platforms, the frontend is typically:
- A dedicated React/Vue/Next.js application built by a frontend team
- An internal tool (Retool, Streamlit Cloud) for stakeholders
- NOT a Gradio widget embedded in the ML service pod

Deploying Gradio alongside FastAPI conflates two concerns: **ML serving** (FastAPI) and **user interface** (Gradio). Mature service architecture separates these.

## Alternatives Considered

| Alternative | Verdict |
|-------------|---------|
| Deploy Gradio as sidecar in BankChurn pod | Rejected — increases pod resource usage, inconsistent with other services |
| Deploy Gradio as separate Deployment + Ingress path | Rejected — full K8s stack for a demo UI that duplicates Swagger UI |
| Add Gradio to all 3 projects | Rejected — NLPInsight and ChicagoTaxi have simple inputs; Swagger UI is sufficient |
| Replace Gradio with a React frontend | Rejected — significant effort, out of portfolio scope (MLOps, not frontend) |

## Consequences

- `app/gradio_demo.py` remains in BankChurn for **local development and demos** (`python app/gradio_demo.py`)
- No K8s deployment, service, or Ingress path for Gradio
- Portfolio UI interaction is demonstrated via **Swagger UI** (`/bankchurn/docs`, `/nlpinsight/docs`, `/chicagotaxi/docs`)
- If a recruiter or interviewer asks about UI capabilities, point to Gradio demo code as evidence of the skill, and explain the architectural decision to keep it out of production

## Principle

> **Every component in the cluster must justify its resource cost and operational burden.** A demo UI that duplicates Swagger UI functionality does not meet this bar. The portfolio's value comes from the MLOps infrastructure (CI/CD, monitoring, auto-scaling, canary deployments), not from a prototype UI.

</div>
