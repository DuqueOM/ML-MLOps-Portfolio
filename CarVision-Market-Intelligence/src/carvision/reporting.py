"""
Reporting utilities.
"""

from __future__ import annotations

import logging
import time

from src.carvision.analysis import MarketAnalyzer

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generador de reportes automáticos."""

    def __init__(self, analyzer: MarketAnalyzer):
        self.analyzer = analyzer

    def generate_html_report(self, output_path: str) -> None:
        """Genera reporte HTML completo."""
        logger.info(f"Generando reporte HTML: {output_path}")

        # Obtener análisis completo
        summary = self.analyzer.generate_executive_summary()

        # Template HTML básico
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CarVision Market Intelligence Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .kpi {{ background: #f0f0f0; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                .insight {{ background: #e8f4fd; padding: 15px; margin: 10px 0; border-left: 4px solid #007acc; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>🚗 CarVision Market Intelligence Report</h1>
            <p><strong>Fecha de generación:</strong> {timestamp}</p>

            <h2>📊 KPIs Principales</h2>
            <div class="kpi">
                <h3>Métricas del Mercado</h3>
                <ul>
                    <li><strong>Total de Vehículos:</strong> {total_vehicles:,}</li>
                    <li><strong>Precio Promedio:</strong> ${avg_price:,.0f}</li>
                    <li><strong>Valor Total del Mercado:</strong> ${total_value:,.0f}</li>
                    <li><strong>Oportunidades Identificadas:</strong> {opportunities}</li>
                    <li><strong>Valor Potencial de Arbitraje:</strong> ${arbitrage_value:,.0f}</li>
                </ul>
            </div>

            <h2>💡 Insights Clave</h2>
            <div class="insight">
                <h3>Análisis de Mercado</h3>
                <ul>
                    <li><strong>Marca Más Popular:</strong> {popular_brand}</li>
                    <li><strong>Marca de Mayor Valor:</strong> {valuable_brand}</li>
                    <li><strong>Tasa de Depreciación Promedio:</strong> {depreciation_rate:.1%}</li>
                </ul>
            </div>

            <h2>🎯 Recomendaciones</h2>
            <ul>
        """.format(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            total_vehicles=summary["kpis"]["total_vehicles"],
            avg_price=summary["kpis"]["average_price"],
            total_value=summary["kpis"]["total_market_value"],
            opportunities=summary["kpis"]["total_opportunities"],
            arbitrage_value=summary["kpis"]["potential_arbitrage_value"],
            popular_brand=summary["insights"]["most_popular_brand"],
            valuable_brand=summary["insights"]["highest_value_brand"],
            depreciation_rate=summary["insights"]["avg_depreciation_rate"],
        )

        # Agregar recomendaciones
        for rec in summary["recommendations"]:
            html_template += f"<li>{rec}</li>"

        html_template += """
            </ul>

            <h2>📈 Oportunidades de Mercado</h2>
            <table>
                <tr>
                    <th>Categoría</th>
                    <th>Cantidad</th>
                    <th>Precio Promedio</th>
                    <th>Valor Potencial</th>
                </tr>
        """

        # Agregar oportunidades
        opportunities = self.analyzer.analysis_results.get("opportunities", [])
        for opp in opportunities:
            html_template += f"""
                <tr>
                    <td>{opp['category']}</td>
                    <td>{opp['count']}</td>
                    <td>${opp['avg_price']:,.0f}</td>
                    <td>${opp['potential_value']:,.0f}</td>
                </tr>
            """

        html_template += """
            </table>

            <footer>
                <p><em>Reporte generado por CarVision Market Intelligence v1.0.0</em></p>
            </footer>
        </body>
        </html>
        """

        # Guardar reporte
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_template)

        logger.info(f"Reporte HTML guardado en: {output_path}")
