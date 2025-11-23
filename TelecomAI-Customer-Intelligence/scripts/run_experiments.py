from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# Asegurar que el root del proyecto está en sys.path para imports relativos
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.preprocess import build_preprocessor, get_features_target, load_dataset  # noqa: E402
from evaluate import compute_classification_metrics  # noqa: E402
from main import Config, build_model, load_config  # noqa: E402
from sklearn.model_selection import ParameterSampler, train_test_split  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402


def _get_search_space() -> Dict[str, Dict[str, List[Any]]]:
    """Define un espacio pequeño pero razonable de hiperparámetros por modelo.

    Este espacio está pensado para demos (no para producción),
    manteniendo un número reducido de combinaciones.
    """

    return {
        "logreg": {
            "C": [0.1, 1.0, 10.0],
            "penalty": ["l2"],
            "solver": ["liblinear"],
            "class_weight": ["balanced"],
        },
        "random_forest": {
            "n_estimators": [200, 400],
            "max_depth": [None, 10],
            "min_samples_leaf": [1, 2],
            "class_weight": ["balanced"],
            "n_jobs": [-1],
        },
        "gradient_boosting": {
            "n_estimators": [100, 200],
            "learning_rate": [0.05, 0.1],
            "max_depth": [2, 3],
        },
    }


def run_experiments(config_path: str, n_iter: int, seed: int) -> None:
    """Ejecuta una búsqueda aleatoria simple sobre varios modelos.

    Cada combinación (modelo + hiperparámetros) se entrena, evalúa y se
    logea como un run en MLflow (si está disponible).
    """

    cfg: Config = load_config(config_path)

    df = load_dataset(cfg.paths["data_csv"])
    X, y = get_features_target(df, cfg.features, cfg.target)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=float(cfg.split.get("test_size", 0.2)),
        stratify=y if cfg.split.get("stratify", True) else None,
        random_state=int(seed),
    )

    preprocessor = build_preprocessor(cfg.features)
    search_space = _get_search_space()

    # Importar MLflow de forma segura dentro de la función para evitar problemas de ámbito
    mlflow_client = None
    use_mlflow = False
    if cfg.mlflow is not None:
        try:  # pragma: no cover - fallo en MLflow no debe romper los experimentos
            import mlflow  # type: ignore
            import mlflow.sklearn  # type: ignore  # noqa: F401

            mlflow_client = mlflow  # type: ignore
            use_mlflow = True
        except Exception:
            mlflow_client = None
            use_mlflow = False

    if use_mlflow and mlflow_client is not None and cfg.mlflow is not None:
        tracking_uri = cfg.mlflow.get("tracking_uri") or "file:./mlruns"
        mlflow_client.set_tracking_uri(tracking_uri)
        experiment_name = cfg.mlflow.get("experiment", cfg.project_name)
        if experiment_name:
            mlflow_client.set_experiment(experiment_name)

    best_auc = -np.inf
    best_info: Dict[str, Any] | None = None

    for model_name, param_grid in search_space.items():
        sampler = ParameterSampler(param_grid, n_iter=n_iter, random_state=seed)
        for params in sampler:
            model_cfg: Dict[str, Any] = {"name": model_name, "params": params}
            clf = build_model(model_cfg)
            pipeline = Pipeline(steps=[("preprocess", preprocessor), ("clf", clf)])

            pipeline.fit(X_train, y_train)
            y_pred = pipeline.predict(X_test)
            y_proba = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else None

            metrics = compute_classification_metrics(y_test.to_numpy(), y_pred, y_proba)
            auc = float(metrics.get("roc_auc", 0.0))

            run_name = f"exp-{model_name}"
            if use_mlflow and mlflow_client is not None and cfg.mlflow is not None:
                with mlflow_client.start_run(run_name=run_name):
                    # Params
                    log_params: Dict[str, Any] = {"model_name": model_name}
                    log_params.update(params)
                    mlflow_client.log_params(log_params)
                    # Metrics
                    mlflow_client.log_metrics(metrics)
                    # Modelo como artifact (mejor esfuerzo)
                    try:
                        import mlflow.sklearn  # type: ignore  # noqa: F401

                        input_example = X_train.head(1)
                        mlflow.sklearn.log_model(
                            pipeline,
                            "model",
                            input_example=input_example,
                        )  # type: ignore[attr-defined]
                    except Exception:
                        pass

            if auc > best_auc:
                best_auc = auc
                best_info = {
                    "model_name": model_name,
                    "params": params,
                    "metrics": metrics,
                }

    print("=== Experimentos completados ===")
    if best_info is not None:
        print("Mejor modelo:", best_info["model_name"])
        print("Mejores hiperparámetros:", best_info["params"])
        print("Métricas:", best_info["metrics"])
        print("Mejor ROC AUC:", best_auc)
    else:
        print("No se realizaron experimentos (search space vacío?)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("TelecomAI experiments")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/config.yaml",
        help="Ruta al archivo de configuración base.",
    )
    parser.add_argument(
        "--n_iter",
        type=int,
        default=3,
        help="Número de combinaciones por modelo a muestrear.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semilla para reproducibilidad.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_experiments(args.config, args.n_iter, args.seed)
