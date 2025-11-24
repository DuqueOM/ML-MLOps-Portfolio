from __future__ import annotations

from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    project_name: str
    random_seed: int
    paths: Dict[str, str]
    features: List[str]
    target: str
    split: Dict[str, Any]
    model: Dict[str, Any]
    threshold: float = 0.5
    mlflow: Optional[Dict[str, Any]] = None

    @classmethod
    def from_yaml(cls, path: str) -> Config:
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        return cls(**cfg)
