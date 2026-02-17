"""
Advanced model implementations for TelecomAI plan classification.

Provides gradient boosting (XGBoost, LightGBM) and deep learning (PyTorch)
classifiers with a unified factory interface. All models are sklearn-compatible
to integrate with the existing Pipeline infrastructure.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency availability flags
# ---------------------------------------------------------------------------
try:
    import xgboost as xgb

    XGBOOST_AVAILABLE = True
except ImportError:  # pragma: no cover
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb

    LIGHTGBM_AVAILABLE = True
except ImportError:  # pragma: no cover
    LIGHTGBM_AVAILABLE = False

try:
    import torch
    import torch.nn as nn

    TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    TORCH_AVAILABLE = False


# ===================================================================
# XGBoost Classifier
# ===================================================================
def build_xgboost_classifier(params: Dict[str, Any] | None = None, seed: int = 42) -> Any:
    """Build an XGBoost classifier tuned for telecom plan classification."""
    if not XGBOOST_AVAILABLE:
        raise ImportError("xgboost is not installed. Install with: pip install xgboost")

    defaults = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "gamma": 0.1,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "scale_pos_weight": 1.0,
        "eval_metric": "logloss",
        "random_state": seed,
        "n_jobs": -1,
        "use_label_encoder": False,
    }
    if params:
        defaults.update(params)
    return xgb.XGBClassifier(**defaults)


# ===================================================================
# LightGBM Classifier
# ===================================================================
def build_lightgbm_classifier(params: Dict[str, Any] | None = None, seed: int = 42) -> Any:
    """Build a LightGBM classifier tuned for telecom plan classification."""
    if not LIGHTGBM_AVAILABLE:
        raise ImportError("lightgbm is not installed. Install with: pip install lightgbm")

    defaults = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "num_leaves": 15,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_samples": 20,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "is_unbalance": True,
        "random_state": seed,
        "n_jobs": -1,
        "verbose": -1,
    }
    if params:
        defaults.update(params)
    return lgb.LGBMClassifier(**defaults)


# ===================================================================
# PyTorch Tabular Classifier
# ===================================================================
if TORCH_AVAILABLE:  # pragma: no cover

    class _TelecomNet(nn.Module):
        """Compact feed-forward network for telecom plan classification.

        Designed for small-dimensional input (4 features).
        """

        def __init__(self, input_dim: int, hidden_dims: List[int] | None = None, dropout: float = 0.2):
            super().__init__()
            if hidden_dims is None:
                hidden_dims = [64, 32, 16]

            layers: list[nn.Module] = [nn.BatchNorm1d(input_dim)]
            prev_dim = input_dim
            for i, h_dim in enumerate(hidden_dims):
                layers.append(nn.Linear(prev_dim, h_dim))
                layers.append(nn.ReLU())
                drop_rate = max(dropout - i * 0.05, 0.05)
                layers.append(nn.Dropout(drop_rate))
                prev_dim = h_dim
            layers.append(nn.Linear(prev_dim, 2))

            self.network = nn.Sequential(*layers)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.network(x)

    class TorchTabularClassifier(BaseEstimator, ClassifierMixin):
        """Sklearn-compatible PyTorch classifier for telecom plan prediction.

        Parameters
        ----------
        hidden_dims : list[int]
            Hidden layer dimensions.
        lr : float
            Learning rate.
        epochs : int
            Number of training epochs.
        batch_size : int
            Mini-batch size.
        dropout : float
            Base dropout rate.
        weight_decay : float
            L2 regularization.
        early_stopping_patience : int
            Early stopping patience.
        class_weight : str or None
            If 'balanced', compute class weights from training data.
        random_state : int
            Random seed.
        verbose : bool
            Print training progress.
        """

        def __init__(
            self,
            hidden_dims: List[int] | None = None,
            lr: float = 1e-3,
            epochs: int = 80,
            batch_size: int = 128,
            dropout: float = 0.2,
            weight_decay: float = 1e-4,
            early_stopping_patience: int = 10,
            class_weight: str | None = "balanced",
            random_state: int = 42,
            verbose: bool = False,
        ):
            self.hidden_dims = hidden_dims or [64, 32, 16]
            self.lr = lr
            self.epochs = epochs
            self.batch_size = batch_size
            self.dropout = dropout
            self.weight_decay = weight_decay
            self.early_stopping_patience = early_stopping_patience
            self.class_weight = class_weight
            self.random_state = random_state
            self.verbose = verbose
            self.classes_ = np.array([0, 1])
            self.model_: _TelecomNet | None = None
            self.device_ = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        def fit(self, X: np.ndarray, y: np.ndarray) -> "TorchTabularClassifier":
            torch.manual_seed(self.random_state)
            np.random.seed(self.random_state)

            X_t = torch.tensor(np.asarray(X, dtype=np.float32))
            y_t = torch.tensor(np.asarray(y, dtype=np.int64))

            self.classes_ = np.unique(y)
            input_dim = X_t.shape[1]
            self.model_ = _TelecomNet(input_dim, self.hidden_dims, self.dropout).to(self.device_)

            if self.class_weight == "balanced":
                class_counts = np.bincount(y.astype(int))
                weights = torch.tensor(len(y) / (len(self.classes_) * class_counts), dtype=torch.float32).to(
                    self.device_
                )
            else:
                weights = None

            criterion = nn.CrossEntropyLoss(weight=weights)
            optimizer = torch.optim.AdamW(self.model_.parameters(), lr=self.lr, weight_decay=self.weight_decay)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=5)

            n = len(X_t)
            val_size = max(int(n * 0.1), 1)
            indices = torch.randperm(n)
            train_idx, val_idx = indices[val_size:], indices[:val_size]

            best_val_loss = float("inf")
            patience_counter = 0
            best_state = None

            dataset = torch.utils.data.TensorDataset(X_t[train_idx], y_t[train_idx])
            loader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

            self.model_.train()
            for epoch in range(self.epochs):
                epoch_loss = 0.0
                for batch_X, batch_y in loader:
                    batch_X, batch_y = batch_X.to(self.device_), batch_y.to(self.device_)
                    optimizer.zero_grad()
                    logits = self.model_(batch_X)
                    loss = criterion(logits, batch_y)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model_.parameters(), max_norm=1.0)
                    optimizer.step()
                    epoch_loss += loss.item()

                self.model_.eval()
                with torch.no_grad():
                    val_logits = self.model_(X_t[val_idx].to(self.device_))
                    val_loss = criterion(val_logits, y_t[val_idx].to(self.device_)).item()
                self.model_.train()

                scheduler.step(val_loss)

                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                    best_state = {k: v.cpu().clone() for k, v in self.model_.state_dict().items()}
                else:
                    patience_counter += 1

                if self.verbose and epoch % 10 == 0:
                    logger.info(
                        f"Epoch {epoch}/{self.epochs} - loss: {epoch_loss/len(loader):.4f} - "
                        f"val_loss: {val_loss:.4f}"
                    )

                if patience_counter >= self.early_stopping_patience:
                    if self.verbose:
                        logger.info(f"Early stopping at epoch {epoch}")
                    break

            if best_state is not None:
                self.model_.load_state_dict(best_state)

            self.model_.eval()
            return self

        def predict_proba(self, X: np.ndarray) -> np.ndarray:
            if self.model_ is None:
                raise RuntimeError("Model not fitted. Call fit() first.")
            self.model_.eval()
            X_t = torch.tensor(np.asarray(X, dtype=np.float32)).to(self.device_)
            with torch.no_grad():
                logits = self.model_(X_t)
                proba = torch.softmax(logits, dim=1).cpu().numpy()
            return proba

        def predict(self, X: np.ndarray) -> np.ndarray:
            proba = self.predict_proba(X)
            return self.classes_[np.argmax(proba, axis=1)]


# ===================================================================
# Model Factory
# ===================================================================
AVAILABLE_MODELS = {
    "gradient_boosting": "sklearn",
    "random_forest": "sklearn",
    "logistic_regression": "sklearn",
    "mlp": "sklearn",
    "xgboost": "xgboost",
    "lightgbm": "lightgbm",
    "neural_network": "torch",
}


def build_model(
    model_name: str,
    params: Dict[str, Any] | None = None,
    seed: int = 42,
) -> BaseEstimator:
    """Factory function to build any supported classification model.

    Parameters
    ----------
    model_name : str
        One of: 'gradient_boosting', 'random_forest', 'logistic_regression',
        'mlp', 'xgboost', 'lightgbm', 'neural_network'.
    params : dict, optional
        Model-specific hyperparameters.
    seed : int
        Random seed.

    Returns
    -------
    sklearn-compatible estimator
    """
    params = params or {}

    if model_name == "gradient_boosting":
        defaults = {
            "n_estimators": 200,
            "max_depth": 2,
            "learning_rate": 0.05,
            "random_state": seed,
        }
        defaults.update(params)
        return GradientBoostingClassifier(**defaults)

    elif model_name == "random_forest":
        defaults = {
            "n_estimators": 200,
            "max_depth": 10,
            "min_samples_leaf": 5,
            "class_weight": "balanced",
            "random_state": seed,
            "n_jobs": -1,
        }
        defaults.update(params)
        return RandomForestClassifier(**defaults)

    elif model_name == "logistic_regression":
        defaults = {"max_iter": 1000, "random_state": seed, "class_weight": "balanced"}
        defaults.update(params)
        return LogisticRegression(**defaults)

    elif model_name == "mlp":
        defaults = {
            "hidden_layer_sizes": (128, 64, 32),
            "activation": "relu",
            "solver": "adam",
            "alpha": 1e-4,
            "learning_rate_init": 1e-3,
            "max_iter": 500,
            "early_stopping": True,
            "n_iter_no_change": 20,
            "random_state": seed,
        }
        defaults.update(params)
        return MLPClassifier(**defaults)

    elif model_name == "xgboost":
        return build_xgboost_classifier(params, seed)

    elif model_name == "lightgbm":
        return build_lightgbm_classifier(params, seed)

    elif model_name == "neural_network":
        if not TORCH_AVAILABLE:
            raise ImportError("torch is not installed. Install with: pip install torch")
        return TorchTabularClassifier(random_state=seed, **params)

    else:
        raise ValueError(f"Unknown model: '{model_name}'. Available: {list(AVAILABLE_MODELS.keys())}")


def get_available_models() -> Dict[str, bool]:
    """Return availability status of each model type."""
    return {
        "gradient_boosting": True,
        "random_forest": True,
        "logistic_regression": True,
        "mlp": True,
        "xgboost": XGBOOST_AVAILABLE,
        "lightgbm": LIGHTGBM_AVAILABLE,
        "neural_network": TORCH_AVAILABLE,
    }
