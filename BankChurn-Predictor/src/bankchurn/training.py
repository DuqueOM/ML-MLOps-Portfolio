"""Model training pipeline for churn prediction.

This module implements the complete training workflow including:
- Data loading and validation
- Feature preprocessing
- Model training with cross-validation
- Hyperparameter optimization with Optuna
- Model persistence and logging
"""

from __future__ import annotations

import logging
from pathlib import Path

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import BankChurnConfig
from .models import ResampleClassifier

logger = logging.getLogger(__name__)


class ChurnTrainer:
    """Training pipeline for churn prediction models.

    Parameters
    ----------
    config : BankChurnConfig
        Configuration object with all training parameters.
    random_state : int, optional
        Random seed for reproducibility.

    Attributes
    ----------
    model_ : Pipeline
        Fitted model pipeline.
    preprocessor_ : ColumnTransformer
        Fitted preprocessing pipeline.
    train_score_ : float
        Training set performance.
    test_score_ : float
        Test set performance.
    """

    def __init__(self, config: BankChurnConfig, random_state: int | None = None) -> None:
        self.config = config
        self.random_state = random_state or config.model.random_state
        self.model_: Pipeline | None = None
        self.preprocessor_: ColumnTransformer | None = None
        self.train_score_: float | None = None
        self.test_score_: float | None = None

        if self.config.mlflow.enabled:
            try:
                mlflow.set_tracking_uri(self.config.mlflow.tracking_uri)
                mlflow.set_experiment(self.config.mlflow.experiment_name)
                logger.info(f"MLflow tracking enabled: {self.config.mlflow.tracking_uri}")
            except Exception as e:
                logger.warning(f"Failed to configure MLflow: {e}")

    def load_data(self, input_path: str | Path) -> pd.DataFrame:
        """Load and validate input data.

        Parameters
        ----------
        input_path : str or Path
            Path to input CSV file.

        Returns
        -------
        data : DataFrame
            Loaded and validated data.

        Raises
        ------
        FileNotFoundError
            If input file doesn't exist.
        ValueError
            If required columns are missing.
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        data = pd.read_csv(input_path)
        logger.info(f"Loaded data: {data.shape[0]} rows, {data.shape[1]} columns")

        # Validate required columns
        required = [self.config.data.target_column]
        missing = set(required) - set(data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        return data

    def prepare_features(self, data: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target from raw data.

        Parameters
        ----------
        data : DataFrame
            Raw input data.

        Returns
        -------
        X : DataFrame
            Feature matrix.
        y : Series
            Target vector.
        """
        # Drop specified columns
        if self.config.data.drop_columns:
            data = data.drop(columns=self.config.data.drop_columns, errors="ignore")

        # Separate features and target
        y = data[self.config.data.target_column]
        X = data.drop(columns=[self.config.data.target_column])

        logger.info(f"Features: {X.shape[1]} columns, Target: {y.nunique()} classes")

        return X, y

    def build_preprocessor(self, X: pd.DataFrame) -> ColumnTransformer:
        """Build feature preprocessing pipeline.

        Parameters
        ----------
        X : DataFrame
            Feature matrix for schema detection.

        Returns
        -------
        preprocessor : ColumnTransformer
            Feature preprocessing pipeline.
        """
        # Auto-detect feature types if not specified. When explicit
        # feature lists are provided in the config, intersect them
        # with the actual columns in X to avoid errors if a column
        # is missing in a particular dataset or test DataFrame.
        if not self.config.data.categorical_features:
            categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()
        else:
            categorical_features = [col for col in self.config.data.categorical_features if col in X.columns]

        if not self.config.data.numerical_features:
            numerical_features = X.select_dtypes(include=[np.number]).columns.tolist()
        else:
            numerical_features = [col for col in self.config.data.numerical_features if col in X.columns]

        # If after filtering no features remain, fall back to
        # automatic type detection based on the actual DataFrame
        # dtypes. This makes the preprocessor robust for synthetic
        # test DataFrames that do not include the full set of
        # configured feature names.
        if not categorical_features and not numerical_features:
            categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()
            numerical_features = X.select_dtypes(include=[np.number]).columns.tolist()

        logger.info(f"Categorical features: {len(categorical_features)}")
        logger.info(f"Numerical features: {len(numerical_features)}")

        # Build transformer
        transformers = []

        if categorical_features:
            cat_pipeline = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
                    ("onehot", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")),
                ]
            )
            transformers.append(("cat", cat_pipeline, categorical_features))

        if numerical_features:
            num_pipeline = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )
            transformers.append(("num", num_pipeline, numerical_features))

        preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")

        return preprocessor

    def build_model(self) -> Pipeline:
        """Build ensemble model pipeline.

        Returns
        -------
        pipeline : Pipeline
            Complete model pipeline with preprocessing.
        """
        # Build ensemble
        lr_config = self.config.model.logistic_regression
        lr = LogisticRegression(
            C=lr_config.C,
            max_iter=lr_config.max_iter,
            class_weight=lr_config.class_weight,
            solver=lr_config.solver,
            random_state=self.random_state,
        )

        rf_config = self.config.model.random_forest
        rf = RandomForestClassifier(
            n_estimators=rf_config.n_estimators,
            max_depth=rf_config.max_depth,
            min_samples_split=rf_config.min_samples_split,
            min_samples_leaf=rf_config.min_samples_leaf,
            class_weight=rf_config.class_weight,
            random_state=self.random_state,
            n_jobs=rf_config.n_jobs,
        )

        ensemble = VotingClassifier(
            estimators=[("lr", lr), ("rf", rf)],
            voting=self.config.model.ensemble.voting,
            weights=self.config.model.ensemble.weights,
        )

        # Wrap in resample classifier if needed
        model = ResampleClassifier(
            estimator=ensemble,
            strategy=self.config.model.resampling_strategy,
            random_state=self.random_state,
        )

        return model

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        use_cv: bool = True,
    ) -> tuple[Pipeline, dict[str, float]]:
        """Train the model with optional cross-validation.

        Parameters
        ----------
        X : DataFrame
            Feature matrix.
        y : Series
            Target vector.
        use_cv : bool, default=True
            Whether to use cross-validation.

        Returns
        -------
        model : Pipeline
            Fitted model.
        metrics : dict
            Training metrics.
        """
        # Split data
        # CRITICAL: Split BEFORE fitting preprocessor to avoid data leakage
        # We split the raw data first
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=self.config.model.test_size,
            random_state=self.random_state,
            stratify=y,
        )

        # Build preprocessor based on training data only
        self.preprocessor_ = self.build_preprocessor(X_train)

        # Fit preprocessor on TRAIN, transform both
        X_train = self.preprocessor_.fit_transform(X_train)
        X_test = self.preprocessor_.transform(X_test)

        logger.info(f"Train: {X_train.shape[0]} samples, Test: {X_test.shape[0]} samples")

        # Build and train model
        self.model_ = self.build_model()

        if use_cv:
            # Cross-validation
            cv = StratifiedKFold(n_splits=self.config.model.cv_folds, shuffle=True, random_state=self.random_state)

            cv_scores = []
            for fold, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train), 1):
                X_fold_train = X_train[train_idx]
                y_fold_train = y_train.iloc[train_idx]
                X_fold_val = X_train[val_idx]
                y_fold_val = y_train.iloc[val_idx]

                fold_model = self.build_model()
                fold_model.fit(X_fold_train, y_fold_train)

                y_pred = fold_model.predict(X_fold_val)
                fold_f1 = f1_score(y_fold_val, y_pred, average="weighted")
                cv_scores.append(fold_f1)

                logger.info(f"Fold {fold}/{self.config.model.cv_folds}: F1 = {fold_f1:.4f}")

            logger.info(f"CV Mean F1: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores):.4f})")

        # Final training on full train set
        assert self.model_ is not None
        self.model_.fit(X_train, y_train)

        # Evaluate
        y_train_pred = self.model_.predict(X_train)
        y_test_pred = self.model_.predict(X_test)

        self.train_score_ = f1_score(y_train, y_train_pred, average="weighted")
        self.test_score_ = f1_score(y_test, y_test_pred, average="weighted")

        # AUC if probability available
        try:
            assert self.model_ is not None
            y_test_proba = self.model_.predict_proba(X_test)[:, 1]
            test_auc = roc_auc_score(y_test, y_test_proba)
        except Exception:
            test_auc = None

        metrics = {
            "train_f1": self.train_score_,
            "test_f1": self.test_score_,
            "test_auc": test_auc,
        }

        logger.info(f"Training complete - Train F1: {self.train_score_:.4f}, Test F1: {self.test_score_:.4f}")

        if self.config.mlflow.enabled:
            with mlflow.start_run():
                # Log parameters
                mlflow.log_params(self.config.model.dict())
                mlflow.log_params(self.config.data.dict())

                # Log metrics
                mlflow.log_metrics(metrics)

                # Log model (optional, might be large)
                # mlflow.sklearn.log_model(self.model_, "model")
                logger.info("Logged params and metrics to MLflow")

        return self.model_, metrics

    def save_model(self, model_path: str | Path, preprocessor_path: str | Path | None = None) -> None:
        """Save trained model and preprocessor to disk.

        Parameters
        ----------
        model_path : str or Path
            Path to save model (full pipeline).
        preprocessor_path : str or Path, optional
            Path to save preprocessor (kept for compatibility, but model_path contains full pipeline).
        """
        if self.model_ is None or self.preprocessor_ is None:
            raise ValueError("Model and preprocessor must be trained before saving")

        model_path = Path(model_path)

        # Create full pipeline
        full_pipeline = Pipeline([("preprocessor", self.preprocessor_), ("classifier", self.model_)])

        # Create directories
        model_path.parent.mkdir(parents=True, exist_ok=True)

        # Save full pipeline
        joblib.dump(full_pipeline, model_path)
        logger.info(f"Full pipeline saved to {model_path}")

        # Optionally save preprocessor separately if requested (for backward compat or debugging)
        if preprocessor_path:
            preprocessor_path = Path(preprocessor_path)
            preprocessor_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.preprocessor_, preprocessor_path)
            logger.info(f"Preprocessor saved to {preprocessor_path}")
