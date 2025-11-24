import pandas as pd

from src.carvision.features import FeatureEngineer


def test_feature_engineering_consistency():
    df = pd.DataFrame(
        {
            "model_year": [2020, 2010],
            "model": ["ford f-150", "honda civic"],
            "price": [20000, 10000],
            "odometer": [10000, 20000],
        }
    )

    # Fixed year ensures reproducibility
    eng = FeatureEngineer(current_year=2024)
    res = eng.transform(df)

    assert "vehicle_age" in res.columns
    assert res.iloc[0]["vehicle_age"] == 4  # 2024 - 2020
    assert "brand" in res.columns
    assert res.iloc[0]["brand"] == "ford"
    assert "price_per_mile" in res.columns


def test_feature_engineering_no_price():
    # Inference scenario where price/odometer might be missing (or just price)
    df = pd.DataFrame(
        {
            "model_year": [2020],
            "model": ["ford f-150"],
        }
    )

    eng = FeatureEngineer(current_year=2024)
    res = eng.transform(df)

    assert "vehicle_age" in res.columns
    assert "brand" in res.columns
    # Derived analysis features shouldn't be created if missing cols
    assert "price_per_mile" not in res.columns
