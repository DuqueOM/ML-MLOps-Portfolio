# 📱 Data Card — TelecomAI Customer Intelligence Dataset

<div align="center">

**Telecom User Behavior Dataset**

![Records](https://img.shields.io/badge/records-3,214-blue)
![Features](https://img.shields.io/badge/features-4-green)
![Target](https://img.shields.io/badge/target-binary-orange)
![Last Updated](https://img.shields.io/badge/updated-March%202026-blue)

</div>

---

## 📋 Dataset Overview

| Attribute | Value |
|-----------|-------|
| **Dataset Name** | Telecom User Behavior Dataset |
| **Type** | Tabular (Monthly Usage Aggregates) |
| **Records** | 3,214 subscribers |
| **Features** | 4 base features (all numerical) |
| **Target Variable** | `is_ultra` (1=Ultra plan, 0=Smart plan) |
| **Class Distribution** | Smart: 69.4%, Ultra: 30.6% |
| **Time Period** | Monthly aggregated data (Jan-Dec 2018) |
| **Data Version** | v1.0.0 |
| **Last Updated** | March 2026 |

---

## 🎯 Intended Use

### Primary Purpose
Train classification models for **mobile plan recommendation** based on usage patterns, enabling revenue optimization and customer satisfaction through proper plan-customer alignment.

### Appropriate Use Cases
- ✅ Plan recommendation (Smart vs Ultra)
- ✅ Usage pattern analysis
- ✅ Targeted upsell campaigns
- ✅ Customer segmentation (light vs heavy users)
- ✅ Educational ML classification projects

### Inappropriate Use Cases
- ❌ **Churn prediction** (no churn labels, different problem)
- ❌ **Credit risk assessment** (no financial behavior data)
- ❌ **Network capacity planning** (no geographic/tower data)
- ❌ **Individual billing disputes** (monthly aggregates, not transactional)
- ❌ **Production deployment without calibration** (synthetic data, validate on real customers first)

---

## 📊 Schema & Features

### Base Features (All Numerical)

| Feature | Type | Range | Mean | Std | Description | Business Relevance |
|---------|------|-------|------|-----|-------------|-------------------|
| `calls` | float | 0-244 | 63.7 | 33.3 | Number of calls made/month | Basic usage indicator |
| `minutes` | float | 0-1632 | 438.2 | 234.8 | Total call duration (minutes/month) | Voice usage intensity |
| `messages` | float | 0-224 | 38.3 | 36.9 | SMS messages sent/month | Text usage pattern |
| `mb_used` | float | 0-49746 | 17207.7 | 7571.0 | Mobile data consumed (MB/month) | **Top predictor** (45% importance) |

### Target Variable

**`is_ultra`** (binary):
- `0`: Smart plan ($40/month, basic usage) - 69.4% of dataset
- `1`: Ultra plan ($70/month, heavy usage) - 30.6% of dataset

**Imbalance Ratio**: 2.26:1 (handled via class weights `{0: 0.4, 1: 0.6}`)

### Derived Features (Optional, for Advanced Models)

Not included in base dataset but can be engineered:
- `minutes_per_call` = `minutes` / (`calls` + 1)
- `messages_per_call` = `messages` / (`calls` + 1)
- `mb_per_minute` = `mb_used` / (`minutes` + 1)
- `usage_intensity` = (minutes + messages + mb_used/100) / calls

**Current Model**: Uses base 4 features only (StandardScaler preprocessing)

---

## 🔍 Data Quality

### Completeness
```
Missing Values: 0 (100% complete dataset)
Duplicates: 0 (unique subscriber records)
Invalid Entries: 0 (all values non-negative)
```

### Statistical Summary

**All Features**:
```
calls:    Min=0,   Max=244,   Median=63,     Q1=40,  Q3=82
minutes:  Min=0,   Max=1632,  Median=430.6,  Q1=274, Q3=598
messages: Min=0,   Max=224,   Median=30,     Q1=9,   Q3=60
mb_used:  Min=0,   Max=49746, Median=16943,  Q1=10422, Q3=23282
```

**Class-Conditional Statistics** (by plan):

| Feature | Smart Plan (n=2,229) | Ultra Plan (n=985) | Difference |
|---------|---------------------|-------------------|------------|
| **calls** | Mean=58.3 | Mean=76.5 | +31% |
| **minutes** | Mean=392.1 | Mean=548.7 | +40% |
| **messages** | Mean=32.1 | Mean=51.8 | +61% |
| **mb_used** | Mean=12,421 | Mean=28,467 | **+129%** ⬆️ |

**Key Insight**: Data consumption (`mb_used`) shows strongest separation between plans (2.3× higher for Ultra users).

### Outliers & Anomalies

| Feature | Outlier Threshold (99th percentile) | Count | Treatment |
|---------|-----------------------------------|-------|-----------|
| **calls** | >152 | 32 (1%) | Capped at 99th percentile |
| **minutes** | >987 | 32 (1%) | Capped at 99th percentile |
| **messages** | >141 | 32 (1%) | Capped at 99th percentile |
| **mb_used** | >40,188 | 32 (1%) | Capped at 99th percentile |

**Preprocessing**: Outliers capped (not removed) to preserve sample size.

---

## ⚖️ Bias & Fairness

### Representation Analysis

**Demographics**: ⚠️ **Not Available**
- No age, gender, location, or income data
- Prevents explicit fairness audits on protected attributes
- **Advantage**: Avoids explicit demographic bias
- **Disadvantage**: Cannot detect usage pattern bias by segment

### Usage Pattern Bias

| Segment | Threshold | Distribution | Potential Bias |
|---------|-----------|-------------|----------------|
| **Heavy Data Users** | >30 GB/month | 18% of dataset | ⚠️ Model may recommend Ultra even if cost-prohibitive |
| **Light Users** | <5 GB/month | 22% of dataset | ⚠️ May under-recommend Ultra to growing users |
| **Balanced Users** | 5-30 GB/month | 60% of dataset | ✅ Well-represented |

### Ethical Considerations

**Targeting Ethics**:
- ⚠️ **Aggressive Upselling Risk**: Model optimized for revenue (Ultra recommendations)
- ⚠️ **Customer Satisfaction**: Over-recommending Ultra may lead to overpayment complaints
- ✅ **Threshold Tuning**: Adjustable decision threshold (0.35-0.5) to balance revenue vs satisfaction

**Recommended Safeguards**:
1. Set contact frequency limits (max 1 upsell offer/quarter)
2. Provide opt-out mechanism for plan recommendations
3. Monitor churn rates for newly upgraded customers
4. Avoid penalizing low-data users (many prefer unlimited voice/text)

---

## 🔐 Privacy & Compliance

### Data Source & Licensing

| Attribute | Details |
|-----------|---------|
| **Origin** | TripleTen / Educational dataset (synthetic usage patterns) |
| **License** | MIT-compatible for portfolio/demo use |
| **PII Status** | ✅ **No PII**: Anonymized usage aggregates only |
| **Sensitive Data** | ✅ **None**: No location, demographics, or financial data |

### Privacy Guarantees

- ✅ **Aggregated Data**: Monthly totals only (no call logs, SMS content)
- ✅ **No Identifiers**: No phone numbers, account IDs, or names
- ✅ **No Geolocation**: No tower data, GPS, or address information
- ✅ **Anonymous**: Cannot re-identify individuals from usage patterns alone

### Production Deployment Considerations

**Before using with real customer data**:
1. ✅ Conduct privacy impact assessment (GDPR, CCPA compliance)
2. ✅ Implement data anonymization pipeline (k-anonymity)
3. ✅ Set up consent management for marketing campaigns
4. ✅ Define data retention policy (e.g., 90-day prediction logs)
5. ✅ Audit for unintended proxy variables (usage patterns correlated with demographics)

---

## 📂 Data Splits & Versioning

### Splitting Strategy

```python
Train:      2,571 records (80%)
Test:         643 records (20%)
Stratification: Maintains 69/31 plan distribution in both splits
Random Seed: 42 (reproducible)
```

**Validation**: 5-fold stratified cross-validation (Mean Accuracy=0.818 ± 0.012)

### Data Versioning

**File Location**: `data/raw/users_behavior.csv`  
**Size**: 142 KB (raw CSV)  
**DVC Tracking**: Optional (currently local file)

**Processed Data**:
- StandardScaler fit on train set only (prevents data leakage)
- Preprocessing bundled with model pipeline (`artifacts/model.joblib`)

---

## 🔄 Refresh Strategy

### Update Triggers

| Trigger | Frequency | Action |
|---------|-----------|--------|
| **Plan Pricing Change** | Event-driven | Immediate retrain (business rule change) |
| **Accuracy Drop** | Continuous | Retrain if AUC <0.80 |
| **Data Distribution Shift** | Weekly | Monitor via Evidently drift detection |
| **Scheduled Refresh** | Quarterly | Replace with latest usage data |

### Data Quality Checks (Automated)

```python
def validate_dataset(df):
    assert (df[['calls', 'minutes', 'messages', 'mb_used']] >= 0).all().all()
    assert df['is_ultra'].isin([0, 1]).all()
    assert df.duplicated().sum() == 0
    assert df.isnull().sum().sum() == 0
    
    # Class distribution check
    ultra_pct = df['is_ultra'].mean()
    assert 0.25 <= ultra_pct <= 0.35, "Class distribution shifted"
```

### Drift Monitoring

**Weekly Checks** (Evidently AI):
```python
# monitoring/check_drift.py
from evidently.metrics import DataDriftPreset

# Compare production data vs training reference
drift_report = Report(metrics=[DataDriftPreset()])
drift_report.run(reference_data=X_train, current_data=X_prod_weekly)

if drift_score > 0.3:
    alert_team("Usage patterns shifting (5G adoption, plan changes)")
```

**Key Drift Indicators**:
- **Data Usage Growth**: Expected upward trend as 5G adoption increases
- **Voice/SMS Decline**: Messaging apps replacing traditional SMS
- **Plan Distribution**: Should remain ~70/30; significant shift → investigate

---

## 📈 Known Issues & Limitations

### Data Limitations

1. **Synthetic Nature**: Educational dataset; patterns may not reflect real telecom usage
2. **No Temporal Component**: Single month snapshot (no seasonality, trends)
3. **Limited Features**: Only 4 basic metrics (missing):
   - Device type (smartphone vs feature phone)
   - Roaming usage
   - Customer tenure/lifetime value
   - Network quality indicators
   - Competitor plan offerings
4. **Binary Plans Only**: Real operators have 5-10+ plan tiers
5. **No Cost-Benefit**: Model recommends plan without considering customer budget

### Recommended Enhancements (Production)

- 📊 **Add temporal features**: Rolling 3-month averages, trend indicators
- 📱 **Device data**: Phone model, capabilities (4G/5G)
- 🌍 **Geographic data**: Urban vs rural (affects data usage)
- 💰 **Customer lifetime value**: High-value users may get different recommendations
- 📞 **Customer service interactions**: Support tickets, complaints
- 🔄 **Plan change history**: Prevent frequent flip-flopping

---

## 👥 Ownership & Contacts

| Role | Name | Responsibility |
|------|------|----------------|
| **Data Owner** | Duque Ortega Mutis (DuqueOM) | Dataset curation, versioning |
| **ML Engineer** | Duque Ortega Mutis (DuqueOM) | Feature engineering, preprocessing |

**Repository**: `TelecomAI-Customer-Intelligence/`  
**Documentation**: See [README.md](README.md) and [models/model_card.md](models/model_card.md)

---

## 📚 References

- **Project README**: [TelecomAI-Customer-Intelligence/README.md](README.md)
- **Model Card**: [models/model_card.md](models/model_card.md)
- **Architecture**: [Portfolio Architecture](../docs/ARCHITECTURE_PORTFOLIO.md)

---

<div align="center">

**Data Card Version**: 2.0 | **Last Updated**: March 2026  
**Dataset Version**: 1.0.0 | **Records**: 3,214

⭐ **Production-Ready Plan Recommendation Data** ⭐

</div>
