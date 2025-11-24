"""
Visualization components using Plotly.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.carvision.analysis import MarketAnalyzer


class VisualizationEngine:
    """Motor de visualizaciones para análisis de mercado."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def create_price_distribution_chart(self) -> go.Figure:
        """Crea gráfico de distribución de precios."""
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Histograma de Precios",
                "Box Plot por Categoría",
                "Precios por Año",
                "Top 10 Marcas",
            ),
            specs=[
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
            ],
        )

        if "price" in self.df.columns:
            # Histograma
            fig.add_trace(
                go.Histogram(x=self.df["price"], nbinsx=50, name="Distribución"),
                row=1,
                col=1,
            )

        if "price_category" in self.df.columns and "price" in self.df.columns:
            # Box plot por categoría
            for category in self.df["price_category"].unique():
                if pd.notna(category):
                    fig.add_trace(
                        go.Box(
                            y=self.df[self.df["price_category"] == category]["price"],
                            name=str(category),
                        ),
                        row=1,
                        col=2,
                    )

        if "model_year" in self.df.columns and "price" in self.df.columns:
            # Precios por año
            yearly_prices = self.df.groupby("model_year")["price"].mean()
            fig.add_trace(
                go.Scatter(
                    x=yearly_prices.index,
                    y=yearly_prices.values,
                    mode="lines+markers",
                    name="Precio Promedio",
                ),
                row=2,
                col=1,
            )

        if "model" in self.df.columns:
            # Top marcas
            if "brand" not in self.df.columns:
                self.df["brand"] = self.df["model"].str.split().str[0]
            top_brands = self.df["brand"].value_counts().head(10)
            fig.add_trace(
                go.Bar(
                    x=top_brands.values,
                    y=top_brands.index,
                    orientation="h",
                    name="Volumen",
                ),
                row=2,
                col=2,
            )

        fig.update_layout(height=800, title_text="Análisis de Precios del Mercado Automotriz")

        return fig

    def create_market_analysis_dashboard(self) -> go.Figure:
        """Crea dashboard completo de análisis de mercado."""
        # Crear análisis
        analyzer = MarketAnalyzer(self.df)
        summary = analyzer.generate_executive_summary()

        # Crear figura con subplots
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=(
                "KPIs Principales",
                "Oportunidades por Categoría",
                "Depreciación por Edad",
                "Market Share por Marca",
                "Precio vs Millaje",
                "Distribución por Condición",
            ),
            specs=[
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "pie"}],
                [{"type": "scatter"}, {"type": "bar"}],
            ],
        )

        # KPIs
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=summary["kpis"]["average_price"],
                title={"text": "Precio Promedio"},
                number={"prefix": "$", "valueformat": ",.0f"},
            ),
            row=1,
            col=1,
        )

        # Oportunidades
        opportunities = analyzer.analysis_results.get("opportunities", [])
        if opportunities:
            categories = [opp["category"] for opp in opportunities]
            values = [opp["potential_value"] for opp in opportunities]
            fig.add_trace(
                go.Bar(x=categories, y=values, name="Valor Potencial"),
                row=1,
                col=2,
            )

        # Depreciación
        depreciation = analyzer.analysis_results.get("depreciation", {}).get("by_age", {})
        if depreciation:
            ages = list(depreciation.keys())
            prices = list(depreciation.values())
            fig.add_trace(
                go.Scatter(x=ages, y=prices, mode="lines+markers", name="Depreciación"),
                row=2,
                col=1,
            )

        # Market share
        market_by_brand = analyzer.analysis_results.get("market_by_brand", {})
        brand_volume = market_by_brand.get("volume", {})
        if brand_volume:
            brands = list(brand_volume.keys())[:5]  # Top 5
            volumes = [brand_volume[brand] for brand in brands]
            fig.add_trace(
                go.Pie(labels=brands, values=volumes, name="Market Share"),
                row=2,
                col=2,
            )

        # Precio vs Millaje
        if "odometer" in self.df.columns and "price" in self.df.columns:
            sample_data = self.df.sample(min(1000, len(self.df)))  # Muestra para performance
            fig.add_trace(
                go.Scatter(
                    x=sample_data["odometer"],
                    y=sample_data["price"],
                    mode="markers",
                    name="Precio vs Millaje",
                    opacity=0.6,
                ),
                row=3,
                col=1,
            )

        # Distribución por condición
        if "condition" in self.df.columns:
            condition_counts = self.df["condition"].value_counts()
            fig.add_trace(
                go.Bar(
                    x=condition_counts.index,
                    y=condition_counts.values,
                    name="Por Condición",
                ),
                row=3,
                col=2,
            )

        fig.update_layout(height=1200, title_text="CarVision Market Intelligence Dashboard")

        return fig
