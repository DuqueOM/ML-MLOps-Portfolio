# Model Card: NLPInsight Sentiment Analyzer

## Model Details

- **Model Name**: NLPInsight Sentiment Analyzer
- **Model Type**: Fine-tuned DistilBERT for binary sentiment classification
- **Base Model**: `distilbert-base-uncased` (66M parameters)
- **Framework**: PyTorch + HuggingFace Transformers
- **Version**: 1.0.0
- **License**: MIT

## Intended Use

- **Primary Use**: Sentiment analysis of English text (reviews, feedback, comments)
- **Users**: Product teams, customer success, marketing analytics
- **Out of Scope**: Non-English text, sarcasm detection, fine-grained emotion classification

## Training Data

- **Dataset**: Binary sentiment classification dataset (positive/negative)
- **Split**: 85% train / 15% validation (stratified)
- **Preprocessing**: Tokenization with DistilBERT tokenizer, max_length=256, padding, truncation

## Training Procedure

- **Optimizer**: AdamW (lr=2e-5, weight_decay=0.01)
- **Schedule**: Linear warmup (10% of steps) + linear decay
- **Epochs**: 3 (with early stopping, patience=2)
- **Batch Size**: 16
- **Hardware**: CPU (GPU optional with FP16 support)
- **Reproducibility**: Seed=42, deterministic training

## Evaluation

| Metric | Value |
|--------|-------|
| Accuracy | TBD (after training) |
| F1 (weighted) | TBD |
| Precision (weighted) | TBD |
| Recall (weighted) | TBD |

## Limitations

- English-only — no multilingual support
- Binary classification only — no neutral/mixed sentiment
- Max input length 256 tokens — longer texts are truncated
- No domain adaptation — general-purpose sentiment, may underperform on domain-specific jargon

## Ethical Considerations

- **Bias**: Pre-trained on English web text which may contain cultural and demographic biases
- **Misuse**: Should not be used for automated content moderation without human review
- **Privacy**: No PII stored in model weights; input texts are not logged in production by default

## Infrastructure

- **Serving**: FastAPI with Prometheus metrics, batch inference support
- **Container**: Multi-stage Docker (CPU-optimized PyTorch, ~600MB)
- **Orchestration**: Kubernetes with HPA (CPU-based autoscaling)
- **Monitoring**: Prometheus + Grafana dashboards
