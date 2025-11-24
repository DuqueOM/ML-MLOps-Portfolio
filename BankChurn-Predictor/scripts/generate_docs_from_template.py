#!/usr/bin/env python3
"""
Script to generate documentation from templates.
Usage: python scripts/generate_docs_from_template.py --project-name "BankChurn-Predictor" --output-dir "BankChurn-Predictor"
"""
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-name", required=True, help="Name of the project")
    parser.add_argument("--output-dir", required=True, help="Directory to output generated docs")
    parser.add_argument("--template-path", default="docs/templates/DOCS_TEMPLATE.md", help="Path to template")
    args = parser.parse_args()

    template_path = Path(args.template_path)
    if not template_path.exists():
        logger.error(f"Template not found: {template_path}")
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read template
    content = template_path.read_text()

    # Simple replacements (In a real scenario, this could use Jinja2)
    content = content.replace("[Project Name]", args.project_name)
    # Add more replacements as needed or leave placeholders for manual filling

    # Output file
    output_file = output_dir / "README.md"

    # Check if we should overwrite
    if output_file.exists():
        logger.warning(f"{output_file} already exists. Saving as README_GENERATED.md to avoid overwrite.")
        output_file = output_dir / "README_GENERATED.md"

    output_file.write_text(content)
    logger.info(f"Generated {output_file}")


if __name__ == "__main__":
    main()
