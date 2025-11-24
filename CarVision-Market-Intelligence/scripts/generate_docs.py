import sys
from pathlib import Path


def generate_docs():
    project_name = "CarVision Market Intelligence"
    coverage = "96"
    tldr = "End-to-end ML system for vehicle price prediction and market analytics. Features centralized feature engineering, FastAPI serving, and Streamlit dashboards."

    sample_req = """{
  "model_year": 2018,
  "odometer": 45000,
  "model": "ford f-150",
  "fuel": "gas",
  "transmission": "automatic"
}"""

    sample_res = """{
  "prediction": 24500.0,
  "vehicle_age": 6,
  "brand": "ford"
}"""

    template_path = Path("docs/DOCS_TEMPLATE.md")
    if not template_path.exists():
        print(f"Template not found at {template_path}")
        sys.exit(1)

    template = template_path.read_text()
    content = template.format(
        PROJECT_NAME=project_name,
        COVERAGE_PERCENT=coverage,
        TLDR_SUMMARY=tldr,
        SAMPLE_REQUEST_JSON=sample_req,
        SAMPLE_RESPONSE_JSON=sample_res,
    )

    readme_path = Path("README.md")
    readme_path.write_text(content)
    print(f"Generated {readme_path}")


if __name__ == "__main__":
    generate_docs()
