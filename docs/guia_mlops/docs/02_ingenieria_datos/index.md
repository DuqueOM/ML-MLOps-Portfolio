# 02 — Ingeniería de Datos

> **Tiempo estimado**: 4 días (32 horas)
> 
> **Prerrequisitos**: Módulo 01 completado

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Crear **loaders de datos** reutilizables y tipados
2. ✅ Implementar **validación de datos** con schemas
3. ✅ Construir **pipelines ETL** reproducibles
4. ✅ Escribir **tests de integridad** de datos

---

## 📖 Contenido Teórico

### 1. Principios de Ingeniería de Datos para ML

#### ¿Por qué importa la calidad de datos?

> "Garbage in, garbage out" — Los mejores modelos no pueden compensar datos malos.

| Problema de Datos | Impacto en ML |
|:------------------|:--------------|
| Valores faltantes | Errores de entrenamiento, sesgos |
| Duplicados | Overfitting, métricas infladas |
| Tipos incorrectos | Errores de runtime |
| Outliers no tratados | Modelos sensibles a ruido |
| Data leakage | Métricas irreales, fallo en producción |

#### Pipeline de Datos Típico

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Extracción │ --> │   Validación │ --> │ Transformación│ --> │    Carga     │
│   (Extract)  │     │  (Validate)  │     │  (Transform) │     │   (Load)     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
      │                    │                    │                    │
      v                    v                    v                    v
   raw/*.csv          schemas/              processed/           outputs/
                      contracts            *.parquet            train/test
```

---

### 2. Carga de Datos Profesional

#### Loader Básico con Type Hints

```python
"""data.py — Módulo de carga de datos."""
from pathlib import Path
from typing import Optional
import pandas as pd


def load_csv(
    path: str | Path,
    columns: Optional[list[str]] = None,
    dtype: Optional[dict[str, str]] = None,
) -> pd.DataFrame:
    """Carga un archivo CSV con validaciones básicas.
    
    Args:
        path: Ruta al archivo CSV
        columns: Columnas a seleccionar (opcional)
        dtype: Tipos de datos por columna (opcional)
        
    Returns:
        DataFrame con los datos cargados
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si las columnas especificadas no existen
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    
    df = pd.read_csv(path, dtype=dtype)
    
    if columns:
        missing = set(columns) - set(df.columns)
        if missing:
            raise ValueError(f"Columnas no encontradas: {missing}")
        df = df[columns]
    
    return df
```

#### Loader con Caché y Logging

```python
"""data.py — Loader avanzado."""
from functools import lru_cache
from pathlib import Path
from typing import Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """Cargador de datos con caché y logging."""
    
    def __init__(self, base_path: str | Path = "data"):
        self.base_path = Path(base_path)
        self._cache: dict[str, pd.DataFrame] = {}
    
    def load(
        self,
        filename: str,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """Carga datos con caché opcional."""
        
        if use_cache and filename in self._cache:
            logger.info(f"Usando caché para {filename}")
            return self._cache[filename].copy()
        
        path = self.base_path / filename
        logger.info(f"Cargando datos desde {path}")
        
        # Detectar formato por extensión
        if path.suffix == ".csv":
            df = pd.read_csv(path)
        elif path.suffix == ".parquet":
            df = pd.read_parquet(path)
        elif path.suffix == ".json":
            df = pd.read_json(path)
        else:
            raise ValueError(f"Formato no soportado: {path.suffix}")
        
        if use_cache:
            self._cache[filename] = df.copy()
        
        logger.info(f"Cargados {len(df)} registros, {len(df.columns)} columnas")
        return df
    
    def clear_cache(self) -> None:
        """Limpia la caché."""
        self._cache.clear()
        logger.info("Caché limpiada")
```

---

### 3. Validación de Datos con Schemas

#### Esquema con Pydantic

```python
"""schemas.py — Contratos de datos."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"


class CustomerRecord(BaseModel):
    """Schema para un registro de cliente."""
    
    customer_id: str = Field(..., min_length=1)
    age: int = Field(..., ge=18, le=120)
    gender: Gender
    balance: float = Field(..., ge=0)
    tenure: int = Field(..., ge=0)
    is_active: bool
    churn: Optional[bool] = None
    
    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("customer_id no puede estar vacío")
        return v.strip()


def validate_dataframe(
    df: pd.DataFrame,
    schema: type[BaseModel],
) -> tuple[pd.DataFrame, list[dict]]:
    """Valida un DataFrame contra un schema Pydantic.
    
    Returns:
        Tuple de (DataFrame válido, lista de errores)
    """
    valid_records = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            record = schema(**row.to_dict())
            valid_records.append(record.model_dump())
        except Exception as e:
            errors.append({
                "index": idx,
                "error": str(e),
                "data": row.to_dict()
            })
    
    return pd.DataFrame(valid_records), errors
```

#### Validación con Pandera (Alternativa)

```python
"""schemas_pandera.py — Schemas con Pandera."""
import pandera as pa
from pandera import Column, Check, DataFrameSchema


customer_schema = DataFrameSchema(
    columns={
        "customer_id": Column(str, Check.str_length(min_value=1)),
        "age": Column(int, Check.in_range(18, 120)),
        "gender": Column(str, Check.isin(["Male", "Female"])),
        "balance": Column(float, Check.ge(0)),
        "tenure": Column(int, Check.ge(0)),
        "is_active": Column(bool),
        "churn": Column(bool, nullable=True),
    },
    strict=True,  # No permite columnas extra
    coerce=True,  # Intenta convertir tipos
)


def validate_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Valida DataFrame de clientes."""
    return customer_schema.validate(df)
```

---

### 4. Transformaciones y Limpieza

#### Funciones de Limpieza

```python
"""transformations.py — Transformaciones de datos."""
import pandas as pd
import numpy as np
from typing import Optional


def remove_duplicates(
    df: pd.DataFrame,
    subset: Optional[list[str]] = None,
    keep: str = "first",
) -> pd.DataFrame:
    """Elimina registros duplicados.
    
    Args:
        df: DataFrame de entrada
        subset: Columnas para detectar duplicados
        keep: 'first', 'last', o False
        
    Returns:
        DataFrame sin duplicados
    """
    n_before = len(df)
    df = df.drop_duplicates(subset=subset, keep=keep)
    n_removed = n_before - len(df)
    
    if n_removed > 0:
        print(f"Eliminados {n_removed} duplicados ({n_removed/n_before:.1%})")
    
    return df


def handle_missing(
    df: pd.DataFrame,
    strategy: dict[str, str],
    fill_values: Optional[dict[str, any]] = None,
) -> pd.DataFrame:
    """Maneja valores faltantes por columna.
    
    Args:
        df: DataFrame de entrada
        strategy: {"columna": "drop"|"mean"|"median"|"mode"|"constant"}
        fill_values: Valores para estrategia "constant"
        
    Returns:
        DataFrame con valores faltantes tratados
    """
    df = df.copy()
    fill_values = fill_values or {}
    
    for col, strat in strategy.items():
        if col not in df.columns:
            continue
            
        if strat == "drop":
            df = df.dropna(subset=[col])
        elif strat == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif strat == "median":
            df[col] = df[col].fillna(df[col].median())
        elif strat == "mode":
            df[col] = df[col].fillna(df[col].mode().iloc[0])
        elif strat == "constant":
            df[col] = df[col].fillna(fill_values.get(col, 0))
    
    return df


def clip_outliers(
    df: pd.DataFrame,
    columns: list[str],
    lower_quantile: float = 0.01,
    upper_quantile: float = 0.99,
) -> pd.DataFrame:
    """Recorta outliers usando percentiles.
    
    Args:
        df: DataFrame de entrada
        columns: Columnas numéricas a procesar
        lower_quantile: Percentil inferior
        upper_quantile: Percentil superior
        
    Returns:
        DataFrame con outliers recortados
    """
    df = df.copy()
    
    for col in columns:
        if col not in df.columns:
            continue
        
        lower = df[col].quantile(lower_quantile)
        upper = df[col].quantile(upper_quantile)
        df[col] = df[col].clip(lower=lower, upper=upper)
    
    return df
```

---

### 5. Pipeline ETL Completo

```python
"""etl.py — Pipeline ETL reproducible."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import pandas as pd
import logging

from .data import DataLoader
from .transformations import remove_duplicates, handle_missing, clip_outliers
from .schemas import validate_customers

logger = logging.getLogger(__name__)


@dataclass
class ETLConfig:
    """Configuración del pipeline ETL."""
    
    input_path: str
    output_path: str
    duplicate_subset: Optional[list[str]] = None
    missing_strategy: dict[str, str] = None
    outlier_columns: list[str] = None
    
    def __post_init__(self):
        self.missing_strategy = self.missing_strategy or {}
        self.outlier_columns = self.outlier_columns or []


class ETLPipeline:
    """Pipeline ETL reproducible para datos de clientes."""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.loader = DataLoader()
        self._stats: dict = {}
    
    def run(self) -> pd.DataFrame:
        """Ejecuta el pipeline completo.
        
        Returns:
            DataFrame procesado
        """
        logger.info("=== Iniciando ETL Pipeline ===")
        
        # 1. Extracción
        df = self._extract()
        
        # 2. Limpieza
        df = self._clean(df)
        
        # 3. Validación
        df = self._validate(df)
        
        # 4. Carga
        self._load(df)
        
        logger.info("=== ETL Pipeline completado ===")
        self._log_stats()
        
        return df
    
    def _extract(self) -> pd.DataFrame:
        """Paso 1: Extracción."""
        logger.info("Paso 1: Extracción")
        df = self.loader.load(self.config.input_path, use_cache=False)
        self._stats["raw_records"] = len(df)
        return df
    
    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Paso 2: Limpieza."""
        logger.info("Paso 2: Limpieza")
        
        # Eliminar duplicados
        df = remove_duplicates(df, subset=self.config.duplicate_subset)
        self._stats["after_dedup"] = len(df)
        
        # Manejar valores faltantes
        df = handle_missing(df, strategy=self.config.missing_strategy)
        self._stats["after_missing"] = len(df)
        
        # Recortar outliers
        if self.config.outlier_columns:
            df = clip_outliers(df, columns=self.config.outlier_columns)
        
        return df
    
    def _validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Paso 3: Validación."""
        logger.info("Paso 3: Validación")
        
        try:
            df = validate_customers(df)
            self._stats["validation_errors"] = 0
        except Exception as e:
            logger.error(f"Error de validación: {e}")
            self._stats["validation_errors"] = 1
            raise
        
        return df
    
    def _load(self, df: pd.DataFrame) -> None:
        """Paso 4: Carga."""
        logger.info("Paso 4: Carga")
        
        output_path = Path(self.config.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar en Parquet (más eficiente)
        df.to_parquet(output_path, index=False)
        
        self._stats["final_records"] = len(df)
        self._stats["output_path"] = str(output_path)
    
    def _log_stats(self) -> None:
        """Registra estadísticas del pipeline."""
        logger.info("=== Estadísticas ===")
        for key, value in self._stats.items():
            logger.info(f"  {key}: {value}")
```

---

### 6. Tests de Integridad

```python
"""test_data_integrity.py — Tests de integridad de datos."""
import pytest
import pandas as pd
import numpy as np


class TestDataIntegrity:
    """Tests de integridad para datos procesados."""
    
    @pytest.fixture
    def sample_data(self) -> pd.DataFrame:
        """Datos de ejemplo para tests."""
        return pd.DataFrame({
            "customer_id": ["C001", "C002", "C003"],
            "age": [25, 35, 45],
            "balance": [1000.0, 2000.0, 3000.0],
            "churn": [0, 1, 0],
        })
    
    def test_no_duplicates(self, sample_data):
        """Verifica que no hay duplicados."""
        assert not sample_data.duplicated().any()
    
    def test_no_null_in_required(self, sample_data):
        """Verifica que columnas requeridas no tienen nulls."""
        required = ["customer_id", "age", "churn"]
        for col in required:
            assert not sample_data[col].isnull().any(), f"Nulls en {col}"
    
    def test_valid_age_range(self, sample_data):
        """Verifica rango de edad válido."""
        assert sample_data["age"].between(18, 120).all()
    
    def test_positive_balance(self, sample_data):
        """Verifica que balance es positivo."""
        assert (sample_data["balance"] >= 0).all()
    
    def test_binary_target(self, sample_data):
        """Verifica que target es binario."""
        assert set(sample_data["churn"].unique()).issubset({0, 1})
    
    def test_unique_ids(self, sample_data):
        """Verifica que IDs son únicos."""
        assert sample_data["customer_id"].is_unique
    
    def test_schema_columns(self, sample_data):
        """Verifica que todas las columnas esperadas existen."""
        expected = {"customer_id", "age", "balance", "churn"}
        assert expected.issubset(set(sample_data.columns))
```

---

## 🔧 Mini-Proyecto: ETL Reproducible

### Objetivo

Crear un pipeline ETL que:
1. Cargue datos de un CSV
2. Limpie y valide los datos
3. Exporte a Parquet
4. Tenga tests de integridad

### Estructura a Crear

```
work/02_ingenieria_datos/
├── src/
│   ├── __init__.py
│   ├── data.py
│   ├── schemas.py
│   ├── transformations.py
│   └── etl.py
├── data/
│   ├── raw/
│   │   └── sample_customers.csv
│   └── processed/
├── tests/
│   ├── __init__.py
│   ├── test_data.py
│   ├── test_transformations.py
│   └── test_etl.py
├── run_etl.py
└── pyproject.toml
```

### Dataset de Ejemplo

Crea `data/raw/sample_customers.csv`:

```csv
customer_id,age,gender,balance,tenure,is_active,churn
C001,25,Male,1000.50,12,True,0
C002,35,Female,2500.00,24,True,0
C003,45,Male,500.00,6,False,1
C004,55,Female,3000.00,36,True,0
C005,30,Male,1500.00,18,True,0
C006,40,Female,,12,True,0
C007,28,Male,2000.00,8,False,1
C008,50,Female,4000.00,48,True,0
C009,35,Male,1800.00,15,True,0
C010,42,Female,2200.00,20,False,1
```

### Criterios de Éxito

- [ ] ETL ejecuta sin errores: `python run_etl.py`
- [ ] Genera archivo Parquet en `data/processed/`
- [ ] Tests pasan: `pytest tests/ -v`
- [ ] Sin valores nulos en columnas requeridas
- [ ] IDs únicos verificados

---

## ✅ Validación

```bash
cd work/02_ingenieria_datos

# Ejecutar ETL
python run_etl.py

# Ejecutar tests
pytest tests/ -v

# Desde la raíz de la guía
make check-02
```

---

## ❌ Errores Comunes

| Error | Causa | Solución |
|:------|:------|:---------|
| `FileNotFoundError` | Path incorrecto | Verificar que existe `data/raw/` |
| `ValidationError` | Tipos incompatibles | Revisar schema vs datos |
| `KeyError: column` | Columna faltante | Verificar nombres de columnas |
| `ParquetError` | Tipos mixtos | Forzar tipos con `dtype` |

---

## 📚 Recursos Adicionales

- [Pandera Documentation](https://pandera.readthedocs.io/)
- [Pandas Best Practices](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)
- [Great Expectations](https://greatexpectations.io/) - Framework de validación

---

## ➡️ Siguiente Módulo

**[03 — Feature Engineering](../03_feature_engineering/index.md)**

---

*Última actualización: 2024-12*
