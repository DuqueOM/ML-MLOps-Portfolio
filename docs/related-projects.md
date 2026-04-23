# Related Projects

## ML-MLOps Production Template

[**github.com/DuqueOM/ML-MLOps-Production-Template** →](https://github.com/DuqueOM/ML-MLOps-Production-Template)

This portfolio is the **reference implementation** from which a reusable,
opinionated **production template** was extracted. The template encodes the
operational patterns, ADR-driven conventions, and agentic development workflows
distilled from building this portfolio end-to-end.

### What's in the template

- **Agentic system** — rules, skills, and workflows that guide AI coding
  assistants (Windsurf Cascade, Claude Code, Cursor) to follow enterprise
  MLOps patterns automatically
- **Production templates** for every layer: FastAPI serving, training loop,
  Terraform (GKE + EKS), CI/CD (GitHub Actions), Kustomize overlays,
  monitoring (Prometheus + Grafana)
- **12 encoded anti-patterns** — automated checks that prevent the most common
  ML production failures (event-loop blocking, memory-based HPA, models baked
  into images, multi-worker uvicorn under K8s, etc.)
- **Engineering calibration** — every component sized to actual requirements,
  avoiding both under- and over-engineering

### Portfolio vs. Template — which should I use?

| I want to… | Use this |
|-----------|---------|
| **Learn how MLOps is done in production** — see real code, real ADRs, real incidents | This portfolio (`ML-MLOps-Portfolio`) |
| **Start a new MLOps project from a proven foundation** | The template (`ML-MLOps-Production-Template`) |
| **Calibrate my own portfolio project** against a live example | This portfolio |
| **Evaluate how agentic workflows accelerate ML engineering** | Both (portfolio for "how it was used", template for "how to reuse") |

### Relationship

```
ML-MLOps-Portfolio (this repo)
    │
    │  Real deployments, 3 ML services, 18 ADRs,
    │  measured incidents, 395+ tests
    │
    └──▶ ML-MLOps-Production-Template
            │
            │  Extracted patterns, reusable templates,
            │  agentic rules/skills/workflows,
            │  anti-pattern detection
            │
            └──▶ Your next MLOps project
```

The template is the **codified knowledge** from this portfolio — the portfolio
is the **evidence** that the template's patterns work in practice.
