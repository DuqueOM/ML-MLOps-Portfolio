# Contributing to ML/MLOps Portfolio

Thank you for your interest in contributing to this portfolio! While this is primarily a showcase project, improvements and suggestions are welcome.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Commit Messages](#commit-messages)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a simple code of conduct:

- Be respectful and professional
- Provide constructive feedback
- Focus on code quality and best practices
- Respect the portfolio's educational purpose

## Getting Started

### Prerequisites

- Python 3.10+ (3.8+ for BankChurn-Predictor)
- Git
- Docker (for containerized workflows)
- Make (optional, but recommended)

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/Portafolio-ML-MLOps.git
cd Portafolio-ML-MLOps

# Add upstream remote
git remote add upstream https://github.com/DuqueOM/Portafolio-ML-MLOps.git
```

## Development Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Install development dependencies
cd BankChurn-Predictor  # Or any project
pip install -e ".[dev]"  # If pyproject.toml exists
# OR
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy pre-commit
```

### 2. Install Pre-commit Hooks

```bash
# From repository root
pre-commit install
pre-commit run --all-files  # Test hooks
```

### 3. Verify Setup

```bash
# Run tests
pytest

# Check code quality
black --check .
flake8 .
mypy .
```

## Code Standards

### Python Style

- **PEP 8** compliance (enforced by `black` and `flake8`)
- **Line length:** 120 characters
- **Imports:** Organized with `isort` (black profile)
- **Type hints:** Required for all public functions
- **Docstrings:** Google style for all modules, classes, and functions

### Example

```python
"""Module for customer churn prediction.

This module implements ensemble models for binary classification
with class imbalance handling.
"""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def train_model(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: Optional[int] = None
) -> Tuple[RandomForestClassifier, float]:
    """Train a random forest classifier.

    Args:
        X: Feature matrix with shape (n_samples, n_features).
        y: Target vector with shape (n_samples,).
        random_state: Random seed for reproducibility.

    Returns:
        Trained model and training score.

    Raises:
        ValueError: If X and y have incompatible shapes.
    """
    if len(X) != len(y):
        raise ValueError(f"X and y must have same length, got {len(X)} and {len(y)}")
    
    model = RandomForestClassifier(random_state=random_state)
    model.fit(X, y)
    score = model.score(X, y)
    
    return model, score
```

### Testing

- **Coverage:** Maintain ≥70% coverage
- **Test types:**
  - Unit tests: Core logic and transformations
  - Integration tests: End-to-end workflows
  - Fairness tests: Demographic bias checks (where applicable)
- **Naming:** `test_*.py` files, `test_*` functions
- **Fixtures:** Use `conftest.py` for shared fixtures

### Example Test

```python
import pytest
import pandas as pd
from main import train_model


def test_train_model_returns_tuple():
    """Test that train_model returns a tuple of (model, score)."""
    X = pd.DataFrame({"feature": [1, 2, 3, 4, 5]})
    y = pd.Series([0, 0, 1, 1, 1])
    
    model, score = train_model(X, y, random_state=42)
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_train_model_raises_on_length_mismatch():
    """Test that train_model raises ValueError for mismatched lengths."""
    X = pd.DataFrame({"feature": [1, 2, 3]})
    y = pd.Series([0, 1])
    
    with pytest.raises(ValueError, match="must have same length"):
        train_model(X, y)
```

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (deps, CI, etc.)
- `ci`: CI/CD changes

### Examples

```bash
feat(bankchurn): add SHAP explainability to API

Implement SHAP values calculation for model interpretability.
Adds /explain endpoint to FastAPI application.

Closes #42
```

```bash
fix(carvision): correct temporal validation split

Fixed data leakage in temporal validation where future data
was leaking into training set. Now uses strict cutoff date.
```

```bash
docs: update README with Docker quick start

Add comprehensive Docker section with examples for all projects.
```

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific marker
pytest -m unit
pytest -m "not slow"

# Specific file
pytest tests/test_model.py

# Verbose output
pytest -v
```

### Writing Tests

1. **File location:** Place in `tests/` directory
2. **Naming:** `test_<module>.py`
3. **Coverage:** Aim for ≥70% coverage
4. **Markers:** Use `@pytest.mark.slow` for slow tests
5. **Fixtures:** Define in `tests/conftest.py`

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/amazing-feature
```

### 2. Make Your Changes

- Write code following style guidelines
- Add tests for new functionality
- Update documentation (README, docstrings)
- Run pre-commit hooks

### 3. Test Locally

```bash
# Format code
black .
isort .

# Lint
flake8 .
mypy .

# Test
pytest --cov=. --cov-fail-under=70
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat(scope): add amazing feature"
```

### 5. Push and Create PR

```bash
git push origin feature/amazing-feature
```

Then create a Pull Request on GitHub with:

- **Title:** Clear, descriptive (follows commit convention)
- **Description:** 
  - What changed and why
  - Related issues (e.g., `Closes #123`)
  - Testing performed
  - Screenshots (if UI changes)

### 6. Code Review

- Address reviewer feedback
- Keep commits atomic and well-described
- Squash commits if requested

### 7. Merge

Once approved, the PR will be merged by maintainers.

## Project-Specific Guidelines

### BankChurn-Predictor

- Ensure fairness tests pass for protected attributes
- Maintain calibration plots in results
- Update model card if metrics change

### CarVision-Market-Intelligence

- Temporal validation must use strict cutoffs
- Update Streamlit dashboard if features change
- Check backtesting results

### All Projects

- Maintain backwards compatibility of APIs
- Update requirements.txt/pyproject.toml
- Keep Dockerfiles functional
- Update CI/CD workflows if needed

## Questions?

If you have questions or need help:

1. Check existing issues and documentation
2. Open an issue with the `question` label
3. Reach out via GitHub Discussions (if enabled)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
