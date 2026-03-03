# Models Directory

**Last Updated**: February 2026

## Current Files

### 📄 model_card.md (18 KB)
**Status**: ✅ **Active - Production Documentation**

Comprehensive model card following MLOps Staff best practices:
- Model architecture and performance metrics
- Feature importance and explainability (SHAP)
- Deployment instructions and monitoring
- Limitations, bias analysis, and governance

**Updated**: February 2026 with hybrid professional format

---

### 🗂️ Legacy Files (For Reference Only)

The following files are **legacy artifacts** from earlier development iterations and are **not used in production**:

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `model.joblib` | ~4 MB | Production model (unified sklearn Pipeline) | ✅ **CURRENT** |
| `preprocessor.joblib` | ~4 KB | Standalone preprocessor (optional, for debugging) | ✅ Optional |

**Note**: Production model is a unified sklearn Pipeline saved as `models/model.joblib`.

---

## Production Model Location

**Current**: `artifacts/model.joblib` (trained via `main.py --mode train`)

This file contains the **complete unified pipeline**:
- Preprocessor (SimpleImputer + StandardScaler + OneHotEncoder)
- StackingClassifier (RF + GradientBoosting + XGBoost + LightGBM → LogisticRegression)

**Version**: 3.0.0  
**Framework**: Scikit-learn 1.8+  
**Serialization**: joblib

---

## Migration Notes

**Before (v1.0-1.3)**:
- Separate `models/preprocessor.pkl` + `models/best_model.pkl`
- Manual two-step loading (`.pkl` extension)

**After (v1.4+)**:
- Unified `models/model.joblib`
- Single-step loading via `ChurnPredictor.from_files()`

Legacy files kept for backward compatibility reference only.
