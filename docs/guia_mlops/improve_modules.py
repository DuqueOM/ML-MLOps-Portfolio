#!/usr/bin/env python3
"""
Script para mejorar automáticamente los encabezados de todos los módulos.
"""

from pathlib import Path

GUIDE_DIR = Path(__file__).parent

# Información de cada módulo
MODULES_INFO = {
    "00_INDICE": {
        "emoji": "📚",
        "title": "Índice General",
        "subtitle": "Guía Definitiva MLOps",
        "quote": "Tu roadmap hacia la excelencia en MLOps",
        "level": "N/A",
        "duration": "N/A",
    },
    "01_FUNDAMENTOS": {
        "emoji": "🚀",
        "title": "Fundamentos de MLOps",
        "subtitle": "De la Experimentación a Producción",
        "quote": "El 87% de los modelos ML nunca llegan a producción.",
        "level": "🟢 Principiante",
        "duration": "4-6 horas",
    },
    "02_DISENO_PROYECTO": {
        "emoji": "📐",
        "title": "Diseño del Proyecto",
        "subtitle": "De la Idea al Blueprint",
        "quote": "Un proyecto sin diseño es como construir sin planos.",
        "level": "🟢 Principiante",
        "duration": "3-4 horas",
    },
    "03_ESTRUCTURA_REPO": {
        "emoji": "📁",
        "title": "Estructura del Repositorio",
        "subtitle": "Organización Profesional del Código",
        "quote": "La estructura es el esqueleto de la mantenibilidad.",
        "level": "🟢 Principiante",
        "duration": "2-3 horas",
    },
    "04_GIT_GITHUB": {
        "emoji": "🔀",
        "title": "Control de Versiones",
        "subtitle": "Git y GitHub para ML",
        "quote": "El código sin versionar es código que no existe.",
        "level": "🟢 Principiante",
        "duration": "3-4 horas",
    },
    "05_DVC": {
        "emoji": "📊",
        "title": "Versionado de Datos",
        "subtitle": "DVC - Data Version Control",
        "quote": "Git para código, DVC para datos.",
        "level": "🟡 Intermedio",
        "duration": "3-4 horas",
    },
    "06_PIPELINE_ML": {
        "emoji": "⚙️",
        "title": "Pipeline de Entrenamiento",
        "subtitle": "Pipelines Reproducibles con sklearn",
        "quote": "Un pipeline bien diseñado previene 90% de los bugs.",
        "level": "🟡 Intermedio",
        "duration": "4-5 horas",
    },
    "07_MLFLOW": {
        "emoji": "📈",
        "title": "Tracking de Experimentos",
        "subtitle": "MLflow para ML Profesional",
        "quote": "Si no trackeas, no puedes mejorar.",
        "level": "🟡 Intermedio",
        "duration": "3-4 horas",
    },
    "08_TESTING": {
        "emoji": "🧪",
        "title": "Testing y Calidad",
        "subtitle": "Pytest y Herramientas de Calidad",
        "quote": "El código sin tests es deuda técnica garantizada.",
        "level": "🟡 Intermedio",
        "duration": "4-5 horas",
    },
    "09_CICD": {
        "emoji": "🔄",
        "title": "CI/CD para Machine Learning",
        "subtitle": "GitHub Actions y Automatización",
        "quote": "Automatiza todo lo que puedas, revisa lo que no.",
        "level": "🟡 Intermedio",
        "duration": "4-5 horas",
    },
    "10_DOCKER": {
        "emoji": "🐳",
        "title": "Contenerización con Docker",
        "subtitle": "Del Desarrollo a Producción",
        "quote": "Funciona en mi máquina → Funciona en Docker.",
        "level": "🟡 Intermedio",
        "duration": "4-5 horas",
    },
    "11_FASTAPI": {
        "emoji": "🌐",
        "title": "APIs REST con FastAPI",
        "subtitle": "Serving de Modelos ML",
        "quote": "Un modelo sin API es un modelo sin valor.",
        "level": "🟡 Intermedio",
        "duration": "3-4 horas",
    },
    "12_KUBERNETES": {
        "emoji": "☸️",
        "title": "Orquestación con Kubernetes",
        "subtitle": "Escalando Modelos ML",
        "quote": "K8s: De un contenedor a mil, sin cambiar código.",
        "level": "🔴 Avanzado",
        "duration": "5-6 horas",
    },
    "13_TERRAFORM": {
        "emoji": "🏗️",
        "title": "Infraestructura como Código",
        "subtitle": "Terraform para MLOps",
        "quote": "Infraestructura reproducible = Confianza total.",
        "level": "🔴 Avanzado",
        "duration": "4-5 horas",
    },
    "14_MONITOREO": {
        "emoji": "📊",
        "title": "Observabilidad y Monitoreo",
        "subtitle": "Prometheus, Grafana y Alertas",
        "quote": "No puedes mejorar lo que no mides.",
        "level": "🔴 Avanzado",
        "duration": "4-5 horas",
    },
    "15_DOCUMENTACION": {
        "emoji": "📝",
        "title": "Documentación Profesional",
        "subtitle": "README, Docstrings y MkDocs",
        "quote": "El código habla a las máquinas, la documentación a los humanos.",
        "level": "🟢 Principiante",
        "duration": "2-3 horas",
    },
    "16_MODEL_CARDS": {
        "emoji": "🎴",
        "title": "Model Cards y Data Cards",
        "subtitle": "Documentación de Modelos ML",
        "quote": "Transparencia en ML = Confianza en producción.",
        "level": "🟡 Intermedio",
        "duration": "2-3 horas",
    },
    "17_DEMO": {
        "emoji": "🎬",
        "title": "Demo y Presentación",
        "subtitle": "Mostrando tu Portafolio",
        "quote": "Un buen demo vale más que mil líneas de código.",
        "level": "🟢 Principiante",
        "duration": "3-4 horas",
    },
    "18_GLOSARIO": {
        "emoji": "📖",
        "title": "Glosario Completo",
        "subtitle": "Términos de MLOps A-Z",
        "quote": "Dominar el vocabulario es el primer paso.",
        "level": "📚 Referencia",
        "duration": "Consulta",
    },
    "19_DECISIONES_TECH": {
        "emoji": "⚖️",
        "title": "Decisiones Tecnológicas",
        "subtitle": "Por qué Elegimos Cada Herramienta",
        "quote": "Cada decisión tiene trade-offs, documéntalos.",
        "level": "📚 Referencia",
        "duration": "Consulta",
    },
    "20_PLAN_ESTUDIOS": {
        "emoji": "📅",
        "title": "Plan de Estudios",
        "subtitle": "Roadmap de 10 Semanas",
        "quote": "Un camino claro hacia la maestría en MLOps.",
        "level": "📚 Referencia",
        "duration": "10 semanas",
    },
    "21_PLANTILLAS": {
        "emoji": "📋",
        "title": "Plantillas Reutilizables",
        "subtitle": "Templates para Proyectos ML",
        "quote": "No reinventes la rueda, usa plantillas.",
        "level": "📚 Referencia",
        "duration": "Consulta",
    },
    "22_CHECKLIST": {
        "emoji": "✅",
        "title": "Checklist Final",
        "subtitle": "Verificación del Portafolio",
        "quote": "La calidad se verifica, no se asume.",
        "level": "📚 Referencia",
        "duration": "1 hora",
    },
    "23_RECURSOS": {
        "emoji": "🔗",
        "title": "Recursos y Referencias",
        "subtitle": "Links, Cursos y Comunidades",
        "quote": "El aprendizaje nunca termina.",
        "level": "📚 Referencia",
        "duration": "Consulta",
    },
}


