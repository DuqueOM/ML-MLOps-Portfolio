# Technical Evidence

This page is for hiring managers and technical reviewers who want proof behind
the simpler portfolio story.

## System Evidence

| Area | Evidence |
|------|----------|
| ML services | Three projects: churn prediction, financial sentiment, and taxi demand forecasting. |
| APIs | FastAPI services with health checks, metrics endpoints, and Swagger docs. |
| Containers | Dockerized services with deployment artifacts and local demo flow. |
| MLOps | MLflow tracking, model versioning patterns, DVC, drift detection, and retraining hooks. |
| Cloud deployment | Kubernetes manifests and Terraform examples for GCP and AWS. |
| CI/CD | GitHub Actions pipelines with tests, security checks, Docker builds, and deployment workflows. |
| Monitoring | Prometheus, Grafana, load tests, API metrics, and documented operational status. |
| Documentation | Model cards, runbooks, Architecture Decision Records, and project summaries. |

## Debugging And Reliability

One of the strongest signals in the portfolio is not a tool choice; it is the
debugging habit.

During load testing, an ML API reached an 81% error rate. The fix was not to
blindly add resources. I traced the failure to the serving pattern, changed the
inference execution model, and verified the result with a new test. The error
rate dropped to 0%.

Other documented lessons include:

- SHAP explanations returning zero values because the wrong explainer was used
  for the model architecture.
- Memory-based autoscaling being a poor signal for ML services with a fixed
  memory footprint.
- A forecasting project where leakage had to be identified and removed before
  the metric could be trusted.

## Cost And Business Judgment

The portfolio also documents cost choices. One example compares two cloud
deployments that both met the service goal but had very different monthly cost
profiles. The point is not that the cheapest cloud always wins. The point is
that engineering choices should be connected to value, constraints, and scale.

## Important Links

- [Projects overview](projects/overview.md)
- [Architecture overview](architecture/overview.md)
- [Decision records](architecture/decisions.md)
- [Deployment evidence](DEPLOYMENT_EVIDENCE.md)
- [Portfolio status](PORTFOLIO_STATUS.md)
- [Operations and monitoring](operations/monitoring.md)
- [API reference](api/rest-apis.md)
