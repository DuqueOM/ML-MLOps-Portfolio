# Acceptance Checklist

## 1. Code Quality
- [ ] **Linting:** `make lint` passes without errors.
- [ ] **Tests:** `pytest` passes (all green).
- [ ] **Coverage:** Code coverage > 80%.

## 2. Functionality
- [ ] **Training:** `python main.py --mode train` produces a valid `model.joblib`.
- [ ] **Evaluation:** `python main.py --mode eval` produces reasonable metrics (Acc > 0.75).
- [ ] **Prediction:** `python main.py --mode predict ...` generates a CSV with predictions.
- [ ] **API:** `/predict` endpoint returns valid JSON for sample inputs.

## 3. Infrastructure
- [ ] **Docker:** Image builds successfully.
- [ ] **Demo:** `make start-demo` brings up the service and passes health checks.
