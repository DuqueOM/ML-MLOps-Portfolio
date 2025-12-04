#!/usr/bin/env python3
"""make_manifest.py — Genera inventario de archivos .md y detecta inconsistencias.

Ejecutar desde la raíz de guia_mlops/:
    python scripts/make_manifest.py

Produce:
    - MANIFEST.csv: inventario completo de archivos
    - reports/orphans_report.md: archivos sin módulo asignado
    - reports/inconsistencies.md: problemas detectados
"""

import csv
import os
import re
from datetime import datetime
from pathlib import Path

import yaml

# Configuración
ROOT = Path(__file__).parent.parent
MODULES_FILE = ROOT / "MODULES_CANON.yaml"
MKDOCS_FILE = ROOT / "mkdocs.yml"
OUT_MANIFEST = ROOT / "MANIFEST.csv"
REPORTS_DIR = ROOT / "reports"

MD_EXT = ".md"


def read_first_header(path: Path) -> str:
    """Lee el primer H1 o título del front-matter."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Intentar front-matter primero
        fm = extract_front_matter(path)
        if fm and "title" in fm:
            return fm["title"]

        # Buscar primer H1
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# "):
                return line.lstrip("# ").strip()

        return ""
    except Exception:
        return ""


def extract_front_matter(path: Path) -> dict:
    """Extrae front-matter YAML si existe."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        if not text.startswith("---"):
            return {}

        # Encontrar cierre del front-matter
        end = text.find("---", 3)
        if end == -1:
            return {}

        fm_text = text[3:end]
        return yaml.safe_load(fm_text) or {}
    except Exception:
        return {}


def has_front_matter(path: Path) -> bool:
    """Verifica si el archivo tiene front-matter."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
        return first_line == "---"
    except Exception:
        return False


def get_file_size(path: Path) -> int:
    """Obtiene tamaño del archivo en bytes."""
    return path.stat().st_size


def count_words(path: Path) -> int:
    """Cuenta palabras aproximadas."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        # Remover código
        text = re.sub(r"```[\s\S]*?```", "", text)
        return len(text.split())
    except Exception:
        return 0


