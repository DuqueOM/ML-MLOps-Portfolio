# Models Directory

**Last Updated**: March 2026

## Current Files

### 📄 model_card.md (18 KB)
**Status**: ✅ **Active - Production Documentation**

Comprehensive model card following MLOps Staff best practices:
- Model architecture and performance metrics
- Feature importance and explainability (SHAP)
- Deployment instructions and monitoring
- Limitations, bias analysis, and governance

**Updated**: March 2026 with hybrid professional format

---

### 🗂️ Legacy Files (For Reference Only)

The following files are **legacy artifacts** from earlier development iterations and are **not used in production**:

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `best_model.pkl` | 4.0 MB | Old model artifact (pre-pipeline unification) | ⚠️ **LEGACY** |
| `preprocessor.pkl` | 4.4 KB | Separate preprocessor (pre-pipeline unification) | ⚠️ **LEGACY** |
| `model_v1.0.0.pkl` | 39 MB | Initial baseline model (demo/reference) | ⚠️ **LEGACY** |

**Note**: Current production model is trained to `artifacts/model.joblib` (unified pipeline).

---

## Production Model Location

**Current**: `artifacts/model.joblib` (trained via `main.py --mode train`)

This file contains the **complete unified pipeline**:
- Preprocessor (SimpleImputer + StandardScaler + OneHotEncoder)
- VotingClassifier (LogisticRegression + RandomForest)

**Version**: 1.5.0  
**Framework**: Scikit-learn 1.3+  
**Serialization**: joblib

---

## Migration Notes

**Before (v1.0-1.3)**:
- Separate `models/preprocessor.pkl` + `models/best_model.pkl`
- Manual two-step loading

**After (v1.4+)**:
- Unified `artifacts/model.joblib`
- Single-step loading via `ChurnPredictor.from_files()`

Legacy files kept for backward compatibility reference only.
