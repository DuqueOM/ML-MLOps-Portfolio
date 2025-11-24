#!/usr/bin/env python3
"""
CarVision Market Intelligence - Sistema de análisis de mercado automotriz

Uso:
    python main.py --mode analysis --input data/raw/vehicles_us.csv
    python main.py --mode dashboard --port 8501
    python main.py --mode report --output reports/market_analysis.html
    python main.py --mode export --format excel --output market_data.xlsx

Autor: Daniel Duque
Versión: 1.0.0
Fecha: 2024-11-16
"""

import argparse
import json
import logging
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any, Dict

import yaml

# Core imports
from src.carvision.analysis import MarketAnalyzer
from src.carvision.data import clean_data, load_data
from src.carvision.evaluation import evaluate_model
from src.carvision.prediction import predict_price
from src.carvision.reporting import ReportGenerator
from src.carvision.training import train_model

try:
    from common_utils.seed import set_seed
except ModuleNotFoundError:  # pragma: no cover
    BASE_DIR = Path(__file__).resolve().parents[1]
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    from common_utils.seed import set_seed

# Configuración de warnings y logging
warnings.filterwarnings("ignore", category=FutureWarning)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("carvision.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    """Función principal con CLI."""
    parser = argparse.ArgumentParser(description="CarVision Market Intelligence - Análisis de mercado automotriz")

    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=[
            "analysis",
            "dashboard",
            "report",
            "export",
            "train",
            "eval",
            "predict",
        ],
        help="Modo de ejecución",
    )

    parser.add_argument(
        "--input",
        type=str,
        default="data/raw/vehicles_us.csv",
        help="Ruta al archivo de datos de entrada",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Ruta de salida para reportes/exports",
    )

    parser.add_argument(
        "--format",
        type=str,
        default="html",
        choices=["html", "excel", "json"],
        help="Formato de salida",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Puerto para dashboard Streamlit",
    )

    parser.add_argument(
        "--config",
        type=str,
        default="configs/config.yaml",
        help="Archivo de configuración",
    )

    parser.add_argument(
        "--input_json",
        type=str,
        default=None,
        help="Ruta a JSON con payload para modo predict",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Semilla para reproducibilidad (sobrescribe config)",
    )

    args = parser.parse_args()

    # Resolver semilla global (CLI > SEED env > 42)
    seed_used = set_seed(args.seed)
    logger.info("Using seed: %s", seed_used)

    # Crear directorios necesarios
    Path("reports").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    try:
        if args.mode == "analysis":
            logger.info("=== MODO ANÁLISIS ===")
            df = clean_data(load_data(args.input))
            analyzer = MarketAnalyzer(df)
            summary = analyzer.generate_executive_summary()

            print("\n=== RESUMEN EJECUTIVO ===")
            print(f"Total de vehículos analizados: {summary['kpis']['total_vehicles']:,}")
            print(f"Precio promedio: ${summary['kpis']['average_price']:,.0f}")
            print(f"Oportunidades identificadas: {summary['kpis']['total_opportunities']}")
            print(f"Valor potencial de arbitraje: ${summary['kpis']['potential_arbitrage_value']:,.0f}")

            print("\n=== INSIGHTS CLAVE ===")
            for key, value in summary["insights"].items():
                print(f"{key}: {value}")

        elif args.mode == "dashboard":
            logger.info("=== MODO DASHBOARD ===")
            subprocess.run(
                [
                    "streamlit",
                    "run",
                    "app/streamlit_app.py",
                    "--server.port",
                    str(args.port),
                ]
            )

        elif args.mode == "report":
            logger.info("=== MODO REPORTE ===")
            df = clean_data(load_data(args.input))
            analyzer = MarketAnalyzer(df)
            report_gen = ReportGenerator(analyzer)

            if args.format == "html":
                output_file = f"{args.output}.html" if not args.output.endswith(".html") else args.output
                report_gen.generate_html_report(output_file)

            logger.info(f"Reporte generado: {output_file}")

        elif args.mode == "export":
            logger.info("=== MODO EXPORT ===")
            df_clean = clean_data(load_data(args.input))
            if args.format == "excel":
                output_file = f"{args.output}.xlsx" if not args.output.endswith(".xlsx") else args.output
                df_clean.to_excel(output_file, index=False)
            elif args.format == "json":
                output_file = f"{args.output}.json" if not args.output.endswith(".json") else args.output
                df_clean.to_json(output_file, orient="records", indent=2)
            logger.info(f"Datos exportados: {output_file}")

        elif args.mode == "train":
            logger.info("=== MODO TRAIN ===")
            cfg = load_config(args.config)
            cfg["seed"] = int(seed_used)
            result = train_model(cfg)
            logger.info(f"Modelo guardado en: {result['model_path']}")
            print(json.dumps(result["val_metrics"], indent=2))

        elif args.mode == "eval":
            logger.info("=== MODO EVAL ===")
            cfg = load_config(args.config)
            cfg["seed"] = int(seed_used)
            results = evaluate_model(cfg)
            print(json.dumps(results, indent=2))

        elif args.mode == "predict":
            logger.info("=== MODO PREDICT ===")
            if not args.input_json or not Path(args.input_json).exists():
                raise FileNotFoundError("Debe especificar --input_json con ruta válida")

            cfg = load_config(args.config)
            cfg["seed"] = int(seed_used)
            payload = json.loads(Path(args.input_json).read_text())

            result = predict_price(payload, cfg)
            print(json.dumps(result, indent=2))

    except Exception as e:
        logger.error(f"Error en ejecución: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