def load_modules_canon() -> dict:
    """Carga el archivo de módulos canónicos."""
    if not MODULES_FILE.exists():
        return {}

    with open(MODULES_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_mkdocs_nav() -> set:
    """Extrae archivos referenciados en mkdocs.yml nav."""
    if not MKDOCS_FILE.exists():
        return set()

    try:
        with open(MKDOCS_FILE, "r", encoding="utf-8") as f:
            # Usar Loader básico que ignora tags desconocidos
            mkdocs = yaml.load(f, Loader=yaml.BaseLoader)
    except Exception as e:
        print(f"⚠️ Error leyendo mkdocs.yml: {e}")
        return set()

    nav_files = set()

    def extract_files(nav_item):
        if isinstance(nav_item, dict):
            for v in nav_item.values():
                extract_files(v)
        elif isinstance(nav_item, list):
            for item in nav_item:
                extract_files(item)
        elif isinstance(nav_item, str) and nav_item.endswith(".md"):
            nav_files.add(nav_item)

    if "nav" in mkdocs:
        extract_files(mkdocs["nav"])

    return nav_files


def main():
    print("=" * 60)
    print("GENERANDO MANIFEST DE GUÍA MLOPS")
    print("=" * 60)

    # Crear directorio de reportes
    REPORTS_DIR.mkdir(exist_ok=True)

    # Cargar datos
    canon = load_modules_canon()
    file_mapping = canon.get("file_mapping", {})
    modules = canon.get("modules", {})
    nav_files = load_mkdocs_nav()

    # Encontrar todos los .md
    md_files = []
    for subdir, dirs, files in os.walk(ROOT):
        # Excluir directorios de backup
        dirs[:] = [d for d in dirs if d not in ["archive", "backup", ".git", "__pycache__"]]

        for file in files:
            if file.lower().endswith(MD_EXT):
                full_path = Path(subdir) / file
                md_files.append(full_path)

    md_files.sort()
    print(f"\nEncontrados {len(md_files)} archivos .md")

    # Construir manifest
    rows = []
    orphans = []
    no_frontmatter = []

    for md in md_files:
        rel = str(md.relative_to(ROOT))
        title = read_first_header(md) or md.stem
        fm = extract_front_matter(md)

        # Obtener módulo asignado
        module = fm.get("module", "")
        if not module and rel in file_mapping:
            module = file_mapping[rel]

        order = fm.get("order", "")
        tags = ",".join(fm.get("tags", [])) if fm.get("tags") else ""
        status = fm.get("status", "unknown")
        has_fm = has_front_matter(md)
        in_nav = "yes" if rel in nav_files else "no"
        size = get_file_size(md)
        words = count_words(md)

        # Obtener info del módulo canónico
        module_title = ""
        if module and module in modules:
            module_title = modules[module].get("title", "")

        rows.append(
            {
                "path": rel,
                "title": title[:80],
                "module": module,
                "module_title": module_title,
                "order": order,
                "tags": tags,
                "status": status,
                "has_frontmatter": "yes" if has_fm else "no",
                "in_mkdocs_nav": in_nav,
                "size_bytes": size,
                "word_count": words,
            }
        )

        # Detectar problemas
        if not module:
            orphans.append((rel, title))
        if not has_fm:
            no_frontmatter.append((rel, title))

    # Escribir MANIFEST.csv
    with open(OUT_MANIFEST, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "path",
            "title",
            "module",
            "module_title",
            "order",
            "tags",
            "status",
            "has_frontmatter",
            "in_mkdocs_nav",
            "size_bytes",
            "word_count",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ MANIFEST generado: {OUT_MANIFEST}")

    # Escribir reporte de huérfanos
    orphans_report = REPORTS_DIR / "orphans_report.md"
    with open(orphans_report, "w", encoding="utf-8") as r:
        r.write("# Archivos sin Módulo Asignado\n\n")
        r.write(f"*Generado: {datetime.now().isoformat()}*\n\n")

        if orphans:
            r.write(f"**{len(orphans)} archivos** sin módulo asignado:\n\n")
            r.write("| Archivo | Título | Acción Sugerida |\n")
            r.write("|:--------|:-------|:----------------|\n")
            for rel, title in orphans:
                r.write(f"| `{rel}` | {title[:50]} | Asignar módulo o mover a APENDICE |\n")
        else:
            r.write("✅ Todos los archivos tienen módulo asignado.\n")

    print(f"✅ Reporte de huérfanos: {orphans_report}")

    # Escribir reporte de inconsistencias
    inconsistencies_report = REPORTS_DIR / "inconsistencies.md"
    with open(inconsistencies_report, "w", encoding="utf-8") as r:
        r.write("# Reporte de Inconsistencias\n\n")
        r.write(f"*Generado: {datetime.now().isoformat()}*\n\n")

        # Sin front-matter
        r.write("## Archivos sin Front-matter YAML\n\n")
        if no_frontmatter:
            r.write(f"**{len(no_frontmatter)} archivos** sin front-matter:\n\n")
            for rel, title in no_frontmatter[:20]:  # Limitar a 20
                r.write(f"- `{rel}`\n")
            if len(no_frontmatter) > 20:
                r.write(f"\n... y {len(no_frontmatter) - 20} más\n")
        else:
            r.write("✅ Todos los archivos tienen front-matter.\n")

        # Huérfanos
        r.write("\n## Archivos Huérfanos (sin módulo)\n\n")
        if orphans:
            r.write(f"**{len(orphans)} archivos** huérfanos\n")
        else:
            r.write("✅ Todos asignados.\n")

        # Resumen
        r.write("\n## Resumen\n\n")
        r.write(f"- Total archivos .md: **{len(md_files)}**\n")
        r.write(f"- Con front-matter: **{len(md_files) - len(no_frontmatter)}**\n")
        r.write(f"- Sin front-matter: **{len(no_frontmatter)}**\n")
        r.write(f"- Huérfanos: **{len(orphans)}**\n")
        r.write(f"- En mkdocs nav: **{sum(1 for r in rows if r['in_mkdocs_nav'] == 'yes')}**\n")

    print(f"✅ Reporte de inconsistencias: {inconsistencies_report}")

    # Resumen en consola
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"  Archivos .md totales:    {len(md_files)}")
    print(f"  Con front-matter:        {len(md_files) - len(no_frontmatter)}")
    print(f"  Sin front-matter:        {len(no_frontmatter)}")
    print(f"  Huérfanos:               {len(orphans)}")
    print(f"  En mkdocs.yml nav:       {sum(1 for r in rows if r['in_mkdocs_nav'] == 'yes')}")
    print("=" * 60)

    return len(orphans), len(no_frontmatter)


if __name__ == "__main__":
    main()
