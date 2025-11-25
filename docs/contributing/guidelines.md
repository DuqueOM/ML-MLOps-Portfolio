# Contributing Guidelines

Thank you for your interest in contributing to the ML-MLOps Portfolio! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.11 or 3.12
- Docker and Docker Compose
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Install project dependencies (example for BankChurn)
cd BankChurn-Predictor
pip install -e ".[dev]"
```

## Development Workflow

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<description>` | `feature/add-shap-explainer` |
| Bug Fix | `fix/<description>` | `fix/prediction-timeout` |
| Documentation | `docs/<description>` | `docs/update-readme` |
| Refactor | `refactor/<description>` | `refactor/simplify-pipeline` |

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat(bankchurn): add SHAP explainer for predictions
fix(carvision): handle missing odometer values
docs(telecom): update API documentation
refactor(training): extract preprocessing logic
```

## Code Standards

### Python Style

- **Formatter**: Black (line length 120)
- **Linter**: Flake8
- **Type Hints**: Required for public functions
- **Docstrings**: Google style

### Pre-commit Checks

All commits run these checks automatically:

```bash
# Run manually
pre-commit run --all-files

# Individual tools
black .
isort .
flake8 .
```

## Testing

### Running Tests

```bash
# Run all tests for a project
cd BankChurn-Predictor
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/bankchurn --cov-report=html

# Specific test
pytest tests/test_training.py::test_train_model -v
```

### Writing Tests

- Place tests in `tests/` directory
- Name files `test_<module>.py`
- Use fixtures for shared setup
- Aim for >70% coverage

## Pull Request Process

1. **Create a branch** from `main`
2. **Make changes** with appropriate tests
3. **Run pre-commit** and ensure all checks pass
4. **Push branch** and create PR
5. **Fill out PR template** completely
6. **Request review** from maintainers
7. **Address feedback** and update
8. **Merge** after approval

### PR Template

```markdown
## Summary
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
Describe how you tested the changes.

## Checklist
- [ ] Tests pass locally
- [ ] Pre-commit hooks pass
- [ ] Documentation updated (if needed)
```

## Documentation

### MkDocs Site

```bash
# Install docs dependencies
pip install -r requirements-docs.txt

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

### Docstrings

Use Google-style docstrings:

```python
def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Make predictions on input data.
    
    Args:
        X: Feature matrix for prediction.
        threshold: Classification threshold (default: 0.5).
    
    Returns:
        DataFrame with predictions and probabilities.
    
    Raises:
        ValueError: If X has incorrect columns.
    """
```

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: See [Security Policy](https://github.com/DuqueOM/ML-MLOps-Portfolio/security/policy)

---

Thank you for contributing! 🎉
