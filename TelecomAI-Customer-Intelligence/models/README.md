# Models Directory

**Last Updated**: February 2026

## Current Files

### 📄 model_card.md (14 KB)
**Status**: ✅ **Active - Production Documentation**

Comprehensive model card following MLOps Staff best practices:
- VotingClassifier ensemble (LogReg + GradientBoosting + RandomForest)
- Performance metrics (AUC=0.84, Accuracy=82%)
- Business impact analysis ($5.4M annual ROI)
- Deployment instructions and monitoring
- Threshold optimization strategies

**Updated**: February 2026 with hybrid professional format

---

### 🗂️ Legacy Files (For Reference Only)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `model.joblib` | ~156 KB | Production model (unified sklearn Pipeline) | ✅ **CURRENT** |

**Note**: Production model is a unified sklearn Pipeline saved as `models/model.joblib`.

---

## Production Model Location

**Current**: `models/model.joblib` (trained via `main.py --mode train`)

This file contains the **complete pipeline**:
- Preprocessor (StandardScaler on 4 numerical features)
- VotingClassifier (soft voting, weights=[1, 2, 2])
  - LogisticRegression
  - GradientBoostingClassifier  
  - RandomForestClassifier

**Version**: 1.5.0  
**Framework**: Scikit-learn 1.3+  
**Serialization**: joblib

---

## Model Configuration

**Features**: `calls`, `minutes`, `messages`, `mb_used` (all numerical)  
**Target**: `is_ultra` (0=Smart plan $40/mo, 1=Ultra plan $70/mo)  
**Class Weights**: {0: 0.4, 1: 0.6} (handle 69/31 imbalance)

**Threshold Optimization**:
- Conservative: 0.5 (minimize false positives)
- Balanced: 0.42 (maximize F1-score)
- Aggressive: 0.35 (maximize revenue)
