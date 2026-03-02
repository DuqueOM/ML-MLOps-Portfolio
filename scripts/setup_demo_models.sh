#!/bin/bash
set -e

echo "🔧 Setting up models for demo integration tests..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Use Python 3.11 if available (matches Docker image)
PY311="/home/duque_om/miniconda3/envs/ml-py311/bin/python"
if [ -x "$PY311" ]; then
    PYTHON="$PY311"
    echo -e "${GREEN}Using Python 3.11 (matches Docker): $PYTHON${NC}"
else
    PYTHON="python"
    echo -e "${BLUE}Using system Python: $(python --version)${NC}"
    echo "  ⚠️  For production, use: conda activate ml-py311"
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

# CarVision: Train quick baseline model
echo -e "${BLUE}Training CarVision model...${NC}"
cd CarVision-Market-Intelligence
$PYTHON -c "
import sys
import json
sys.path.insert(0, '.')
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Features matching the API schema (VehicleFeatures)
cat_features = ['model', 'condition', 'fuel', 'transmission', 'drive', 'type', 'paint_color']
num_features = ['model_year', 'cylinders', 'odometer']

# Try to load real data, otherwise create synthetic
data_path = Path('data/raw/vehicles_us.csv')
if data_path.exists():
    df = pd.read_csv(data_path).head(500).dropna(subset=['price'])
    # Rename columns to match API schema
    if 'year' in df.columns and 'model_year' not in df.columns:
        df['model_year'] = df['year']
    print('Using real data')
else:
    # Create synthetic demo data matching API schema
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        'model_year': np.random.randint(2010, 2023, n),
        'model': np.random.choice(['civic', 'corolla', 'camry', 'accord', 'f150'], n),
        'condition': np.random.choice(['good', 'excellent', 'fair', 'like new'], n),
        'cylinders': np.random.choice([4, 6, 8], n).astype(float),
        'fuel': np.random.choice(['gas', 'diesel', 'hybrid', 'electric'], n),
        'odometer': np.random.uniform(10000, 150000, n),
        'transmission': np.random.choice(['automatic', 'manual'], n),
        'drive': np.random.choice(['fwd', 'rwd', '4wd'], n),
        'type': np.random.choice(['sedan', 'suv', 'truck', 'coupe'], n),
        'paint_color': np.random.choice(['white', 'black', 'silver', 'red', 'blue'], n),
        'price': np.random.uniform(5000, 50000, n)
    })
    print('Using synthetic data (real data not found)')

# Ensure all features exist
for col in cat_features:
    if col not in df.columns:
        df[col] = 'unknown'
for col in num_features:
    if col not in df.columns:
        df[col] = 0

# Prepare data
X = df[cat_features + num_features].copy()
for col in cat_features:
    X[col] = X[col].fillna('unknown').astype(str)
for col in num_features:
    X[col] = pd.to_numeric(X[col], errors='coerce').fillna(0)

y = df['price']

# Build pipeline with named steps
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features),
    ('num', StandardScaler(), num_features)
])

model = Pipeline([
    ('pre', preprocessor),
    ('model', RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42))
])

model.fit(X, y)

# Save model and feature columns
Path('models').mkdir(exist_ok=True)
joblib.dump(model, 'models/model.joblib')

Path('artifacts').mkdir(exist_ok=True)
feature_columns = cat_features + num_features
Path('artifacts/feature_columns.json').write_text(json.dumps(feature_columns))

print('✅ CarVision model saved to models/model.joblib')
print(f'   Features: {feature_columns}')
"
cd ..
echo -e "${GREEN}CarVision model ready${NC}"

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
