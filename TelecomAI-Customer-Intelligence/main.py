#!/usr/bin/env python3
"""
TelecomAI Customer Intelligence - Main CLI
"""
import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml

# Core imports
from src.telecom.evaluation import evaluate_model
from src.telecom.prediction import predict_batch
from src.telecom.training import train_model

try:
    from common_utils.seed import set_seed
except ModuleNotFoundError:  # pragma: no cover
    BASE_DIR = Path(__file__).resolve().parents[1]
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    from common_utils.seed import set_seed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("telecomai")


@dataclass
class Config:
    project_name: str
    random_seed: int
    paths: Dict[str, str]
    features: list
    target: str
    split: Dict[str, Any]
    model: Dict[str, Any]
    threshold: float = 0.5
    mlflow: Any = None


def load_config(path: str) -> Config:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return Config(**cfg)


def main() -> None:
    parser = argparse.ArgumentParser(description="TelecomAI CLI")
    parser.add_argument("--mode", choices=["train", "eval", "predict"], required=True)
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--input_csv", type=str)
    parser.add_argument("--output_path", type=str)
    parser.add_argument("--seed", type=int, help="Random seed override")

    args = parser.parse_args()
    cfg = load_config(args.config)

    seed_used = set_seed(args.seed)
    logger.info("Using seed: %s", seed_used)
    cfg.random_seed = int(seed_used)

    if args.mode == "train":
        train_model(cfg)
    elif args.mode == "eval":
        evaluate_model(cfg)
    elif args.mode == "predict":
        if not args.input_csv or not args.output_path:
            raise ValueError("Predict mode requires --input_csv and --output_path")
        predict_batch(args.input_csv, args.output_path, cfg.paths["model_path"], cfg.features)


if __name__ == "__main__":
    main()
