import sys
from pathlib import Path


def generate_docs(project_name, coverage, tldr, sample_req, sample_res):
    template_path = Path("docs/DOCS_TEMPLATE.md")
    if not template_path.exists():
        print("Template not found!")
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
    # TelecomAI Specifics
    generate_docs(
        project_name="TelecomAI Customer Intelligence",
        coverage="96",
        tldr="A production-ready ML system for predicting telecom customer churn/plan upgrades using Scikit-Learn and FastAPI. Features automated pipelines, Dockerized inference, and comprehensive testing.",
        sample_req='{\n  "calls": 40.0,\n  "minutes": 311.9,\n  "messages": 83.0,\n  "mb_used": 19915.42\n}',
        sample_res='{\n  "prediction": 0,\n  "probability_is_ultra": 0.12\n}',
    )
