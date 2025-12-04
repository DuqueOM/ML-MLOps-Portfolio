# 01 — Python Moderno para ML/MLOps

> **Tiempo estimado**: 2 días (16 horas)
> 
> **Prerrequisitos**: Python básico (funciones, clases, módulos)

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Usar **type hints** para código más robusto y documentado
2. ✅ Implementar **dataclasses** para estructuras de datos simples
3. ✅ Usar **Pydantic** para validación de configuraciones
4. ✅ Aplicar principios **SOLID** básicos
5. ✅ Estructurar un **paquete Python** profesional

---

## 📖 Contenido Teórico

### 1. Type Hints (Tipado Estático)

Python es dinámicamente tipado, pero desde Python 3.5+ podemos agregar **anotaciones de tipo** que ayudan a:
- Documentar el código
- Detectar errores antes de ejecutar
- Mejor autocompletado en IDEs

#### Sintaxis Básica

```python
# Sin type hints (difícil de entender)
def process_data(data, threshold):
    return [x for x in data if x > threshold]

# Con type hints (claro y documentado)
def process_data(data: list[float], threshold: float) -> list[float]:
    """Filtra valores mayores al umbral."""
    return [x for x in data if x > threshold]
```

#### Tipos Comunes

```python
from typing import Optional, Union, Any
from collections.abc import Callable, Iterable

# Tipos básicos
name: str = "modelo"
count: int = 42
score: float = 0.95
is_valid: bool = True

# Colecciones (Python 3.9+)
features: list[str] = ["age", "income"]
params: dict[str, float] = {"lr": 0.01, "epochs": 100}
unique_ids: set[int] = {1, 2, 3}
point: tuple[float, float] = (1.0, 2.0)

# Opcionales y Uniones
threshold: Optional[float] = None  # Puede ser float o None
value: Union[int, float] = 1.5     # Puede ser int o float
value: int | float = 1.5           # Python 3.10+ (sintaxis nueva)

# Funciones como parámetros
def apply_func(data: list[float], func: Callable[[float], float]) -> list[float]:
    return [func(x) for x in data]
```

#### Type Hints en Clases

```python
class ChurnPredictor:
    """Predictor de abandono de clientes."""
    
    def __init__(self, model_path: str, threshold: float = 0.5) -> None:
        self.model_path = model_path
        self.threshold = threshold
        self._model: Optional[Any] = None  # Atributo privado
    
    def predict(self, features: dict[str, float]) -> bool:
        """Predice si un cliente abandonará."""
        probability = self._get_probability(features)
        return probability > self.threshold
    
    def _get_probability(self, features: dict[str, float]) -> float:
        """Método privado para obtener probabilidad."""
        # Implementación...
        return 0.7
```

💡 **Tip**: Usa `mypy` para verificar tipos estáticamente:
```bash
pip install mypy
mypy src/
```

---

### 2. Dataclasses

Las **dataclasses** (Python 3.7+) simplifican la creación de clases que principalmente almacenan datos:

```python
from dataclasses import dataclass, field
from typing import Optional

# Sin dataclass (verboso)
class ModelConfigOld:
    def __init__(self, name: str, version: str, threshold: float = 0.5):
        self.name = name
        self.version = version
        self.threshold = threshold
    
    def __repr__(self):
        return f"ModelConfig(name={self.name}, version={self.version})"
    
    def __eq__(self, other):
        return (self.name == other.name and 
                self.version == other.version and
                self.threshold == other.threshold)

# Con dataclass (limpio y automático)
@dataclass
class ModelConfig:
    name: str
    version: str
    threshold: float = 0.5
    tags: list[str] = field(default_factory=list)
    
    def full_name(self) -> str:
        """Método adicional."""
        return f"{self.name}-v{self.version}"

# Uso
config = ModelConfig(name="churn", version="1.0")
print(config)  # ModelConfig(name='churn', version='1.0', threshold=0.5, tags=[])
print(config.full_name())  # churn-v1.0
```

#### Dataclasses Inmutables

```python
@dataclass(frozen=True)
class Prediction:
    """Predicción inmutable."""
    customer_id: str
    probability: float
    label: bool

pred = Prediction("C001", 0.85, True)
# pred.probability = 0.9  # Error! frozen=True previene modificación
```

---

### 3. Pydantic para Configuraciones

**Pydantic** va más allá de dataclasses: valida tipos en runtime y parsea datos automáticamente.

#### Instalación

```bash
pip install pydantic pydantic-settings
```

