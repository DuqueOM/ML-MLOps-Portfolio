# ADR-003: StackingClassifier for BankChurn

**Status**: Accepted  
**Date**: 2026-02-28  
**Decision Makers**: DuqueOM

## Context

BankChurn requires a binary classifier for customer churn prediction. Evaluated: LogisticRegression, RandomForest, XGBoost, LightGBM, VotingClassifier, StackingClassifier, and a PyTorch MLP.

## Decision

Use StackingClassifier with 4 diverse base learners (RF + GradientBoosting + XGBoost + LightGBM) and a LogisticRegression meta-learner with 5-fold CV.

## Rationale

- **AUC 0.87** vs 0.84 (best single model) — 3.6% improvement
- **Low variance**: CV AUC 0.856 ± 0.006 across 5 folds
- Diverse base learners capture complementary patterns (bagging + boosting + tree + gradient)
- Meta-learner is interpretable (LogReg weights show base learner contributions)
- sklearn-compatible — integrates with existing Pipeline + MLflow infrastructure

## Consequences

- **Positive**: Best predictive performance, robust generalization
- **Negative**: 4× training time vs single model (~20 min vs ~5 min)
- **Negative**: Larger model artifact (~4MB vs ~1MB)

## Revisit When

Training data grows >100K rows (consider online learning) or latency requirement drops below 10ms.