def create_header(module_name: str) -> str:
    """Crear encabezado mejorado para un módulo."""
    info = MODULES_INFO.get(module_name, {})
    if not info:
        return ""

    num = module_name.split("_")[0]

    header = f"""# ════════════════════════════════════════════════════════════════════════════════
# MÓDULO {num}: {info["title"].upper()}
# {info["subtitle"]}
# Guía MLOps v2.0 | DuqueOM | Noviembre 2025
# ════════════════════════════════════════════════════════════════════════════════

<div align="center">

# {info["emoji"]} MÓDULO {num}: {info["title"]}

**{info["subtitle"]}**

*"{info["quote"]}"*

| Nivel | Duración |
|:-----:|:--------:|
| {info["level"]} | {info["duration"]} |

</div>

---
"""
    return header


def improve_module(file_path: Path) -> bool:
    """Mejorar un módulo individual."""
    module_name = file_path.stem

    if module_name not in MODULES_INFO:
        print(f"⚠️ Sin info para: {module_name}")
        return False

    # Leer contenido actual
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar si ya tiene el nuevo formato
    if "════════════════" in content[:200]:
        print(f"✅ Ya mejorado: {module_name}")
        return True

    # Encontrar dónde empieza el contenido real (después del primer ##)
    lines = content.split("\n")
    content_start = 0
    for i, line in enumerate(lines):
        if line.startswith("## ") and i > 0:
            content_start = i
            break

    # Crear nuevo contenido
    new_header = create_header(module_name)
    remaining_content = "\n".join(lines[content_start:])

    new_content = new_header + "\n" + remaining_content

    # Añadir footer si no existe
    if "© 2025 DuqueOM" not in new_content:
        new_content += """

---

<div align="center">

*© 2025 DuqueOM - Guía MLOps v2.0*

</div>
"""

    # Guardar
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Mejorado: {module_name}")
    return True


def main():
    """Función principal."""
    print("=" * 60)
    print("🔧 MEJORANDO MÓDULOS DE LA GUÍA MLOps")
    print("=" * 60)

    md_files = sorted(GUIDE_DIR.glob("*.md"))
    md_files = [f for f in md_files if not f.name.startswith(("generate", "improve"))]

    print(f"\n📁 Encontrados {len(md_files)} archivos\n")

    success = 0
    for md_file in md_files:
        if improve_module(md_file):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"📊 COMPLETADO: {success}/{len(md_files)} módulos mejorados")
    print("=" * 60)


if __name__ == "__main__":
    main()
