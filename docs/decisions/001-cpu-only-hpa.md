# ADR-001: CPU-Only HPA for ML Services

**Status**: Accepted  
**Date**: 2026-02-20  
**Decision Makers**: DuqueOM

## Context

ML inference services load models into RAM at startup with a fixed memory footprint (~300Mi BankChurn, ~550Mi CarVision, ~140Mi NLPInsight). Memory-based HPA never triggered scale-down because `ceil(replicas × usage / target)` with constant memory always returns the same or higher replica count.

## Decision

Remove memory metric from all HPAs. Use CPU-only scaling (70% BankChurn/CarVision, 75% NLPInsight).

## Consequences

- **Positive**: BankChurn correctly scaled 3→2→1 in ~8 minutes during low traffic
- **Positive**: Cost savings during off-peak hours
- **Negative**: No memory-based protection (mitigated by resource limits)

## Revisit When

Memory usage becomes variable (e.g., batch inference, dynamic model loading).
