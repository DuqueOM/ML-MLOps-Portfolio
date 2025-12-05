#!/usr/bin/env python3
# flake8: noqa
"""
GENERADOR PDF PRO v9.0 - WeasyPrint Edition
- Generación nativa de PDF (texto seleccionable garantizado)
- Control estricto de huérfanos y viudas
- Portadas y contenido integrados
"""

import re
from pathlib import Path
from typing import List, Optional

import markdown
from PyPDF2 import PdfMerger
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "pdf"
FINAL_FILENAME = "GUIA_MLOPS_COMPLETA_v5.pdf"

ORDERED_FILES = [
    "00_INDICE.md",
    "SYLLABUS.md",
    "PLAN_ESTUDIOS.md",
    "01_PYTHON_MODERNO.md",
    "02_DISENO_SISTEMAS.md",
    "03_ESTRUCTURA_PROYECTO.md",
    "04_ENTORNOS.md",
    "05_GIT_PROFESIONAL.md",
    "06_VERSIONADO_DATOS.md",
    "SIMULACRO_ENTREVISTA_JUNIOR.md",
    "07_SKLEARN_PIPELINES.md",
    "08_INGENIERIA_FEATURES.md",
    "09_TRAINING_PROFESIONAL.md",
    "10_EXPERIMENT_TRACKING.md",
    "11_TESTING_ML.md",
    "12_CI_CD.md",
    "13_DOCKER.md",
    "14_FASTAPI.md",
    "15_STREAMLIT.md",
    "SIMULACRO_ENTREVISTA_MID.md",
    "16_OBSERVABILIDAD.md",
    "17_DESPLIEGUE.md",
    "18_INFRAESTRUCTURA.md",
    "19_DOCUMENTACION.md",
    "20_PROYECTO_INTEGRADOR.md",
    "SIMULACRO_ENTREVISTA_SENIOR_PARTE1.md",
    "SIMULACRO_ENTREVISTA_SENIOR_PARTE2.md",
    "21_GLOSARIO.md",
    "22_CHECKLIST.md",
    "23_RECURSOS.md",
    "RECURSOS_POR_MODULO.md",
    "EJERCICIOS.md",
    "EJERCICIOS_SOLUCIONES.md",
    "PLANTILLAS.md",
    "DECISIONES_TECH.md",
    "RUBRICA_EVALUACION.md",
    "APENDICE_A_SPEECH_PORTAFOLIO.md",
    "APENDICE_B_TALKING_POINTS.md",
    "GUIA_AUDIOVISUAL.md",
    "MAINTENANCE_GUIDE.md",
]

# Mapa de Emojis a Símbolos Unicode
EMOJI_TO_SYMBOL = {
    "📚": "▣",
    "📖": "▤",
    "📄": "□",
    "📑": "▥",
    "📘": "▦",
    "🎯": "◎",
    "💡": "★",
    "⚡": "★",
    "🔥": "★",
    "✨": "★",
    "🔴": "●",
    "🟡": "◐",
    "🟢": "○",
    "🏷️": "▪",
    "🎬": "▶",
    "🧪": "◆",
    "🔬": "◆",
    "⚗️": "◆",
    "🐳": "▶",
    "🐍": "▷",
    "🚀": "►",
    "📊": "▣",
    "📈": "▲",
    "📉": "▼",
    "🔧": "●",
    "⚙️": "●",
    "🛠️": "●",
    "🔩": "●",
    "✅": "✓",
    "✔️": "✓",
    "☑️": "✓",
    "❌": "✗",
    "⛔": "✗",
    "⚠️": "▲",
    "🚨": "▲",
    "💥": "▲",
    "📦": "■",
    "📁": "■",
    "📂": "■",
    "🔗": "→",
    "➡️": "→",
    "👉": "→",
    "⬅️": "←",
    "📐": "◇",
    "🏗️": "◇",
    "🏛️": "◇",
    "🧠": "◎",
    "💭": "◎",
    "🤔": "◎",
    "📝": "▪",
    "✏️": "▪",
    "🖊️": "▪",
    "🎨": "◐",
    "🖼️": "◐",
    "🔒": "◑",
    "🔑": "◑",
    "🛡️": "◑",
    "⏰": "◒",
    "🕐": "◒",
    "⏱️": "◒",
    "💻": "▢",
    "🖥️": "▢",
    "📱": "▢",
    "🌐": "◯",
    "🌍": "◯",
    "🌎": "◯",
    "📺": "▣",
    "🎥": "▣",
    "🧭": "◈",
    "🗺️": "◈",
    "👤": "●",
    "👥": "●",
    "🙋": "●",
    "💬": "◆",
    "🗣️": "◆",
    "🏆": "★",
    "🥇": "★",
    "🎖️": "★",
    "📋": "▤",
    "🗒️": "▤",
    "📃": "▤",
}

