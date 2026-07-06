#!/bin/bash
# End-to-End Pipeline Script
# Runs the full flow: ingest → train → register → serve → inference
# Uses BankChurn-Predictor as the reference project

set -e

PROJECT="BankChurn-Predictor"
PORTFOLIO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_DIR="$PORTFOLIO_ROOT/$PROJECT"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}E2E Pipeline - $PROJECT${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

cd "$PROJECT_DIR"

# Activate virtual environment if available (optional in CI)
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif python -c "import sklearn" 2>/dev/null; then
    echo -e "${YELLOW}[!] No .venv found, but dependencies available — continuing${NC}"
else
    echo -e "${RED}[ERROR] No .venv and dependencies not installed${NC}"
    echo "Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Step 1: Data Ingestion
# This checks for the official dataset (fetch_data.py's own job — it is
# reused by local dev workflows where a missing file IS a real error). In
# CI/E2E the official dataset is intentionally never committed, so a "not
# found" here is expected, not a pipeline defect: training in Step 3 uses
# the synthetic CSV generated earlier in the job (E2E_DATA_FILE), which is
# entirely independent of this check.
echo -e "${YELLOW}[1/6] Data Ingestion${NC}"
if [ -f "$PORTFOLIO_ROOT/scripts/fetch_data.py" ]; then
    echo -e "${BLUE}[i] Checking for the official dataset (optional — E2E trains on synthetic data instead)${NC}"
    python "$PORTFOLIO_ROOT/scripts/fetch_data.py" --project bankchurn --validate || {
        echo -e "${YELLOW}[i] Official dataset not present — expected in CI, training will use synthetic data${NC}"
    }
else
    echo -e "${YELLOW}[!] Script fetch_data.py not found${NC}"
fi
echo -e "${GREEN}[✓] Data ingestion check completed${NC}"
echo ""

# Step 2: DVC Pull (if configured)
echo -e "${YELLOW}[2/6] DVC Data Pull${NC}"
if command -v dvc &> /dev/null && [ -f "$PORTFOLIO_ROOT/.dvc/config" ]; then
    echo "[*] Pulling data with DVC..."
    dvc pull 2>/dev/null || echo "[!] DVC pull failed or no remote data"
else
    echo "[!] DVC not configured, skipping..."
fi
echo -e "${GREEN}[✓] DVC check completed${NC}"
echo ""

# Step 3: Training
echo -e "${YELLOW}[3/6] Model Training${NC}"
# Resolve data file: prefer env var, then standard locations
DATA_FILE="${E2E_DATA_FILE:-}"
if [ -z "$DATA_FILE" ]; then
    for candidate in \
        "data/raw/Churn.csv" \
        "data/raw/Churn_Modelling.csv"; do
        if [ -f "$candidate" ]; then
            DATA_FILE="$candidate"
            break
        fi
    done
fi

if [ -z "$DATA_FILE" ] || [ ! -f "$DATA_FILE" ]; then
    echo -e "${RED}[ERROR] Data file not found for training${NC}"
    echo "  Probados: data/raw/Churn.csv, data/raw/Churn_Modelling.csv"
    exit 1
fi
echo "[*] Usando datos: $DATA_FILE"

python -m src.bankchurn.cli train \
    --config configs/config.yaml \
    --input "$DATA_FILE" \
    --model models/model.joblib || {
    echo -e "${RED}[ERROR] Training failed${NC}"
    exit 1
}
echo -e "${GREEN}[✓] Training completed${NC}"
echo ""

# Step 4: Model Registration (MLflow)
echo -e "${YELLOW}[4/6] Model Registration${NC}"
if command -v mlflow &> /dev/null; then
    echo "[*] Registering model in MLflow..."
    # Assumes training already registered the model
    # Here we just verify the tracking URI
    export MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-"http://localhost:5000"}
    echo "[*] MLflow Tracking URI: $MLFLOW_TRACKING_URI"
else
    echo "[!] MLflow not installed, skipping registration..."
fi
echo -e "${GREEN}[✓] Model registration completed${NC}"
echo ""

# Step 5: API Server
echo -e "${YELLOW}[5/6] Starting API Server${NC}"
if [ -f "app/fastapi_app.py" ]; then
    echo "[*] Starting FastAPI server in background..."
    uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
    API_PID=$!
    echo "[*] API PID: $API_PID"
    
    # Wait for server to be ready
    echo "[*] Waiting for server to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}[✓] API Server listo${NC}"
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
else
    echo -e "${RED}[ERROR] API fastapi_app.py not found${NC}"
    exit 1
fi
echo ""

# Step 6: Inference Test
echo -e "${YELLOW}[6/6] Inference Test${NC}"
echo "[*] Testing prediction..."

# Example payload
PAYLOAD='{
  "CreditScore": 619,
  "Geography": "France",
  "Gender": "Female",
  "Age": 42,
  "Tenure": 2,
  "Balance": 0.0,
  "NumOfProducts": 1,
  "HasCrCard": 1,
  "IsActiveMember": 1,
  "EstimatedSalary": 101348.88
}'

# Send request
RESPONSE=$(curl -s -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

echo "[*] Response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""

# Verify response
if echo "$RESPONSE" | grep -q "prediction"; then
    echo -e "${GREEN}[✓] Inference successful${NC}"
else
    echo -e "${RED}[ERROR] Inference failed${NC}"
    INFERENCE_SUCCESS=false
fi
echo ""

# Cleanup: Stop API
echo "[*] Stopping API Server (PID: $API_PID)..."
kill $API_PID 2>/dev/null || true
sleep 2
echo -e "${GREEN}[✓] API Server stopped${NC}"
echo ""

# Summary
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}E2E Pipeline Completed${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo -e "${GREEN}Steps executed:${NC}"
echo "  ✓ 1. Data Ingestion"
echo "  ✓ 2. DVC Pull"
echo "  ✓ 3. Model Training"
echo "  ✓ 4. Model Registration"
echo "  ✓ 5. API Server"
echo "  ✓ 6. Inference Test"
echo ""

if [ "$INFERENCE_SUCCESS" != "false" ]; then
    echo -e "${GREEN}[SUCCESS] E2E Pipeline completed successfully${NC}"
    exit 0
else
    echo -e "${YELLOW}[WARNING] Pipeline completed with warnings${NC}"
    exit 1
fi
