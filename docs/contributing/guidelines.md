# Contributing to ML/MLOps Portfolio

Thank you for your interest in contributing to this portfolio! This project demonstrates production-grade MLOps practices.

## Getting Started

### Prerequisites
- **Python 3.11+** (3.12 also supported)
- **Docker** & **Docker Compose**
- **Make** utility
- **pytest** for running tests

### Recommended Reading
Before contributing, please review:
- **[Architecture Documentation](../ARCHITECTURE_PORTFOLIO.md)**: Understand the system design
- **[Deployment Guide](../operations/deployment.md)**: Learn deployment and monitoring procedures
- **[Deployment Evidence](../DEPLOYMENT_EVIDENCE.md)**: Multi-cloud deployment verification

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
- `NLPInsight-Customer-Intelligence/` (FastAPI + VotingClassifier)

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
- **Coverage**: Must remain above 80% (actual: 88-95%, [Codecov verified](https://app.codecov.io/gh/DuqueOM/ML-MLOps-Portfolio)).

**Run integration tests**:
```bash
# Start demo stack
docker compose -f docker-compose.demo.yml up -d

# Run tests
pytest tests/integration/test_demo.py -v

# Tear down
docker compose -f docker-compose.demo.yml down
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

## Development Process & AI Transparency

This portfolio was developed using **AI-assisted tools** (Cursor / Cascade) for code generation and boilerplate acceleration. All architectural decisions, project selection, MLOps pipeline design, infrastructure choices, and system integration were made by the author.

**What AI tools were used for:**
- Boilerplate code generation (FastAPI endpoints, test scaffolding, Dockerfile templates)
- Documentation drafting and formatting
- Code refactoring suggestions and performance optimization patterns

**What the author owns and maintains independently:**
- All architectural and design decisions
- MLOps pipeline design (CI/CD workflow, security scanning strategy, coverage enforcement)
- Infrastructure choices (Terraform modules, Kubernetes manifests, monitoring stack)
- Model selection, experiment design, and hyperparameter tuning strategy
- System integration, debugging, and production operations
- Docker optimization and multi-stage build design

This transparency reflects the industry-standard practice of leveraging AI tools as productivity accelerators while retaining full engineering ownership.

## License
By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Last Updated**: February 2026
