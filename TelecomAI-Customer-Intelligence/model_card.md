# Model Card — TelecomAI Plan Classification (Smart vs Ultra)

- **Primary model**: Gradient Boosting Classifier (binary classification)
- **Baseline model**: Logistic Regression
- **Version**: v1.0
- **Task**: Predict if a customer should be on Ultra plan (`is_ultra` = 1) based on usage (`calls`, `minutes`, `messages`, `mb_used`).
- **Dataset**: `data/raw/data/raw/users_behavior.csv` (tabular, synthetic/educational). Size ~3.2K rows.
- **Target**: `is_ultra` (0/1)
- **Features (raw)**: numeric — `calls`, `minutes`, `messages`, `mb_used`
- **Features (engineered)**: `minutes_per_call`, `messages_per_call`, `mb_per_minute`

## Performance
- Metrics (holdout, split 80/20, seed=42):
  - Reported during training in `artifacts/metrics.json` (accuracy, precision, recall, f1, roc_auc)
  - Typical values for the current best model (Gradient Boosting) are around: accuracy ~0.82, precision ~0.83, recall ~0.53, F1 ~0.65, ROC AUC ~0.85 (see README for details).

**Ejemplo de impacto (ilustrativo)**
- Si, sobre una base de ~3,200 clientes con ~40% potencialmente Ultra, el modelo obtiene recall≈0.80 y precision≈0.75 en `is_ultra=1`:
  - ≈1,024 clientes elegibles se identifican correctamente.
  - Si cada migración correcta aporta +5 USD/mes de ARPU y el coste de contacto es 0.5 USD, el ROI neto puede situarse en varios miles de USD/mes (ver README para el detalle del ejemplo).

## Intended Use
- Support plan recommendations and analytics use-cases in telecom contexts.
- Not for autonomous decision-making without human oversight.

## Limitations & Risks
- Dataset may not cover all usage patterns; potential sampling bias.
- Concept/Data drift likely in real scenarios — requires monitoring.
- Fairness: Without demographic features, disparate impact cannot be assessed.

## Ethical Considerations
- Avoid using sensitive attributes for decision-making.
- Provide contestability: allow customers to review/appeal decisions.
- Transparency: expose feature importances and thresholds.

## Threshold & Decision Logic

- El modelo devuelve probabilidades `P(is_ultra=1)`; la implementación actual utiliza el threshold implícito 0.5 de scikit-learn.
- En un despliegue real se recomienda:
  - Ajustar el threshold en función del trade-off negocio: coste de sobre-oferta (FP) vs coste de infra-oferta (FN).
  - Evaluar curvas precision–recall y escenarios de ROI antes de fijar un umbral por defecto.
  - Documentar umbrales y excepciones en las políticas comerciales (no en el código) para asegurar trazabilidad.

## Maintenance
- Retrain quarterly or upon drift alerts.
- Track experiments via metrics artifacts. Version models in `artifacts/`.

## Security & Privacy
- No PII in dataset. Do not log raw payloads in production.

## Contact
- Owner: Daniel Duque
- Issues: open GitHub issues or contact maintainer.
