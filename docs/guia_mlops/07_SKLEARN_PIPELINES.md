# 07. sklearn Pipelines: El Corazón de MLOps

## 🎯 Objetivo del Módulo

Dominar el patrón más importante de ML profesional: **pipelines unificados** que garantizan reproducibilidad desde entrenamiento hasta producción.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🚨 EL ERROR #1 EN PRODUCCIÓN ML:                                            ║
║                                                                              ║
║  Entrenar con una transformación, servir con otra.                           ║
║                                                                              ║
║  Ejemplo real:                                                               ║
║  • Training: StandardScaler fitted en train set (mean=45000, std=20000)      ║
║  • Production: StandardScaler fitted en cada request (mean=???, std=???)     ║
║  • Resultado: Predicciones COMPLETAMENTE diferentes                          ║
║                                                                              ║
║  🛡️ LA SOLUCIÓN: Pipeline unificado que guarda TODO junto                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Contenido

1. [¿Por Qué Pipelines?](#71-por-qué-pipelines)
2. [ColumnTransformer: Transformaciones Paralelas](#72-columntransformer-transformaciones-paralelas)
3. [Custom Transformers](#73-custom-transformers-tu-superpoder)
4. [Pipeline Completo: Código Real](#74-pipeline-completo-código-real)
5. [Ejercicios Prácticos](#75-ejercicios-prácticos)

---

## 7.1 ¿Por Qué Pipelines?

### La Analogía de la Línea de Ensamblaje

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  🏭 IMAGINA UNA FÁBRICA DE AUTOS:                                         ║
║                                                                           ║
║  SIN LÍNEA DE ENSAMBLAJE (código suelto):                                 ║
║  • Trabajador 1 pone ruedas, pero a veces se le olvida                    ║
║  • Trabajador 2 pinta, pero usa colores diferentes cada día               ║
║  • Trabajador 3 instala motor, pero a veces del modelo equivocado         ║
║  • Resultado: Cada auto es diferente, imposible de mantener               ║
║                                                                           ║
║  CON LÍNEA DE ENSAMBLAJE (Pipeline):                                      ║
║  • Paso 1: Chasis → Paso 2: Motor → Paso 3: Pintura → Paso 4: Ruedas      ║
║  • Cada paso está definido y es SIEMPRE igual                             ║
║  • El proceso completo es una sola unidad                                 ║
║  • Resultado: Todos los autos son consistentes                            ║
║                                                                           ║
║  sklearn Pipeline = Línea de ensamblaje para ML                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### El Problema Real: Training-Serving Skew

```python
# ❌ CÓDIGO PROBLEMÁTICO (muy común en notebooks convertidos a producción)

# === ENTRENAMIENTO ===
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Ajustar scaler en datos de entrenamiento
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train[num_cols])  # ← fit aquí

encoder = OneHotEncoder()
X_train_encoded = encoder.fit_transform(X_train[cat_cols])  # ← fit aquí

# Entrenar modelo
model = RandomForestClassifier()
model.fit(X_train_processed, y_train)

# Guardar modelo... pero ¿y el scaler? ¿y el encoder?
joblib.dump(model, "model.pkl")  # ← Solo guarda el modelo!

# === PRODUCCIÓN (meses después, otro desarrollador) ===
model = joblib.load("model.pkl")

# ¿Cómo transformo los datos nuevos?
# 🤷 No tengo el scaler ni el encoder fitted
# 🤷 Incluso si los tuviera, ¿cómo sé qué columnas usar?
# 🤷 ¿Era StandardScaler o MinMaxScaler?

# "Solución" del desarrollador desesperado:
scaler = StandardScaler()
X_new_scaled = scaler.fit_transform(X_new[num_cols])  # ← fit en datos NUEVOS!
# ⚠️ Ahora mean y std son DIFERENTES a los de entrenamiento
# ⚠️ Las predicciones son BASURA

# ============================================================================
# ✅ SOLUCIÓN: Pipeline Unificado
# ============================================================================

# === ENTRENAMIENTO ===
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Definir pipeline completo
pipeline = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ])),
    ('model', RandomForestClassifier())
])

# Un solo fit entrena TODO
pipeline.fit(X_train, y_train)

# Guardar TODO junto
joblib.dump(pipeline, "pipeline.pkl")  # ← Scaler + Encoder + Model

# === PRODUCCIÓN ===
pipeline = joblib.load("pipeline.pkl")

# Una sola llamada hace TODO (con los parámetros de entrenamiento)
predictions = pipeline.predict(X_new)  # ← Transforma Y predice

# ✅ El scaler usa mean/std del entrenamiento
# ✅ El encoder conoce las categorías del entrenamiento
# ✅ Las predicciones son consistentes
```

---

## 7.2 ColumnTransformer: Transformaciones Paralelas

### El Problema: Diferentes Columnas, Diferentes Tratamientos

```
Datos de un banco:
┌─────────────┬───────────┬─────────┬─────────┬────────┐
│ CreditScore │ Geography │ Gender  │   Age   │ Balance│
├─────────────┼───────────┼─────────┼─────────┼────────┤
│     619     │  France   │  Female │    42   │  10000 │
│     608     │   Spain   │  Female │    41   │  83808 │
│     502     │  France   │  Female │    42   │      0 │
└─────────────┴───────────┴─────────┴─────────┴────────┘

Columnas numéricas (CreditScore, Age, Balance):
→ StandardScaler: normalizar a mean=0, std=1

Columnas categóricas (Geography, Gender):
→ OneHotEncoder: convertir a columnas binarias
```

### ColumnTransformer: La Solución Elegante

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# Definir qué columnas son de cada tipo
num_cols = ["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "EstimatedSalary"]
cat_cols = ["Geography", "Gender"]

# Pipeline para numéricas: Imputar NaN → Escalar
num_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),  # NaN → mediana
    ('scaler', StandardScaler())                     # Normalizar
])

# Pipeline para categóricas: Imputar NaN → One-Hot
cat_pipeline = Pipeline([
    ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
    ('encoder', OneHotEncoder(handle_unknown='ignore'))  # Categorías nuevas → ignorar
])

# ColumnTransformer: Aplica cada pipeline a sus columnas
preprocessor = ColumnTransformer(
    transformers=[
        ('num', num_pipeline, num_cols),  # (nombre, transformer, columnas)
        ('cat', cat_pipeline, cat_cols)
    ],
    remainder='drop'  # Columnas no listadas se eliminan
)

# Resultado: Un solo objeto que sabe transformar todo
X_processed = preprocessor.fit_transform(X_train)
```

### Visualización del Flujo

```
                        ColumnTransformer
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        num_pipeline    cat_pipeline    remainder
              │               │               │
              │               │               │
    ┌─────────┴─────────┐     │               │
    │                   │     │               │
    ▼                   ▼     ▼               ▼
┌─────────┐       ┌─────────┐ ┌─────────┐   drop
│Imputer  │       │ Scaler  │ │ Imputer │
│(median) │       │         │ │(Unknown)│
└─────────┘       └─────────┘ └────┬────┘
                                   │
                                   ▼
                              ┌─────────┐
                              │ OneHot  │
                              │ Encoder │
                              └─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
    [6 columnas numéricas]  [3 Geography cols]  [2 Gender cols]
         escaladas            (France, Spain,     (Female, Male)
                               Germany)

    Output: 11 columnas totales (6 + 3 + 2)
```

---

## 7.3 Custom Transformers: Tu Superpoder

### ¿Cuándo Crear un Custom Transformer?

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  Crea un Custom Transformer cuando:                                       ║
║                                                                           ║
║  ✅ Necesitas feature engineering específico del dominio                  ║
║  ✅ La transformación debe aplicarse igual en train y producción          ║
║  ✅ sklearn no tiene un transformer que haga lo que necesitas             ║
║                                                                           ║
║  Ejemplos del portafolio:                                                 ║
║  • CarVision: Calcular vehicle_age desde model_year                       ║
║  • CarVision: Extraer brand desde model                                   ║
║  • BankChurn: Resampling para clases desbalanceadas                       ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Ejemplo 1: FeatureEngineer (CarVision)

```python
# src/carvision/features.py - Código REAL del portafolio

from __future__ import annotations

from typing import Optional

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Centralized feature engineering to ensure consistency across
    Training, Inference, and Analysis.
    
    Este transformer garantiza que las mismas transformaciones
    se apliquen en:
    1. Entrenamiento (training.py)
    2. Inferencia API (fastapi_app.py)
    3. Dashboard (streamlit_app.py)
    
    Attributes
    ----------
    current_year : int, optional
        Año para calcular vehicle_age. Si None, usa año actual.
    
    Examples
    --------
    >>> fe = FeatureEngineer(current_year=2024)
    >>> df_transformed = fe.fit_transform(df)
    >>> print(df_transformed.columns)
    # Incluye: vehicle_age, brand (derivadas de model_year y model)
    """

    def __init__(self, current_year: Optional[int] = None):
        self.current_year = current_year

    def fit(self, X: pd.DataFrame, y: pd.DataFrame = None) -> "FeatureEngineer":
        """Fit no hace nada (stateless transformer)."""
        # Este transformer es stateless: no aprende nada de los datos
        # Solo necesita fit() para ser compatible con Pipeline
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Aplica feature engineering.
        
        Features creadas:
        - vehicle_age: current_year - model_year
        - brand: primera palabra de model
        - price_per_mile: price / odometer (solo si price existe)
        """
        X = X.copy()  # ← Nunca modificar el input original

        # Usar año configurado o año actual
        year = self.current_year or pd.Timestamp.now().year

        # Feature: Edad del vehículo
        if "model_year" in X.columns:
            X["vehicle_age"] = year - X["model_year"]

        # Feature: Marca (primera palabra del modelo)
        if "model" in X.columns:
            X["brand"] = X["model"].astype(str).str.split().str[0]

        # Features derivadas (solo en training, no en inferencia)
        # Porque price no está disponible en inferencia
        if "odometer" in X.columns and "price" in X.columns:
            X["price_per_mile"] = X["price"] / (X["odometer"] + 1)

        return X
    
    # Métodos opcionales para mejor introspección
    def get_feature_names_out(self, input_features=None):
        """Retorna nombres de features de salida."""
        base = list(input_features) if input_features else []
        return base + ["vehicle_age", "brand"]
```

### Ejemplo 2: ResampleClassifier (BankChurn)

```python
# src/bankchurn/models.py - Código REAL del portafolio

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_is_fitted


class ResampleClassifier(BaseEstimator, ClassifierMixin):
    """Custom classifier with resampling for imbalanced datasets.
    
    Implementa oversampling (SMOTE), undersampling, y class weighting
    para mejorar performance en clasificación desbalanceada.
    
    Este wrapper permite:
    1. Probar diferentes estrategias de resampling fácilmente
    2. Mantener la interfaz sklearn estándar (fit/predict)
    3. Ser parte de un Pipeline (incluyendo GridSearchCV)
    
    Parameters
    ----------
    estimator : estimator object, optional
        Clasificador base. Si None, usa LogisticRegression.
    strategy : {"none", "oversample", "undersample", "class_weight"}
        Estrategia de resampling:
        - "none": Sin resampling
        - "oversample": SMOTE oversampling de clase minoritaria
        - "undersample": Undersampling de clase mayoritaria
        - "class_weight": Balanceo automático de pesos
    random_state : int, default=42
        Semilla para reproducibilidad.
    
    Examples
    --------
    >>> clf = ResampleClassifier(
    ...     estimator=RandomForestClassifier(),
    ...     strategy="oversample",
    ...     random_state=42
    ... )
    >>> clf.fit(X_train, y_train)
    >>> predictions = clf.predict(X_test)
    """

    def __init__(
        self,
        estimator: BaseEstimator | None = None,
        strategy: str = "none",
        random_state: int = 42,
    ) -> None:
        self.estimator = estimator
        self.strategy = strategy
        self.random_state = random_state

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ResampleClassifier":
        """Entrena el clasificador con resampling opcional."""
        from sklearn.linear_model import LogisticRegression

        # Inicializar estimador si no se proporcionó
        if self.estimator is None:
            self.estimator_ = LogisticRegression(random_state=self.random_state)
        else:
            # Clonar para no modificar el original
            from sklearn.base import clone
            self.estimator_ = clone(self.estimator)

        # Guardar clases (requerido por sklearn)
        self.classes_ = np.unique(y)

        # Aplicar estrategia de resampling
        X_resampled, y_resampled = self._apply_resampling(X, y)

        # Entrenar estimador base
        self.estimator_.fit(X_resampled, y_resampled)

        return self

    def _apply_resampling(
        self, X: np.ndarray, y: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Aplica la estrategia de resampling."""
        if self.strategy == "none":
            return X, y
        
        elif self.strategy == "oversample":
            try:
                from imblearn.over_sampling import SMOTE
                smote = SMOTE(random_state=self.random_state)
                return smote.fit_resample(X, y)
            except ImportError:
                # Si imblearn no está instalado, ignorar
                return X, y
        
        elif self.strategy == "undersample":
            try:
                from imblearn.under_sampling import RandomUnderSampler
                rus = RandomUnderSampler(random_state=self.random_state)
                return rus.fit_resample(X, y)
            except ImportError:
                return X, y
        
        elif self.strategy == "class_weight":
            # No modifica datos, el estimador maneja los pesos
            if hasattr(self.estimator_, 'class_weight'):
                self.estimator_.set_params(class_weight='balanced')
            return X, y
        
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predice clases."""
        check_is_fitted(self, ['estimator_', 'classes_'])
        return self.estimator_.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predice probabilidades."""
        check_is_fitted(self, ['estimator_', 'classes_'])
        return self.estimator_.predict_proba(X)
```

### La Plantilla: Crea Tu Propio Transformer

```python
from sklearn.base import BaseEstimator, TransformerMixin

class MiTransformer(BaseEstimator, TransformerMixin):
    """
    Plantilla para crear transformers custom.
    
    REGLAS IMPORTANTES:
    1. __init__ solo guarda parámetros (no computa nada)
    2. fit() aprende de los datos (puede ser no-op)
    3. transform() aplica la transformación
    4. Nunca modificar input, siempre X.copy()
    """
    
    def __init__(self, param1: str = "default", param2: int = 10):
        # Solo guardar parámetros, NO computar nada
        self.param1 = param1
        self.param2 = param2
    
    def fit(self, X, y=None):
        """Aprende de los datos (opcional).
        
        Ejemplos de qué aprender:
        - Media/std para normalización
        - Vocabulario para encoding
        - Umbrales para binning
        """
        # Si el transformer es stateless, solo retorna self
        # Si aprende algo:
        # self.learned_param_ = compute_something(X)
        return self
    
    def transform(self, X):
        """Aplica la transformación."""
        X = X.copy()  # ← Siempre copiar
        # ... tu lógica de transformación ...
        return X
```

---

## 7.4 Pipeline Completo: Código Real

### CarVision: El Pipeline de 3 Etapas

```python
# src/carvision/training.py - Pipeline REAL del portafolio

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor

from src.carvision.features import FeatureEngineer

def build_pipeline(cfg: dict) -> Pipeline:
    """Construye el pipeline completo de CarVision.
    
    Estructura: Features → Preprocessing → Model
    
    Esta arquitectura de 3 etapas garantiza:
    1. Feature engineering consistente (FeatureEngineer)
    2. Preprocesamiento apropiado por tipo de columna (ColumnTransformer)
    3. Modelo entrenado con datos correctamente transformados
    """
    # Parámetros de configuración
    num_cols = cfg["preprocessing"]["numeric_features"]
    cat_cols = cfg["preprocessing"]["categorical_features"]
    dataset_year = cfg.get("dataset_year", 2024)
    rf_params = cfg["training"].get("random_forest_params", {})
    
    # Etapa 1: Feature Engineering
    feature_engineer = FeatureEngineer(current_year=dataset_year)
    
    # Etapa 2: Preprocessing (después de feature engineering)
    # Nota: Las columnas aquí son las que EXISTEN después del FeatureEngineer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), num_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ]), cat_cols)
        ],
        remainder='drop'
    )
    
    # Etapa 3: Modelo
    model = RandomForestRegressor(**rf_params)
    
    # Pipeline completo: Una sola unidad entrenable/guardable
    pipeline = Pipeline([
        ('features', feature_engineer),    # Crea vehicle_age, brand
        ('pre', preprocessor),              # Escala y encoda
        ('model', model)                    # Predice
    ])
    
    return pipeline


# === USO ===
# Entrenamiento
pipeline = build_pipeline(config)
pipeline.fit(X_train, y_train)

# Guardar TODO junto
joblib.dump(pipeline, "artifacts/model.joblib")

# Producción
pipeline = joblib.load("artifacts/model.joblib")
price = pipeline.predict(X_new)  # Una llamada hace TODO
```

### BankChurn: Pipeline con Ensemble

```python
# src/bankchurn/training.py - Pipeline REAL del portafolio

def build_pipeline(self) -> Pipeline:
    """Construye el pipeline de BankChurn.
    
    Estructura:
    - Preprocessing: ColumnTransformer (num + cat)
    - Model: VotingClassifier o ResampleClassifier
    """
    # Columnas desde config
    num_cols = self.config.data.numerical_features
    cat_cols = self.config.data.categorical_features
    
    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), num_cols),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
                ('encoder', OneHotEncoder(handle_unknown='ignore'))
            ]), cat_cols)
        ]
    )
    
    # Modelo: Ensemble o single model
    if self.config.model.type == "ensemble":
        model = VotingClassifier(
            estimators=[
                ('lr', LogisticRegression(
                    **self.config.model.logistic_regression.dict()
                )),
                ('rf', RandomForestClassifier(
                    **self.config.model.random_forest.dict()
                ))
            ],
            voting=self.config.model.ensemble.voting,
            weights=self.config.model.ensemble.weights
        )
    else:
        # Con wrapper de resampling
        model = ResampleClassifier(
            estimator=RandomForestClassifier(
                **self.config.model.random_forest.dict()
            ),
            strategy=self.config.model.resampling_strategy,
            random_state=self.random_state
        )
    
    # Pipeline final
    return Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
```

---

## 7.5 Ejercicios Prácticos

### Ejercicio 1: Construir un ColumnTransformer

```python
# Datos de telecom:
# - calls: float (numérico)
# - minutes: float (numérico)
# - messages: int (numérico)
# - mb_used: float (numérico)
# - plan_type: str (categórico) - "basic", "premium"
# - region: str (categórico) - "north", "south", "east", "west"

# Tu tarea: Crea un ColumnTransformer que:
# 1. Escale las columnas numéricas con StandardScaler
# 2. Encode las columnas categóricas con OneHotEncoder
# 3. Maneje valores faltantes apropiadamente

num_cols = ["calls", "minutes", "messages", "mb_used"]
cat_cols = ["plan_type", "region"]

# Escribe tu código aquí:
preprocessor = ColumnTransformer(
    # ...
)
```

<details>
<summary>📝 Ver Solución</summary>

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

num_cols = ["calls", "minutes", "messages", "mb_used"]
cat_cols = ["plan_type", "region"]

preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), num_cols),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ]), cat_cols)
    ],
    remainder='drop'
)

# Verificar
print(f"Transformers: {[t[0] for t in preprocessor.transformers]}")
# Output: ['num', 'cat']
```

</details>

---

### Ejercicio 2: Crear un Custom Transformer

```python
# Tu tarea: Crea un transformer que calcule ratios de uso de telecom
# 
# Features a crear:
# - minutes_per_call = minutes / (calls + 1)
# - mb_per_message = mb_used / (messages + 1)
# - total_usage = calls + messages + (mb_used / 1000)
#
# Requisitos:
# - Debe heredar de BaseEstimator y TransformerMixin
# - fit() debe retornar self
# - transform() debe retornar DataFrame con nuevas columnas

from sklearn.base import BaseEstimator, TransformerMixin

class TelecomFeatureEngineer(BaseEstimator, TransformerMixin):
    # Tu código aquí
    pass
```

<details>
<summary>📝 Ver Solución</summary>

```python
from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


class TelecomFeatureEngineer(BaseEstimator, TransformerMixin):
    """Feature engineering para datos de telecom."""
    
    def __init__(self):
        pass
    
    def fit(self, X: pd.DataFrame, y=None):
        """No aprende nada (stateless)."""
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Crea features derivadas."""
        X = X.copy()
        
        # Minutos por llamada
        if "minutes" in X.columns and "calls" in X.columns:
            X["minutes_per_call"] = X["minutes"] / (X["calls"] + 1)
        
        # MB por mensaje
        if "mb_used" in X.columns and "messages" in X.columns:
            X["mb_per_message"] = X["mb_used"] / (X["messages"] + 1)
        
        # Uso total normalizado
        if all(col in X.columns for col in ["calls", "messages", "mb_used"]):
            X["total_usage"] = X["calls"] + X["messages"] + (X["mb_used"] / 1000)
        
        return X
    
    def get_feature_names_out(self, input_features=None):
        """Retorna nombres de features creadas."""
        return ["minutes_per_call", "mb_per_message", "total_usage"]


# Verificar
import pandas as pd

df = pd.DataFrame({
    "calls": [50, 100],
    "minutes": [200, 500],
    "messages": [100, 50],
    "mb_used": [5000, 10000]
})

fe = TelecomFeatureEngineer()
df_transformed = fe.fit_transform(df)
print(df_transformed.columns.tolist())
# Output incluye: minutes_per_call, mb_per_message, total_usage
```

</details>

---

### Ejercicio 3: Pipeline Completo para TelecomAI

```python
# Tu tarea: Construye un pipeline completo para TelecomAI
# 
# Estructura:
# 1. TelecomFeatureEngineer (del ejercicio anterior)
# 2. ColumnTransformer para preprocessing
# 3. LogisticRegression como modelo
#
# El pipeline debe ser guardable con joblib

# Tu código aquí:
def build_telecom_pipeline():
    pass
```

<details>
<summary>📝 Ver Solución</summary>

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
import joblib


def build_telecom_pipeline(config: dict = None) -> Pipeline:
    """Construye pipeline completo para TelecomAI."""
    
    # Configuración por defecto
    if config is None:
        config = {
            "num_cols": ["calls", "minutes", "messages", "mb_used", 
                        "minutes_per_call", "mb_per_message", "total_usage"],
            "cat_cols": [],
            "random_state": 42
        }
    
    num_cols = config["num_cols"]
    cat_cols = config.get("cat_cols", [])
    
    # Etapa 1: Feature Engineering
    feature_engineer = TelecomFeatureEngineer()
    
    # Etapa 2: Preprocessing
    transformers = [
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), num_cols)
    ]
    
    if cat_cols:
        transformers.append(
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore'))
            ]), cat_cols)
        )
    
    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder='drop'
    )
    
    # Etapa 3: Modelo
    model = LogisticRegression(
        random_state=config.get("random_state", 42),
        max_iter=1000
    )
    
    # Pipeline completo
    pipeline = Pipeline([
        ('features', feature_engineer),
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    return pipeline


# Uso
pipeline = build_telecom_pipeline()
# pipeline.fit(X_train, y_train)
# joblib.dump(pipeline, "artifacts/model.joblib")
```

</details>

---

## 🧨 Errores habituales y cómo depurarlos en sklearn Pipelines

Los errores en este módulo rara vez son “fallos exóticos” del algoritmo; casi siempre son **desalineaciones** entre datos, columnas, transformers y cómo guardas/cargas el pipeline.

### 1) `ValueError: number of features does not match` (mismatch entre train e inference)

**Síntomas típicos**

- En entrenamiento todo bien, pero al predecir obtienes:
  ```text
  ValueError: X has 15 features, but StandardScaler is expecting 12 features as input.
  ```
- O bien errores de índice similares en `OneHotEncoder`.

**Cómo identificarlo**

- Verifica que usas **el mismo pipeline serializado** en training e inference:
  - ¿Guardas y cargas `pipeline.pkl`/`model.joblib`, o solo el modelo suelto?
- Comprueba que las columnas de entrada en producción tienen el mismo orden y nombres que en entrenamiento.

**Cómo corregirlo**

- En el portafolio, **siempre** serializa el pipeline completo:
  ```python
  joblib.dump(pipeline, "artifacts/model.joblib")
  pipeline = joblib.load("artifacts/model.joblib")
  ```
- Asegúrate de que el orden y nombres de columnas que construyes en la API/Streamlit coincidan con las listas `num_cols` y `cat_cols` del pipeline.

---

### 2) Data leakage por features que usan el target (especialmente en CarVision)

**Síntomas típicos**

- Métricas en training/validation son **sospechosamente altas**, pero en producción caen.
- Features como `price_per_mile` o `price_category` dependen de la variable objetivo (`price`).

**Cómo identificarlo**

- Examina tu `FeatureEngineer` y lista de columnas que entran al modelo:
  - ¿Estás incluyendo columnas derivadas del target en el `ColumnTransformer`?
- Revisa tu config (`cfg["preprocessing"]["numeric_features"]`, etc.) y confirma que solo incluyes features válidos.

**Cómo corregirlo**

- Asegúrate de que features que dependen del target **no** se usen como input del modelo.
- En CarVision, por ejemplo, `price_per_mile` y `price_category` se calculan solo para análisis, pero se excluyen de `num_cols` para el pipeline.

---

### 3) Custom transformers que modifican el input in-place o no respetan la API sklearn

**Síntomas típicos**

- Errores del tipo:
  ```text
  TypeError: __init__() takes 1 positional argument but 2 were given
  ```
  o
  ```text
  AttributeError: 'MiTransformer' object has no attribute 'fit'
  ```
- Comportamientos raros donde un transformer “ensucia” los datos para otros steps.

**Cómo identificarlo**

- Revisa que tu transformer:
  - Herede de `BaseEstimator` y `TransformerMixin`.
  - Tenga `__init__`, `fit`, `transform` con las firmas estándar.
  - Use `X = X.copy()` dentro de `transform`.

**Cómo corregirlo**

- Usa la plantilla de este módulo (`MiTransformer`) como referencia.
- Evita lógica pesada en `__init__`; ahí solo se guardan parámetros.
- Añade tests unitarios simples (`fit_transform` sobre un `DataFrame` pequeño) para validar que mantiene columnas esperadas.

---

### 4) Pipelines diferentes en training y en la API

**Síntomas típicos**

- El pipeline usado en `training.py` no coincide con el que se monta en `fastapi_app.py` o `streamlit_app.py`.
- Bugs donde la API aplica transformaciones manuales **además** del pipeline.

**Cómo identificarlo**

- Busca en el proyecto si estás construyendo pipelines duplicados:
  - En CarVision, la única fuente de verdad debe ser `build_pipeline` en `src/carvision/training.py`.
  - La API y Streamlit solo deberían **cargar** el pipeline serializado, no recrearlo a mano.

**Cómo corregirlo**

- Centraliza la construcción del pipeline en una función (`build_pipeline` / `build_telecom_pipeline`).
- En la API/Streamlit, no replicar lógicas de preprocesado; limitarse a cargar y usar el pipeline.

---

### 5) Patrón general de debugging para pipelines

1. **Reproduce el error** con un input mínimo (1–2 filas de `DataFrame`).
2. **Inspecciona shapes y columnas** tras cada etapa:
   - Usa `pipeline.named_steps["pre"].transform(X_sample)` o similares.
3. **Verifica la serialización**: guarda, vuelve a cargar, y compara predicciones en un mismo batch.
4. **Conecta el problema** con el concepto del módulo:
   - Training-serving skew → pipeline parcial o mal serializado.
   - Mismatch de columnas → listas `num_cols`/`cat_cols` desincronizadas.
   - Transformers rotos → no respetan `fit`/`transform`.

Con este enfoque, los pipelines dejan de ser una “caja negra mágica” y se convierten en una línea de ensamblaje transparente y depurable.

---

## ✅ Checkpoint: ¿Completaste el Módulo?

Antes de continuar, verifica:

- [ ] Entiendes por qué los pipelines previenen training-serving skew
- [ ] Sabes usar ColumnTransformer para diferentes tipos de columnas
- [ ] Puedes crear un Custom Transformer con fit/transform
- [ ] Has construido un pipeline de 3 etapas (features → preprocessing → model)
- [ ] Puedes guardar y cargar un pipeline completo con joblib

---

## 🔗 ADR: Decisiones de Arquitectura

### ADR-007: Pipeline Unificado Obligatorio

**Contexto**: Transformaciones separadas causan inconsistencias en producción.

**Decisión**: Todo el flujo (features → preprocessing → model) debe estar en un solo Pipeline.

**Consecuencias**:
- ✅ Una sola serialización guarda todo
- ✅ Imposible olvidar una transformación
- ✅ Reproducibilidad garantizada
- ❌ Más complejo de debuggear (caja negra)
- ❌ Requiere entender sklearn profundamente

### ADR-008: Custom Transformers para Feature Engineering

**Contexto**: sklearn no tiene transformers para lógica de negocio específica.

**Decisión**: Crear FeatureEngineer como TransformerMixin.

**Consecuencias**:
- ✅ Reutilizable en train, API, y dashboard
- ✅ Testeable unitariamente
- ✅ Documentación clara de features derivadas
- ❌ Más código que escribir
- ❌ Requiere entender BaseEstimator/TransformerMixin

---

## 📦 Cómo se Usó en el Portafolio

Los pipelines sklearn son el corazón de los 3 proyectos del portafolio:

### Pipeline Unificado de BankChurn

```python
# BankChurn-Predictor/src/bankchurn/pipeline.py (estructura real)
def build_pipeline(config: BankChurnConfig) -> Pipeline:
    """Pipeline completo de 3 etapas."""
    return Pipeline([
        ('preprocessor', ColumnTransformer([
            ('num', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]), config.data.numerical_features),
            ('cat', Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
                ('encoder', OneHotEncoder(handle_unknown='ignore'))
            ]), config.data.categorical_features)
        ])),
        ('model', get_model(config))
    ])
```

### FeatureEngineer de CarVision

```python
# CarVision-Market-Intelligence/src/carvision/features.py
class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Custom transformer para features de autos."""
    
    def __init__(self, current_year: int = None):
        self.current_year = current_year
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        # vehicle_age, brand, mileage_category, etc.
        return X
```

### Archivos Clave por Proyecto

| Proyecto | Pipeline | Features | Artefacto |
|----------|----------|----------|-----------|
| BankChurn | `src/bankchurn/pipeline.py` | En preprocessor | `artifacts/pipeline.joblib` |
| CarVision | `src/carvision/pipeline.py` | `src/carvision/features.py` | `artifacts/pipeline.joblib` |
| TelecomAI | `src/telecomai/training.py` | En pipeline | `artifacts/model.joblib` |

### 🔧 Ejercicio: Explora los Pipelines Reales

```bash
# 1. Ve a BankChurn y carga el pipeline
cd BankChurn-Predictor
python -c "
import joblib
pipe = joblib.load('artifacts/pipeline.joblib')
print('Steps:', [name for name, _ in pipe.steps])
print('Preprocessor:', pipe.named_steps['preprocessor'])
"

# 2. Inspecciona el FeatureEngineer de CarVision
cat CarVision-Market-Intelligence/src/carvision/features.py
```

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **¿Por qué Pipelines?**: Evitan data leakage, garantizan reproducibilidad, simplifican deployment.

2. **Custom Transformers**: Demuestra que puedes crear transformadores con `fit()` y `transform()`.

3. **ColumnTransformer**: Explica cómo aplicar diferentes transformaciones a diferentes columnas.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Features nuevas | Añade transformadores al pipeline, no código suelto |
| Debugging | Usa `pipeline.named_steps` para inspeccionar etapas |
| Producción | Serializa el pipeline completo, no solo el modelo |
| Testing | Testea cada transformador individualmente |

### Patrones Avanzados

- **FeatureUnion**: Combinar features de diferentes fuentes
- **Pipeline dentro de Pipeline**: Para transformaciones complejas
- **make_pipeline**: Sintaxis simplificada sin nombres
- **clone**: Para cross-validation sin modificar original


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [sklearn Pipelines - Data School](https://www.youtube.com/watch?v=irHhDMbw3xo) | Video |
| 🟡 | [Custom Transformers - ArjanCodes](https://www.youtube.com/watch?v=e8IIYRMnxcE) | Video |

**Documentación oficial:**
- [sklearn Pipeline](https://scikit-learn.org/stable/modules/compose.html)
- [ColumnTransformer](https://scikit-learn.org/stable/modules/generated/sklearn.compose.ColumnTransformer.html)
- [Custom Transformers](https://scikit-learn.org/stable/developers/develop.html)

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **Pipeline**: Cadena de transformaciones + modelo
- **ColumnTransformer**: Procesamiento paralelo de columnas
- **Data Leakage**: Filtración de información del target

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 07:
- **7.1**: Pipeline básico con scaler + modelo
- **7.2**: ColumnTransformer para features mixtas

---

<div align="center">

[← Volver al Índice](00_INDICE.md) | [Siguiente: Ingeniería de Features →](08_INGENIERIA_FEATURES.md)

</div>
