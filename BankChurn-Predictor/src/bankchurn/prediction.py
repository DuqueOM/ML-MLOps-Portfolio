"""Batch prediction for churn prediction models.

This module provides functionality for making predictions on new data.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

logger = logging.getLogger(__name__)


class ChurnPredictor:
    """Batch prediction for churn models.

    Parameters
    ----------
    model : object
        Trained model with predict and predict_proba methods.
    preprocessor : object
        Fitted preprocessor for feature transformation.

    Attributes
    ----------
    model : object
        Loaded model.
    preprocessor : object
        Loaded preprocessor.
    """

    def __init__(self, model: Any, preprocessor: Any) -> None:
        self.model = model
        self.preprocessor = preprocessor

    @classmethod
    def from_files(cls, model_path: str | Path, preprocessor_path: str | Path) -> ChurnPredictor:
        """Load model and preprocessor from disk.

        Parameters
        ----------
        model_path : str or Path
            Path to saved model.
        preprocessor_path : str or Path
            Path to saved preprocessor.

        Returns
        -------
        predictor : ChurnPredictor
            Initialized predictor with loaded artifacts.
        """
        model = joblib.load(model_path)
        preprocessor = joblib.load(preprocessor_path)
        logger.info(f"Loaded model from {model_path}")
        logger.info(f"Loaded preprocessor from {preprocessor_path}")
        return cls(model, preprocessor)

    def predict(
        self,
        X: pd.DataFrame,
        include_proba: bool = True,
        threshold: float = 0.5,
    ) -> pd.DataFrame:
        """Make predictions on new data.

        Parameters
        ----------
        X : DataFrame
            Feature matrix for prediction.
        include_proba : bool, default=True
            Whether to include probability scores.
        threshold : float, default=0.5
            Classification threshold for binary predictions.

        Returns
        -------
        predictions : DataFrame
            Predictions with columns:
            - prediction: Binary class (0 or 1)
            - probability: Probability of positive class (if include_proba=True)
            - risk_level: Risk category (low/medium/high)
        """
        # Transform features
        X_transformed = self.preprocessor.transform(X)

        # Predict
        y_pred = self.model.predict(X_transformed)

        # Build results dataframe
        results = pd.DataFrame({"prediction": y_pred})

        # Add probabilities if requested and available
        if include_proba:
            try:
                y_proba = self.model.predict_proba(X_transformed)

                # Assuming binary classification, take positive class
                if y_proba.shape[1] == 2:
                    results["probability"] = y_proba[:, 1]

                    # Apply custom threshold
                    results["prediction"] = (results["probability"] >= threshold).astype(int)

                    # Risk levels
                    results["risk_level"] = pd.cut(
                        results["probability"],
                        bins=[0, 0.3, 0.7, 1.0],
                        labels=["low", "medium", "high"],
                    )
                else:
                    # Multi-class: include all class probabilities
                    for i in range(y_proba.shape[1]):
                        results[f"probability_class_{i}"] = y_proba[:, i]

            except AttributeError:
                logger.warning("Model does not support predict_proba, skipping probabilities")

        logger.info(f"Generated predictions for {len(results)} samples")

        if "risk_level" in results.columns:
            risk_counts = results["risk_level"].value_counts()
            logger.info(f"Risk distribution: {dict(risk_counts)}")

        return results

    def predict_batch(
        self,
        input_path: str | Path,
        output_path: str | Path,
        include_proba: bool = True,
        threshold: float = 0.5,
    ) -> pd.DataFrame:
        """Make predictions on data from CSV file and save results.

        Parameters
        ----------
        input_path : str or Path
            Path to input CSV file.
        output_path : str or Path
            Path to save predictions CSV.
        include_proba : bool, default=True
            Whether to include probability scores.
        threshold : float, default=0.5
            Classification threshold.

        Returns
        -------
        predictions : DataFrame
            DataFrame with predictions.

        Raises
        ------
        FileNotFoundError
            If input file doesn't exist.
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Load data
        data = pd.read_csv(input_path)
        logger.info(f"Loaded {len(data)} rows from {input_path}")

        # Make predictions
        predictions = self.predict(data, include_proba=include_proba, threshold=threshold)

        # Combine with original data (optional)
        results_df = pd.concat([data.reset_index(drop=True), predictions.reset_index(drop=True)], axis=1)

        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(output_path, index=False)
        logger.info(f"Predictions saved to {output_path}")

        return results_df

    def explain_prediction(self, X: pd.DataFrame, sample_idx: int = 0) -> dict[str, Any]:
        """Explain a single prediction (basic feature importance).

        Parameters
        ----------
        X : DataFrame
            Feature matrix.
        sample_idx : int, default=0
            Index of sample to explain.

        Returns
        -------
        explanation : dict
            Dictionary with prediction and feature contributions.

        Notes
        -----
        For more advanced explanations, consider integrating SHAP or LIME.
        """
        X_transformed = self.preprocessor.transform(X)
        sample = X_transformed[sample_idx : sample_idx + 1]

        prediction = self.model.predict(sample)[0]

        try:
            probability = self.model.predict_proba(sample)[0, 1]
        except (AttributeError, IndexError):
            probability = None

        explanation = {
            "sample_idx": sample_idx,
            "prediction": int(prediction),
            "probability": float(probability) if probability is not None else None,
            "input_features": X.iloc[sample_idx].to_dict(),
        }

        logger.info(f"Explained prediction for sample {sample_idx}: {prediction}")

        return explanation
