---
description: Monthly cloud cost review — collect, analyze, optimize, document
---

# /cost-review Workflow

## 1. Collect GCP Costs

```bash
gcloud billing accounts list
# Check budget status
gcloud billing budgets list --billing-account=${BILLING_ACCOUNT}
```

## 2. Collect AWS Costs

```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## 3. Build Cost Breakdown

Fill in the template:
```
Compute serving (N APIs × 2 clouds):  $___/mo
Compute training (Spot, monthly avg):  $___/mo
Databases (Cloud SQL + RDS):           $___/mo
Storage (GCS + S3):                    $___/mo
Registry (Artifact Registry + ECR):    $___/mo
Monitoring and Logging:                $___/mo
───────────────────────────────────────────────
TOTAL:                                 $___/mo
vs Budget:                             $___/mo
vs Last Month:                         $___/mo (↑/↓ __%)
```

## 4. Check FinOps Rules

- [ ] Training jobs using Spot/Preemptible instances
- [ ] Serving pods on On-Demand instances
- [ ] No memory-based HPA causing idle pods
- [ ] Lifecycle rules active on all buckets
- [ ] Budget alerts configured at 50% and 90%
- [ ] No non-production clusters running overnight
- [ ] Old container images cleaned up

## 5. Check Prometheus Utilization Metrics

```bash
# CPU utilization per pod (actual vs requested)
curl -s 'http://prometheus:9090/api/v1/query?query=avg(rate(container_cpu_usage_seconds_total{namespace="ml-services"}[5m])) by (pod)'

# Memory utilization per pod
curl -s 'http://prometheus:9090/api/v1/query?query=avg(container_memory_working_set_bytes{namespace="ml-services"}) by (pod)'

# Prediction throughput (requests/min)
curl -s 'http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{namespace="ml-services"}[1h])) by (service) * 60'

# HPA utilization (are we over-provisioned?)
curl -s 'http://prometheus:9090/api/v1/query?query=kube_horizontalpodautoscaler_status_current_replicas / kube_horizontalpodautoscaler_spec_max_replicas'
```

## 6. Identify Optimizations

### Right-Sizing
```bash
# Pods with CPU usage < 30% of request (candidates for downsizing)
kubectl top pods -n ${NAMESPACE} --sort-by=cpu

# Check HPA min/max vs actual replicas
kubectl get hpa -n ${NAMESPACE}
```

### Storage Cleanup
```bash
# Check bucket sizes
gsutil du -s gs://${BUCKET}
aws s3 ls --summarize --human-readable s3://${BUCKET}
```

### Image Cleanup
```bash
# Delete images older than 90 days
gcloud artifacts docker images list ${REGISTRY} --filter="updateTime<-P90D"
```

## 7. Document Findings

Update:
- Service READMEs with current costs
- FinOps ADR with trend analysis
- Budget projections for next month

## 8. Action Items

Create GitHub Issues for any optimization opportunities:
```bash
gh issue create \
  --title "FinOps: ${OPTIMIZATION}" \
  --body "Estimated savings: $${AMOUNT}/mo\nDetails: ${DETAILS}" \
  --label "finops"
```
