# 04 — Modelado

> **Tiempo estimado**: 6 días (48 horas)
> 
> **Prerrequisitos**: Módulos 01-03 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Construir **pipelines sklearn completos** (preprocesamiento + modelo)
2. ✅ Implementar **validación cruzada** correctamente
3. ✅ Realizar **hyperparameter tuning** reproducible
4. ✅ Crear una clase **Trainer** profesional

---

## 📖 Contenido Teórico

### 1. Pipeline Completo sklearn

```python
"""pipeline.py — Pipeline unificado."""
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier


def create_pipeline(
    numeric_features: list[str],
    categorical_features: list[str],
    n_estimators: int = 100,
    max_depth: int | None = None,
    random_state: int = 42,
) -> Pipeline:
    """Crea un pipeline completo de clasificación.
    
    El pipeline incluye:
    1. Preprocesamiento (imputación + transformación)
    2. Modelo de clasificación
    
    Returns:
        Pipeline sklearn listo para fit/predict
    """
    # Preprocesador numérico
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    
    # Preprocesador categórico
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    
    # Combinar preprocesadores
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop",
    )
    
    # Pipeline completo
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
        )),
    ])
    
    return pipeline
```

---

### 2. Validación Cruzada

```python
"""validation.py — Validación cruzada."""
from sklearn.model_selection import (
    cross_val_score,
    StratifiedKFold,
    TimeSeriesSplit,
)
import numpy as np
import pandas as pd


def cross_validate_model(
    pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    cv: int = 5,
    scoring: str = "roc_auc",
    stratified: bool = True,
) -> dict:
    """Realiza validación cruzada estratificada.
    
    Args:
        pipeline: Pipeline sklearn
        X: Features
        y: Target
        cv: Número de folds
        scoring: Métrica a optimizar
        stratified: Si usar splits estratificados
        
    Returns:
        Dict con métricas de CV
    """
    if stratified:
        cv_splitter = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    else:
        cv_splitter = cv
    
    scores = cross_val_score(
        pipeline, X, y,
        cv=cv_splitter,
        scoring=scoring,
        n_jobs=-1,
    )
    
    return {
        "scores": scores.tolist(),
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
        "min": float(np.min(scores)),
        "max": float(np.max(scores)),
    }


def temporal_cross_validation(
    pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    n_splits: int = 5,
    scoring: str = "roc_auc",
) -> dict:
    """Validación cruzada temporal (para series de tiempo)."""
    tscv = TimeSeriesSplit(n_splits=n_splits)
    
    scores = cross_val_score(
        pipeline, X, y,
        cv=tscv,
        scoring=scoring,
    )
    
    return {
        "scores": scores.tolist(),
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
    }
```

---

### 3. Hyperparameter Tuning

```python
"""tuning.py — Búsqueda de hiperparámetros."""
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from scipy.stats import randint, uniform
import numpy as np


def tune_random_forest(
    pipeline,
    X: pd.DataFrame,
    y: pd.Series,
    n_iter: int = 50,
    cv: int = 5,
    scoring: str = "roc_auc",
    random_state: int = 42,
) -> dict:
    """Búsqueda aleatoria de hiperparámetros para RandomForest.
    
    Returns:
        Dict con mejores parámetros y score
    """
    # Espacio de búsqueda
    param_distributions = {
        "classifier__n_estimators": randint(50, 300),
        "classifier__max_depth": [None, 5, 10, 15, 20],
        "classifier__min_samples_split": randint(2, 20),
        "classifier__min_samples_leaf": randint(1, 10),
        "classifier__max_features": ["sqrt", "log2", None],
    }
    
    search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_distributions,
        n_iter=n_iter,
        cv=cv,
        scoring=scoring,
        random_state=random_state,
        n_jobs=-1,
        verbose=1,
    )
    
    search.fit(X, y)
    
    return {
        "best_params": search.best_params_,
        "best_score": float(search.best_score_),
        "cv_results": {
            "mean_test_score": search.cv_results_["mean_test_score"].tolist(),
            "std_test_score": search.cv_results_["std_test_score"].tolist(),
        },
    }
```

