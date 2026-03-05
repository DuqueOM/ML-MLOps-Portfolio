"""
Gradio demo for BankChurn Predictor.

Interactive UI for churn prediction — no API server required.
Usage: python app/gradio_demo.py
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

import gradio as gr
import joblib
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bankchurn-gradio")

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "model.joblib"
PREPROCESSOR_PATH = BASE_DIR / "models" / "preprocessor.joblib"
METADATA_PATH = BASE_DIR / "models" / "best_model_metadata.json"

FEATURE_COLUMNS = [
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
]


def load_model():
    """Load the trained model pipeline."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run training first: make train")
    model = joblib.load(MODEL_PATH)
    logger.info("Model loaded from %s", MODEL_PATH)
    return model


def load_metadata() -> Dict[str, Any]:
    """Load model metadata if available."""
    if METADATA_PATH.exists():
        with open(METADATA_PATH) as f:
            return json.load(f)
    return {}


# Load model at import time
model = load_model()
metadata = load_metadata()


def predict_churn(
    credit_score: int,
    geography: str,
    gender: str,
    age: int,
    tenure: int,
    balance: float,
    num_products: int,
    has_credit_card: str,
    is_active: str,
    salary: float,
    threshold: float,
) -> str:
    """Run churn prediction and return formatted results."""
    row = {
        "CreditScore": credit_score,
        "Geography": geography,
        "Gender": gender,
        "Age": age,
        "Tenure": tenure,
        "Balance": balance,
        "NumOfProducts": num_products,
        "HasCrCard": 1 if has_credit_card == "Yes" else 0,
        "IsActiveMember": 1 if is_active == "Yes" else 0,
        "EstimatedSalary": salary,
    }

    df = pd.DataFrame([row])

    try:
        proba = model.predict_proba(df)[0]
        churn_prob = float(proba[1])
    except Exception:
        pred = int(model.predict(df)[0])
        return f"**Prediction**: {'CHURN' if pred == 1 else 'STAY'}\n\n_(Model does not support probability output)_"

    churn_pred = 1 if churn_prob >= threshold else 0

    if churn_prob < 0.3:
        risk = "LOW"
        risk_color = "🟢"
        action = "Standard engagement. Monitor at next review cycle."
    elif churn_prob < 0.7:
        risk = "MEDIUM"
        risk_color = "🟡"
        action = "Proactive outreach recommended. Consider loyalty offer or fee waiver."
    else:
        risk = "HIGH"
        risk_color = "🔴"
        action = "Immediate intervention required. Assign to retention specialist."

    result = f"""## {risk_color} Churn Risk: **{risk}**

| Metric | Value |
|--------|-------|
| **Churn Probability** | {churn_prob:.1%} |
| **Prediction** | {'CHURN' if churn_pred == 1 else 'STAY'} |
| **Threshold** | {threshold:.0%} |
| **Confidence** | {max(churn_prob, 1 - churn_prob):.1%} |

### Recommended Action
{action}

---
<small>Model: StackingClassifier (RF + GB + XGB + LGBM → LogReg) · AUC 0.87</small>
"""
    return result


# --- Gradio Interface ---

with gr.Blocks(
    title="BankChurn Predictor",
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown("""
        # 🏦 BankChurn Predictor
        **Interactive customer churn prediction** — Enter customer details below to assess churn risk.

        Model: StackingClassifier ensemble (4 base learners + LogReg meta-learner) · AUC 0.87 · F1 0.62
        """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Customer Profile")
            credit_score = gr.Slider(300, 850, value=650, step=1, label="Credit Score")
            geography = gr.Radio(["France", "Spain", "Germany"], value="France", label="Geography")
            gender = gr.Radio(["Male", "Female"], value="Male", label="Gender")
            age = gr.Slider(18, 100, value=40, step=1, label="Age")
            tenure = gr.Slider(0, 10, value=5, step=1, label="Tenure (years)")

        with gr.Column(scale=1):
            gr.Markdown("### Financial Details")
            balance = gr.Number(value=60000.0, label="Account Balance ($)")
            num_products = gr.Slider(1, 4, value=2, step=1, label="Number of Products")
            has_credit_card = gr.Radio(["Yes", "No"], value="Yes", label="Has Credit Card")
            is_active = gr.Radio(["Yes", "No"], value="Yes", label="Active Member")
            salary = gr.Number(value=50000.0, label="Estimated Salary ($)")
            threshold = gr.Slider(
                0.1,
                0.9,
                value=0.35,
                step=0.05,
                label="Decision Threshold",
                info="Lower = catch more churners (higher recall). Production default: 0.35",
            )

    predict_btn = gr.Button("🔍 Predict Churn Risk", variant="primary", size="lg")

    output = gr.Markdown(label="Prediction Result")

    predict_btn.click(
        fn=predict_churn,
        inputs=[
            credit_score,
            geography,
            gender,
            age,
            tenure,
            balance,
            num_products,
            has_credit_card,
            is_active,
            salary,
            threshold,
        ],
        outputs=output,
    )

    gr.Markdown("""
        ---
        ### Quick Test Scenarios

        | Scenario | Credit | Geo | Age | Balance | Products | Active | Expected |
        |----------|--------|-----|-----|---------|----------|--------|----------|
        | **Low risk** | 750 | France | 35 | $80K | 2 | Yes | ~5-15% |
        | **Medium risk** | 600 | Germany | 45 | $120K | 1 | No | ~30-50% |
        | **High risk** | 400 | Germany | 55 | $0 | 4 | No | ~70-90% |

        ---
        <small>
        BankChurn Predictor · ML-MLOps Portfolio · [Model Card](../models/model_card.md) ·
        Production threshold 0.35 optimized for 30:1 cost ratio (missed churner vs unnecessary retention offer)
        </small>
        """)


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
    )
