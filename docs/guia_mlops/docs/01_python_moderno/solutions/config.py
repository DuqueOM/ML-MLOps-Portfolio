"""Configuración con Pydantic — Solución Módulo 01."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ModelConfig(BaseModel):
    """Configuración de un modelo ML.

    Attributes:
        model_name: Nombre del modelo (se normaliza automáticamente)
        version: Versión semántica (formato X.Y.Z)
        threshold: Umbral de clasificación entre 0 y 1
        random_state: Semilla para reproducibilidad
    """

    model_name: str = Field(..., min_length=1, description="Nombre del modelo")
    version: str = Field("1.0.0", pattern=r"^\d+\.\d+\.\d+$", description="Versión semántica (ej: 1.0.0)")
    threshold: float = Field(0.5, ge=0.0, le=1.0, description="Umbral de clasificación")
    random_state: Optional[int] = Field(42, ge=0, description="Semilla para reproducibilidad")

    @field_validator("model_name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normaliza el nombre del modelo.

        - Convierte a minúsculas
        - Elimina espacios al inicio y final
        - Reemplaza espacios por guiones bajos
        """
        return v.lower().strip().replace(" ", "_")

    def full_name(self) -> str:
        """Retorna el nombre completo con versión."""
        return f"{self.model_name}-v{self.version}"


class DataConfig(BaseModel):
    """Configuración de datos para entrenamiento.

    Attributes:
        train_path: Ruta al archivo de entrenamiento
        test_path: Ruta opcional al archivo de test
        target_column: Nombre de la columna objetivo
        test_size: Proporción de datos para test (si no hay test_path)
    """

    train_path: str = Field(..., description="Ruta al archivo de entrenamiento")
    test_path: Optional[str] = Field(None, description="Ruta al archivo de test (opcional)")
    target_column: str = Field("target", description="Nombre de la columna objetivo")
    test_size: float = Field(0.2, gt=0.0, lt=1.0, description="Proporción de datos para test")

    @field_validator("train_path", "test_path")
    @classmethod
    def validate_path_extension(cls, v: Optional[str]) -> Optional[str]:
        """Valida que los paths tengan extensión válida."""
        if v is None:
            return v
        valid_extensions = (".csv", ".parquet", ".json")
        if not v.endswith(valid_extensions):
            raise ValueError(f"Extensión de archivo no soportada. " f"Use: {valid_extensions}")
        return v


class TrainingConfig(BaseModel):
    """Configuración completa de entrenamiento.

    Combina configuración de modelo y datos.
    """

    model: ModelConfig
    data: DataConfig

    # Hiperparámetros de entrenamiento
    learning_rate: float = Field(0.01, gt=0, le=1)
    n_estimators: int = Field(100, ge=10, le=1000)
    max_depth: Optional[int] = Field(None, ge=1, le=50)

    def to_mlflow_params(self) -> dict:
        """Convierte a diccionario para logging en MLflow."""
        return {
            "model_name": self.model.model_name,
            "model_version": self.model.version,
            "threshold": self.model.threshold,
            "learning_rate": self.learning_rate,
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "random_state": self.model.random_state,
        }
