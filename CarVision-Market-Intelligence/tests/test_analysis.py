import pandas as pd
import pytest

from src.carvision.analysis import MarketAnalyzer


def test_market_analyzer_methods():
    df = pd.DataFrame(
        {
            "price": [10000, 15000, 20000, 5000, 30000],
            "model_year": [2015, 2016, 2017, 2010, 2018],
            "model": ["ford focus", "honda civic", "audi a4", "ford focus", "bmw 320i"],
            "odometer": [50000, 40000, 30000, 100000, 10000],
            "price_category": ["Budget", "Mid-Range", "Mid-Range", "Budget", "Premium"],
            "vehicle_age": [9, 8, 7, 14, 6],
        }
    )

    analyzer = MarketAnalyzer(df)

    # Price Distribution
    dist = analyzer.analyze_price_distribution()
    assert "statistics" in dist
    assert "distribution" in dist
    assert dist["statistics"]["mean"] == 16000.0

    # Market by Brand
    brand_stats = analyzer.analyze_market_by_brand()
    assert "volume" in brand_stats
    assert "pricing" in brand_stats
    assert "ford" in brand_stats["volume"]  # Brand derived from model if missing

    # Depreciation
    depr = analyzer.analyze_depreciation_patterns()
    assert "by_age" in depr
    assert "annual_rate" in depr

    # Opportunities
    opps = analyzer.find_market_opportunities()
    assert isinstance(opps, list)
    # Check if any opportunity found (might be none with this small data)

    # Executive Summary
    summary = analyzer.generate_executive_summary()
    assert "kpis" in summary
    assert "insights" in summary
    assert "recommendations" in summary
    assert summary["kpis"]["total_vehicles"] == 5


def test_market_analyzer_missing_columns():
    df = pd.DataFrame({"other": [1, 2, 3]})
    analyzer = MarketAnalyzer(df)

    assert analyzer.analyze_price_distribution() == {}
    assert analyzer.analyze_market_by_brand() == {}
    assert analyzer.analyze_depreciation_patterns() == {}
    assert analyzer.find_market_opportunities() == []

    summary = analyzer.generate_executive_summary()
    assert summary["kpis"]["total_vehicles"] == 3
    assert summary["kpis"]["average_price"] == 0.0
