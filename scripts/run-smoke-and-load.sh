#!/bin/bash
set -e

echo "=== Killing existing port-forwards ==="
pkill -9 -f "kubectl port-forward" 2>/dev/null || true
sleep 3

echo "=== Setting up port-forwards ==="
kubectl port-forward svc/bankchurn-service 8000:80 -n ml-portfolio > /dev/null 2>&1 &
sleep 2
kubectl port-forward svc/carvision-service 8001:80 -n ml-portfolio > /dev/null 2>&1 &
sleep 2
kubectl port-forward svc/telecom-service 8002:80 -n ml-portfolio > /dev/null 2>&1 &
sleep 2

echo "Waiting for port-forwards to stabilize..."
for i in $(seq 1 15); do
  if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "BankChurn ready after ${i}s"
    break
  fi
  sleep 1
done
for i in $(seq 1 15); do
  if curl -sf http://localhost:8001/health > /dev/null 2>&1; then
    echo "CarVision ready after ${i}s"
    break
  fi
  sleep 1
done
for i in $(seq 1 15); do
  if curl -sf http://localhost:8002/health > /dev/null 2>&1; then
    echo "TelecomAI ready after ${i}s"
    break
  fi
  sleep 1
done

echo ""
echo "=========================================="
echo "  SMOKE TESTS"
echo "=========================================="

PASS=0
FAIL=0

# --- BankChurn Health ---
echo -n "[BankChurn] Health check... "
if curl -sf http://localhost:8000/health > /dev/null; then
  echo "PASS"
  PASS=$((PASS+1))
else
  echo "FAIL"
  FAIL=$((FAIL+1))
fi

# --- BankChurn Predict (no SHAP) ---
echo -n "[BankChurn] Predict (no SHAP)... "
RESP=$(curl -sf -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":600,"Geography":"France","Gender":"Male","Age":40,"Tenure":3,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}')
if echo "$RESP" | grep -q "churn_probability"; then
  echo "PASS"
  PASS=$((PASS+1))
else
  echo "FAIL - $RESP"
  FAIL=$((FAIL+1))
fi

# --- BankChurn Predict WITH SHAP ---
echo -n "[BankChurn] Predict (with SHAP explain=true)... "
RESP=$(curl -sf -X POST "http://localhost:8000/predict?explain=true" \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":600,"Geography":"France","Gender":"Male","Age":40,"Tenure":3,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}')
if echo "$RESP" | grep -q "feature_contributions"; then
  echo "PASS"
  PASS=$((PASS+1))
else
  echo "FAIL - $RESP"
  FAIL=$((FAIL+1))
fi

# --- CarVision Health ---
echo -n "[CarVision] Health check... "
if curl -sf http://localhost:8001/health > /dev/null; then
  echo "PASS"
  PASS=$((PASS+1))
else
  echo "FAIL"
  FAIL=$((FAIL+1))
fi

# --- CarVision Predict ---
echo -n "[CarVision] Predict... "
RESP=$(curl -sf -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"model_year":2018,"model":"Ford F-150","condition":"excellent","cylinders":6,"fuel":"gas","odometer":30000,"transmission":"automatic","drive":"4wd","type":"truck","paint_color":"white","state":"ca"}')
if echo "$RESP" | grep -q "predicted_price"; then
  echo "PASS"
  PASS=$((PASS+1))
else
  echo "FAIL - $RESP"
  FAIL=$((FAIL+1))
fi

# --- TelecomAI Health ---
echo -n "[TelecomAI] Health check... "
if curl -sf http://localhost:8002/health > /dev/null; then
  echo "PASS"
  PASS=$((PASS+1))
else
  echo "FAIL"
  FAIL=$((FAIL+1))
fi

# --- TelecomAI Predict ---
echo -n "[TelecomAI] Predict... "
RESP=$(curl -sf -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{"calls":50,"minutes":300.5,"messages":40,"mb_used":2048.0}')
if echo "$RESP" | grep -q "prediction"; then
  echo "PASS"
  PASS=$((PASS+1))
else
  echo "FAIL - $RESP"
  FAIL=$((FAIL+1))
fi

echo ""
echo "=========================================="
echo "  SMOKE RESULTS: $PASS passed, $FAIL failed"
echo "=========================================="

if [ "$FAIL" -gt 0 ]; then
  echo "SMOKE TESTS FAILED - aborting load test"
  pkill -f "kubectl port-forward" || true
  exit 1
fi

echo ""
echo "=========================================="
echo "  LATENCY BENCHMARKS (single request)"
echo "=========================================="

echo -n "[BankChurn] Single predict latency: "
curl -sf -o /dev/null -w "%{time_total}s\n" -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":600,"Geography":"France","Gender":"Male","Age":40,"Tenure":3,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}'

echo -n "[BankChurn] Predict with SHAP:     "
curl -sf -o /dev/null -w "%{time_total}s\n" -X POST "http://localhost:8000/predict?explain=true" \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":600,"Geography":"France","Gender":"Male","Age":40,"Tenure":3,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}'

echo -n "[CarVision] Single predict latency: "
curl -sf -o /dev/null -w "%{time_total}s\n" -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"model_year":2018,"model":"Ford F-150","condition":"excellent","cylinders":6,"fuel":"gas","odometer":30000,"transmission":"automatic","drive":"4wd","type":"truck","paint_color":"white","state":"ca"}'

echo -n "[TelecomAI] Single predict latency: "
curl -sf -o /dev/null -w "%{time_total}s\n" -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{"calls":50,"minutes":300.5,"messages":40,"mb_used":2048.0}'

echo ""
echo "Port-forwards still running. Ready for load tests."
echo "To run load test: python -m locust --headless -u 30 -r 5 --run-time 2m --host http://localhost:8000"
