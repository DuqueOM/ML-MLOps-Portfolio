#!/bin/bash
set -e

echo "=== Applying updated K8s manifests ==="
kubectl apply --filename k8s/bankchurn-deployment.yaml
