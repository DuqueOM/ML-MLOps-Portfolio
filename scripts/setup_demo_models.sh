#!/bin/bash
set -e

echo "🔧 Setting up models for demo integration tests..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Run in the workspace's locked environment (uv.lock, ADR-019), so the demo
# models are saved with the same scikit-learn the services load them with.
# They need only scikit-learn, pandas and joblib, which BankChurn's locked
# environment carries; that avoids installing the transformer stack the other
# services use for a TF-IDF demo.
if command -v uv >/dev/null 2>&1; then
    PYTHON="uv run --frozen --package bankchurn-predictor python"
    echo -e "${GREEN}Using the locked environment (uv.lock)${NC}"
else
    PYTHON="python"
    echo -e "${BLUE}uv not found; using system Python: $(python --version)${NC}"
    echo "  ⚠️  Install uv (https://docs.astral.sh/uv/) to use the locked environment"
fi

# BankChurn: Train quick baseline model
echo -e "${BLUE}Training BankChurn model...${NC}"
cd BankChurn-Predictor
$PYTHON -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Define features matching API schema (CustomerData)
cat_features = ['Geography', 'Gender']
num_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary']

# Try to load real data
data_path = Path('data/raw/Churn_Modelling.csv')
if data_path.exists():
    df = pd.read_csv(data_path).head(500)
    print('Using real data')
else:
    # Create synthetic demo data matching API schema
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        'CreditScore': np.random.randint(300, 850, n),
        'Geography': np.random.choice(['France', 'Spain', 'Germany'], n),
        'Gender': np.random.choice(['Male', 'Female'], n),
        'Age': np.random.randint(18, 80, n),
        'Tenure': np.random.randint(0, 10, n),
        'Balance': np.random.uniform(0, 200000, n),
        'NumOfProducts': np.random.randint(1, 4, n),
        'HasCrCard': np.random.choice([0, 1], n),
        'IsActiveMember': np.random.choice([0, 1], n),
        'EstimatedSalary': np.random.uniform(10000, 200000, n),
        'Exited': np.random.choice([0, 1], n, p=[0.8, 0.2])
    })
    print('Using synthetic data (no data file found)')

X = df[cat_features + num_features]
y = df['Exited']

# Create pipeline
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features),
    ('num', StandardScaler(), num_features)
])

model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42))
])

model.fit(X, y)

Path('models').mkdir(exist_ok=True)
joblib.dump(model, 'models/model.joblib')
print('✅ BankChurn model saved to models/model.joblib')
"
cd ..
echo -e "${GREEN}BankChurn model ready${NC}"

# NLPInsight: Train quick TF-IDF baseline for sentiment analysis
echo -e "${BLUE}Training NLPInsight model...${NC}"
cd NLPInsight-Analyzer
$PYTHON -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

data_path = Path('data/raw/train.csv')
if data_path.exists():
    df = pd.read_csv(data_path)
    print(f'Using Financial PhraseBank from {data_path} ({len(df)} rows)')
else:
    # Synthetic fallback
    np.random.seed(42)
    texts = ['great earnings report'] * 50 + ['losses increased'] * 30 + ['no change expected'] * 70
    labels = [2] * 50 + [0] * 30 + [1] * 70
    df = pd.DataFrame({'text': texts, 'label_id': labels})
    print('Using synthetic data (run download_financial_phrasebank.py first)')

X = df['text']
y = df['label_id']

model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
    ('classifier', LogisticRegression(max_iter=1000, random_state=42))
])

model.fit(X, y)

Path('models').mkdir(exist_ok=True)
joblib.dump(model, 'models/model.joblib')
print('✅ NLPInsight model saved to models/model.joblib')
print(f'   Classes: negative(0), neutral(1), positive(2)')
"
cd ..
echo -e "${GREEN}NLPInsight model ready${NC}"

echo -e "${GREEN}✅ All demo models are ready!${NC}"