#### Modelo Básico

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class TrainingConfig(BaseModel):
    """Configuración de entrenamiento con validación."""
    
    # Campos con valores por defecto
    model_name: str = Field(..., description="Nombre del modelo")
    learning_rate: float = Field(0.01, gt=0, le=1)
    n_estimators: int = Field(100, ge=10, le=1000)
    random_state: Optional[int] = 42
    
    # Validador personalizado
    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("model_name no puede estar vacío")
        return v.lower().strip()

# Uso - Pydantic valida automáticamente
config = TrainingConfig(
    model_name="  RandomForest  ",
    learning_rate=0.1,
    n_estimators=200
)
print(config.model_name)  # "randomforest" (normalizado)
print(config.model_dump())  # Convertir a dict
```

#### BaseSettings para Variables de Entorno

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Configuración desde variables de entorno."""
    
    # Lee de variable de entorno MLFLOW_TRACKING_URI
    mlflow_tracking_uri: str = Field("file:./mlruns")
    
    # Lee de variable MODEL_PATH
    model_path: str = Field("models/model.pkl")
    
    # Configuración de lectura
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

# Uso
settings = Settings()  # Lee .env automáticamente
print(settings.mlflow_tracking_uri)
```

---

### 4. Principios SOLID Básicos

SOLID son 5 principios de diseño orientado a objetos:

#### S — Single Responsibility (Responsabilidad Única)

```python
# ❌ Mal: Una clase hace demasiado
class ModelManager:
    def load_data(self): ...
    def train(self): ...
    def evaluate(self): ...
    def save(self): ...
    def deploy(self): ...
    def monitor(self): ...

# ✅ Bien: Cada clase tiene una responsabilidad
class DataLoader:
    def load(self, path: str) -> pd.DataFrame: ...

class Trainer:
    def train(self, data: pd.DataFrame) -> Model: ...

class Evaluator:
    def evaluate(self, model: Model, data: pd.DataFrame) -> dict: ...
```

#### O — Open/Closed (Abierto/Cerrado)

```python
from abc import ABC, abstractmethod

# Abierto para extensión, cerrado para modificación
class Preprocessor(ABC):
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

class StandardScalerPreprocessor(Preprocessor):
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        # Implementación específica
        ...

class MinMaxPreprocessor(Preprocessor):
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        # Otra implementación
        ...
```

#### D — Dependency Inversion (Inversión de Dependencias)

```python
# ❌ Mal: Dependencia directa
class Trainer:
    def __init__(self):
        self.logger = FileLogger()  # Acoplado a implementación

# ✅ Bien: Depender de abstracciones
class Trainer:
    def __init__(self, logger: Logger):  # Inyección de dependencia
        self.logger = logger

# Uso
trainer = Trainer(logger=ConsoleLogger())  # Flexible
trainer = Trainer(logger=MLflowLogger())   # Fácil de cambiar
```

---

### 5. Estructura de Paquete Python

Estructura profesional para proyectos ML:

```
mi_proyecto/
├── src/
│   └── mi_paquete/
│       ├── __init__.py
│       ├── config.py      # Configuración (Pydantic)
│       ├── data.py         # Carga de datos
│       ├── features.py     # Ingeniería de features
│       ├── train.py        # Entrenamiento
│       ├── predict.py      # Inferencia
│       └── utils.py        # Utilidades
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_data.py
│   └── conftest.py         # Fixtures de pytest
├── pyproject.toml          # Configuración del paquete
├── README.md
└── Makefile
```

#### pyproject.toml Mínimo

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mi-paquete"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pandas>=2.0.0",
    "scikit-learn>=1.3.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
]

[tool.setuptools.packages.find]
where = ["src"]
```

---

## 🔧 Mini-Proyecto: Librería `utils/`

### Objetivo

Crear una mini-librería con:
1. `config.py` — Configuración con Pydantic
2. `mathops.py` — Funciones matemáticas tipadas
3. Tests unitarios

### Estructura a Crear

```
work/01_python_moderno/
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── mathops.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_mathops.py
└── pyproject.toml
```

### Paso 1: Crear `utils/config.py`

```python
"""Configuración con Pydantic."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ModelConfig(BaseModel):
    """Configuración de un modelo ML."""
    
    model_name: str = Field(..., min_length=1, description="Nombre del modelo")
    version: str = Field("1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    threshold: float = Field(0.5, ge=0.0, le=1.0)
    random_state: Optional[int] = Field(42, ge=0)
    
    @field_validator("model_name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.lower().strip().replace(" ", "_")


class DataConfig(BaseModel):
    """Configuración de datos."""
    
    train_path: str
    test_path: Optional[str] = None
    target_column: str = "target"
    test_size: float = Field(0.2, gt=0.0, lt=1.0)
```

### Paso 2: Crear `utils/mathops.py`

```python
"""Operaciones matemáticas con type hints."""
from typing import Sequence
import math

def add(a: float, b: float) -> float:
    """Suma dos números."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiplica dos números."""
    return a * b

