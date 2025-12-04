# 03 — Feature Engineering

> **Tiempo estimado**: 3 días (24 horas)
> 
> **Prerrequisitos**: Módulos 01-02 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Crear **pipelines de transformación** serializables
2. ✅ Implementar **custom transformers** con sklearn
3. ✅ Evitar **data leakage** en feature engineering
4. ✅ Persistir y cargar **transformadores entrenados**

---

## 📖 Contenido Teórico

### 1. Pipelines Serializables

#### ¿Por qué usar pipelines?

```python
# ❌ Mal: Transformaciones manuales (no reproducible)
X_train_scaled = scaler.fit_transform(X_train)
X_train_encoded = encoder.fit_transform(X_train_scaled)
# En producción: ¿cómo reproducir?

# ✅ Bien: Pipeline unificado (serializable)
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("encoder", OneHotEncoder()),
])
pipeline.fit(X_train)
joblib.dump(pipeline, "pipeline.pkl")
```

#### Estructura de Pipeline sklearn

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Definir columnas
numeric_features = ["age", "balance", "tenure"]
categorical_features = ["gender", "country"]

# Pipeline numérico
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

# Pipeline categórico
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
    ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

# Combinar en ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_pipeline, numeric_features),
        ("cat", categorical_pipeline, categorical_features),
    ],
    remainder="drop",  # Ignorar columnas no especificadas
)
```

---

### 2. Custom Transformers

#### Transformer Básico

```python
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np


class AgeGroupTransformer(BaseEstimator, TransformerMixin):
    """Transforma edad en grupos categóricos."""
    
    def __init__(self, bins: list[int] = None, labels: list[str] = None):
        self.bins = bins or [0, 25, 35, 50, 65, 120]
        self.labels = labels or ["young", "adult", "middle", "senior", "elderly"]
    
    def fit(self, X: pd.DataFrame, y=None):
        """No aprende nada, solo valida."""
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Aplica la transformación."""
        X = X.copy()
        X["age_group"] = pd.cut(
            X["age"], 
            bins=self.bins, 
            labels=self.labels,
            include_lowest=True
        )
        return X
```

#### FeatureEngineer Class Completo

```python
"""features.py — FeatureEngineer centralizado."""
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np
from typing import Optional


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Ingeniero de features centralizado para el proyecto.
    
    Esta clase encapsula toda la lógica de feature engineering,
    garantizando consistencia entre entrenamiento e inferencia.
    """
    
    def __init__(
        self,
        create_ratios: bool = True,
        create_bins: bool = True,
        drop_originals: bool = False,
    ):
        self.create_ratios = create_ratios
        self.create_bins = create_bins
        self.drop_originals = drop_originals
        
        # Estadísticas aprendidas durante fit
        self._fitted = False
        self._feature_names: list[str] = []
    
    def fit(self, X: pd.DataFrame, y=None) -> "FeatureEngineer":
        """Aprende estadísticas necesarias de los datos.
        
        En este caso, solo almacenamos los nombres de features.
        Para transformaciones más complejas, aquí calcularíamos
        estadísticas (medias, percentiles, etc.)
        """
        self._feature_names = list(X.columns)
        self._fitted = True
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Aplica todas las transformaciones de features.
        
        IMPORTANTE: Esta función debe ser idempotente y
        no modificar el DataFrame original.
        """
        if not self._fitted:
            raise RuntimeError("FeatureEngineer no ha sido entrenado. Llama fit() primero.")
        
        X = X.copy()
        
        if self.create_ratios:
            X = self._add_ratios(X)
        
        if self.create_bins:
            X = self._add_bins(X)
        
        if self.drop_originals:
            X = self._drop_original_columns(X)
        
        return X
    
    def _add_ratios(self, X: pd.DataFrame) -> pd.DataFrame:
        """Agrega ratios calculados."""
        # Ejemplo: ratio balance/tenure
        if "balance" in X.columns and "tenure" in X.columns:
            # Evitar división por cero
            X["balance_per_tenure"] = X["balance"] / X["tenure"].replace(0, 1)
        
        return X
    
    def _add_bins(self, X: pd.DataFrame) -> pd.DataFrame:
        """Agrega variables binned."""
        if "age" in X.columns:
            X["age_group"] = pd.cut(
                X["age"],
                bins=[0, 30, 50, 120],
                labels=["young", "middle", "senior"],
                include_lowest=True
            )
        
        return X
    
    def _drop_original_columns(self, X: pd.DataFrame) -> pd.DataFrame:
        """Elimina columnas originales si se solicita."""
        # Implementar según necesidad
        return X
    
    def get_feature_names_out(self) -> list[str]:
        """Retorna nombres de features de salida."""
        return self._feature_names
```

---

### 3. Prevención de Data Leakage

#### ⚠️ Qué es Data Leakage

Data leakage ocurre cuando información del conjunto de test "filtra" hacia el entrenamiento, resultando en métricas irreales.

```python
# ❌ INCORRECTO: Fit en todo el dataset
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Usa estadísticas de TODO X
X_train, X_test = train_test_split(X_scaled)  # Test "contaminado"

# ✅ CORRECTO: Fit solo en train
X_train, X_test = train_test_split(X)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Solo train
X_test_scaled = scaler.transform(X_test)  # Sin fit!
```

#### Features que causan leakage

```python
# ❌ LEAKAGE: Features derivadas del target
df["avg_churn_by_country"] = df.groupby("country")["churn"].transform("mean")

# ❌ LEAKAGE: Features del futuro
df["next_month_balance"] = df["balance"].shift(-1)

# ✅ CORRECTO: Solo usar información disponible en producción
df["balance_change"] = df["balance"] - df["previous_balance"]
```

---

### 4. Persistencia de Transformadores

```python
"""persistence.py — Guardar y cargar pipelines."""
import joblib
from pathlib import Path
from typing import Any


def save_pipeline(pipeline: Any, path: str | Path) -> None:
    """Guarda un pipeline serializado."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)
    print(f"Pipeline guardado en {path}")


def load_pipeline(path: str | Path) -> Any:
    """Carga un pipeline serializado."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Pipeline no encontrado: {path}")
    return joblib.load(path)


# Uso
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

pipeline = Pipeline([("scaler", StandardScaler())])
pipeline.fit(X_train)

# Guardar
save_pipeline(pipeline, "models/preprocessor.pkl")

# Cargar (en otro script/sesión)
pipeline = load_pipeline("models/preprocessor.pkl")
X_new_transformed = pipeline.transform(X_new)
```

---

## 🔧 Mini-Proyecto: FeatureEngineer Serializable

### Objetivo

Crear una clase `FeatureEngineer` que:
1. Implemente transformaciones de features
2. Sea compatible con sklearn Pipeline
3. Se pueda serializar con joblib
4. Tenga tests unitarios

### Estructura

```
work/03_feature_engineering/
├── src/
│   ├── __init__.py
│   ├── features.py        # FeatureEngineer
│   └── persistence.py     # Guardar/cargar
├── tests/
│   ├── __init__.py
│   └── test_features.py
├── artifacts/
│   └── .gitkeep
└── pyproject.toml
```

### Criterios de Éxito

- [ ] FeatureEngineer funciona en pipeline sklearn
- [ ] Se puede serializar y deserializar
- [ ] No hay data leakage (fit solo en train)
- [ ] Tests pasan: `pytest tests/ -v`

---

## ✅ Validación

```bash
make check-03
```

---

## ➡️ Siguiente Módulo

**[04 — Modelado](../04_modelado/index.md)**

---

*Última actualización: 2024-12*
