---
description: Retrain an ML model — data validation, training, evaluation against baseline, MLflow registration, deployment prep
---

## Model Retraining Workflow

1. Ask the user which service to retrain: BankChurn, NLPInsight, or ChicagoTaxi

2. Validate training data integrity:
   ```bash
   python -c "
   import pandas as pd
   df = pd.read_csv('data/train.csv')
   print(f'Shape: {df.shape}')
   print(f'Nulls: {df.isnull().sum().sum()}')
   print(f'Duplicates: {df.duplicated().sum()}')
   "
   ```

3. Run the training script:
   ```bash
   python scripts/train_production_models.py --service <service-name>
   ```

4. Evaluate against baseline metrics (invoke the `model-retrain` skill for thresholds):
   - BankChurn: AUC ≥ 0.85, F1 ≥ 0.60, no regression >2%
   - NLPInsight: Accuracy ≥ 0.95, F1-weighted ≥ 0.95
   - ChicagoTaxi: R² ≥ 0.75, RMSE ≤ $7,500

5. If metrics pass, register in MLflow:
   ```bash
   python scripts/register_model.py --service <service-name> --version v${VERSION}
   ```

6. Upload model artifact to GCS:
   ```bash
   gsutil cp models/<service>/model.joblib \
     gs://ml-portfolio-duque-om-202602-ml-models-production/<service>/v${VERSION}/
   ```

7. Update the ConfigMap with new model version:
   ```bash
   kubectl edit configmap <service>-config
   ```

8. Deploy using the `/release` workflow or manual `kubectl apply -k`

9. Run load test to verify inference latency:
   ```bash
   python scripts/load_test_services.py --service <service-name> --users 10 --duration 30
   ```

10. If any step fails, document the failure reason and keep current production model active
