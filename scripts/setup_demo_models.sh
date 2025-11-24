#!/bin/bash
set -e

echo "🔧 Setting up models for demo integration tests..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# BankChurn: Train quick baseline model
echo -e "${BLUE}Training BankChurn model...${NC}"
cd BankChurn-Predictor
if [ -f "main.py" ]; then
    # Create minimal config for fast training
    python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load minimal data
data_path = Path('data/raw/Churn_Modelling.csv')
if not data_path.exists():
    print('⚠️  Data file not found, skipping BankChurn model')
    sys.exit(0)

df = pd.read_csv(data_path).head(1000)  # Use only 1000 rows for speed

# Define features
cat_features = ['Geography', 'Gender']
num_features = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts', 'HasCrCard', 'IsActiveMember', 'EstimatedSalary']

X = df[cat_features + num_features]
y = df['Exited']

# Create simple pipeline
preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_features),
    ('num', StandardScaler(), num_features)
])

model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42))
])

# Train
model.fit(X, y)

# Save
Path('models').mkdir(exist_ok=True)
joblib.dump(model, 'models/best_model.pkl')
print('✅ BankChurn model saved')
"
fi
cd ..
echo -e "${GREEN}BankChurn model ready${NC}"

# CarVision: Train quick baseline model
echo -e "${BLUE}Training CarVision model...${NC}"
cd CarVision-Market-Intelligence
if [ -f "main.py" ]; then
    python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Load minimal data
data_path = Path('data/raw/vehicles_us.csv')
if not data_path.exists():
    print('⚠️  Data file not found, skipping CarVision model')
    sys.exit(0)

df = pd.read_csv(data_path).head(1000).dropna(subset=['price'])

# Simple features
cat_features = ['type', 'fuel', 'transmission']
num_features = ['year', 'odometer']

# Filter to available columns
available_cols = [c for c in cat_features + num_features if c in df.columns]
if 'price' not in df.columns or len(available_cols) == 0:
    print('⚠️  Required columns not found')
    sys.exit(0)

# Separate by dtype before filling
cat_cols = [c for c in available_cols if df[c].dtype == 'object']
num_cols = [c for c in available_cols if df[c].dtype != 'object']

# Fill missing values appropriately by type
X = df[available_cols].copy()
for col in cat_cols:
    X[col] = X[col].fillna('unknown')
for col in num_cols:
    X[col] = X[col].fillna(0)

y = df['price']

transformers = []
if cat_cols:
    transformers.append(('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols))
if num_cols:
    transformers.append(('num', StandardScaler(), num_cols))

preprocessor = ColumnTransformer(transformers)

model = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42))
])

model.fit(X, y)

Path('artifacts').mkdir(exist_ok=True)
joblib.dump(model, 'artifacts/model.joblib')
print('✅ CarVision model saved')
"
fi
cd ..
echo -e "${GREEN}CarVision model ready${NC}"

# TelecomAI: Train quick baseline model  
echo -e "${BLUE}Training TelecomAI model...${NC}"
cd TelecomAI-Customer-Intelligence
if [ -f "main.py" ]; then
    python -c "
import sys
sys.path.insert(0, '.')
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import joblib
import numpy as np

# Load minimal data
data_path = Path('data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv')
if not data_path.exists():
    print('⚠️  Data file not found, skipping TelecomAI model')
    sys.exit(0)

df = pd.read_csv(data_path).head(1000)

# Use actual columns from users_behavior.csv dataset
feature_cols = ['calls', 'minutes', 'messages', 'mb_used']
target_col = 'is_ultra'

# Check if columns exist
if target_col not in df.columns:
    print('⚠️  Target column not found')
    sys.exit(0)

available_features = [f for f in feature_cols if f in df.columns]
if not available_features:
    print('⚠️  No features found')
    sys.exit(0)

X = df[available_features].fillna(0)
y = df[target_col]

model = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42))
])

model.fit(X, y)

Path('artifacts').mkdir(exist_ok=True)
joblib.dump(model, 'artifacts/model.joblib')
print('✅ TelecomAI model saved')
"
fi
cd ..
echo -e "${GREEN}TelecomAI model ready${NC}"

echo -e "${GREEN}✅ All demo models are ready!${NC}"
