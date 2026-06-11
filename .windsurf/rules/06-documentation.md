---
trigger: glob
globs: ["docs/**/*.md", "**/README.md", "AGENTS.md"]
description: Documentation standards — ADRs, READMEs, runbooks
---

# Documentation Rules

## Document Types

| Type | Audience | Location |
|------|----------|----------|
| ADRs | ML engineers, tech leads | `docs/decisions/` |
| Service READMEs | Any new engineer | `{Service}/README.md` |
| Infrastructure READMEs | DevOps/Platform engineers | `infra/terraform/*/README.md` |
| AGENTS.md | AI maintenance agents | Repo root |
| Runbooks | On-call engineers | `docs/runbooks/` |

## ADR Standards

Every ADR MUST include:
1. **Status**: Proposed | Accepted | Deprecated | Superseded by ADR-NNN
2. **Date**: YYYY-MM-DD
3. **Context**: What problem are we solving? What constraints exist?
4. **Options Considered**: Table with Pros/Cons for each option
5. **Decision**: What we decided
6. **Rationale**: Why this option over others
7. **Consequences**: Positive and Negative trade-offs
8. **Revisit When**: Conditions that would invalidate this decision

Use template: `templates/docs/decisions/adr-template.md`

## Service README Standards

Every service README MUST include:
- **Purpose**: One sentence describing the business problem
- **Quick Start**: How to run locally in < 3 commands
- **Endpoints**: Full API documentation with examples
- **Model**: Architecture, metrics, training date
- **Deploy**: How to deploy to each cloud
- **Monitoring**: Where to find dashboards, what alerts exist

## Measured Data Requirements

- NEVER use vague language ("fast", "efficient", "good performance")
- ALWAYS use measured values ("p50=12ms, p95=45ms on e2-medium")
- ALWAYS include the date of measurement and the conditions
- Costs MUST be real measured numbers, not estimates from pricing calculators

## AGENTS.md Updates

When adding a new service or changing architecture:
- Update service table with model type, key metrics
- Add any new invariants specific to the service
- Update anti-pattern detectors if new patterns discovered

## Runbook Standards

Every service MUST have a runbook with executable steps for:
- **P1** (15 min SLA): Immediate rollback commands
- **P2** (4 hours SLA): Trigger retraining commands
- **P3** (24 hours SLA): Investigation steps
- **P4** (1 week SLA): Documentation and review steps

Use template: `templates/docs/runbooks/runbook-template.md`
