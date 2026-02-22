"""
Advanced model implementations for CarVision price prediction.

Provides gradient boosting (XGBoost, LightGBM) and deep learning (PyTorch)
regressors with a unified factory interface. All models are sklearn-compatible
to integrate with the existing Pipeline infrastructure.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor

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
# XGBoost Regressor
# ===================================================================
def build_xgboost_regressor(params: Dict[str, Any] | None = None, seed: int = 42) -> Any:
    """Build an XGBoost regressor with defaults tuned for vehicle pricing."""
    if not XGBOOST_AVAILABLE:
        raise ImportError("xgboost is not installed. Install with: pip install xgboost")

    defaults = {
        "n_estimators": 500,
        "max_depth": 8,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "gamma": 0.1,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "random_state": seed,
        "n_jobs": -1,
    }
    if params:
        defaults.update(params)
    return xgb.XGBRegressor(**defaults)


# ===================================================================
# LightGBM Regressor
# ===================================================================
def build_lightgbm_regressor(params: Dict[str, Any] | None = None, seed: int = 42) -> Any:
    """Build a LightGBM regressor with defaults tuned for vehicle pricing."""
    if not LIGHTGBM_AVAILABLE:
        raise ImportError("lightgbm is not installed. Install with: pip install lightgbm")

    defaults = {
        "n_estimators": 500,
        "max_depth": 8,
        "learning_rate": 0.05,
        "num_leaves": 63,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_samples": 20,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "random_state": seed,
        "n_jobs": -1,
        "verbose": -1,
    }
    if params:
        defaults.update(params)
    return lgb.LGBMRegressor(**defaults)


# ===================================================================
# PyTorch Regression Network
# ===================================================================
if TORCH_AVAILABLE:  # pragma: no cover

    class _PriceNet(nn.Module):
        """Feed-forward regression network for vehicle price prediction.

        Architecture
        ------------
        Input → BatchNorm → Linear(d,256) → ReLU → Dropout
              → Linear(256,128) → ReLU → Dropout
              → Linear(128,64)  → ReLU → Dropout
              → Linear(64,1)    → output
        """

        def __init__(self, input_dim: int, hidden_dims: List[int] | None = None, dropout: float = 0.3):
            super().__init__()
            if hidden_dims is None:
                hidden_dims = [256, 128, 64]

            layers: list[nn.Module] = [nn.BatchNorm1d(input_dim)]
            prev_dim = input_dim
            for i, h_dim in enumerate(hidden_dims):
                layers.append(nn.Linear(prev_dim, h_dim))
                layers.append(nn.ReLU())
                drop_rate = max(dropout - i * 0.1, 0.05)
                layers.append(nn.Dropout(drop_rate))
                prev_dim = h_dim
            layers.append(nn.Linear(prev_dim, 1))

            self.network = nn.Sequential(*layers)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.network(x).squeeze(-1)

    class TorchTabularRegressor(BaseEstimator, RegressorMixin):
        """Sklearn-compatible wrapper for PyTorch tabular regressor.

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
            Stop training if val loss does not improve for this many epochs.
        random_state : int
            Random seed.
        verbose : bool
            Print training progress.
        """

        def __init__(
            self,
            hidden_dims: List[int] | None = None,
            lr: float = 1e-3,
            epochs: int = 100,
            batch_size: int = 256,
            dropout: float = 0.3,
            weight_decay: float = 1e-4,
            early_stopping_patience: int = 10,
            random_state: int = 42,
            verbose: bool = False,
        ):
            self.hidden_dims = hidden_dims or [256, 128, 64]
            self.lr = lr
            self.epochs = epochs
            self.batch_size = batch_size
            self.dropout = dropout
            self.weight_decay = weight_decay
            self.early_stopping_patience = early_stopping_patience
            self.random_state = random_state
            self.verbose = verbose
            self.model_: _PriceNet | None = None
            self.device_ = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.y_mean_: float = 0.0
            self.y_std_: float = 1.0

        def fit(self, X: np.ndarray, y: np.ndarray) -> "TorchTabularRegressor":
            torch.manual_seed(self.random_state)
            np.random.seed(self.random_state)

            # Normalize target for stable training
            self.y_mean_ = float(np.mean(y))
            self.y_std_ = float(np.std(y)) + 1e-8
            y_norm = (np.asarray(y, dtype=np.float32) - self.y_mean_) / self.y_std_

            X_t = torch.tensor(np.asarray(X, dtype=np.float32))
            y_t = torch.tensor(y_norm, dtype=torch.float32)

            input_dim = X_t.shape[1]
            self.model_ = _PriceNet(input_dim, self.hidden_dims, self.dropout).to(self.device_)

            criterion = nn.MSELoss()
            optimizer = torch.optim.AdamW(self.model_.parameters(), lr=self.lr, weight_decay=self.weight_decay)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=5)

            # Train/val split for early stopping
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
                    batch_X = batch_X.to(self.device_)
                    batch_y = batch_y.to(self.device_)
                    optimizer.zero_grad()
                    preds = self.model_(batch_X)
                    loss = criterion(preds, batch_y)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model_.parameters(), max_norm=1.0)
                    optimizer.step()
                    epoch_loss += loss.item()

                # Validation
                self.model_.eval()
                with torch.no_grad():
                    val_preds = self.model_(X_t[val_idx].to(self.device_))
                    val_loss = criterion(val_preds, y_t[val_idx].to(self.device_)).item()
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

        def predict(self, X: np.ndarray) -> np.ndarray:
            if self.model_ is None:
                raise RuntimeError("Model not fitted. Call fit() first.")

            self.model_.eval()
            X_t = torch.tensor(np.asarray(X, dtype=np.float32)).to(self.device_)

            with torch.no_grad():
                preds = self.model_(X_t).cpu().numpy()

            # Denormalize
            return preds * self.y_std_ + self.y_mean_


# ===================================================================
# Model Factory
# ===================================================================
AVAILABLE_MODELS = {
    "random_forest": "sklearn",
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
    """Factory function to build any supported regression model.

    Parameters
    ----------
    model_name : str
        One of: 'random_forest', 'xgboost', 'lightgbm', 'neural_network'.
    params : dict, optional
        Model-specific hyperparameters.
    seed : int
        Random seed.

    Returns
    -------
    sklearn-compatible estimator
    """
    params = params or {}

    if model_name == "random_forest":
        defaults = {
            "n_estimators": 300,
            "max_depth": 12,
            "min_samples_leaf": 2,
            "random_state": seed,
            "n_jobs": -1,
        }
        defaults.update(params)
        return RandomForestRegressor(**defaults)

    elif model_name == "mlp":
        defaults = {
            "hidden_layer_sizes": (256, 128, 64),
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
        return MLPRegressor(**defaults)

    elif model_name == "xgboost":
        return build_xgboost_regressor(params, seed)

    elif model_name == "lightgbm":
        return build_lightgbm_regressor(params, seed)

    elif model_name == "neural_network":
        if not TORCH_AVAILABLE:
            raise ImportError("torch is not installed. Install with: pip install torch")
        nn_params = {k: v for k, v in params.items() if k != "random_state"}
        return TorchTabularRegressor(random_state=seed, **nn_params)

    else:
        raise ValueError(f"Unknown model: '{model_name}'. Available: {list(AVAILABLE_MODELS.keys())}")


def get_available_models() -> Dict[str, bool]:
    """Return availability status of each model type."""
    return {
        "random_forest": True,
        "mlp": True,
        "xgboost": XGBOOST_AVAILABLE,
        "lightgbm": LIGHTGBM_AVAILABLE,
        "neural_network": TORCH_AVAILABLE,
    }
