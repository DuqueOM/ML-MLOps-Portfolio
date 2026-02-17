# Models Directory

**Last Updated**: February 2026

## Current Files

### 📄 model_card.md (16 KB)
**Status**: ✅ **Active - Production Documentation**

Comprehensive model card following MLOps Staff best practices:
- RandomForest regression architecture
- Performance metrics (R²=0.766, RMSE=$4,794)
- Feature engineering (centralized FeatureEngineer class)
- Deployment instructions (API + Streamlit Dashboard)
- Monitoring and drift detection

**Updated**: February 2026 with hybrid professional format

---

### 🗂️ Legacy Files (For Reference Only)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| `model_v1.0.0.pkl` | 5.8 KB | Initial baseline model (demo/reference) | ⚠️ **LEGACY** |

**Note**: Current production model is trained to `artifacts/model.joblib`.

---

## Production Model Location

**Current**: `artifacts/model.joblib` (trained via `main.py --mode train`)

This file contains the **complete pipeline**:
- FeatureEngineer (vehicle_age, brand extraction)
- Preprocessor (StandardScaler + OneHotEncoder)
- RandomForestRegressor (n_estimators=100, max_depth=15)

**Version**: 1.5.0  
**Framework**: Scikit-learn 1.3+  
**Serialization**: joblib

---

## Key Features

**Centralized Feature Engineering**: All feature transformations handled by `src/carvision/features.py::FeatureEngineer`
- Training: Creates `vehicle_age`, `brand`, `price_per_mile`
- Inference: Applies same transformations (excluding target-dependent features)

**Data Leakage Prevention**: `price_per_mile` and `price_category` excluded from inference (depend on target `price`)
