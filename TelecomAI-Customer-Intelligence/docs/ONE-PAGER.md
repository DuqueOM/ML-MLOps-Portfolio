# TelecomAI Customer Intelligence — One-Pager

> **TL;DR**: ML-powered plan recommendation system for telecom customers. Predicts optimal plan (Standard vs Ultra) with 82% accuracy and 0.84 AUC-ROC.

---

## 🎯 Business Problem

Telecom companies need to match customers with the right plan based on usage patterns. Misaligned plans lead to churn (over-paying customers) or revenue loss (under-paying customers).

---

## 🔧 Solution

```mermaid
graph LR
    A[Usage Data] --> B[Preprocessing]
    B --> C[GradientBoosting]
    C --> D[Plan Recommendation]
    D --> E[Upsell/Retain]
```

**Classifier** analyzes calls, minutes, messages, and data usage to recommend the optimal plan tier.

---

## 📊 Key Metrics

| Metric | Value | Business Impact |
|--------|-------|-----------------|
| **AUC-ROC** | 0.84 | Strong discrimination |
| **Accuracy** | 82% | 4 out of 5 correct |
| **F1-Score** | 0.63 | Balanced performance |
| **Coverage** | 97% | Comprehensive tests |

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-red)

- **ML**: Scikit-learn, GradientBoosting, SHAP
- **API**: FastAPI with async support
- **Ops**: Docker, GitHub Actions CI/CD
- **Monitoring**: Prometheus metrics, MLflow

---

## 🚀 Quick Demo

```bash
# Start API
docker run -p 8003:8000 ghcr.io/duqueom/telecom-api:latest

# Make prediction
curl -X POST "http://localhost:8003/predict" \
     -H "Content-Type: application/json" \
     -d '{"calls":40,"minutes":311.9,"messages":83,"mb_used":19915.42}'

# Response
# {"prediction": 1, "probability_is_ultra": 0.78}
```

---

## 📈 Feature Importance

| Feature | Importance | Insight |
|---------|------------|---------|
| **mb_used** | 0.45 | Data usage is primary driver |
| **minutes** | 0.28 | Heavy callers need Ultra |
| **calls** | 0.15 | Call frequency matters |
| **messages** | 0.12 | SMS usage secondary |

---

## 🔗 Links

| Resource | URL |
|----------|-----|
| **GitHub** | [DuqueOM/ML-MLOps-Portfolio](https://github.com/DuqueOM/ML-MLOps-Portfolio) |
| **API Docs** | `http://localhost:8003/docs` |
| **Model Card** | [models/model_card.md](../models/model_card.md) |
| **Video Demo** | [YouTube](https://youtu.be/qmw9VlgUcn8) |

---

## 👤 Author

**Daniel Duque** — ML/MLOps Engineer  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/duqueom)
