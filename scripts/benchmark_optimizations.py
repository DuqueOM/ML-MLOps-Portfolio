#!/usr/bin/env python3
"""
Benchmark script to measure performance improvements from optimizations.

Measures:
- Model loading time (with/without compression)
- DataFrame memory usage (with/without dtype optimization)
- Preprocessing time (with/without n_jobs=-1)
- Batch prediction time (with/without iterrows)
"""

import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# Add project roots to path
sys.path.insert(0, str(Path(__file__).parent.parent / "BankChurn-Predictor"))
sys.path.insert(0, str(Path(__file__).parent.parent / "CarVision-Market-Intelligence"))


def benchmark_joblib_compression():
    """Benchmark Joblib compression impact."""
    print("\n" + "=" * 60)
    print("BENCHMARK: Joblib Compression")
    print("=" * 60)

    # Create dummy model
    from sklearn.ensemble import RandomForestClassifier

    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    X_dummy = np.random.randn(1000, 20)
    y_dummy = np.random.randint(0, 2, 1000)
    model.fit(X_dummy, y_dummy)

    # Test without compression
    path_no_compress = Path("/tmp/model_no_compress.pkl")
    start = time.time()
    joblib.dump(model, path_no_compress, compress=0)
    time_no_compress = time.time() - start
    size_no_compress = path_no_compress.stat().st_size / (1024 * 1024)

    # Test with compression
    path_compress = Path("/tmp/model_compress.pkl")
    start = time.time()
    joblib.dump(model, path_compress, compress=3)
    time_compress = time.time() - start
    size_compress = path_compress.stat().st_size / (1024 * 1024)

    # Load times
    start = time.time()
    _ = joblib.load(path_no_compress)
    load_time_no_compress = time.time() - start

    start = time.time()
    _ = joblib.load(path_compress)
    load_time_compress = time.time() - start

    print("\n📦 Save Performance:")
    print(f"  No compression: {time_no_compress*1000:.2f}ms, Size: {size_no_compress:.2f}MB")
    print(f"  With compress=3: {time_compress*1000:.2f}ms, Size: {size_compress:.2f}MB")
    print(f"  💾 Size reduction: {((size_no_compress - size_compress) / size_no_compress * 100):.1f}%")

    print("\n📂 Load Performance:")
    print(f"  No compression: {load_time_no_compress*1000:.2f}ms")
    print(f"  With compress=3: {load_time_compress*1000:.2f}ms")

    # Cleanup
    path_no_compress.unlink()
    path_compress.unlink()

    return {
        "size_reduction_pct": ((size_no_compress - size_compress) / size_no_compress * 100),
        "save_time_ms": time_compress * 1000,
        "load_time_ms": load_time_compress * 1000,
    }


def benchmark_pandas_dtypes():
    """Benchmark Pandas dtype optimization."""
    print("\n" + "=" * 60)
    print("BENCHMARK: Pandas dtype Optimization")
    print("=" * 60)

    # Create dummy DataFrame
    n_rows = 100000
    df_data = {
        "price": np.random.uniform(1000, 50000, n_rows),
        "year": np.random.randint(1990, 2025, n_rows),
        "cylinders": np.random.randint(4, 8, n_rows),
        "odometer": np.random.uniform(0, 200000, n_rows),
        "condition": np.random.choice(["excellent", "good", "fair", "poor"], n_rows),
        "fuel": np.random.choice(["gas", "diesel", "electric", "hybrid"], n_rows),
        "transmission": np.random.choice(["automatic", "manual"], n_rows),
    }

    # Default dtypes
    df_default = pd.DataFrame(df_data)
    memory_default = df_default.memory_usage(deep=True).sum() / (1024 * 1024)

    # Optimized dtypes
    df_optimized = pd.DataFrame(
        {
            "price": df_data["price"].astype("float32"),
            "year": df_data["year"].astype("int16"),
            "cylinders": df_data["cylinders"].astype("int8"),
            "odometer": df_data["odometer"].astype("float32"),
            "condition": pd.Categorical(df_data["condition"]),
            "fuel": pd.Categorical(df_data["fuel"]),
            "transmission": pd.Categorical(df_data["transmission"]),
        }
    )
    memory_optimized = df_optimized.memory_usage(deep=True).sum() / (1024 * 1024)

    print(f"\n💾 Memory Usage ({n_rows:,} rows):")
    print(f"  Default dtypes: {memory_default:.2f}MB")
    print(f"  Optimized dtypes: {memory_optimized:.2f}MB")
    print(f"  💰 Memory reduction: {((memory_default - memory_optimized) / memory_default * 100):.1f}%")

    return {
        "memory_reduction_pct": ((memory_default - memory_optimized) / memory_default * 100),
        "memory_default_mb": memory_default,
        "memory_optimized_mb": memory_optimized,
    }