FILE_TITLES = {
    "00_INDICE.md": "ÍNDICE",
    "SYLLABUS.md": "SYLLABUS",
    "PLAN_ESTUDIOS.md": "PLAN DE ESTUDIOS",
    "01_PYTHON_MODERNO.md": "PYTHON MODERNO",
    "02_DISENO_SISTEMAS.md": "DISEÑO DE SISTEMAS",
    "03_ESTRUCTURA_PROYECTO.md": "ESTRUCTURA DE PROYECTO",
    "04_ENTORNOS.md": "ENTORNOS",
    "05_GIT_PROFESIONAL.md": "GIT PROFESIONAL",
    "06_VERSIONADO_DATOS.md": "VERSIONADO DE DATOS",
    "SIMULACRO_ENTREVISTA_JUNIOR.md": "SIMULACRO ENTREVISTA JUNIOR",
    "07_SKLEARN_PIPELINES.md": "SKLEARN PIPELINES",
    "08_INGENIERIA_FEATURES.md": "INGENIERÍA DE FEATURES",
    "09_TRAINING_PROFESIONAL.md": "TRAINING PROFESIONAL",
    "10_EXPERIMENT_TRACKING.md": "EXPERIMENT TRACKING",
    "11_TESTING_ML.md": "TESTING ML",
    "12_CI_CD.md": "CI/CD",
    "13_DOCKER.md": "DOCKER",
    "14_FASTAPI.md": "FASTAPI",
    "15_STREAMLIT.md": "STREAMLIT",
    "SIMULACRO_ENTREVISTA_MID.md": "SIMULACRO ENTREVISTA MID",
    "16_OBSERVABILIDAD.md": "OBSERVABILIDAD",
    "17_DESPLIEGUE.md": "DESPLIEGUE",
    "18_INFRAESTRUCTURA.md": "INFRAESTRUCTURA",
    "19_DOCUMENTACION.md": "DOCUMENTACIÓN",
    "20_PROYECTO_INTEGRADOR.md": "PROYECTO INTEGRADOR",
    "SIMULACRO_ENTREVISTA_SENIOR_PARTE1.md": "SIMULACRO SENIOR (PARTE 1)",
    "SIMULACRO_ENTREVISTA_SENIOR_PARTE2.md": "SIMULACRO SENIOR (PARTE 2)",
    "21_GLOSARIO.md": "GLOSARIO",
    "22_CHECKLIST.md": "CHECKLIST",
    "23_RECURSOS.md": "RECURSOS",
    "RECURSOS_POR_MODULO.md": "RECURSOS POR MÓDULO",
    "EJERCICIOS.md": "EJERCICIOS",
    "EJERCICIOS_SOLUCIONES.md": "SOLUCIONES DE EJERCICIOS",
    "PLANTILLAS.md": "PLANTILLAS",
    "DECISIONES_TECH.md": "DECISIONES TÉCNICAS",
    "RUBRICA_EVALUACION.md": "RÚBRICA DE EVALUACIÓN",
    "APENDICE_A_SPEECH_PORTAFOLIO.md": "APÉNDICE A: SPEECH PORTAFOLIO",
    "APENDICE_B_TALKING_POINTS.md": "APÉNDICE B: TALKING POINTS",
    "GUIA_AUDIOVISUAL.md": "GUÍA AUDIOVISUAL",
    "MAINTENANCE_GUIDE.md": "GUÍA DE MANTENIMIENTO",
}

