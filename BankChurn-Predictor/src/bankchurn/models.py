"""Machine learning models for churn prediction.

This module contains custom classifiers and model wrappers for handling
imbalanced datasets and ensemble methods.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_is_fitted

logger = logging.getLogger(__name__)


class ResampleClassifier(BaseEstimator, ClassifierMixin):
    """Custom classifier with resampling for imbalanced datasets.

    Implements oversampling (SMOTE), undersampling, and class weighting
    to improve performance on imbalanced classification tasks.

    Parameters
    ----------
    estimator : estimator object, optional
        Base classifier to wrap. If None, uses LogisticRegression.
    strategy : {"none", "oversample", "undersample", "class_weight"}, default="none"
        Resampling strategy to apply:
        - "none": No resampling
        - "oversample": SMOTE oversampling of minority class
        - "undersample": Random undersampling of majority class
        - "class_weight": Automatic class weight balancing
    random_state : int, default=42
        Random seed for reproducibility.

    Attributes
    ----------
    classes_ : ndarray of shape (n_classes,)
        Unique class labels.
    estimator_ : estimator object
        Fitted base estimator.

    Examples
    --------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> clf = ResampleClassifier(
    ...     estimator=RandomForestClassifier(),
    ...     strategy="oversample",
    ...     random_state=42
    ... )
    >>> clf.fit(X_train, y_train)
    >>> predictions = clf.predict(X_test)
    """

    def __init__(
        self,
        estimator: BaseEstimator | None = None,
        strategy: str = "none",
        random_state: int = 42,
    ) -> None:
        self.estimator = estimator
        self.strategy = strategy
        self.random_state = random_state

    def fit(self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray) -> ResampleClassifier:
        """Fit the classifier with optional resampling.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.

        Returns
        -------
        self : ResampleClassifier
            Fitted estimator.
        """
        from sklearn.linear_model import LogisticRegression

        # Initialize base estimator if not provided
        if self.estimator is None:
            self.estimator_ = LogisticRegression(random_state=self.random_state)
        else:
            self.estimator_ = self.estimator

        # Store classes
        self.classes_ = np.unique(y)

        # Apply resampling strategy
        X_resampled, y_resampled = self._apply_resampling(X, y)

        # Fit base estimator
        self.estimator_.fit(X_resampled, y_resampled)

        logger.info(
            f"ResampleClassifier fitted with strategy='{self.strategy}' "
            f"(original samples: {len(y)}, resampled: {len(y_resampled)})"
        )

        return self

    def predict(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict class labels.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples to predict.

        Returns
        -------
        y_pred : ndarray of shape (n_samples,)
            Predicted class labels.
        """
        check_is_fitted(self, "estimator_")
        return self.estimator_.predict(X)

    def predict_proba(self, X: pd.DataFrame | np.ndarray) -> np.ndarray:
        """Predict class probabilities.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Samples to predict.

        Returns
        -------
        proba : ndarray of shape (n_samples, n_classes)
            Class probabilities.
        """
        check_is_fitted(self, "estimator_")
        return self.estimator_.predict_proba(X)

    def _apply_resampling(
        self, X: pd.DataFrame | np.ndarray, y: pd.Series | np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Apply the specified resampling strategy.

        Parameters
        ----------
        X : array-like
            Features.
        y : array-like
            Labels.

        Returns
        -------
        X_resampled : ndarray
            Resampled features.
        y_resampled : ndarray
            Resampled labels.
        """
        # Convert to numpy if pandas
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        if self.strategy == "none":
            return X, y

        elif self.strategy == "oversample":
            try:
                from imblearn.over_sampling import SMOTE

                smote = SMOTE(random_state=self.random_state)
                X_resampled, y_resampled = smote.fit_resample(X, y)
                return X_resampled, y_resampled
            except ImportError:
                logger.warning("imblearn not installed, falling back to no resampling")
                return X, y

        elif self.strategy == "undersample":
            try:
                from imblearn.under_sampling import RandomUnderSampler

                rus = RandomUnderSampler(random_state=self.random_state)
                X_resampled, y_resampled = rus.fit_resample(X, y)
                return X_resampled, y_resampled
            except ImportError:
                logger.warning("imblearn not installed, falling back to no resampling")
                return X, y

        elif self.strategy == "class_weight":
            # For class_weight, we don't resample, just pass through
            # The estimator should handle class_weight parameter
            return X, y

        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
