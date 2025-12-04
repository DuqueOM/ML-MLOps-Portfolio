#!/usr/bin/env python3
"""gen_mkdocs_nav.py — Genera mkdocs.yml con navegación completa.

Ejecutar desde la raíz de guia_mlops/:
    python3 scripts/gen_mkdocs_nav.py
"""

from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
MODULES_FILE = ROOT / "MODULES_CANON.yaml"
MANIFEST_FILE = ROOT / "MANIFEST.csv"
OUTPUT_FILE = ROOT / "mkdocs_generated.yml"


def load_modules_canon() -> dict:
    """Carga configuración de módulos."""
    with open(MODULES_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_manifest() -> list:
    """Carga MANIFEST.csv."""
    import csv

    rows = []
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def generate_nav(manifest: list, modules: dict, file_mapping: dict) -> list:
    """Genera estructura de navegación para mkdocs."""

    # Agrupar archivos por módulo
    by_module = defaultdict(list)

    for row in manifest:
        path = row["path"]
        title = row["title"]
        module = row["module"] or file_mapping.get(path, "APENDICE")
        order = int(row["order"]) if row["order"] else 999

        by_module[module].append(
            {
                "path": path,
                "title": title,
                "order": order,
            }
        )

    # Construir navegación
    nav = []

    # Home
    nav.append({"Home": "index.md"})

    # Módulos en orden
    phases = defaultdict(list)

    for mod_id, mod_info in modules.items():
        if mod_id == "APENDICE":
            continue

        phase = mod_info.get("phase", 0)
        phases[phase].append((mod_id, mod_info))

    # Agregar por fase
    phase_names = {
        1: "Fundamentos",
        2: "Ingeniería de Datos",
        3: "Feature Engineering",
        4: "Modelado",
        5: "Experiment Tracking",
        6: "Despliegue",
        7: "CI/CD & Testing",
        8: "Producción",
        9: "Mantenimiento",
        10: "Documentación",
        11: "Habilidades Profesionales",
    }

    for phase_num in sorted(phases.keys()):
        if phase_num == 0:
            continue

        phase_name = phase_names.get(phase_num, f"Fase {phase_num}")
        phase_items = []

        for mod_id, mod_info in sorted(phases[phase_num], key=lambda x: x[0]):
            mod_name = mod_info["title"]
            mod_files = by_module.get(mod_id, [])

            if mod_files:
                # Ordenar por order
                mod_files.sort(key=lambda x: x["order"])

                # Si solo hay un archivo, link directo
                if len(mod_files) == 1:
                    phase_items.append({mod_name: mod_files[0]["path"]})
                else:
                    # Múltiples archivos: crear sección
                    sub_items = []
                    for f in mod_files:
                        sub_items.append({f["title"]: f["path"]})
                    phase_items.append({mod_name: sub_items})
            else:
                # Buscar en docs/
                docs_path = f"docs/{mod_id.zfill(2)}_{mod_info['name']}/index.md"
                if (ROOT / docs_path).exists():
                    phase_items.append({mod_name: docs_path})

        if phase_items:
            nav.append({f"Fase {phase_num}: {phase_name}": phase_items})

    # Apéndice
    apendice_files = by_module.get("APENDICE", [])
    if apendice_files:
        apendice_items = []
        for f in sorted(apendice_files, key=lambda x: x["order"]):
            apendice_items.append({f["title"]: f["path"]})
        nav.append({"Apéndice": apendice_items})

    return nav


def generate_mkdocs_config(nav: list) -> dict:
    """Genera configuración completa de mkdocs."""
    return {
        "site_name": "Guía MLOps v3 — Portfolio Edition",
        "site_description": "Curso completo de ML/MLOps desde básico hasta Staff",
        "site_author": "DuqueOM",
        "theme": {
            "name": "material",
            "language": "es",
            "palette": [
                {
                    "scheme": "default",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {"icon": "material/brightness-7", "name": "Modo oscuro"},
                },
                {
                    "scheme": "slate",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {"icon": "material/brightness-4", "name": "Modo claro"},
                },
            ],
            "features": [
                "navigation.tabs",
                "navigation.sections",
                "navigation.expand",
                "navigation.top",
                "search.suggest",
                "search.highlight",
                "content.code.copy",
                "content.tabs.link",
            ],
        },
        "nav": nav,
        "markdown_extensions": [
            "admonition",
            "codehilite",
            "toc",
            "tables",
            "attr_list",
            "md_in_html",
            {"pymdownx.highlight": {"anchor_linenums": True}},
            "pymdownx.superfences",
            "pymdownx.tabbed",
            "pymdownx.emoji",
        ],
        "plugins": [
            "search",
        ],
    }


def main():
    print("=" * 60)
    print("GENERANDO MKDOCS.YML")
    print("=" * 60)

    # Cargar datos
    canon = load_modules_canon()
    modules = canon.get("modules", {})
    file_mapping = canon.get("file_mapping", {})

    # Cargar manifest si existe
    if MANIFEST_FILE.exists():
        manifest = load_manifest()
    else:
        print("⚠️ MANIFEST.csv no existe. Ejecuta primero make_manifest.py")
        manifest = []

    # Generar navegación
    nav = generate_nav(manifest, modules, file_mapping)

    # Generar config
    config = generate_mkdocs_config(nav)

    # Escribir archivo
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"✅ Generado: {OUTPUT_FILE}")
    print(f"   Módulos en nav: {len(nav)}")

    print("\n💡 Revisa el archivo y cópialo a mkdocs.yml si está correcto:")
    print(f"   cp {OUTPUT_FILE} mkdocs.yml")


if __name__ == "__main__":
    main()
