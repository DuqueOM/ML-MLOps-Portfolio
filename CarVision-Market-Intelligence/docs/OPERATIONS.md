# Operations Runbook - CarVision Market Intelligence

## System Information
-   **Service Name**: CarVision API
-   **Repository**: `DuqueOM/ML-MLOps-Portfolio/CarVision-Market-Intelligence`
-   **Tech Stack**: Python 3.11, FastAPI, Scikit-learn, Docker

## 🚀 Deployment

### Standard Deployment (Docker)
1.  **Build Image**:
    ```bash
    docker build -t carvision:latest .
    ```
2.  **Run Container**:
    ```bash
    docker run -d -p 8000:8000 --name carvision-api carvision:latest
    ```
3.  **Verify**:
    ```bash
    curl http://localhost:8000/health
    # Expected: {"status": "healthy"}
    ```

### CI/CD Deployment
Deployment is automated via GitHub Actions on merge to `main`.
1.  Tests run.
2.  Docker image is built and pushed to registry (if configured).
3.  Continuous Deployment triggers (e.g., via webhook or GitOps).

## 🔄 Retraining Pipeline
To update the model with new data:

1.  **Update Data**:
    Place new `data/raw/vehicles_us.csv` in `data/raw/` or pull via DVC.
    ```bash
    dvc pull
    ```

2.  **Run Pipeline**:
    ```bash
    dvc repro
    ```
    This executes cleaning, feature engineering, and training steps defined in `dvc.yaml`.

3.  **Commit Changes**:
    ```bash
    git add dvc.lock
    git commit -m "Retrain model with new data"
    git push
    ```

4.  **Compare Metrics**:
    Check MLflow for performance regression.
    ```bash
    mlflow ui
    ```

## ⚠️ Monitoring & Alerting

### Key Metrics to Monitor
-   **API Latency**: P99 response time should be < 200ms.
-   **Error Rate**: 5xx responses should be < 1%.
-   **Data Drift**: Monitor distribution of `price` and `vehicle_age`.

### Alert Thresholds
-   **High Latency**: Alert if P95 > 500ms for 5 minutes.
-   **Model Failure**: Alert if `/health` returns non-200.
-   **Disk Space**: Alert if usage > 85% (logs can fill disk).

## 🚑 Troubleshooting

### Scenario: Model API returns 500 Error
1.  Check logs:
    ```bash
    docker logs carvision-api
    ```
2.  Look for "Missing column" errors. This indicates schema mismatch between input and model expectation.
3.  Verify `config.yaml` `drop_columns` matches the deployed model version.

### Scenario: Low Accuracy reported by users
1.  Check `vehicle_age` distribution in recent requests.
2.  If users are querying for 2025 models but model trained on 2018 data, accuracy will drop (Concept Drift).
3.  **Action**: Trigger Retraining Pipeline with newer data.

### Scenario: Pipeline fails at "clean_data"
1.  Check input CSV schema.
2.  Ensure `filters` in `config.yaml` are not too aggressive (filtering all data).

## 🛡️ Maintenance
-   **Log Rotation**: Ensure logs are rotated daily.
-   **Dependency Updates**: Run `pip-compile --upgrade` monthly to update locked dependencies.
-   **Security**: Monitor `gitleaks` output in CI for exposed secrets.