# CSS Optimizado para WeasyPrint (Estilo Compacto y Profesional)
CONTENT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
/* Intentar cargar fuente de emojis si está disponible localmente */
@font-face {
  font-family: 'Noto Color Emoji';
  src: local('Noto Color Emoji'), local('Apple Color Emoji'), local('Segoe UI Emoji');
}

@page {
    size: Letter;
    margin: 10mm 15mm 10mm 15mm; /* Márgenes de página reducidos (1.5cm laterales, 1cm verticales) */
    @bottom-right {
        content: counter(page);
        font-family: 'Inter', sans-serif;
        font-size: 9pt;
        color: #64748b;
        margin-bottom: 5mm;
        margin-right: 5mm;
    }
}

@page :first {
    margin: 0;
    @bottom-right { content: none; }
}

@page cover {
    margin: 0;
    size: Letter;
    @bottom-right { content: none; }
}

* { box-sizing: border-box; }

body {
    font-family: 'Inter', 'Noto Color Emoji', sans-serif;
    font-size: 8.5pt;
    line-height: 1.4;
    color: #1e293b;
    margin: 0;
    padding: 0; /* SIN padding para que las portadas funcionen */
    max-width: 100%;
}

/* Contenido con margen de seguridad */
.content {
    padding: 0 15px 0 5px; /* Padding solo en el contenido, no en portadas */
}

/* Headers */
h1, h2, h3, h4 { 
    font-family: 'Inter', sans-serif; 
    line-height: 1.2; 
    max-width: 100%;
    word-wrap: break-word;
    page-break-after: avoid;
}

h1 {
    font-size: 11pt; /* Reducido drásticamente */
    font-weight: 700;
    color: #1e3a8a;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 4px;
    margin: 0 0 6px 0;
}

h2 {
    font-size: 10pt; /* Reducido */
    font-weight: 600;
    color: #1e40af;
    margin: 8px 0 4px 0;
    padding-bottom: 2px;
    border-bottom: 1px solid #e2e8f0;
}

h3 {
    font-size: 9pt; /* Reducido */
    font-weight: 600;
    color: #2563eb;
    margin: 6px 0 3px 0;
}

h4 {
    font-size: 8.5pt; /* Mismo tamaño que body pero bold */
    font-weight: 600;
    color: #3b82f6;
    margin: 4px 0 2px 0;
}

/* Evitar partir tablas, imágenes y CÓDIGO */
table, img, figure, .admonition, pre {
    page-break-inside: avoid;
    break-inside: avoid; /* Refuerzo para navegadores modernos/WeasyPrint */
}

/* Text Blocks */
p, li {
    margin: 0 0 6px 0;
    text-align: left; /* Izquierda para mejor legibilidad */
    orphans: 2;
    widows: 2;
    overflow-wrap: anywhere;
    word-break: normal;
    max-width: 100%;
}

ul, ol { margin: 0 0 8px 0; padding-left: 16px; max-width: 100%; }
li { margin-bottom: 2px; text-align: left; }
}
blockquote p { margin: 0; text-align: left; } /* Forzar izquierda dentro del blockquote */

/* Links - IMPORTANTE para PDF */
a {
    color: #2563eb;
    text-decoration: underline;
    cursor: pointer;
}
a:hover {
    color: #1d4ed8;
}
/* Links en tablas */
td a, th a {
    color: #2563eb;
    text-decoration: underline;
}

/* Code */
code {
    background: #f1f5f9;
    color: #be185d;
    padding: 0px 2px;
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9em;
    overflow-wrap: break-word;
    word-break: break-all; /* Romper links largos */
}

pre {
    background: #0f172a;
    color: #f1f5f9;
    border-radius: 4px;
    padding: 8px;
    
    /* FIX ANCHO */
    width: auto;
    margin: 8px 10px 8px 0;
    
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.5pt;
    line-height: 1.3;
    white-space: pre-wrap;
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-all;
    text-align: left;
    break-inside: auto;
    border: 1px solid #1e293b;
}
pre code { background: none; color: inherit; padding: 0; word-break: break-all; }

/* Imágenes */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 8px auto;
}

