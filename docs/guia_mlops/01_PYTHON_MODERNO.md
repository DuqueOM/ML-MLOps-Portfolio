# 01. Python Moderno para MLOps

## 🎯 Objetivo del Módulo

Transformar tu código de "funciona en un notebook" a "pasa code review en una empresa FAANG".

En este portafolio aplicarás estos patrones sobre `common_utils/` y el código de los tres proyectos
(BankChurn-Predictor, CarVision-Market-Intelligence, TelecomAI-Customer-Intelligence), para que
tu Python sea consistente en todo el stack.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ANTES (Data Scientist típico)          DESPUÉS (MLOps Engineer)            ║
║   ───────────────────────────            ─────────────────────────           ║
║   • Un archivo gigante                   • Paquete instalable                ║
║   • Sin tipos                            • Type hints en todo                ║
║   • Config hardcodeada                   • Pydantic validation               ║
║   • "Funciona en mi máquina"             • Funciona en cualquier máquina     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Contenido

1. [Type Hints: Tu Contrato con el Futuro](#11-type-hints-tu-contrato-con-el-futuro)
2. [Pydantic: Validación Automática](#12-pydantic-validación-automática)
3. [src/ Layout: Estructura Profesional](#13-src-layout-estructura-profesional)
4. [Principios SOLID para ML](#14-principios-solid-para-ml)
5. [Ejercicios Prácticos](#15-ejercicios-prácticos)

---

## 1.1 Type Hints: Tu Contrato con el Futuro

### La Analogía del Restaurante

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  🍽️ IMAGINA UN RESTAURANTE:                                               ║
║                                                                           ║
║  SIN MENÚ (código sin tipos):                                             ║
║  - "Tráeme algo de comer"                                                 ║
║  - El chef improvisa                                                      ║
║  - El cliente no sabe qué esperar                                         ║
║  - Resultado: sorpresas (bugs)                                            ║
║                                                                           ║
║  CON MENÚ (código con tipos):                                             ║
║  - "Quiero el plato #5: Pasta Carbonara"                                  ║
║  - El chef sabe exactamente qué preparar                                  ║
║  - El cliente sabe qué recibirá                                           ║
║  - Resultado: consistencia                                                ║
║                                                                           ║
║  TYPE HINTS = El menú de tu código                                        ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Código Real del Portafolio: Sin Tipos vs Con Tipos

```python
# ❌ ANTES: ¿Qué recibe? ¿Qué retorna? 
# (Esto es lo que encontrarías en un notebook)

def prepare_features(df, num_cols, cat_cols, target):
    X = df.drop(columns=[target])
    y = df[target]
    
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(), cat_cols)
    ])
    
    X_transformed = preprocessor.fit_transform(X)
    return X_transformed, y, preprocessor
```

```python
# ✅ DESPUÉS: Código real de BankChurn-Predictor/src/bankchurn/training.py

from __future__ import annotations  # Permite usar tipos modernos en Python 3.9+

from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def prepare_features(
    df: pd.DataFrame,
    num_cols: List[str],
    cat_cols: List[str],
    target: str
) -> Tuple[NDArray[np.float64], pd.Series, ColumnTransformer]:
    """Prepara features para entrenamiento.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con datos crudos.
    num_cols : List[str]
        Nombres de columnas numéricas.
    cat_cols : List[str]
        Nombres de columnas categóricas.
    target : str
        Nombre de la columna objetivo.
    
    Returns
    -------
    Tuple[NDArray, pd.Series, ColumnTransformer]
        Features transformadas, target, y preprocessor fitted.
    """
    X = df.drop(columns=[target])
    y = df[target]
    
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ])
    
    X_transformed = preprocessor.fit_transform(X)
    return X_transformed, y, preprocessor
```

### Los Tipos Esenciales para ML

```python
# ═══════════════════════════════════════════════════════════════════════════
# TIPOS BÁSICOS - Los usarás constantemente
# ═══════════════════════════════════════════════════════════════════════════

from typing import (
    List,       # Lista de elementos: List[str] = ["a", "b"]
    Dict,       # Diccionario: Dict[str, float] = {"acc": 0.95}
    Tuple,      # Tupla fija: Tuple[int, int] = (100, 10)
    Optional,   # Puede ser None: Optional[Path] = None
    Union,      # Múltiples tipos: Union[str, List[str]]
    Any,        # Cualquier tipo (evitar si posible)
    Literal,    # Valores específicos: Literal["train", "eval"]
)
from pathlib import Path

# Ejemplos del portafolio real:

# BankChurn: features son listas de strings
features: List[str] = ["CreditScore", "Age", "Balance"]

# CarVision: métricas son diccionario string->float
metrics: Dict[str, float] = {"rmse": 4794.27, "r2": 0.77}

# TelecomAI: puede recibir path o None
model_path: Optional[Path] = None

# ═══════════════════════════════════════════════════════════════════════════
# TIPOS PARA ML - Específicos de Machine Learning
# ═══════════════════════════════════════════════════════════════════════════

import pandas as pd
import numpy as np
from numpy.typing import NDArray
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline

# DataFrame de pandas
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

# Array NumPy tipado
def predict_proba(X: NDArray[np.float64]) -> NDArray[np.float64]:
    return model.predict_proba(X)[:, 1]

# Modelo sklearn
def train_model(X: NDArray, y: NDArray) -> BaseEstimator:
    model = RandomForestClassifier()
    model.fit(X, y)
    return model

# ═══════════════════════════════════════════════════════════════════════════
# TIPOS AVANZADOS - Para código más robusto
# ═══════════════════════════════════════════════════════════════════════════

from typing import TypedDict, Literal

# TypedDict: diccionarios con estructura conocida
class MetricsDict(TypedDict):
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float

# Literal: solo valores específicos permitidos
ModelType = Literal["random_forest", "logistic", "gradient_boosting"]

def build_model(model_type: ModelType, seed: int) -> BaseEstimator:
    """
    mypy SABE que model_type solo puede ser estos 3 valores.
    Si escribes build_model("xgboost", 42), mypy dará error.
    """
    if model_type == "random_forest":
        return RandomForestClassifier(random_state=seed)
    elif model_type == "logistic":
        return LogisticRegression(random_state=seed)
    else:  # gradient_boosting
        return GradientBoostingClassifier(random_state=seed)
```

### Configurar mypy

Añade esto a tu `pyproject.toml`:

```toml
# pyproject.toml - Configuración de mypy
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true      # ← Fuerza tipos en todas las funciones
ignore_missing_imports = true     # ← Para librerías sin stubs

# Ignorar librerías de ML que no tienen stubs completos
[[tool.mypy.overrides]]
module = [
    "sklearn.*",
    "pandas.*", 
    "numpy.*",
    "mlflow.*",
    "joblib.*",
]
ignore_missing_imports = true
```

Ejecutar:
```bash
mypy src/  # Verifica tipos en todo el código
```

---

## 1.2 Pydantic: Validación Automática

### La Analogía del Guardia de Seguridad

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  🛡️ IMAGINA UN EDIFICIO DE OFICINAS:                                      ║
║                                                                           ║
║  SIN GUARDIA (código sin Pydantic):                                       ║
║  - Cualquiera entra con cualquier cosa                                    ║
║  - Descubres problemas CUANDO YA PASARON                                  ║
║  - "¿Por qué hay un test_size de 1.5?" → Error en producción              ║
║                                                                           ║
║  CON GUARDIA (código con Pydantic):                                       ║
║  - Verifica credenciales EN LA ENTRADA                                    ║
║  - Problemas detectados ANTES de causar daño                              ║
║  - "test_size debe ser entre 0 y 1" → Error inmediato y claro             ║
║                                                                           ║
║  PYDANTIC = El guardia de tu configuración                                ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Código Real: BankChurn Config (Nivel Staff)

Este es el archivo `src/bankchurn/config.py` del portafolio:

```python
"""Configuration management for BankChurn predictor.

Este módulo demuestra Pydantic a nivel profesional:
- Validación de rangos con Field
- Configuraciones anidadas
- Valores por defecto sensatos
- Carga desde YAML
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List

import yaml
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIONES ANIDADAS - Cada componente tiene su propia config
# ═══════════════════════════════════════════════════════════════════════════

class LogisticRegressionConfig(BaseModel):
    """Hiperparámetros de Logistic Regression."""
    C: float = 0.1
    class_weight: str = "balanced"
    solver: str = "liblinear"
    max_iter: int = 1000


class RandomForestConfig(BaseModel):
    """Hiperparámetros de Random Forest."""
    n_estimators: int = 100
    max_depth: int = 10
    min_samples_split: int = 10
    min_samples_leaf: int = 5
    class_weight: str = "balanced_subsample"
    n_jobs: int = -1


class EnsembleConfig(BaseModel):
    """Configuración del ensemble."""
    voting: str = Field("soft", pattern="^(hard|soft)$")  # ← Solo permite "hard" o "soft"
    weights: List[float] = [0.4, 0.6]


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN PRINCIPAL - Agrupa todo con validación
# ═══════════════════════════════════════════════════════════════════════════

class ModelConfig(BaseModel):
    """Configuración de entrenamiento del modelo."""
    type: str = "ensemble"
    test_size: float = Field(0.2, ge=0.0, le=1.0)   # ← VALIDACIÓN: entre 0 y 1
    random_state: int = 42
    cv_folds: int = Field(5, ge=2)                   # ← VALIDACIÓN: mínimo 2
    resampling_strategy: str = "none"
    
    # Configuraciones de modelos específicos (anidadas)
    ensemble: EnsembleConfig = EnsembleConfig()
    logistic_regression: LogisticRegressionConfig = LogisticRegressionConfig()
    random_forest: RandomForestConfig = RandomForestConfig()


class DataConfig(BaseModel):
    """Configuración de datos."""
    target_column: str = "Exited"
    categorical_features: List[str] = []
    numerical_features: List[str] = []
    drop_columns: List[str] = []


class MLflowConfig(BaseModel):
    """Configuración de MLflow tracking."""
    tracking_uri: str = "file:./mlruns"
    experiment_name: str = "bankchurn"
    enabled: bool = True


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN RAÍZ - El punto de entrada
# ═══════════════════════════════════════════════════════════════════════════

class BankChurnConfig(BaseModel):
    """Configuración completa de BankChurn.
    
    Uso:
        config = BankChurnConfig.from_yaml("configs/config.yaml")
        print(config.model.test_size)  # 0.2
    """
    model: ModelConfig
    data: DataConfig
    mlflow: MLflowConfig

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> BankChurnConfig:
        """Carga configuración desde archivo YAML.
        
        Parameters
        ----------
        config_path : str or Path
            Ruta al archivo YAML.
            
        Returns
        -------
        BankChurnConfig
            Configuración validada.
            
        Raises
        ------
        FileNotFoundError
            Si el archivo no existe.
        ValidationError
            Si la configuración es inválida.
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f) or {}
        
        # Valores por defecto para secciones faltantes
        if "model" not in config_dict:
            config_dict["model"] = ModelConfig().dict()
        if "data" not in config_dict:
            config_dict["data"] = DataConfig().dict()
        if "mlflow" not in config_dict:
            config_dict["mlflow"] = MLflowConfig().dict()
        
        return cls(**config_dict)  # ← Pydantic valida automáticamente
```

### El YAML Correspondiente

```yaml
# configs/config.yaml
model:
  type: ensemble
  test_size: 0.2         # Si pones 1.5, Pydantic dará error
  random_state: 42
  cv_folds: 5            # Si pones 1, Pydantic dará error
  resampling_strategy: none
  
  ensemble:
    voting: soft         # Si pones "maybe", Pydantic dará error
    weights: [0.4, 0.6]
    
  random_forest:
    n_estimators: 200
    max_depth: 10

data:
  target_column: Exited
  categorical_features:
    - Geography
    - Gender
  numerical_features:
    - CreditScore
    - Age
    - Balance
  drop_columns:
    - RowNumber
    - CustomerId
    - Surname

mlflow:
  tracking_uri: "file:./mlruns"
  experiment_name: bankchurn
  enabled: true
```

### Ejemplo de Error de Validación

```python
# ❌ Esto FALLA inmediatamente con un error claro

config_dict = {
    "model": {
        "test_size": 1.5,  # ← Error: debe ser <= 1.0
        "cv_folds": 1,     # ← Error: debe ser >= 2
    },
    "data": {},
    "mlflow": {}
}

try:
    config = BankChurnConfig(**config_dict)
except ValidationError as e:
    print(e)
    # Output:
    # 2 validation errors for BankChurnConfig
    # model -> test_size
    #   ensure this value is less than or equal to 1.0 (type=value_error.number.not_le)
    # model -> cv_folds
    #   ensure this value is greater than or equal to 2 (type=value_error.number.not_ge)
```

---

## 1.3 src/ Layout: Estructura Profesional

### La Analogía de la Casa

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  🏠 IMAGINA ORGANIZAR UNA CASA:                                           ║
║                                                                           ║
║  CASA DESORDENADA (código en raíz):                                       ║
║  - Todo en el living: ropa, comida, herramientas                          ║
║  - Imposible encontrar algo                                               ║
║  - Invitas a alguien: "perdón por el desorden"                            ║
║                                                                           ║
║  CASA ORGANIZADA (src/ layout):                                           ║
║  - Cocina para cocinar, baño para baño, closet para ropa                  ║
║  - Cada cosa en su lugar                                                  ║
║  - Invitas a alguien: "bienvenido, siéntate"                              ║
║                                                                           ║
║  src/ layout = Organización profesional de código                         ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Estructura del Portafolio

```
BankChurn-Predictor/
├── src/                          # ← TODO el código fuente aquí
│   ├── __init__.py               # Hace src/ un paquete
│   └── bankchurn/                # ← El paquete principal
│       ├── __init__.py           # Exporta la API pública
│       ├── config.py             # Configuración Pydantic
│       ├── training.py           # Pipeline de entrenamiento
│       ├── evaluation.py         # Métricas y evaluación
│       ├── prediction.py         # Inferencia
│       ├── models.py             # Custom classifiers
│       └── cli.py                # Interfaz de línea de comandos
│
├── app/                          # ← Aplicaciones (no es un paquete)
│   └── fastapi_app.py            # API REST
│
├── tests/                        # ← Tests (espejo de src/)
│   ├── __init__.py
│   ├── conftest.py               # Fixtures compartidas
│   ├── test_config.py            # Tests para config.py
│   ├── test_training.py          # Tests para training.py
│   └── ...
│
├── configs/                      # ← Configuración externa
│   └── config.yaml
│
├── data/                         # ← Datos (gitignored)
│   └── raw/
│       └── Churn_Modelling.csv
│
├── artifacts/                    # ← Artefactos generados (gitignored)
│   ├── model.joblib
│   └── training_results.json
│
├── pyproject.toml                # ← Metadata del proyecto
├── Makefile                      # ← Comandos comunes
├── Dockerfile                    # ← Containerización
└── README.md                     # ← Documentación
```

### ¿Por qué src/ y no código en la raíz?

```python
# ❌ PROBLEMA: Sin src/, Python puede importar código no instalado
# Esto causa el famoso "funciona en mi máquina pero no en CI"

# Estructura plana (problemática):
# myproject/
# ├── mymodule.py
# └── tests/
#     └── test_mymodule.py

# En test_mymodule.py:
import mymodule  # ← ¿De dónde viene? ¿Del directorio actual? ¿De pip?

# ✅ SOLUCIÓN: Con src/, el código DEBE estar instalado para importar
# myproject/
# ├── src/
# │   └── mymodule/
# │       └── __init__.py
# └── tests/
#     └── test_mymodule.py

# En test_mymodule.py:
from mymodule import something  # ← Solo funciona si `pip install -e .`
```

### pyproject.toml: El Corazón del Proyecto

```toml
# pyproject.toml - Configuración completa del proyecto
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "bankchurn"
version = "1.0.0"
description = "Bank Customer Churn Prediction System"
authors = [
    {name = "Daniel Duque", email = "duque@example.com"}
]
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}

dependencies = [
    "pandas>=2.0.0",
    "scikit-learn>=1.3.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "mlflow>=2.9.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "mypy>=1.7.0",
    "ruff>=0.1.0",
]

[project.scripts]
bankchurn = "bankchurn.cli:main"  # ← Comando CLI

# ═══════════════════════════════════════════════════════════════════════════
# HERRAMIENTAS
# ═══════════════════════════════════════════════════════════════════════════

[tool.setuptools.packages.find]
where = ["src"]  # ← Busca paquetes en src/

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=src/bankchurn --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]

[tool.coverage.report]
fail_under = 79  # ← Coverage mínimo para pasar CI

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
disallow_untyped_defs = true
ignore_missing_imports = true
```

### Instalación en Modo Editable

```bash
# Instalar el paquete en modo editable (para desarrollo)
pip install -e .

# Ahora puedes importar desde cualquier lugar
python -c "from bankchurn.config import BankChurnConfig; print('✅ Funciona!')"

# Y los tests también funcionan
pytest tests/
```

---

## 1.4 Principios SOLID para ML

### Single Responsibility: Un Módulo, Una Tarea

```python
# ❌ ANTES: Un archivo hace TODO
# training.py (500 líneas)
def train_model(data_path, config_path, output_path):
    # Carga datos (líneas 1-50)
    # Limpia datos (líneas 51-100)
    # Feature engineering (líneas 101-200)
    # Entrena modelo (líneas 201-300)
    # Evalúa modelo (líneas 301-400)
    # Guarda artefactos (líneas 401-450)
    # Loguea a MLflow (líneas 451-500)
    pass

# ✅ DESPUÉS: Cada archivo tiene UNA responsabilidad
# src/bankchurn/
# ├── data.py         → Solo carga y valida datos
# ├── features.py     → Solo feature engineering
# ├── training.py     → Solo entrenamiento
# ├── evaluation.py   → Solo métricas
# └── prediction.py   → Solo inferencia
```

### Código Real del Portafolio

```python
# src/bankchurn/training.py - SOLO se encarga de entrenar
class ChurnTrainer:
    """Training pipeline - Single Responsibility."""
    
    def __init__(self, config: BankChurnConfig):
        self.config = config
    
    def load_data(self, path: Path) -> pd.DataFrame:
        """Delega a módulo de datos."""
        pass
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepara X e y."""
        pass
    
    def build_pipeline(self) -> Pipeline:
        """Construye el pipeline sklearn."""
        pass
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Entrena el modelo."""
        pass
    
    def cross_validate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Valida con CV."""
        pass

# src/bankchurn/evaluation.py - SOLO se encarga de evaluar
def evaluate_model(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> Dict[str, float]:
    """Calcula métricas - Single Responsibility."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }
```

---

## 1.5 Ejercicios Prácticos

### Ejercicio 1: Añadir Type Hints

```python
# ❌ Código sin tipos (típico de notebook)
# Tu tarea: Añade type hints completos

def process_training_data(df, config):
    target = config["target"]
    features = config["features"]
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.get("test_size", 0.2)
    )
    
    return X_train, X_test, y_train, y_test


def calculate_metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred)
    }
```

<details>
<summary>📝 Ver Solución</summary>

```python
from typing import Dict, List, Tuple, Any
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score


def process_training_data(
    df: pd.DataFrame,
    config: Dict[str, Any]
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Procesa datos para entrenamiento.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con datos crudos.
    config : Dict[str, Any]
        Configuración con keys: "target", "features", "test_size" (opcional).
    
    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]
        X_train, X_test, y_train, y_test
    """
    target: str = config["target"]
    features: List[str] = config["features"]
    
    X: pd.DataFrame = df[features]
    y: pd.Series = df[target]
    
    test_size: float = config.get("test_size", 0.2)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    return X_train, X_test, y_train, y_test


def calculate_metrics(
    y_true: pd.Series,
    y_pred: pd.Series
) -> Dict[str, float]:
    """Calcula métricas de clasificación.
    
    Parameters
    ----------
    y_true : pd.Series
        Labels verdaderos.
    y_pred : pd.Series
        Predicciones del modelo.
    
    Returns
    -------
    Dict[str, float]
        Diccionario con accuracy y f1.
    """
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "f1": float(f1_score(y_true, y_pred))
    }
```

</details>

---

### Ejercicio 2: Crear Config con Pydantic

```python
# Tu tarea: Crea una configuración Pydantic para TelecomAI
# Requisitos:
# - project_name: str
# - random_seed: int (entre 0 y 1000)
# - test_size: float (entre 0.1 y 0.5)
# - model_type: solo puede ser "logreg", "random_forest", o "gradient_boosting"
# - features: lista de strings
# - target: str

# Escribe tu código aquí:
from pydantic import BaseModel, Field
from typing import List, Literal

class TelecomConfig(BaseModel):
    # ... tu código
    pass
```

<details>
<summary>📝 Ver Solución</summary>

```python
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from pathlib import Path
import yaml


class TelecomConfig(BaseModel):
    """Configuración para TelecomAI Customer Intelligence."""
    
    project_name: str = Field(..., min_length=1)
    random_seed: int = Field(42, ge=0, le=1000)
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    model_type: Literal["logreg", "random_forest", "gradient_boosting"] = "logreg"
    features: List[str] = Field(..., min_items=1)
    target: str
    
    # Opcionales
    threshold: float = Field(0.5, ge=0.0, le=1.0)
    mlflow_enabled: bool = True
    
    @classmethod
    def from_yaml(cls, path: str | Path) -> "TelecomConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    class Config:
        extra = "forbid"  # No permite campos extra en el YAML


# Uso:
config = TelecomConfig(
    project_name="TelecomAI",
    features=["calls", "minutes", "messages", "mb_used"],
    target="is_ultra"
)

# Esto FALLA:
# config = TelecomConfig(
#     project_name="",  # Error: min_length=1
#     test_size=0.8,    # Error: le=0.5
#     model_type="xgboost",  # Error: not in Literal
#     features=[],      # Error: min_items=1
# )
```

</details>

---

### Ejercicio 3: Convertir a src/ Layout

```
Tu tarea: Reorganiza esta estructura plana a src/ layout

ANTES:
myproject/
├── train.py
├── predict.py
├── utils.py
├── config.yaml
├── data.csv
└── test_train.py

DESPUÉS:
myproject/
├── src/
│   └── ???
├── tests/
│   └── ???
├── configs/
│   └── ???
├── data/
│   └── ???
└── pyproject.toml
```

<details>
<summary>📝 Ver Solución</summary>

```
myproject/
├── src/
│   ├── __init__.py
│   └── myproject/
│       ├── __init__.py
│       ├── training.py      # Antes: train.py
│       ├── prediction.py    # Antes: predict.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures compartidas
│   └── test_training.py     # Antes: test_train.py
├── configs/
│   └── config.yaml
├── data/
│   └── raw/
│       └── data.csv
├── artifacts/               # Para modelos generados
│   └── .gitkeep
├── pyproject.toml
├── Makefile
└── README.md
```

 </details>

---

## 🧨 Errores habituales y cómo depurarlos

En este módulo suelen aparecer siempre los mismos problemas. La idea no es solo evitarlos, sino **saber reconocerlos rápido** en tus propios proyectos.

### 1) Type hints + mypy: errores ruidosos en pandas/sklearn

**Síntomas típicos**

- `Function is missing a type annotation for parameter 'df'`
- `Incompatible return value type (got "DataFrame", expected "Series")`
- Cientos de warnings en librerías externas (`pandas.*`, `sklearn.*`).

**Proceso para identificarlos**

- Ejecuta siempre:
  ```bash
  mypy src/  # o mypy src/bankchurn src/carvision src/telecomai
  ```
- Localiza primero los errores **en tu código** (archivos dentro de `src/`), ignora de momento los de librerías.
- Si ves muchos errores en `site-packages` o módulos externos, revisa tu sección `[tool.mypy]` del `pyproject.toml` (ver ejemplo en este mismo módulo).

**Cómo solucionarlos (patrón general)**

- Añade tipos a **todas las firmas públicas** (funciones/clases usadas fuera de su archivo).
- Usa tipos específicos para ML:
  - `pd.DataFrame`, `pd.Series`
  - `NDArray[np.float64]`
  - `BaseEstimator`, `Pipeline`
- Aísla tipos muy complejos usando `TypedDict` o `Alias`:
  ```python
  class MetricsDict(TypedDict):
      accuracy: float
      f1: float
      roc_auc: float
  ```
- Para **reducir ruido de mypy** con librerías ML:
  - Configura `ignore_missing_imports = true` y los overrides mostrados en este módulo.
  - Re-lanza `mypy` y verifica que solo quedan errores en tu código.

> 💡 **Regla práctica**: si mypy empieza a gritar en medio de un refactor, reduce el problema a una función pequeña, tipa bien esa función, y después propaga los tipos al resto.

---

### 2) Pydantic: `ValidationError` por config mal definida

**Síntomas típicos**

- Al cargar la configuración:
  ```text
  pydantic.error_wrappers.ValidationError: 2 validation errors for ModelConfig
  model -> test_size
    ensure this value is less than or equal to 1.0 (type=value_error.number.not_le)
  model -> cv_folds
    ensure this value is greater than or equal to 2 (type=value_error.number.not_ge)
  ```
- Tu servicio/API no arranca porque falla la lectura de `config.yaml`.

**Proceso para identificarlos**

- Localiza **qué modelo Pydantic** está fallando (`ModelConfig`, `BankChurnConfig`, `TelecomConfig`, etc.).
- Revisa el `traceback`: casi siempre indica **la ruta completa del campo** (`model -> test_size`, `data -> categorical_features`, etc.).
- Abre el YAML correspondiente (`configs/config.yaml`) y compara **valor real** vs **restricción en `Field(...)`**.

**Cómo solucionarlos (patrón general)**

- Ajusta el YAML para respetar los rangos:
  - `test_size` entre `0.0` y `1.0`.
  - `cv_folds` ≥ 2.
  - Literales válidos (`voting: "hard" | "soft"`, `model_type: "logreg" | "random_forest" | ...`).
- Si el error te parece injustificado, revisa la declaración del modelo:
  ```python
  test_size: float = Field(0.2, ge=0.0, le=1.0)
  ```
  Quizá necesitas permitir un rango distinto en tu contexto.
- En desarrollo, **falla rápido**: no atrapes el `ValidationError` salvo para mostrar un mensaje más amigable; deja que la app se caiga antes que usar una config corrupta.

> 🔧 **Ejercicio mental**: rompe a propósito tu `configs/config.yaml` (pon `test_size: 1.5`) y observa el error. Luego arréglalo. Hazlo una vez y nunca más te asustará un `ValidationError` en producción.

---

### 3) src/ layout e imports: `ModuleNotFoundError` en CI pero no en tu máquina

**Síntomas típicos**

- En local “todo funciona”, pero en GitHub Actions o en otra máquina obtienes:
  ```text
  ModuleNotFoundError: No module named 'bankchurn'
  ```
- Los tests solo pasan si ejecutas `pytest` desde la raíz exacta del proyecto.

**Proceso para identificarlos**

- Revisa la **estructura** de tu proyecto (debería parecerse al diagrama de este módulo):
  - Código dentro de `src/<paquete>/`.
  - Tests bajo `tests/` usando imports del paquete, no rutas relativas raras.
- Verifica tu `pyproject.toml`:
  - `[project.name]` coincide con el paquete (`bankchurn`, `carvision`, `telecomai`).
  - `[tool.setuptools.packages.find] where = ["src"]`.
- Comprueba si instalaste en modo editable:
  ```bash
  pip install -e .
  python -c "import bankchurn; print(bankchurn.__file__)"
  ```

**Cómo solucionarlos (patrón general)**

- Mueve el código de raíz a `src/` siguiendo el ejemplo de este módulo.
- Cambia imports tipo:
  ```python
  # ❌ from .training import train_model  (desde scripts sueltos)
  # ✅ from bankchurn.training import train_model
  ```
- Asegúrate de que los comandos de CI usan instalación editable:
  ```yaml
  - name: Install
    run: pip install -e ".[dev]"
  ```

> ⚠️ **Bandera roja**: si tus tests solo funcionan cuando haces `cd src` o ajustas manualmente `PYTHONPATH`, tu layout todavía no está bien resuelto.

---

### 4) Patrón general de debugging para este módulo

1. **Reproduce el error** con un comando simple y determinista:
   - `mypy src/`
   - `python -m src.proyecto.training`
   - `pytest -k nombre_test`.
2. **Lee literalmente** el mensaje de error (campo, valor, restricción).
3. **Conecta el error con el concepto del módulo**:
   - Type hints → firma de función o tipo de retorno.
   - Pydantic → `Field(...)` y YAML.
   - src/ layout → estructura de carpetas + `pyproject.toml` + instalación editable.
4. **Aplica el patrón de solución** que viste arriba.

Si automatizas este ciclo en tus tres proyectos del portafolio, tu tiempo de debugging se reduce drásticamente y es justo lo que se espera de un perfil Senior/Staff.

---

## ✅ Checkpoint: ¿Completaste el Módulo?

Antes de continuar, verifica:

- [ ] Tu código tiene type hints en todas las funciones
- [ ] Puedes ejecutar `mypy src/` sin errores críticos
- [ ] Tienes al menos una clase Pydantic para configuración
- [ ] Tu proyecto tiene estructura src/ layout
- [ ] Puedes instalar tu paquete con `pip install -e .`

---

## 🔗 ADR: ¿Por Qué Estas Decisiones?

### ADR-001: Type Hints Obligatorios

**Contexto**: El código de ML suele ser difícil de mantener porque las funciones aceptan "cualquier cosa".

**Decisión**: Requerimos type hints en todas las funciones públicas.

**Consecuencias**:
- ✅ El IDE autocompleta correctamente
- ✅ Errores detectados antes de ejecutar
- ✅ Documentación implícita
- ❌ Más código que escribir inicialmente
- ❌ Curva de aprendizaje para tipos complejos

### ADR-002: Pydantic para Configuración

**Contexto**: Configuraciones en diccionarios son propensas a errores.

**Decisión**: Toda configuración pasa por Pydantic.

**Consecuencias**:
- ✅ Validación automática
- ✅ Errores claros
- ✅ Documentación de la config
- ❌ Dependencia adicional
- ❌ Más verboso que un dict simple

### ADR-003: src/ Layout

**Contexto**: Código en raíz causa problemas de importación.

**Decisión**: Todo código en `src/<paquete>/`.

**Consecuencias**:
- ✅ Importaciones consistentes
- ✅ Funciona igual en desarrollo y CI
- ✅ Estándar de la industria
- ❌ Requiere `pip install -e .`
- ❌ Path más largo para imports

---

## 📦 Cómo se Usó en el Portafolio

Este módulo se aplica **directamente** en los 3 proyectos del portafolio. Aquí están los archivos reales que implementan cada concepto:

### Type Hints en el Portafolio

```python
# BankChurn-Predictor/src/bankchurn/config.py (líneas 89-109)
@classmethod
def from_yaml(cls, config_path: str | Path) -> BankChurnConfig:
    """Load configuration from YAML file.
    
    Parameters
    ----------
    config_path : str or Path
        Path to YAML configuration file.
    
    Returns
    -------
    config : BankChurnConfig
        Validated configuration object.
    """
```

### Pydantic en el Portafolio

Cada proyecto tiene su configuración Pydantic:

| Proyecto | Archivo | Clases principales |
|----------|---------|-------------------|
| BankChurn | `src/bankchurn/config.py` | `BankChurnConfig`, `ModelConfig`, `DataConfig` |
| CarVision | `src/carvision/config.py` | `CarVisionConfig`, `FiltersConfig` |
| TelecomAI | `src/telecomai/config.py` | `TelecomConfig` |

```python
# Ejemplo real: BankChurn-Predictor/src/bankchurn/config.py
class ModelConfig(BaseModel):
    """Model training configuration."""
    type: str = "ensemble"
    test_size: float = Field(0.2, ge=0.0, le=1.0)  # ← Validación automática
    random_state: int = 42
    cv_folds: int = Field(5, ge=2)  # ← Mínimo 2 folds
```

### src/ Layout en el Portafolio

Los 3 proyectos siguen exactamente la estructura descrita:

```
BankChurn-Predictor/
├── src/bankchurn/       ← Paquete instalable
│   ├── __init__.py
│   ├── config.py        ← Pydantic configs
│   ├── pipeline.py      ← sklearn Pipeline
│   └── trainer.py       ← Clase de entrenamiento
├── pyproject.toml       ← Metadata y dependencias
└── setup.py             ← Fallback para pip install -e .
```

### 🔧 Ejercicio: Verifica en el Repo Real

```bash
# 1. Ve al proyecto BankChurn
cd BankChurn-Predictor

# 2. Instala en modo editable
pip install -e ".[dev]"

# 3. Verifica tipos con mypy
mypy src/bankchurn/config.py

# 4. Prueba que Pydantic valida correctamente
python -c "from bankchurn.config import BankChurnConfig; print(BankChurnConfig.from_yaml('configs/config.yaml'))"
```

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **Domina Type Hints**: Los entrevistadores valoran código tipado. Practica explicar por qué `def process(data: pd.DataFrame) -> Dict[str, float]` es mejor que `def process(data)`.

2. **Conoce Pydantic vs Dataclasses**: Pregunta común: "¿Cuándo usarías uno u otro?" Respuesta: Pydantic para validación de datos externos (APIs, configs), dataclasses para estructuras internas simples.

3. **Demuestra comprensión de `__init__.py`**: Explica cómo controla la API pública de un paquete y por qué `from package import *` es peligroso.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Código legacy sin tipos | Añade tipos gradualmente, empezando por funciones públicas |
| Validación de configs | Usa Pydantic con `model_validator` para validaciones cruzadas |
| Logs en producción | Usa `structlog` o `loguru` en lugar de `print()` |
| Errores en producción | Implementa excepciones personalizadas con contexto útil |

### Anti-patrones a Evitar

- ❌ `from typing import *` — importa solo lo que necesitas
- ❌ `except Exception:` sin logging — siempre registra el error
- ❌ Funciones de más de 50 líneas — refactoriza en funciones más pequeñas
- ❌ Nombres como `data`, `info`, `result` — usa nombres descriptivos


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [Type Hints - ArjanCodes](https://www.youtube.com/watch?v=dgBCEB2jVU0) | Video |
| 🔴 | [Pydantic V2 Tutorial](https://www.youtube.com/watch?v=502XOB0u8OY) | Video |
| 🟡 | [Python Type Checking - Real Python](https://realpython.com/python-type-checking/) | Tutorial |

**Documentación oficial:**
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Packaging Guide](https://packaging.python.org/)

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **Type Hints**: Anotaciones de tipos en Python
- **Pydantic**: Validación de datos con type hints
- **src/ Layout**: Estructura de proyecto profesional

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 01:
- **1.1**: Añadir type hints a funciones
- **1.2**: Crear config con Pydantic
- **1.3**: Estructurar proyecto con src/ layout

---

<div align="center">

[← Volver al Índice](00_INDICE.md) | [Siguiente: Diseño de Sistemas ML →](02_DISENO_SISTEMAS.md)

</div>