def benchmark_sklearn_parallelization():
    """Benchmark sklearn n_jobs parallelization."""
    print("\n" + "=" * 60)
    print("BENCHMARK: sklearn Parallelization")
    print("=" * 60)

    from sklearn.compose import ColumnTransformer
    from sklearn.preprocessing import StandardScaler

    # Create dummy data
    n_samples = 50000
    n_features = 50
    X = pd.DataFrame(np.random.randn(n_samples, n_features))

    # Without parallelization
    transformer_no_parallel = ColumnTransformer(
        transformers=[("scaler", StandardScaler(), list(range(n_features)))], n_jobs=1
    )

    start = time.time()
    transformer_no_parallel.fit_transform(X)
    time_no_parallel = time.time() - start

    # With parallelization
    transformer_parallel = ColumnTransformer(
        transformers=[("scaler", StandardScaler(), list(range(n_features)))], n_jobs=-1
    )

    start = time.time()
    transformer_parallel.fit_transform(X)
    time_parallel = time.time() - start

    print(f"\n⚡ Preprocessing Time ({n_samples:,} samples, {n_features} features):")
    print(f"  n_jobs=1: {time_no_parallel*1000:.2f}ms")
    print(f"  n_jobs=-1: {time_parallel*1000:.2f}ms")
    print(f"  🚀 Speedup: {time_no_parallel/time_parallel:.2f}x")

    return {
        "speedup": time_no_parallel / time_parallel,
        "time_no_parallel_ms": time_no_parallel * 1000,
        "time_parallel_ms": time_parallel * 1000,
    }


def benchmark_numpy_vectorization():
    """Benchmark NumPy vectorization improvements."""
    print("\n" + "=" * 60)
    print("BENCHMARK: NumPy Vectorization")
    print("=" * 60)

    n = 100000
    y_true = np.random.uniform(1000, 50000, n)
    y_pred = y_true + np.random.randn(n) * 1000

    # Old approach (with np.array conversion)
    start = time.time()
    for _ in range(100):
        y_t = np.array(y_true)
        y_p = np.array(y_pred)
        _ = np.mean(np.abs((y_t - y_p) / (y_t + 1e-8))) * 100
    time_old = time.time() - start

    # New approach (with np.asarray and np.maximum)
    start = time.time()
    for _ in range(100):
        y_t = np.asarray(y_true)
        y_p = np.asarray(y_pred)
        _ = np.mean(np.abs((y_t - y_p) / np.maximum(y_t, 1e-8))) * 100
    time_new = time.time() - start

    print(f"\n🔢 MAPE Calculation (100 iterations, {n:,} samples):")
    print(f"  Old approach: {time_old*1000:.2f}ms")
    print(f"  Optimized approach: {time_new*1000:.2f}ms")
    print(f"  🚀 Speedup: {time_old/time_new:.2f}x")

    return {
        "speedup": time_old / time_new,
        "time_old_ms": time_old * 1000,
        "time_new_ms": time_new * 1000,
    }


def benchmark_iterrows_elimination():
    """Benchmark elimination of iterrows()."""
    print("\n" + "=" * 60)
    print("BENCHMARK: Elimination of iterrows()")
    print("=" * 60)

    n = 10000
    df = pd.DataFrame(
        {
            "probability": np.random.rand(n),
            "prediction": np.random.randint(0, 2, n),
        }
    )

    # Old approach (with iterrows)
    start = time.time()
    results_old = []
    for i, row in df.iterrows():
        results_old.append(
            {
                "prob": float(row["probability"]),
                "pred": int(row["prediction"]),
            }
        )
    time_old = time.time() - start

    # New approach (list comprehension with iloc)
    start = time.time()
    _ = [
        {
            "prob": float(df.iloc[i]["probability"]),
            "pred": int(df.iloc[i]["prediction"]),
        }
        for i in range(len(df))
    ]
    time_new = time.time() - start

    print(f"\n Batch Processing ({n:,} predictions):")
    print(f"  With iterrows(): {time_old*1000:.2f}ms")
    print(f"  With iloc: {time_new*1000:.2f}ms")
    print(f"  🚀 Speedup: {time_old/time_new:.2f}x")

    return {
        "speedup": time_old / time_new,
        "time_old_ms": time_old * 1000,
        "time_new_ms": time_new * 1000,
    }


def main():
    """Run all benchmarks."""
    print("\n" + "=" * 60)
    print("🚀 ML-MLOps PORTFOLIO OPTIMIZATION BENCHMARKS")
    print("=" * 60)

    results = {}

    # Run benchmarks
    results["joblib"] = benchmark_joblib_compression()
    results["pandas"] = benchmark_pandas_dtypes()
    results["sklearn"] = benchmark_sklearn_parallelization()
    results["numpy"] = benchmark_numpy_vectorization()
    results["iterrows"] = benchmark_iterrows_elimination()

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY OF IMPROVEMENTS")
    print("=" * 60)
    print("\n✅ Joblib Compression:")
    print(f"   Size reduction: {results['joblib']['size_reduction_pct']:.1f}%")

    print("\n✅ Pandas dtype Optimization:")
    print(f"   Memory reduction: {results['pandas']['memory_reduction_pct']:.1f}%")

    print("\n✅ sklearn Parallelization:")
    print(f"   Speedup: {results['sklearn']['speedup']:.2f}x")

    print("\n✅ NumPy Vectorization:")
    print(f"   Speedup: {results['numpy']['speedup']:.2f}x")

    print("\n✅ Elimination of iterrows():")
    print(f"   Speedup: {results['iterrows']['speedup']:.2f}x")

    print("\n" + "=" * 60)
    print("✨ All benchmarks completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