/* Tables */
table {
    width: 100%;
    max-width: 100%;
    table-layout: auto; /* Auto para optimizar ancho de columnas según contenido */
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 8pt;
    break-inside: auto;
    border: 1px solid #e2e8f0;
}

th {
    background: #f1f5f9;
    color: #1e293b;
    font-weight: 600;
    text-align: left;
    padding: 8px 8px;
    border-bottom: 2px solid #e2e8f0;
    overflow-wrap: break-word;
    word-break: break-word;
}

td {
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 8px;
    vertical-align: top;
    text-align: left; /* Texto en tablas siempre a la izquierda */
    overflow-wrap: break-word;
    word-wrap: break-word;
    word-break: break-word;
}

tr:nth-child(even) { background: #f8fafc; }

/* Portadas - FULL PAGE sin márgenes */
.cover-page {
    page: cover;
    break-after: page;
    width: 100%;
    height: 279.4mm; /* Altura exacta Letter */
    background: linear-gradient(160deg, #1e3a8a 0%, #172554 100%);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    margin: 0;
    padding: 0;
    position: relative;
    box-sizing: border-box;
}

.cover-content {
    width: 80%;
    padding: 40px 20px;     /* Más padding vertical */
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    background: rgba(255,255,255,0.03);
}

.cover-title {
    font-size: 24pt;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
    line-height: 1.2;
    color: #ffffff;
}

.cover-subtitle {
    font-size: 12pt;
    font-weight: 300;
    color: #bfdbfe;
    letter-spacing: 2px;
    margin-bottom: 30px;
    text-transform: uppercase;
}

.cover-badge {
    display: inline-block;
    background: #3b82f6;
    color: white;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 10pt;
    font-weight: 600;
    letter-spacing: 1px;
}

.global-cover {
    background: #0f172a;
    background-image: radial-gradient(circle at 50% 50%, #1e293b 0%, #0f172a 100%);
}

.global-title {
    font-size: 42pt;
    font-weight: 900;
    color: #60a5fa;
    letter-spacing: 3px;
    margin-bottom: 10px;
    line-height: 1;
}

/* Anti-huérfanos CSS puro (sin wrappers) */
h2, h3, h4 {
    break-after: avoid-page;
}
h2 + *, h3 + *, h4 + * {
    break-before: avoid-page;
}
"""


class PDFGenerator:
    def __init__(self):
        OUTPUT_DIR.mkdir(exist_ok=True)
        self.font_config = FontConfiguration()
        self.css = CSS(string=CONTENT_CSS, font_config=self.font_config)

    def clean_markdown(self, text: str) -> str:
        lines = text.split("\n")
        cleaned = []
        in_code = False

        for line in lines:
            s = line.strip()

            # Manejo de bloques de código
            if s.startswith("```"):
                in_code = not in_code
                cleaned.append(line)
                continue

            if in_code:
                cleaned.append(line)
                continue

            # Limpieza de regex (headers, nav, etc)
            if re.match(r"^[-_*]{3,}\s*$", s):
                continue
            if re.match(r"^═+\s*$", s) or "════" in s:
                continue
            if "[←" in s or "Volver al Índice" in s or "[Siguiente:" in s:
                continue

            # Eliminar divs HTML que rompen tablas Markdown
            if "<div" in s or "</div>" in s:
                continue

            # Limpieza de artefactos '# #' que aparecen antes de títulos
            if re.match(r"^#+\s+#+\s+", s):
                s = re.sub(r"^#+\s+#+\s+", "", s)

            # Limpieza específica para '# # ' suelto
            s = re.sub(r"^#\s+#\s+", "", s)

            # Para headers: usar la versión limpia (s) para que Markdown los reconozca
            # Los espacios iniciales rompen el parseo de headers
            if s.startswith("#"):
                # Asegurar línea en blanco antes de headers
                if cleaned and cleaned[-1].strip() != "":
                    cleaned.append("")
                cleaned.append(s)  # Usar versión sin espacios iniciales
                continue

            # Lógica de Tablas:
            if s.startswith("|"):
                if cleaned:
                    prev_s = cleaned[-1].strip()
                    if prev_s != "" and not prev_s.startswith("|"):
                        cleaned.append("")

            cleaned.append(line)

        return "\n".join(cleaned)

    def transform_internal_links(self, text: str, debug: bool = False) -> str:
        """
        Convierte enlaces Markdown [Texto](archivo.md) a enlaces internos HTML <a href="#archivo">Texto</a>.
        """
        transformed_count = 0

        def replace_link(match):
            nonlocal transformed_count
            link_text = match.group(1)
            path = match.group(2)

            # Links web: no tocar
            if path.startswith("http"):
                return match.group(0)

            # Links a archivos .md: convertir a anclas internas
            if path.endswith(".md"):
                filename = Path(path).name
                # ID: mod_FILENAME (sin extensión, limpio)
                base_name = filename.replace(".md", "")
                clean_id = "mod_" + re.sub(r"[^\w]+", "_", base_name)
                transformed_count += 1
                return f"[{link_text}](#{clean_id})"

            return match.group(0)

        result = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, text)

        if debug and transformed_count > 0:
            print(f"    [DEBUG] {transformed_count} links transformados a anclas internas")

        return result

    def get_cover_title(self, filename: str) -> str:
        return FILE_TITLES.get(filename, filename.replace(".md", "").replace("_", " ").upper())

    def generate_module_html(self, title: str, md_content: str, filename: str) -> str:
        # 1. Limpiar Markdown
        clean_md = self.clean_markdown(md_content)

        # 2. Transformar enlaces a internos (con debug)
        linked_md = self.transform_internal_links(clean_md, debug=True)

        content_html = markdown.markdown(linked_md, extensions=["tables", "fenced_code", "nl2br"])

        # ID para el ancla: mod_FILENAME (mismo formato que transform_internal_links)
        base_name = filename.replace(".md", "")
        module_id = "mod_" + re.sub(r"[^\w]+", "_", base_name)

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
            <!-- PORTADA CON ANCLA INTEGRADA -->
            <div id="{module_id}" class="cover-page">
                <a name="{module_id}"></a>
                <div class="cover-content">
                    <div style="font-size:40pt;margin-bottom:20px;">💎</div>
                    <div class="cover-title">{title}</div>
                    <div class="cover-subtitle">Guía MLOps v5.0</div>
                    <div class="cover-badge">PORTFOLIO EDITION</div>
                </div>
                <div style="position:absolute;bottom:30px;font-size:10pt;opacity:0.6;">DUQUEOM | 2025</div>
            </div>

            <!-- CONTENIDO -->
            <div class="content">
                {content_html}
            </div>
        </body>
        </html>
        """
        return full_html

    def generate_global_cover_html(self) -> str:
        return """
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
            <div class="cover-page global-cover">
                <div class="cover-content" style="border-color:rgba(96,165,250,0.3);background:rgba(15,23,42,0.6);">
                    <div style="font-size:60pt;margin-bottom:30px;">🚀</div>
                    <div class="global-title">GUÍA MLOPS</div>
                    <div class="cover-subtitle" style="color:#94a3b8;margin-bottom:40px;">De Cero a Senior / Staff</div>
                    <div class="cover-badge" style="background:linear-gradient(90deg,#3b82f6,#8b5cf6);border:none;padding:10px 30px;">VERSION 5.0 — PORTFOLIO EDITION</div>
                </div>
                <div style="position:absolute;bottom:30px;font-size:11pt;color:#64748b;">DUQUEOM | 2025</div>
            </div>
        </body>
        </html>
        """

    def process_module(self, md_file: str, debug_html: bool = False) -> Optional[Path]:
        path = BASE_DIR / md_file
        if not path.exists():
            return None

        print(f"  > {md_file}")
        raw = path.read_text(encoding="utf-8")
        clean = self.clean_markdown(raw)
        title = self.get_cover_title(md_file)

        html_content = self.generate_module_html(title, clean, md_file)

        # DEBUG: Guardar HTML del índice para inspección
        if debug_html and md_file == "00_INDICE.md":
            debug_path = OUTPUT_DIR / "_DEBUG_00_INDICE.html"
            debug_path.write_text(html_content, encoding="utf-8")
            print(f"    [DEBUG] HTML guardado en {debug_path}")

        stem = md_file.replace(".md", "")
        pdf_path = OUTPUT_DIR / f"{stem}.pdf"

        HTML(string=html_content, base_url=str(BASE_DIR)).write_pdf(target=pdf_path, stylesheets=[self.css])
        return pdf_path

    def generate_global_cover(self) -> Path:
        html = self.generate_global_cover_html()
        pdf_path = OUTPUT_DIR / "_000_COVER.pdf"
        HTML(string=html, base_url=str(BASE_DIR)).write_pdf(target=pdf_path, stylesheets=[self.css])
        return pdf_path

    def merge_all(self, pdfs: List[Path]):
        final = OUTPUT_DIR / FINAL_FILENAME
        print(f"\n[*] Combinando {len(pdfs)} PDFs...")
        m = PdfMerger()
        for p in pdfs:
            if p.exists():
                m.append(str(p))
        m.write(str(final))
        m.close()
        print(f"[OK] {final.name} ({final.stat().st_size / 1e6:.1f} MB)")


def main():
    print("=" * 50)
    print("  GENERADOR PDF PRO v9.1 (WeasyPrint - Single Document)")
    print("=" * 50)

    gen = PDFGenerator()

    # Generar TODO como un solo HTML para preservar links internos
    print("\n[1] Generando documento único...")

    all_html_parts = []

    # Portada global
    all_html_parts.append(gen.generate_global_cover_html())
    print("  > Portada global")

    # Módulos
    print("\n[2] Procesando módulos:")
    for f in ORDERED_FILES:
        path = BASE_DIR / f
        if not path.exists():
            continue

        print(f"  > {f}")
        raw = path.read_text(encoding="utf-8")
        clean = gen.clean_markdown(raw)
        title = gen.get_cover_title(f)

        # Transformar links
        linked_md = gen.transform_internal_links(clean, debug=True)

        # Convertir a HTML
        content_html = markdown.markdown(linked_md, extensions=["tables", "fenced_code", "nl2br"])

        # ID para el ancla
        base_name = f.replace(".md", "")
        module_id = "mod_" + re.sub(r"[^\w]+", "_", base_name)

        # HTML del módulo - ID en el título visible para que WeasyPrint genere el destino PDF
        module_html = f"""
            <!-- MÓDULO: {f} -->
            <div class="cover-page">
                <div class="cover-content">
                    <div style="font-size:40pt;margin-bottom:20px;">💎</div>
                    <div id="{module_id}" class="cover-title">{title}</div>
                    <div class="cover-subtitle">Guía MLOps v5.0</div>
                    <div class="cover-badge">PORTFOLIO EDITION</div>
                </div>
                <div style="position:absolute;bottom:30px;font-size:10pt;opacity:0.6;">DUQUEOM | 2025</div>
            </div>
            <div class="content">
                {content_html}
            </div>
        """
        all_html_parts.append(module_html)

    # Combinar todo en un solo HTML
    print("\n[3] Combinando en documento único...")

    # Extraer solo el body content de la portada global
    global_cover_body = gen.generate_global_cover_html()
    # Buscar el contenido del body
    import re as re_module

    body_match = re_module.search(r"<body>(.*?)</body>", global_cover_body, re_module.DOTALL)
    global_cover_content = body_match.group(1) if body_match else ""

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body>
        {global_cover_content}
        {"".join(all_html_parts[1:])}
    </body>
    </html>
    """

    # Guardar HTML de debug
    debug_path = OUTPUT_DIR / "_DEBUG_FULL.html"
    debug_path.write_text(full_html, encoding="utf-8")
    print(f"  [DEBUG] HTML completo guardado en {debug_path}")

    # Generar PDF único
    print("\n[4] Generando PDF final...")
    final_path = OUTPUT_DIR / "GUIA_MLOPS_COMPLETA_v5.pdf"

    HTML(string=full_html, base_url=str(BASE_DIR)).write_pdf(target=final_path, stylesheets=[gen.css])

    print(f"\n[OK] {final_path.name} ({final_path.stat().st_size / 1e6:.1f} MB)")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
