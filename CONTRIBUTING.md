# Contributing to ML/MLOps Portfolio

Thank you for your interest in contributing to this portfolio! This project demonstrates production-grade MLOps practices.

## 📋 Table of Contents
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Getting Started

### Prerequisites
- **Python 3.11+** (3.12 also supported)
- **Docker** & **Docker Compose**
- **Make** utility
- **pytest** for running tests

### Recommended Reading
Before contributing, please review:
- **[Architecture Documentation](docs/ARCHITECTURE_PORTFOLIO.md)**: Understand the system design
- **[Operations Runbook](docs/OPERATIONS_PORTFOLIO.md)**: Learn deployment and monitoring procedures
- **[Dependency Management](docs/DEPENDENCY_CONFLICTS.md)**: Understand dependency strategy
- **[PR Plan](docs/PR_PLAN.md)**: See planned improvements and priorities

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
   cd ML-MLOps-Portfolio
   ```

2. **Install Dependencies**
   We use `make` to manage dependencies across all projects:
   ```bash
   make install
   ```

3. **Verify Environment**
   Run the test suite to ensure everything is working:
   ```bash
   make test
   ```

## Development Workflow

### 1. Project Structure
The portfolio consists of three main microservices:
- `BankChurn-Predictor/` (FastAPI + Scikit-learn)
- `CarVision-Market-Intelligence/` (Streamlit + FastAPI)
- `TelecomAI-Customer-Intelligence/` (FastAPI + VotingClassifier)

### 2. Dependency Management
We use `requirements.in` for direct dependencies and `pip-compile` for locking.
**To add a package:**
1. Edit `requirements.in` in the specific project folder.
2. Run:
   ```bash
   pip-compile requirements.in
   ```
3. Re-install: `pip install -r requirements.txt`

### 3. Running Locally
Use the unified Docker stack for testing integration:
```bash
make docker-demo
```

## Code Standards

### Python Style
- **Formatter**: `black`
- **Linter**: `flake8`
- **Type Checking**: `mypy`
- **Imports**: `isort`

Run the linting suite before committing:
```bash
make lint
```

### Testing
- **Unit Tests**: Required for all new logic (`tests/test_*.py`).
- **Integration Tests**: Required for API endpoints.
  - Use `tests/integration/test_demo.py` for cross-project validation.
  - Ensure all services pass health checks and prediction tests.
- **Coverage**: Must remain above 70% (target: 75%+).

**Run integration tests**:
```bash
# Start demo stack
docker-compose -f docker-compose.demo.yml up -d

# Run tests
pytest tests/integration/test_demo.py -v

# Tear down
docker-compose -f docker-compose.demo.yml down
```

## Commit Messages
We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `chore`: Maintenance (deps, build)
- `refactor`: Code restructuring

**Example:**
```text
feat(bankchurn): add probability calibration to XGBoost model
```

## Pull Request Process

1. Create a branch: `feat/my-new-feature`
2. Commit changes ensuring `make test` passes.
3. Open a PR targeting `main`.
4. Ensure the CI pipeline (Tests, Lint, Docker Build) is green.
5. Request review.

## License
By contributing, you agree that your contributions will be licensed under the MIT License.
