# src/telecom/config.py

## Purpose
Defines the strict schema for project configuration using Pydantic. It replaces loose dictionary lookups with typed attribute access, reducing runtime errors caused by typos or missing keys.

## Key Features
- **Type Validation:** Automatically validates that `random_seed` is an integer, `threshold` is a float, etc.
- **YAML Integration:** Includes a helper method `from_yaml` to load and parse `config.yaml` files directly into the Pydantic model.
- **Fail-Fast:** Raises helpful error messages immediately at startup if the configuration is invalid.

## Validation
You can test the config loading in a Python shell:
```python
from src.telecom.config import Config
cfg = Config.from_yaml("configs/config.yaml")
print(cfg.model)
```
