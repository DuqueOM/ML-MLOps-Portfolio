---
trigger: glob
globs: ["examples/**/*"]
description: Rules for working in the examples directory — educational, simplified demonstrations
---

# Working in Examples Directory

These are educational, simplified demonstrations — NOT the full production template.

## DO
- Keep examples self-contained (no external dependencies beyond pip)
- Use synthetic or public datasets only (never real/proprietary data)
- Show the pattern with minimal boilerplate
- Keep each example runnable in < 5 minutes
- Include a README.md with copy-paste commands
- Demonstrate key invariants (async inference, SHAP, quality gates)

## DO NOT
- Apply full Terraform/K8s complexity to examples
- Require GCP/AWS credentials to run
- Add production-scale monitoring (Prometheus metrics OK, AlertManager rules not needed)
- Create Kustomize overlays or Helm charts
- Require Docker to run the example

## Reminder
The full production templates are in `templates/`, not here.
Examples exist to prove the template works and to onboard new users quickly.
