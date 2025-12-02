#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Cross-Project Demo Integration Tests...${NC}"

# Base URLs
BANKCHURN_URL="http://localhost:8001"
CARVISION_URL="http://localhost:8002"
TELECOM_URL="http://localhost:8003"
MLFLOW_URL="http://localhost:5000"

# Helper function to check health with retries
check_health() {
    local url=$1
    local name=$2
    local max_retries=6
    local retry_delay=10
    
    echo -n "Checking $name ($url/health)... "
    
    for i in $(seq 1 $max_retries); do
        if curl -s -f "$url/health" > /dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}"
            return 0
        fi
        if [ $i -lt $max_retries ]; then
            echo -n "retry $i/$max_retries... "
            sleep $retry_delay
        fi
    done
    
    echo -e "${RED}FAILED${NC}"
    return 1
}

# Helper function to check HTTP 200 on root/docs
check_endpoint() {
    local url=$1
    local name=$2
    echo -n "Checking $name ($url)... "
    
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    if [ "$code" == "200" ]; then
        echo -e "${GREEN}OK (200)${NC}"
        return 0
    else
        echo -e "${RED}FAILED ($code)${NC}"
        return 1
    fi
}

# 1. Verify MLflow
check_health "$MLFLOW_URL" "MLflow Server"

# 2. Verify BankChurn Predictor
check_health "$BANKCHURN_URL" "BankChurn API"
check_endpoint "$BANKCHURN_URL/docs" "BankChurn Docs"

# 3. Verify CarVision Market Intelligence
check_health "$CARVISION_URL" "CarVision API"
check_endpoint "$CARVISION_URL/docs" "CarVision Docs"
# Verify Streamlit is up (simple check)
echo -n "Checking CarVision Dashboard (http://localhost:8501)... "
code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8501/_stcore/health" || echo "000")
if [ "$code" == "200" ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED ($code)${NC}"
    # Don't fail the script for dashboard yet as it might take longer
fi

# 4. Verify TelecomAI Customer Intelligence
check_health "$TELECOM_URL" "TelecomAI API"
check_endpoint "$TELECOM_URL/docs" "TelecomAI Docs"

# 5. Test Prediction Endpoints (Smoke Test)

# BankChurn Prediction Test
echo -n "Testing BankChurn Prediction... "
RESPONSE=$(curl -s -X POST "$BANKCHURN_URL/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "CreditScore": 650,
       "Geography": "France",
       "Gender": "Female",
       "Age": 40,
       "Tenure": 3,
       "Balance": 60000,
       "NumOfProducts": 2,
       "HasCrCard": 1,
       "IsActiveMember": 1,
       "EstimatedSalary": 50000
     }')

if echo "$RESPONSE" | grep -q "churn_prediction"; then
    echo -e "${GREEN}SUCCESS${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

# CarVision Prediction Test
echo -n "Testing CarVision Prediction... "
RESPONSE=$(curl -s -X POST "$CARVISION_URL/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "model_year": 2015,
       "model": "civic",
       "condition": "good",
       "cylinders": 4,
       "fuel": "gas",
       "odometer": 50000,
       "transmission": "automatic",
       "drive": "fwd",
       "type": "sedan",
       "paint_color": "white"
     }')

if echo "$RESPONSE" | grep -q "prediction"; then
    echo -e "${GREEN}SUCCESS${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

# TelecomAI Prediction Test
echo -n "Testing TelecomAI Prediction... "
RESPONSE=$(curl -s -X POST "$TELECOM_URL/predict" \
     -H "Content-Type: application/json" \
     -d '{
        "calls": 40.0,
        "minutes": 311.9,
        "messages": 83.0,
        "mb_used": 19915.42
     }')

if echo "$RESPONSE" | grep -q "prediction"; then
    echo -e "${GREEN}SUCCESS${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo -e "${GREEN}All integration tests passed! 🚀${NC}"
exit 0
