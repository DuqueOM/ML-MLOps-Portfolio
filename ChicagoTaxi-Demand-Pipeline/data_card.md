# Data Card — Chicago Taxi Trips Dataset

| Attribute | Value |
|-----------|-------|
| **Dataset Name** | Chicago Taxi Trips (2013–2023) |
| **Type** | Tabular — Transportation / Mobility |
| **Raw Records** | 6,364,313 trip records |
| **Clean Records** | 5,369,172 (15.6% dropped by cleaning rules) |
| **Aggregated Records** | 357,055 hourly demand rows (used for modeling) |
| **Source** | [Chicago Open Data Portal](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew) |
| **License** | Open Data — public domain |
| **Format** | CSV (raw), Parquet (processed) |
| **Size** | 2.8 GB raw CSV → 95 MB Parquet (97% compression) |
| **Last Updated** | March 2026 |

---

## Intended Use

### Primary Purpose
Train hourly demand prediction models per Chicago community area. The aggregated dataset captures temporal patterns (rush hours, weekends, seasons) and spatial patterns (77 community areas with different demand profiles).

### Appropriate Use Cases
- Demand forecasting for ride-hailing resource allocation
- Urban mobility pattern analysis
- PySpark/Dask pipeline development and benchmarking
- Educational data engineering projects

### Inappropriate Use Cases
- Individual trip tracking or re-identification (data is anonymized)
- Fare prediction (fare is an input feature, not the target)
- Real-time routing (this is batch/aggregate data)
- Direct application to other cities (Chicago-specific geography)

---

## Schema

### Raw Columns (from source CSV)

| Column | Type | Description |
|--------|------|-------------|
| `Trip ID` | string | Anonymized trip identifier |
| `Taxi ID` | string | Anonymized taxi identifier |
| `Trip Start Timestamp` | datetime | Pickup time |
| `Trip End Timestamp` | datetime | Dropoff time |
| `Trip Seconds` | int | Duration in seconds |
| `Trip Miles` | float | Distance in miles |
| `Pickup Community Area` | int | Chicago community area (1–77) |
| `Dropoff Community Area` | int | Chicago community area (1–77) |
| `Fare` | string | Trip fare (currency format, e.g., "$12.50") |
| `Tips` | string | Tip amount (currency format) |
| `Tolls` | string | Toll charges |
| `Extras` | string | Extra charges |
| `Trip Total` | string | Total trip cost |
| `Payment Type` | string | Cash, Credit Card, etc. |
| `Company` | string | Taxi company name |

### Aggregated Columns (model input)

| Column | Type | Description |
|--------|------|-------------|
| `pickup_community_area` | int (1–77) | Community area ID |
| `hour` | int (0–23) | Hour of day |
| `day_of_week` | int (1–7) | Day of week (1=Sunday) |
| `is_weekend` | binary | Weekend indicator |
| `avg_distance_miles` | float | Mean trip distance in that hour/area |
| `avg_fare` | float | Mean fare in that hour/area |
| `avg_speed_mph` | float | Mean speed in that hour/area |
| `demand_count` | int | **Target** — number of trips in that hour/area |

---

## Data Quality

### Cleaning Rules Applied (PySpark ETL)

| Rule | Threshold | Rows Affected |
|------|-----------|--------------|
| Trip duration | 60s ≤ t ≤ 86,400s | ~8% dropped |
| Trip distance | 0.1 ≤ d ≤ 500 mi | ~3% dropped |
| Community area | 1 ≤ area ≤ 77 | ~4% dropped (nulls, 0s) |
| Fare range | $0 ≤ fare ≤ $10,000 | <1% dropped |
| **Total drop rate** | — | **15.6%** |

Rules are documented in `src/chicagotaxi/cleaning.py` with unit tests in `tests/test_cleaning.py`.

### Known Limitations

- **Temporal bias**: Data skews toward pre-pandemic patterns (2013–2019 dominates volume). Post-2020 trips are fewer due to COVID impact on taxi ridership.
- **Spatial bias**: ~60% of trips originate from 10 of 77 community areas (Loop, Near North, O'Hare, etc.). Low-traffic areas have sparse hourly counts.
- **Missing fields**: ~4% of rows lack community area IDs (dropped during cleaning).
- **Currency parsing**: Fare columns use string format ("$12.50") requiring `strip_currency()` preprocessing.

---

## Privacy & Ethics

- **No PII**: Trip and taxi IDs are anonymized hashes in the source dataset
- **Public data**: Released by City of Chicago under open data policy
- **Aggregation**: Model training uses hourly aggregates, not individual trips
- **Fairness concern**: Low-demand areas often correlate with lower-income neighborhoods. Model predictions should inform equitable service allocation, not justify service reduction

---

## Versioning

| Version | Date | Description |
|---------|------|-------------|
| v1.0.0 | March 2026 | Initial ETL from 2013–2023 CSV extract |

Data tracked via `.gitignore` (raw CSV too large for Git). Processed Parquet outputs are reproducible by re-running the ETL pipeline:

```bash
python scripts/spark_etl.py --input <path-to-csv> --output data/processed/
```

---

*Last Updated: March 2026 — v3.5.0*
