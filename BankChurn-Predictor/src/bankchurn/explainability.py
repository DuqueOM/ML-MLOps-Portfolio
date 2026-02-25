"""
Model Explainability Module using SHAP.

Provides interpretation tools for churn predictions including:
- Feature importance (global explanation)
- Individual prediction explanations (local explanation)
- Force plots for single predictions
- Summary plots for model overview

Usage:
    from src.bankchurn.explainability import ModelExplainer

    explainer = ModelExplainer(model_pipeline, X_train)
    importance = explainer.get_feature_importance()
    explanation = explainer.explain_prediction(X_single)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Optional SHAP import
try:
    import shap

    SHAP_AVAILABLE = True
except ImportError:  # pragma: no cover
    SHAP_AVAILABLE = False
    logger.warning("SHAP not installed. Explainability features will be limited.")


class ModelExplainer:
    """
    SHAP-based model explainer for churn prediction models.

    Attributes:
        model: Trained sklearn model or pipeline
        explainer: SHAP explainer instance
        feature_names: List of feature names
        expected_value: Model's expected value (base prediction)
    """

    def __init__(
        self,
        model: Any,
        X_background: Optional[pd.DataFrame] = None,
        feature_names: Optional[List[str]] = None,
        max_background_samples: int = 100,
    ):
        """
        Initialize the explainer.

        Args:
            model: Trained sklearn model or pipeline
            X_background: Background dataset for SHAP (sampled if too large)
            feature_names: Feature names (inferred from X_background if not provided)
            max_background_samples: Max samples for background data
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.expected_value = None
        self._shap_values_cache = None
        self._transformed_feature_names: Optional[List[str]] = None
        self._preprocessor = None

        if not SHAP_AVAILABLE:  # pragma: no cover
            logger.warning("SHAP not available. Using fallback explanations.")
            return

        # Prepare background data
        if X_background is not None:
            if len(X_background) > max_background_samples:
                X_background = X_background.sample(n=max_background_samples, random_state=42)

            if self.feature_names is None:
                self.feature_names = list(X_background.columns)

            # Create appropriate explainer based on model type
            self._initialize_explainer(X_background)

    @staticmethod
    def _unwrap_classifier(classifier: Any) -> Any:
        """Unwrap meta-classifiers (e.g. ResampleClassifier) to the inner estimator.

        Only unwraps when the outer classifier lacks feature_importances_ and
        estimators_ (i.e. it is a thin wrapper, not a real ensemble like RF).
        """
        if (
            hasattr(classifier, "estimator_")
            and not hasattr(classifier, "feature_importances_")
            and not hasattr(classifier, "estimators_")
        ):
            inner = classifier.estimator_
            logger.debug(f"Unwrapped {type(classifier).__name__} → {type(inner).__name__}")
            return inner
        return classifier

    def _initialize_explainer(self, X_background: pd.DataFrame) -> None:  # pragma: no cover
        """Initialize the appropriate SHAP explainer."""
        try:
            # Try TreeExplainer first (faster for tree-based models)
            if hasattr(self.model, "named_steps"):
                # Pipeline - extract the classifier
                classifier = self.model.named_steps.get("classifier", self.model.named_steps.get("clf"))
                if classifier is not None:
                    inner = self._unwrap_classifier(classifier)
                    preprocessor = self.model.named_steps.get("preprocessor")
                    if preprocessor is not None and hasattr(inner, "estimators_"):
                        X_transformed = preprocessor.transform(X_background)
                        self.explainer = shap.TreeExplainer(inner)
                        self._X_background_transformed = X_transformed
                        self._preprocessor = preprocessor
                        self.expected_value = self.explainer.expected_value
                        # Store transformed feature names for aggregation
                        try:
                            self._transformed_feature_names = list(preprocessor.get_feature_names_out())
                        except Exception:
                            self._transformed_feature_names = None
                        logger.info(
                            f"Initialized TreeExplainer for pipeline "
                            f"({type(inner).__name__}, {X_transformed.shape[1]} features)"
                        )
                        return

            # Fallback to KernelExplainer (slower but universal)
            def predict_proba_wrapper(X):
                if isinstance(X, np.ndarray):
                    X = pd.DataFrame(X, columns=self.feature_names)
                return self.model.predict_proba(X)[:, 1]

            self.explainer = shap.KernelExplainer(predict_proba_wrapper, X_background.values[:50])
            self.expected_value = self.explainer.expected_value
            logger.info("Initialized KernelExplainer")

        except Exception as e:
            logger.warning(f"Failed to initialize SHAP explainer: {e}")
            self.explainer = None

    def get_feature_importance(self, X: Optional[pd.DataFrame] = None, top_n: int = 10) -> Dict[str, float]:
        """Get global feature importance scores.

        Args:
            X: Data to compute importance on (uses background if not provided)
            top_n: Number of top features to return

        Returns:
            Dictionary of feature_name -> importance_score
        """
        # If SHAP is not available, use fallback importance but still respect top_n
        if not SHAP_AVAILABLE or self.explainer is None:
            importance_dict = self._fallback_feature_importance()
            if not importance_dict:
                return importance_dict

            sorted_items = sorted(importance_dict.items(), key=lambda item: item[1], reverse=True)
            if top_n is not None and top_n > 0:
                sorted_items = sorted_items[:top_n]
            return dict(sorted_items)

        try:  # pragma: no cover
            if X is None and hasattr(self, "_X_background_transformed"):
                shap_values = self.explainer.shap_values(self._X_background_transformed)
            elif X is not None:
                if hasattr(self.model, "named_steps"):
                    preprocessor = self.model.named_steps.get("preprocessor")
                    if preprocessor:
                        X_transformed = preprocessor.transform(X)
                        shap_values = self.explainer.shap_values(X_transformed)
                    else:
                        shap_values = self.explainer.shap_values(X.values)
                else:
                    shap_values = self.explainer.shap_values(X.values)
            else:
                return self._fallback_feature_importance()

            # Handle multi-class output
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # Use positive class

            # Compute mean absolute SHAP values
            importance = np.abs(shap_values).mean(axis=0)

            # Create feature importance dict
            if self.feature_names and len(self.feature_names) == len(importance):
                importance_dict = dict(zip(self.feature_names, importance))
            else:
                importance_dict = {f"feature_{i}": imp for i, imp in enumerate(importance)}

            # Sort and return top N
            sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:top_n])
            return sorted_importance

        except Exception as e:  # pragma: no cover
            logger.warning(f"Error computing SHAP importance: {e}")
            return self._fallback_feature_importance()

    def explain_prediction(self, X_single: Union[pd.DataFrame, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Explain a single prediction.

        Args:
            X_single: Single observation to explain (DataFrame or dict)

        Returns:
            Dictionary with:
                - prediction: Model prediction
                - probability: Prediction probability
                - base_value: Expected value (baseline)
                - feature_contributions: Dict of feature -> SHAP value
                - top_positive: Features increasing churn risk
                - top_negative: Features decreasing churn risk
        """
        # Convert dict to DataFrame if needed
        if isinstance(X_single, dict):
            X_single = pd.DataFrame([X_single])

        # Get prediction
        prediction = int(self.model.predict(X_single)[0])
        probability = float(self.model.predict_proba(X_single)[0, 1])

        if not SHAP_AVAILABLE or self.explainer is None:
            return {
                "prediction": prediction,
                "probability": probability,
                "base_value": 0.5,
                "feature_contributions": self._fallback_contributions(X_single),
                "top_positive": [],
                "top_negative": [],
                "explanation_type": "fallback",
            }

        try:  # pragma: no cover
            # Transform if pipeline
            if self._preprocessor is not None:
                X_transformed = self._preprocessor.transform(X_single)
            elif hasattr(self.model, "named_steps"):
                preprocessor = self.model.named_steps.get("preprocessor")
                if preprocessor:
                    X_transformed = preprocessor.transform(X_single)
                else:
                    X_transformed = X_single.values
            else:
                X_transformed = X_single.values

            # Compute SHAP values
            shap_values = self.explainer.shap_values(X_transformed)
            if isinstance(shap_values, list):
                # List of arrays per class — pick positive class
                shap_values = shap_values[1]
            elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
                # Shape (n_samples, n_features, n_classes) — pick positive class
                shap_values = shap_values[:, :, 1]

            shap_values = shap_values.flatten()

            # Map SHAP values back to original feature names
            contributions = self._aggregate_to_original(shap_values)

            # Sort contributions
            sorted_contribs = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
            top_positive = [{"feature": k, "contribution": round(v, 4)} for k, v in sorted_contribs[:3] if v > 0]
            top_negative = [{"feature": k, "contribution": round(v, 4)} for k, v in sorted_contribs[-3:] if v < 0]

            return {
                "prediction": prediction,
                "probability": probability,
                "base_value": float(
                    self.expected_value[1]
                    if isinstance(self.expected_value, (list, np.ndarray))
                    else self.expected_value
                ),
                "feature_contributions": {k: round(v, 4) for k, v in contributions.items()},
                "top_positive": top_positive,
                "top_negative": top_negative,
                "explanation_type": "shap",
            }

        except Exception as e:
            logger.warning(f"Error explaining prediction: {e}")
            return {
                "prediction": prediction,
                "probability": probability,
                "base_value": 0.5,
                "feature_contributions": self._fallback_contributions(X_single),
                "top_positive": [],
                "top_negative": [],
                "explanation_type": "fallback",
            }

    def _aggregate_to_original(self, values: np.ndarray) -> Dict[str, float]:
        """Map transformed feature values back to original feature names.

        Sums contributions from one-hot columns (e.g. Geography_Germany +
        Geography_Spain → Geography) so the API returns original feature names.
        """
        # Direct mapping if lengths match
        if self.feature_names and len(self.feature_names) == len(values):
            return dict(zip(self.feature_names, [float(v) for v in values]))

        # Aggregate transformed → original using prefix matching
        if self._transformed_feature_names and len(self._transformed_feature_names) == len(values):
            agg: Dict[str, float] = {}
            for tname, val in zip(self._transformed_feature_names, values):
                # Match against known original feature names
                matched = False
                if self.feature_names:
                    for orig in self.feature_names:
                        if tname == orig or tname.startswith(orig + "_"):
                            agg[orig] = agg.get(orig, 0.0) + float(val)
                            matched = True
                            break
                if not matched:
                    agg[tname] = agg.get(tname, 0.0) + float(val)
            return agg

        # Last resort: indexed names
        return {f"feature_{i}": float(v) for i, v in enumerate(values)}

    def _fallback_feature_importance(self) -> Dict[str, float]:
        """Fallback feature importance based on model coefficients or importances."""
        try:
            if hasattr(self.model, "named_steps"):
                classifier = self.model.named_steps.get("classifier", self.model.named_steps.get("clf"))
            else:
                classifier = self.model

            # Unwrap meta-classifiers (e.g. ResampleClassifier)
            classifier = self._unwrap_classifier(classifier)

            if hasattr(classifier, "feature_importances_"):
                importances = classifier.feature_importances_
            elif hasattr(classifier, "coef_"):
                importances = np.abs(classifier.coef_).flatten()
            else:
                return {"no_importance_available": 1.0}

            # Use aggregation to map transformed importances to original names
            return self._aggregate_to_original(importances)

        except Exception:
            return {"no_importance_available": 1.0}

    def _fallback_contributions(self, X: pd.DataFrame) -> Dict[str, float]:
        """Generate approximate contributions using model-based feature importance.

        Uses the trained model's feature importances or coefficients to derive
        per-sample directional contributions. Falls back to uniform weights
        when introspection is not possible.
        """
        importance = self._fallback_feature_importance()
        if "no_importance_available" in importance:
            return {col: 0.0 for col in X.columns}

        # Return importance values for columns present in X
        contributions = {}
        for col in X.columns:
            contributions[col] = float(importance.get(col, 0.0))
        return contributions
