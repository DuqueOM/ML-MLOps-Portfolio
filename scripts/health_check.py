#!/usr/bin/env python3
"""
Health Check Script for ML-MLOps Portfolio

This script validates that all 3 ML models can be loaded and make predictions.
Use this after cloning the repository to verify your environment is set up correctly.

Usage:
    python scripts/health_check.py

Requirements:
    - All project dependencies installed
    - Model artifacts present in each project's models/ or artifacts/ directory
"""

import sys
from pathlib import Path

# Add project roots to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "BankChurn-Predictor"))
sys.path.insert(0, str(ROOT / "CarVision-Market-Intelligence"))
sys.path.insert(0, str(ROOT / "TelecomAI-Customer-Intelligence"))


def check_bankchurn():
    """Verify BankChurn model loads and predicts."""
    print("🏦 Checking BankChurn-Predictor...", end=" ")
    try:
        import joblib
        import pandas as pd

        model_path = ROOT / "BankChurn-Predictor" / "models" / "model.pkl"
        if not model_path.exists():
            print("⚠️  Model not found (run training first)")
            return False

        model = joblib.load(model_path)

        # Sample prediction
        sample = pd.DataFrame(
            [
                {
                    "CreditScore": 650,
                    "Geography": "France",
                    "Gender": "Female",
                    "Age": 40,
                    "Tenure": 3,
                    "Balance": 60000.0,
                    "NumOfProducts": 2,
                    "HasCrCard": 1,
                    "IsActiveMember": 1,
                    "EstimatedSalary": 50000.0,
                }
            ]
        )

        pred = model.predict(sample)
        print(f"✅ OK (prediction: {pred[0]})")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def check_carvision():
    """Verify CarVision model loads and predicts."""
    print("🚗 Checking CarVision-Market-Intelligence...", end=" ")
    try:
        import joblib
        import pandas as pd

        model_path = ROOT / "CarVision-Market-Intelligence" / "artifacts" / "model.pkl"
        if not model_path.exists():
            print("⚠️  Model not found (run training first)")
            return False

        model = joblib.load(model_path)

        # Sample prediction
        sample = pd.DataFrame(
            [
                {
                    "model_year": 2015,
                    "model": "civic",
                    "condition": "good",
                    "cylinders": 4,
                    "fuel": "gas",
                    "odometer": 50000,
                    "transmission": "automatic",
                    "drive": "fwd",
                    "type": "sedan",
                    "paint_color": "white",
                }
            ]
        )

        pred = model.predict(sample)
        print(f"✅ OK (prediction: ${pred[0]:,.0f})")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def check_telecom():
    """Verify TelecomAI model loads and predicts."""
    print("📱 Checking TelecomAI-Customer-Intelligence...", end=" ")
    try:
        import joblib
        import pandas as pd

        model_path = ROOT / "TelecomAI-Customer-Intelligence" / "artifacts" / "model.pkl"
        if not model_path.exists():
            print("⚠️  Model not found (run training first)")
            return False

        model = joblib.load(model_path)

        # Sample prediction
        sample = pd.DataFrame([{"calls": 40.0, "minutes": 311.9, "messages": 83.0, "mb_used": 19915.42}])

        pred = model.predict(sample)
        print(f"✅ OK (prediction: {pred[0]})")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def main():
    """Run all health checks."""
    print("=" * 60)
    print("🔍 ML-MLOps Portfolio Health Check")
    print("=" * 60)
    print()

    results = []
    results.append(("BankChurn", check_bankchurn()))
    results.append(("CarVision", check_carvision()))
    results.append(("TelecomAI", check_telecom()))

    print()
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"  {name}: {status}")

    print()
    print(f"Result: {passed}/{total} models healthy")

    if passed == total:
        print("\n🎉 All systems operational!")
        return 0
    else:
        print("\n⚠️  Some models need attention. Run training or check artifacts.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
