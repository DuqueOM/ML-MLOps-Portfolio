# Models Directory

**Last Updated**: February 2026

## Current Files

### 📄 model_card.md (16 KB)
**Status**: ✅ **Active - Production Documentation**

Comprehensive model card following MLOps Staff best practices:
- RandomForest regression architecture
- Performance metrics (R²=0.77, RMSE=$4,396)
- Feature engineering (centralized FeatureEngineer class)
- Deployment instructions (API + Streamlit Dashboard)
- Monitoring and drift detection

**Updated**: February 2026 with hybrid professional format

---

### 🗂️ Legacy Files (For Reference Only)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `model.joblib` | ~6 KB | Production model (unified sklearn Pipeline) | ✅ **CURRENT** |

**Note**: Production model is a unified sklearn Pipeline saved as `models/model.joblib`.

---

## Production Model Location

**Current**: `models/model.joblib` (trained via `main.py --mode train`)

This file contains the **complete pipeline**:
- FeatureEngineer (vehicle_age, brand extraction)
- FeatureEngineer (24 engineered features)
- Preprocessor (StandardScaler + OneHotEncoder)
- LightGBM Regressor (n_estimators=500, lr=0.05, max_depth=8)

**Version**: 3.0.0  
**Framework**: LightGBM 4.6+, Scikit-learn 1.8+  
**Serialization**: joblib

---

## Key Features

**Centralized Feature Engineering**: All feature transformations handled by `src/carvision/features.py::FeatureEngineer`
- Training: Creates `vehicle_age`, `brand`, `price_per_mile`
- Inference: Applies same transformations (excluding target-dependent features)

**Data Leakage Prevention**: `price_per_mile` and `price_category` excluded from inference (depend on target `price`)
