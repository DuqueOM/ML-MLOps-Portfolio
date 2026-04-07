# PSI Thresholds Reference

## Population Stability Index (PSI) Formula

```
PSI = Σ (Actual% - Expected%) × ln(Actual% / Expected%)
```

Where:
- Expected% = proportion in each bin from training data
- Actual% = proportion in each bin from production data

## Per-Service Thresholds

### BankChurn-Predictor
| Feature | Warning (0.1) | Alert (0.25) | Notes |
|---------|--------------|-------------|-------|
| CreditScore | 0.10 | 0.25 | Normally distributed, stable |
| Age | 0.10 | 0.25 | Demographic shift possible |
| Balance | 0.15 | 0.30 | Higher variance expected |
| NumOfProducts | 0.10 | 0.25 | Discrete, few values |
| IsActiveMember | 0.10 | 0.25 | Binary, sensitive to campaigns |

### ChicagoTaxi-Demand-Pipeline
| Feature | Warning | Alert | Notes |
|---------|---------|-------|-------|
| hour_of_day | 0.10 | 0.25 | Seasonal patterns expected |
| day_of_week | 0.10 | 0.25 | Holiday effects |
| pickup_community_area | 0.15 | 0.30 | Urban development changes |
| lag_1h / lag_24h | 0.10 | 0.25 | Temporal stability indicator |

### NLPInsight-Analyzer
- Text-based features: Use embedding drift (cosine distance) instead of PSI
- Vocabulary drift: Monitor OOV (out-of-vocabulary) rate
- Alert threshold: OOV rate > 15% of tokens

## Interpretation Guide

```
PSI < 0.1     → STABLE    — No action needed
0.1 ≤ PSI < 0.2 → WATCH   — Log and monitor next 7 days
0.2 ≤ PSI < 0.25 → WARN  — Investigate root cause
PSI ≥ 0.25    → RETRAIN   — Trigger retraining pipeline
```

## Common Causes of Drift

| Cause | Example | Detection |
|-------|---------|-----------|
| Seasonal change | Holiday spending patterns | Expected, calendar-aware thresholds |
| Data pipeline bug | Missing values, wrong encoding | Sudden spike in multiple features |
| Population shift | New customer segment | Gradual increase over weeks |
| Feature schema change | New categories added | Immediate spike in categorical features |
