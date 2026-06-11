---
name: cost-audit
description: Review cloud costs against budget and identify optimization opportunities
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(gcloud:*)
  - Bash(aws:*)
  - Bash(kubectl:*)
when_to_use: >
  Use when reviewing monthly cloud costs, optimizing spend, or preparing FinOps reports.
  Examples: 'review monthly costs', 'cost optimization', 'FinOps report', 'budget review'
argument-hint: "[month] [year]"
authorization_mode:
  collect_billing: AUTO       # read-only billing API queries
  analyze_spend: AUTO         # local computation
  propose_optimizations: AUTO # produces report only, no cluster changes
  apply_optimizations: STOP   # any rightsizing / scale-down requires human approval
  escalation_triggers:
    - cost_over_budget_120: STOP   # spend > 120% of budget → freeze auto-actions
    - new_resource_type: CONSULT   # unknown resource → require human classification
---

# Cost Audit

## Step 1: Collect Current Costs

### GCP
```bash
gcloud billing accounts list
gcloud billing budgets list --billing-account={ACCOUNT_ID}
# Or use the billing export in BigQuery
```

### AWS
```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## Step 2: Cost Breakdown by Category

```
Compute serving (N APIs × 2 clouds):  $___/mo
Compute training (Spot, monthly avg):  $___/mo
Databases (Cloud SQL + RDS):           $___/mo
Storage (GCS + S3):                    $___/mo
Registry (Artifact Registry + ECR):    $___/mo
Monitoring and Logging:                $___/mo
TOTAL:                                 $___/mo
```

## Step 3: Check FinOps Rules

| Rule | Status | Action if Violated |
|------|--------|-------------------|
| Training on Spot/Preemptible | ✅/❌ | Switch to spot instances (70% savings) |
| Serving on On-Demand | ✅/❌ | Do not change — availability required |
| CPU-only HPA (no idle pods) | ✅/❌ | Fix HPA to avoid over-provisioning |
| Lifecycle policies on buckets | ✅/❌ | Archive after N days, delete after M |
| Budget alerts at 50%/90% | ✅/❌ | Configure in Terraform |
| Non-prod clusters destroyed | ✅/❌ | `terraform destroy -var-file=staging.tfvars` |

## Step 4: Identify Optimization Opportunities

- **Right-sizing**: Check if node pool machine types match actual usage
- **Committed use**: If stable baseline, consider 1-year CUDs (30% savings)
- **Storage tiering**: Move infrequently accessed data to Nearline/Glacier
- **Image cleanup**: Delete old container images past retention period
- **Unused resources**: Check for orphaned disks, IPs, load balancers

## Step 5: Update Documentation

Update the TCO section in service READMEs and relevant ADRs with:
- Real measured costs (not estimates)
- Date of measurement
- Comparison with previous period
- Optimization actions taken and their impact

## Step 6: Budget Alert Verification

```bash
# GCP
terraform plan -target=google_billing_budget.ml_budget

# AWS
terraform plan -target=aws_budgets_budget.ml_budget
```

Verify alerts fire at 50% and 90% of monthly budget.

## Success criteria

The audit is complete when ALL of the following hold:

- [ ] Current costs collected from BOTH clouds (GCP billing + AWS Cost Explorer)
- [ ] Cost breakdown table populated with concrete dollar amounts per category
      (compute, storage, network, monitoring, MLflow tracking)
- [ ] Variance vs previous month documented; any single category with > 5%
      change has a one-line explanation
- [ ] Each FinOps rule violation has a corrective action with owner + due date
- [ ] Optimization opportunities ranked by estimated monthly savings
- [ ] ADRs and service READMEs updated with real measured costs (not estimates)
- [ ] Audit entry written to `ops/audit.jsonl` with operation=`cost_review`,
      result=`success`, link to the report
- [ ] Total spend < 120% of budget — else escalation_triggers fires STOP

If `apply_optimizations` was invoked (STOP-class), an additional human
sign-off must be linked from the audit entry per ADR-005.

## Related

- Rule: `.windsurf/rules/01-mlops-conventions.md` §FinOps
- Workflow: `.windsurf/workflows/cost-review.md`
- Invariants: cost-attribution labels per ADR-013
