#!/usr/bin/env python3
"""
NLPInsight Analyzer — CLI entry point.

Usage:
    python main.py --mode train --config configs/config.yaml
    python main.py --mode eval --config configs/config.yaml
    python main.py --mode predict --input "This product is amazing!"

Or install the package first: pip install -e .
"""

import argparse
import json
import logging
from pathlib import Path

from src.nlpinsight.config import NLPInsightConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("nlpinsight")


def cmd_train(cfg: NLPInsightConfig) -> None:
    """Run the training pipeline."""
    from transformers import AutoTokenizer

    from src.nlpinsight.data import TextDataset, encode_labels, load_dataset, split_dataset
    from src.nlpinsight.training import save_model, train_model

    # Load and process data
    df = load_dataset(cfg.data.train_path, cfg.data.text_column, cfg.data.label_column)
    df, label2id, id2label = encode_labels(df, cfg.data.label_column, cfg.data.labels)
    train_df, val_df = split_dataset(df, cfg.data.label_column, seed=cfg.model.seed)

    # Tokenize
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.pretrained_name)
    train_ds = TextDataset(
        train_df[cfg.data.text_column].tolist(),
        train_df[cfg.data.label_column].tolist(),
        tokenizer,
        cfg.data.max_length,
    )
    val_ds = TextDataset(
        val_df[cfg.data.text_column].tolist(),
        val_df[cfg.data.label_column].tolist(),
        tokenizer,
        cfg.data.max_length,
    )

    # Train
    model, metrics = train_model(
        train_dataset=train_ds,
        val_dataset=val_ds,
        model_name=cfg.model.pretrained_name,
        num_labels=cfg.model.num_labels,
        label2id=label2id,
        id2label=id2label,
        output_dir=cfg.paths.model_dir,
        learning_rate=cfg.model.learning_rate,
        epochs=cfg.model.epochs,
        batch_size=cfg.model.batch_size,
        weight_decay=cfg.model.weight_decay,
        warmup_ratio=cfg.model.warmup_ratio,
        fp16=cfg.model.fp16,
        seed=cfg.model.seed,
        early_stopping_patience=cfg.model.early_stopping_patience,
    )

    # Save
    save_model(model, tokenizer, cfg.paths.model_dir, metrics)

    # Save metrics artifact
    Path(cfg.paths.artifacts_dir).mkdir(parents=True, exist_ok=True)
    with open(cfg.paths.metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"Training complete. Metrics: {metrics}")


def cmd_predict(cfg: NLPInsightConfig, text: str) -> None:
    """Run inference on a single text."""
    from src.nlpinsight.inference import SentimentPredictor

    predictor = SentimentPredictor(model_path=cfg.paths.model_dir)
    result = predictor.predict(text, return_all_scores=True)
    print(json.dumps(result, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="NLPInsight Analyzer CLI")
    parser.add_argument("--mode", choices=["train", "predict"], required=True)
    parser.add_argument("--config", type=str, default="configs/config.yaml")
    parser.add_argument("--input", type=str, help="Text for prediction (predict mode)")
    parser.add_argument("--seed", type=int, help="Random seed override")

    args = parser.parse_args()
    cfg = NLPInsightConfig.from_yaml(args.config)

    if args.seed is not None:
        cfg.model.seed = args.seed

    if args.mode == "train":
        cmd_train(cfg)
    elif args.mode == "predict":
        if not args.input:
            raise ValueError("Predict mode requires --input 'text to analyze'")
        cmd_predict(cfg, args.input)


if __name__ == "__main__":
    main()
