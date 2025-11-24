"""
Market analysis logic.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class MarketAnalyzer:
    """Analizador de mercado automotriz."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.analysis_results: Dict[str, Any] = {}

    def analyze_price_distribution(self) -> Dict[str, Any]:
        """Analiza la distribución de precios."""
        logger.info("Analizando distribución de precios")

        if "price" not in self.df.columns:
            logger.warning("Columna 'price' no encontrada.")
            return {}

        price_stats = {
            "mean": float(self.df["price"].mean()),
            "median": float(self.df["price"].median()),
            "std": float(self.df["price"].std()),
            "min": float(self.df["price"].min()),
            "max": float(self.df["price"].max()),
            "q25": float(self.df["price"].quantile(0.25)),
            "q75": float(self.df["price"].quantile(0.75)),
        }

        # Distribución por categoría de precio
        if "price_category" in self.df.columns:
            price_dist = self.df["price_category"].value_counts()
            price_dist_dict = price_dist.to_dict()
        else:
            price_dist_dict = {}

        self.analysis_results["price_distribution"] = {
            "statistics": price_stats,
            "distribution": price_dist_dict,
        }

        return self.analysis_results["price_distribution"]

    def analyze_market_by_brand(self) -> Dict[str, Any]:
        """Analiza el mercado por marca."""
        logger.info("Analizando mercado por marca")

        if "model" not in self.df.columns:
            return {}

        # Ensure brand column exists
        if "brand" not in self.df.columns:
            self.df["brand"] = self.df["model"].str.split().str[0]

        # Top marcas por volumen
        brand_volume = self.df["brand"].value_counts().head(10)

        # Precio promedio por marca
        if "price" in self.df.columns:
            brand_price = self.df.groupby("brand")["price"].agg(["mean", "median", "count"]).round(0)
            brand_price = brand_price[brand_price["count"] >= 100].sort_values("mean", ascending=False)
            pricing_dict = brand_price.to_dict()
        else:
            pricing_dict = {}

        self.analysis_results["market_by_brand"] = {
            "volume": brand_volume.to_dict(),
            "pricing": pricing_dict,
        }

        return self.analysis_results["market_by_brand"]

    def analyze_depreciation_patterns(self) -> Dict[str, Any]:
        """Analiza patrones de depreciación."""
        logger.info("Analizando patrones de depreciación")

        if "vehicle_age" not in self.df.columns or "price" not in self.df.columns:
            return {}

        # Depreciación por edad
        depreciation = self.df.groupby("vehicle_age")["price"].mean().sort_index()

        # Tasa de depreciación anual
        depreciation_rate = depreciation.pct_change().fillna(0) * -1

        self.analysis_results["depreciation"] = {
            "by_age": depreciation.to_dict(),
            "annual_rate": depreciation_rate.to_dict(),
        }

        return self.analysis_results["depreciation"]

    def find_market_opportunities(self) -> List[Dict[str, Any]]:
        """Identifica oportunidades de mercado."""
        logger.info("Identificando oportunidades de mercado")

        opportunities = []

        required = ["price_category", "price", "vehicle_age", "odometer"]
        if not all(col in self.df.columns for col in required):
            return []

        # Vehículos subvalorados (precio < percentil 25 para su categoría)
        for category in self.df["price_category"].unique():
            if pd.isna(category):
                continue

            category_data = self.df[self.df["price_category"] == category]
            if len(category_data) == 0:
                continue

            price_threshold = category_data["price"].quantile(0.25)

            undervalued = category_data[
                (category_data["price"] < price_threshold)
                & (category_data["vehicle_age"] <= 10)
                & (category_data["odometer"] <= 100000)
            ]

            if len(undervalued) > 0:
                opportunities.append(
                    {
                        "category": str(category),
                        "count": int(len(undervalued)),
                        "avg_price": float(undervalued["price"].mean()),
                        "potential_value": float(category_data["price"].median() - undervalued["price"].mean()),
                    }
                )

        self.analysis_results["opportunities"] = opportunities

        return opportunities

    def generate_executive_summary(self) -> Dict[str, Any]:
        """Genera resumen ejecutivo del análisis."""
        logger.info("Generando resumen ejecutivo")

        # Ejecutar todos los análisis si no se han ejecutado
        if "price_distribution" not in self.analysis_results:
            self.analyze_price_distribution()
        if "market_by_brand" not in self.analysis_results:
            self.analyze_market_by_brand()
        if "depreciation" not in self.analysis_results:
            self.analyze_depreciation_patterns()
        if "opportunities" not in self.analysis_results:
            self.find_market_opportunities()

        # KPIs principales
        total_vehicles = len(self.df)
        avg_price = float(self.df["price"].mean()) if "price" in self.df.columns else 0.0
        total_market_value = float(self.df["price"].sum()) if "price" in self.df.columns else 0.0

        # Oportunidades identificadas
        total_opportunities = sum([opp["count"] for opp in self.analysis_results.get("opportunities", [])])
        potential_value = sum(
            [opp["potential_value"] * opp["count"] for opp in self.analysis_results.get("opportunities", [])]
        )

        # Manejar casos sin suficientes datos de marca para evitar IndexError
        market_by_brand = self.analysis_results.get("market_by_brand", {})
        volume_dict = market_by_brand.get("volume", {}) or {}
        pricing_mean_dict = (market_by_brand.get("pricing") or {}).get("mean", {}) or {}

        # Tomar la primera marca disponible o "N/A" si no hay datos
        most_popular_brand = next(iter(volume_dict.keys()), "N/A")
        highest_value_brand = next(iter(pricing_mean_dict.keys()), "N/A")

        depr_rates = list(self.analysis_results.get("depreciation", {}).get("annual_rate", {}).values())
        avg_depr_rate = float(np.mean(depr_rates)) if depr_rates else 0.0

        summary = {
            "kpis": {
                "total_vehicles": total_vehicles,
                "average_price": avg_price,
                "total_market_value": total_market_value,
                "total_opportunities": total_opportunities,
                "potential_arbitrage_value": potential_value,
            },
            "insights": {
                "most_popular_brand": most_popular_brand,
                "highest_value_brand": highest_value_brand,
                "avg_depreciation_rate": avg_depr_rate,
            },
            "recommendations": [
                f"Focus on {total_opportunities} undervalued vehicles for potential ${potential_value:,.0f} profit",
                (f"Target {most_popular_brand} brand for volume opportunities"),
                "Implement dynamic pricing based on vehicle age and market conditions",
            ],
        }

        self.analysis_results["executive_summary"] = summary

        return summary
