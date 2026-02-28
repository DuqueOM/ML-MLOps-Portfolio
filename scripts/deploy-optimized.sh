#!/bin/bash
set -e

echo "=== Applying updated K8s manifests ==="
kubectl apply --filename k8s/bankchurn-deployment.yaml
kubectl apply --filename k8s/carvision-deployment.yaml
kubectl apply --filename k8s/telecom-deployment.yaml

echo ""
echo "=== Rolling restart to pull new images ==="
kubectl rollout restart deployment/bankchurn-predictor -n ml-portfolio
kubectl rollout restart deployment/carvision-intelligence -n ml-portfolio
kubectl rollout restart deployment/telecom-intelligence -n ml-portfolio

echo ""
echo "=== Waiting for rollouts to complete ==="
kubectl rollout status deployment/bankchurn-predictor -n ml-portfolio --timeout=300s
kubectl rollout status deployment/carvision-intelligence -n ml-portfolio --timeout=300s
kubectl rollout status deployment/telecom-intelligence -n ml-portfolio --timeout=300s

echo ""
echo "=== Pod status ==="
kubectl get pods -n ml-portfolio

echo ""
echo "=== Deploy complete ==="
 