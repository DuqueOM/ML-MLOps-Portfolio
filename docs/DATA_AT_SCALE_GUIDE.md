# Data at Scale — Project Guidance

> Local guide for adding a larger-scale data processing project to the portfolio.
> Created March 2026.

## Why This Matters

Your current portfolio datasets:
- **BankChurn**: 10K rows, 11 columns (~1MB)
- **CarVision**: ~50K rows after cleaning (~11MB raw)
- **NLPInsight**: 4,845 sentences (~200KB)

These are fine for demonstrating ML quality, but MLOps roles often involve:
- Datasets with **millions+ rows**
- **Batch processing** pipelines (Spark, Dask, Ray)
- **Data warehousing** patterns (partitioning, schema evolution)
- **Streaming** ingestion (Kafka, Pub/Sub)

Adding one project that handles data at scale would fill this gap.

---

## Option A: Extend Chicago-Mobility-Analytics (Recommended)

**Why**: Chicago taxi data is publicly available at scale (200M+ trips since 2013).

### What to build

1. **Data pipeline**: Download full Chicago taxi dataset (~20GB CSV)
2. **Processing**: Use PySpark or Dask to process the full dataset
3. **Feature engineering**: Same temporal + weather features, but at scale
4. **Storage**: Parquet partitioned by year/month
5. **Training**: Distributed training or batch prediction
6. **Serving**: Same FastAPI pattern, but with batch prediction endpoint

### Implementation steps

```bash
# 1. Download full dataset (or a large subset)
# Chicago Open Data API: https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew
# Export as CSV — full dataset is ~70M rows

# 2. Process with PySpark
pip install pyspark

# 3. Create processing script
# scripts/process_large_dataset.py
```

### Key code to write

```python
# scripts/process_large_dataset.py
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder \
    .appName("ChicagoMobility-LargeScale") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

# Read raw CSV
df = spark.read.csv("data/raw/taxi_trips_full.csv", header=True, inferSchema=True)

# Feature engineering at scale
df = df.withColumn("hour", F.hour("trip_start_timestamp"))
df = df.withColumn("day_of_week", F.dayofweek("trip_start_timestamp"))
df = df.withColumn("month", F.month("trip_start_timestamp"))

# Aggregate: trips per hour per pickup area
hourly = df.groupBy("hour", "day_of_week", "month", "pickup_community_area") \
    .agg(F.count("*").alias("trip_count"))

# Write partitioned Parquet
hourly.write.partitionBy("month").parquet("data/processed/hourly_demand/")
```

### What this demonstrates to recruiters
- Spark/Dask experience (listed in many MLOps JDs)
- Parquet + partitioning (data engineering basics)
- Same ML model but at production scale
- Understanding of when to use distributed tools vs pandas

---

## Option B: Synthetic Large-Scale Pipeline

If you don't want to download large datasets, generate synthetic data:

```python
# scripts/generate_synthetic_data.py
import numpy as np
import pandas as pd

N = 5_000_000  # 5 million rows

df = pd.DataFrame({
    "timestamp": pd.date_range("2020-01-01", periods=N, freq="s"),
    "sensor_id": np.random.randint(1, 100, N),
    "temperature": np.random.normal(25, 5, N),
    "pressure": np.random.normal(1013, 10, N),
    "vibration": np.random.exponential(0.5, N),
    "anomaly": np.random.binomial(1, 0.02, N),  # 2% anomaly rate
})

# Write in chunks to simulate streaming
for i, chunk in enumerate(np.array_split(df, 50)):
    chunk.to_parquet(f"data/raw/batch_{i:03d}.parquet")
```

Then build an anomaly detection pipeline on top of it.

---

## Option C: Add Spark/Dask Processing to Existing BankChurn

Lightest option — add a `scripts/batch_predict.py` that:
1. Reads a large CSV (generate 1M synthetic customers)
2. Processes in batches using Dask
3. Writes predictions to Parquet
4. Reports latency and throughput metrics

```python
# scripts/batch_predict.py
import dask.dataframe as dd
import joblib

model = joblib.load("models/model.joblib")
ddf = dd.read_csv("data/large_customers.csv")

# Process in partitions
predictions = ddf.map_partitions(
    lambda pdf: pdf.assign(churn_prob=model.predict_proba(pdf[features])[:, 1])
)
predictions.to_parquet("data/predictions/", write_index=False)
```

---

## Recommendation

**Option A (Chicago-Mobility with PySpark)** is the strongest choice because:
1. Uses real public data (not synthetic)
2. PySpark is the #1 requested skill for data/ML engineering
3. You already have the project structure and domain knowledge
4. Can be done incrementally (start with 1M rows, scale up)

### Effort estimate
- Download + PySpark processing script: 2-3 hours
- Integration with existing project: 1-2 hours
- Documentation: 1 hour
- Total: **4-6 hours**

### What to add to CV after completing this
```
- **Batch processing**: PySpark pipeline processing 70M+ taxi trips into
  partitioned Parquet for distributed model training
```
