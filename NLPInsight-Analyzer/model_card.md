# Model Card: NLPInsight Sentiment Analyzer

## Model Details

- **Model Name**: NLPInsight Sentiment Analyzer
- **Model Type**: Dual-backend — TF-IDF + LogisticRegression (production) / Fine-tuned DistilBERT (advanced)
- **Production Model**: sklearn Pipeline (TfidfVectorizer → LogisticRegression), 309 KB
- **Advanced Model**: `distilbert-base-uncased` (66M parameters), ~260 MB
- **Framework**: scikit-learn 1.8 (production) / PyTorch 2.0+ + HuggingFace Transformers (advanced)
- **Version**: 2.0.0
- **License**: MIT

## Intended Use

- **Primary Use**: Financial sentiment analysis (earnings reports, market commentary, financial news)
- **Users**: Product teams, financial analysts, portfolio managers
- **Out of Scope**: Non-English text, sarcasm detection, fine-grained emotion beyond 3-class sentiment

## Training Data

- **Dataset**: Financial PhraseBank (Malo et al., 2014) — 4,845 financial sentences
- **Labels**: 3 classes (negative, neutral, positive) — annotated by financial domain experts
- **Split**: 85% train / 15% validation (stratified by label)
- **Preprocessing (sklearn)**: TF-IDF vectorization with sublinear TF
- **Preprocessing (transformer)**: DistilBERT tokenizer, max_length=256, padding, truncation

## Training Procedure

### Production Model (TF-IDF + LogisticRegression)
- **Vectorizer**: TfidfVectorizer (sublinear_tf=True, max_features=10000)
- **Classifier**: LogisticRegression (class_weight='balanced', C=1.0, max_iter=1000)
- **Training**: Single-pass fit on CPU
- **Reproducibility**: Seed=42

### Advanced Model (DistilBERT)
- **Optimizer**: AdamW (lr=2e-5, weight_decay=0.01)
- **Schedule**: Linear warmup (10% of steps) + linear decay
- **Epochs**: 3 (with early stopping, patience=2)
- **Batch Size**: 16
- **Hardware**: CPU (GPU optional with FP16 support)
- **Reproducibility**: Seed=42, deterministic training

## Evaluation

| Metric | TF-IDF + LogReg (production) | DistilBERT |
|--------|------------------------------|------------|
| Accuracy | **88.08%** | ~85% |
| F1 (macro) | **0.826** | ~0.82 |
| Precision (macro) | 0.83 | ~0.83 |
| Recall (macro) | 0.82 | ~0.81 |

### Design Decision

The TF-IDF + LogisticRegression model outperforms DistilBERT on this dataset because Financial PhraseBank is relatively small (4,845 samples) and has clear lexical sentiment signals. The transformer shows no significant advantage but requires 800x more storage and GPU for optimal inference. The dual-backend architecture allows upgrading to DistilBERT without code changes when larger datasets become available.

## Limitations

- English-only — no multilingual support
- 3-class classification only (negative/neutral/positive) — no fine-grained emotion
- Financial domain focus — may underperform on general-purpose sentiment
- Max input length 256 tokens (transformer) — longer texts are truncated
- No domain adaptation beyond Financial PhraseBank

## Ethical Considerations

- **Bias**: Financial text may reflect market biases; model should not be used for automated trading decisions
- **Misuse**: Should not be used for automated content moderation without human review
- **Privacy**: No PII stored in model weights; input texts are not logged in production by default

## Infrastructure

- **Serving**: FastAPI with Prometheus metrics (`nlpinsight_*`), batch inference (up to 500 texts)
- **Container**: Multi-stage Docker (CPU-optimized PyTorch, 2.05 GB)
- **Orchestration**: Kubernetes with HPA (CPU-based autoscaling, 1–3 pods)
- **Monitoring**: Prometheus + Grafana dashboards
- **Memory**: ~140Mi per worker (sklearn backend)
- **Latency**: P95 <220ms (K8s via port-forward), ~87ms avg