---

### 4. Clase Trainer Profesional

```python
"""trainer.py — Entrenador de modelos."""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Any
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
)


@dataclass
class TrainingResult:
    """Resultado de un entrenamiento."""
    
    pipeline: Any
    metrics: dict
    params: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def save(self, output_dir: str | Path) -> None:
        """Guarda resultados en disco."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar pipeline
        joblib.dump(self.pipeline, output_dir / "pipeline.pkl")
        
        # Guardar métricas
        with open(output_dir / "metrics.json", "w") as f:
            json.dump(self.metrics, f, indent=2)
        
        # Guardar parámetros
        with open(output_dir / "params.json", "w") as f:
            json.dump(self.params, f, indent=2)


class Trainer:
    """Entrenador de modelos ML."""
    
    def __init__(
        self,
        pipeline,
        output_dir: str | Path = "outputs",
    ):
        self.pipeline = pipeline
        self.output_dir = Path(output_dir)
        self._is_trained = False
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> TrainingResult:
        """Entrena el modelo y evalúa.
        
        Args:
            X_train: Features de entrenamiento
            y_train: Target de entrenamiento
            X_val: Features de validación (opcional)
            y_val: Target de validación (opcional)
            
        Returns:
            TrainingResult con pipeline, métricas y params
        """
        # Entrenar
        self.pipeline.fit(X_train, y_train)
        self._is_trained = True
        
        # Evaluar en train
        train_metrics = self._evaluate(X_train, y_train, prefix="train")
        
        # Evaluar en validación si existe
        val_metrics = {}
        if X_val is not None and y_val is not None:
            val_metrics = self._evaluate(X_val, y_val, prefix="val")
        
        # Combinar métricas
        metrics = {**train_metrics, **val_metrics}
        
        # Extraer parámetros
        params = self._get_params()
        
        return TrainingResult(
            pipeline=self.pipeline,
            metrics=metrics,
            params=params,
        )
    
    def _evaluate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        prefix: str = "",
    ) -> dict:
        """Calcula métricas de evaluación."""
        y_pred = self.pipeline.predict(X)
        y_proba = self.pipeline.predict_proba(X)[:, 1]
        
        metrics = {
            f"{prefix}_accuracy": float(accuracy_score(y, y_pred)),
            f"{prefix}_precision": float(precision_score(y, y_pred)),
            f"{prefix}_recall": float(recall_score(y, y_pred)),
            f"{prefix}_f1": float(f1_score(y, y_pred)),
            f"{prefix}_roc_auc": float(roc_auc_score(y, y_proba)),
        }
        
        return metrics
    
    def _get_params(self) -> dict:
        """Extrae parámetros del pipeline."""
        params = self.pipeline.get_params()
        # Filtrar solo parámetros serializables
        return {k: v for k, v in params.items() 
                if isinstance(v, (int, float, str, bool, type(None)))}
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Realiza predicciones."""
        if not self._is_trained:
            raise RuntimeError("Modelo no entrenado")
        return self.pipeline.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Realiza predicciones con probabilidades."""
        if not self._is_trained:
            raise RuntimeError("Modelo no entrenado")
        return self.pipeline.predict_proba(X)
```

---

## 🔧 Mini-Proyecto: Training Pipeline

### Objetivo

Crear un sistema de entrenamiento que:
1. Construya pipeline sklearn completo
2. Realice validación cruzada
3. Guarde métricas y artefactos
4. Sea reproducible

### Criterios de Éxito

- [ ] Pipeline entrena sin errores
- [ ] Métricas guardadas en JSON
- [ ] Pipeline serializado en `.pkl`
- [ ] CV score > 0.7
- [ ] Tests pasan

---

## ✅ Validación

```bash
make check-04
```

---

## ➡️ Siguiente Módulo

**[05 — MLflow & DVC](../05_mlflow_dvc/index.md)**

---

*Última actualización: 2024-12*