def mean(values: Sequence[float]) -> float:
    """Calcula la media de una secuencia."""
    if not values:
        raise ValueError("La secuencia no puede estar vacía")
    return sum(values) / len(values)

def std(values: Sequence[float]) -> float:
    """Calcula la desviación estándar."""
    if len(values) < 2:
        raise ValueError("Se necesitan al menos 2 valores")
    avg = mean(values)
    variance = sum((x - avg) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)

def normalize(values: Sequence[float]) -> list[float]:
    """Normaliza valores al rango [0, 1]."""
    if not values:
        return []
    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        return [0.5] * len(values)
    return [(x - min_val) / (max_val - min_val) for x in values]
```

### Paso 3: Crear `utils/__init__.py`

```python
"""Paquete utils."""
from .config import ModelConfig, DataConfig
from .mathops import add, multiply, mean, std, normalize

__all__ = [
    "ModelConfig",
    "DataConfig",
    "add",
    "multiply",
    "mean",
    "std",
    "normalize",
]
```

### Paso 4: Crear Tests

**tests/test_mathops.py**:

```python
"""Tests para mathops."""
import pytest
from utils.mathops import add, multiply, mean, std, normalize

class TestAdd:
    def test_add_positive(self):
        assert add(2, 3) == 5
    
    def test_add_negative(self):
        assert add(-1, 1) == 0
    
    def test_add_floats(self):
        assert add(1.5, 2.5) == 4.0

class TestMean:
    def test_mean_simple(self):
        assert mean([1, 2, 3]) == 2.0
    
    def test_mean_empty_raises(self):
        with pytest.raises(ValueError):
            mean([])

class TestStd:
    def test_std_simple(self):
        result = std([2, 4, 4, 4, 5, 5, 7, 9])
        assert abs(result - 2.138) < 0.01
    
    def test_std_single_raises(self):
        with pytest.raises(ValueError):
            std([1])

class TestNormalize:
    def test_normalize_simple(self):
        result = normalize([0, 5, 10])
        assert result == [0.0, 0.5, 1.0]
    
    def test_normalize_empty(self):
        assert normalize([]) == []
    
    def test_normalize_same_values(self):
        assert normalize([5, 5, 5]) == [0.5, 0.5, 0.5]
```

**tests/test_config.py**:

```python
"""Tests para config."""
import pytest
from pydantic import ValidationError
from utils.config import ModelConfig, DataConfig

class TestModelConfig:
    def test_valid_config(self):
        config = ModelConfig(model_name="test_model")
        assert config.model_name == "test_model"
        assert config.version == "1.0.0"
        assert config.threshold == 0.5
    
    def test_name_normalization(self):
        config = ModelConfig(model_name="  My Model  ")
        assert config.model_name == "my_model"
    
    def test_invalid_threshold(self):
        with pytest.raises(ValidationError):
            ModelConfig(model_name="test", threshold=1.5)
    
    def test_invalid_version_format(self):
        with pytest.raises(ValidationError):
            ModelConfig(model_name="test", version="invalid")

class TestDataConfig:
    def test_valid_config(self):
        config = DataConfig(train_path="data/train.csv")
        assert config.train_path == "data/train.csv"
        assert config.test_size == 0.2
    
    def test_invalid_test_size(self):
        with pytest.raises(ValidationError):
            DataConfig(train_path="data/train.csv", test_size=1.5)
```

### Paso 5: Crear pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "utils"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "mypy>=1.8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
```

---

## ✅ Validación

### Ejecutar Tests

```bash
cd work/01_python_moderno

# Instalar en modo editable
pip install -e ".[dev]"

# Ejecutar tests
pytest tests/ -v

# Verificar tipos
mypy utils/
```

### Desde la Raíz de la Guía

```bash
make check-01
```

---

## ❌ Errores Comunes

| Error | Causa | Solución |
|:------|:------|:---------|
| `ModuleNotFoundError` | Paquete no instalado | `pip install -e .` |
| `ValidationError` | Tipo incorrecto en Pydantic | Revisar tipos esperados |
| `TypeError: unsupported operand` | Type hints incorrectos | Usar `mypy` para detectar |

---

## 📚 Recursos Adicionales

- [Type Hints Cheat Sheet (mypy)](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [Real Python: Dataclasses](https://realpython.com/python-data-classes/)
- [SOLID Principles in Python](https://realpython.com/solid-principles-python/)

---

## ➡️ Siguiente Módulo

**[02 — Ingeniería de Datos](../02_ingenieria_datos/index.md)**

---

*Última actualización: 2024-12*
