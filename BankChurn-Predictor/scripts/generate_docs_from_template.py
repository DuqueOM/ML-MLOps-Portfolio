#!/usr/bin/env python3
"""
Script to generate documentation from templates.
Usage: python scripts/generate_docs_from_template.py --project-name "My Project"
"""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-name", required=True)
    args = parser.parse_args()

    templates_dir = Path("docs/_templates")
    if not templates_dir.exists():
        print("Templates directory not found.")
        return

    # Example of simple substitution
    for template_file in templates_dir.glob("*.template"):
        content = template_file.read_text()
        content = content.replace("[Project Name]", args.project_name)

        output_name = template_file.stem  # removes .template
        if output_name == "README.md":
            # Don't overwrite root README automatically for safety in this demo
            # output_path = Path(f"docs/GENERATED_{output_name}") # Unused
            pass
        else:
            # output_path = Path(output_name)  # root # Unused
            pass

        # print(f"Generating {output_path} from {template_file}...")
        # output_path.write_text(content)
        print(f"Preview generation for {output_name}:")
        print(content[:100] + "...")


if __name__ == "__main__":
    main()
