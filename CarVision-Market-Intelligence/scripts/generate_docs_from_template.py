#!/usr/bin/env python3
"""
Documentation Generator Script.
Applies the common DOCS_TEMPLATE.md to the current project by substituting placeholders.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = PROJECT_ROOT / "docs" / "templates" / "DOCS_TEMPLATE.md"
README_PATH = PROJECT_ROOT / "README.md"

# Project-specific configuration
# In a real multi-repo setup, these could be arguments or loaded from a config file.
CONFIG = {
    "PROJECT_NAME": "CarVision Market Intelligence",
    "REPO_OWNER": "DuqueOM",
    "REPO_NAME": "ML-MLOps-Portfolio",
    "PROJECT_DESCRIPTION": (
        "**CarVision Market Intelligence** is an end-to-end MLOps solution for predicting "
        "vehicle market prices and analyzing automotive trends. It transforms raw classifieds "
        "data into actionable insights using a Random Forest regression model served via a "
        "scalable REST API and an interactive Streamlit dashboard."
    ),
}


def generate_docs():
    if not TEMPLATE_PATH.exists():
        print(f"Error: Template not found at {TEMPLATE_PATH}")
        return

    template_content = TEMPLATE_PATH.read_text()

    # Substitute placeholders
    content = template_content
    for key, value in CONFIG.items():
        content = content.replace(f"{{{key}}}", value)

    # Write to README.md
    # Note: We are not overwriting aggressively to avoid losing manual edits in this demo,
    # but in a standardized pipeline this would likely overwrite or check diffs.
    print("Generating README.md from template...")
    # README_PATH.write_text(content) # Uncomment to enforce overwrite
    print("Preview of generated header:")
    print("\n".join(content.split("\n")[:10]))
    print("\n(To apply changes, uncomment the write_text line in the script)")


if __name__ == "__main__":
    generate_docs()
