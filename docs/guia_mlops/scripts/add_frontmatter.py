#!/usr/bin/env python3
"""add_frontmatter.py — Agrega front-matter YAML a archivos .md

Ejecutar desde la raíz de guia_mlops/:
    python3 scripts/add_frontmatter.py

Opciones:
    --dry-run     Solo muestra cambios sin aplicar
    --file PATH   Procesa solo un archivo específico
"""

import argparse
import os
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
MODULES_FILE = ROOT / "MODULES_CANON.yaml"


def load_modules_canon() -> dict:
    """Carga configuración de módulos."""
    with open(MODULES_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def has_frontmatter(content: str) -> bool:
    """Verifica si ya tiene front-matter."""
    return content.strip().startswith("---")


def extract_title(content: str) -> str:
    """Extrae título del primer H1."""
    for line in content.split("\n"):
        if line.strip().startswith("# "):
            return line.strip().lstrip("# ").strip()
    return ""


def extract_tags_from_content(content: str) -> list:
    """Extrae tags del contenido basado en keywords."""
    tags = []
    content_lower = content.lower()

    keyword_tags = {
        "python": "python",
        "pydantic": "pydantic",
        "sklearn": "sklearn",
        "mlflow": "mlflow",
        "dvc": "dvc",
        "fastapi": "fastapi",
        "streamlit": "streamlit",
        "docker": "docker",
        "kubernetes": "kubernetes",
        "github actions": "ci-cd",
        "testing": "testing",
        "pytest": "testing",
        "observabilidad": "observability",
        "monitoring": "monitoring",
        "entrevista": "interview",
        "speech": "presentation",
        "portafolio": "portfolio",
    }

    for keyword, tag in keyword_tags.items():
        if keyword in content_lower:
            if tag not in tags:
                tags.append(tag)

    return tags[:5]  # Máximo 5 tags


def generate_frontmatter(
    title: str,
    module: str,
    order: int,
    tags: list,
    status: str = "ready",
) -> str:
    """Genera front-matter YAML."""
    fm = {
        "title": title,
        "module": module,
        "order": order,
        "tags": tags,
        "status": status,
    }

    yaml_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return f"---\n{yaml_str}---\n\n"


def process_file(
    filepath: Path,
    file_mapping: dict,
    dry_run: bool = False,
) -> bool:
    """Procesa un archivo y agrega front-matter si falta.

    Returns:
        True si se modificó el archivo
    """
    rel_path = str(filepath.relative_to(ROOT))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Si ya tiene front-matter, skip
    if has_frontmatter(content):
        print(f"  ✓ {rel_path} (ya tiene front-matter)")
        return False

    # Obtener información
    title = extract_title(content) or filepath.stem.replace("_", " ").title()
    module = file_mapping.get(rel_path, "APENDICE")
    tags = extract_tags_from_content(content)

    # Determinar orden basado en nombre de archivo
    order = 1
    match = re.match(r"^(\d+)", filepath.stem)
    if match:
        order = int(match.group(1))

    # Generar front-matter
    frontmatter = generate_frontmatter(title, module, order, tags)

    # Nuevo contenido
    new_content = frontmatter + content

    if dry_run:
        print(f"  📝 {rel_path}")
        print(f"     Módulo: {module}, Título: {title[:40]}...")
        print(f"     Tags: {tags}")
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  ✅ {rel_path}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Agrega front-matter YAML a archivos .md")
    parser.add_argument("--dry-run", action="store_true", help="Solo mostrar cambios")
    parser.add_argument("--file", type=str, help="Procesar solo un archivo")
    args = parser.parse_args()

    print("=" * 60)
    print("AGREGANDO FRONT-MATTER A ARCHIVOS .MD")
    print("=" * 60)

    # Cargar configuración
    canon = load_modules_canon()
    file_mapping = canon.get("file_mapping", {})

    if args.dry_run:
        print("🔍 Modo DRY-RUN (sin cambios)\n")

    # Encontrar archivos
    if args.file:
        md_files = [ROOT / args.file]
    else:
        md_files = []
        for subdir, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in ["archive", "backup", ".git", "__pycache__", "reports"]]
            for file in files:
                if file.endswith(".md"):
                    md_files.append(Path(subdir) / file)

    md_files.sort()

    modified = 0
    skipped = 0

    for filepath in md_files:
        if process_file(filepath, file_mapping, args.dry_run):
            modified += 1
        else:
            skipped += 1

    print("\n" + "=" * 60)
    print(f"RESUMEN: {modified} modificados, {skipped} sin cambios")
    print("=" * 60)

    if args.dry_run and modified > 0:
        print("\n💡 Ejecuta sin --dry-run para aplicar cambios")


if __name__ == "__main__":
    main()
