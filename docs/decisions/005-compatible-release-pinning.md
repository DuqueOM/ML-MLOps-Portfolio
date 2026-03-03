# ADR-005: Compatible Release (~=) Dependency Pinning

**Status**: Accepted  
**Date**: 2026-03-01  
**Decision Makers**: DuqueOM

## Context

Production dependencies were pinned with `>=` (minimum version), causing non-reproducible builds. A numpy version mismatch (1.26 vs 2.4) caused MT19937 BitGenerator deserialization errors when loading sklearn models.

## Decision

Pin all dependencies with `~=` (compatible release operator) in all requirements files.

## Rationale

- `~=1.8.0` allows `1.8.x` patches but blocks `1.9.0` — reproducible yet patchable
- Prevents the exact class of error encountered (sklearn model trained with numpy 2.4 failed to load with numpy 1.26)
- Aligns training and serving environments

## Consequences

- **Positive**: Reproducible builds, model loading guaranteed
- **Positive**: Still receives security patches within minor version
- **Negative**: Must manually bump versions for major upgrades
