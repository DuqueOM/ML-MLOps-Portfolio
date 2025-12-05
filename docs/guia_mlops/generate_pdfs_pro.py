#!/usr/bin/env python3
"""
GENERADOR PDF PRO v8.0
- Símbolos Unicode que funcionan en wkhtmltopdf
- Títulos de portada basados en nombre de archivo
"""

import re
import subprocess
from pathlib import Path
from typing import List, Optional

import markdown
from bs4 import BeautifulSoup

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

# Símbolos Unicode que SÍ funcionan en wkhtmltopdf
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
    "🎬": "▣",
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

# Nombres legibles para portadas (basados en nombre de archivo)
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

CONTENT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Inter', 'DejaVu Sans', Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.6;
    color: #1a1a2e;
}

h1 {
    font-size: 22pt;
    font-weight: 700;
    color: #1e3a8a;
    border-bottom: 3px solid #3b82f6;
    padding-bottom: 10px;
    margin: 0 0 25px 0;
    page-break-after: avoid;
}

h2 {
    font-size: 15pt;
    font-weight: 600;
    color: #1e40af;
    margin: 28px 0 14px 0;
    padding-bottom: 5px;
    border-bottom: 2px solid #dbeafe;
    page-break-after: avoid;
}

h3 {
    font-size: 12pt;
    font-weight: 600;
    color: #2563eb;
    margin: 22px 0 10px 0;
    page-break-after: avoid;
}

h4 {
    font-size: 11pt;
    font-weight: 600;
    color: #3b82f6;
    margin: 18px 0 8px 0;
}

p {
    margin: 0 0 11px 0;
    text-align: justify;
    orphans: 4;
    widows: 4;
}

ul, ol { margin: 0 0 14px 0; padding-left: 22px; }
li { margin-bottom: 5px; }
strong { color: #1e3a8a; }

blockquote {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 0 8px 8px 0;
    margin: 18px 0;
    padding: 14px 18px;
    page-break-inside: avoid;
}

blockquote p { margin: 0; }

code {
    background: #f1f5f9;
    color: #be185d;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88em;
}

pre {
    background: #1e293b;
    color: #e2e8f0;
    border-radius: 6px;
    padding: 14px;
    margin: 18px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 8.5pt;
    line-height: 1.4;
    white-space: pre-wrap;
    page-break-inside: avoid;
}

pre code { background: none; color: inherit; padding: 0; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th {
    background: #1e40af;
    color: white;
    font-weight: 600;
    text-align: left;
    padding: 10px 12px;
}

td {
    border: 1px solid #e5e7eb;
    padding: 8px 12px;
    vertical-align: top;
}

tr:nth-child(even) { background: #f8fafc; }

.section-block {
    page-break-inside: avoid;
    margin-bottom: 12px;
}

hr { display: none; }
"""


class PDFGenerator:
    def __init__(self):
        OUTPUT_DIR.mkdir(exist_ok=True)
        (OUTPUT_DIR / "_style.css").write_text(CONTENT_CSS, encoding="utf-8")

    def convert_emojis(self, text: str) -> str:
        """Convierte emojis a símbolos Unicode que funcionan en wkhtmltopdf."""
        for emoji, symbol in EMOJI_TO_SYMBOL.items():
            text = text.replace(emoji, symbol)
        # Eliminar emojis restantes que no están en el mapa
        text = re.sub(r"[\U00010000-\U0010ffff]", "", text)
        return text

    def clean_markdown(self, text: str) -> str:
        """Limpia markdown y convierte emojis."""
        text = self.convert_emojis(text)

        lines = text.split("\n")
        cleaned = []
        in_code = False

        for line in lines:
            s = line.strip()
            if s.startswith("```"):
                in_code = not in_code
                cleaned.append(line)
                continue
            if in_code:
                cleaned.append(line)
                continue
            # Eliminar HR
            if re.match(r"^[-_*]{3,}\s*$", s):
                continue
            # Eliminar HTML
            if "<div" in s or "</div>" in s or "<p " in s:
                continue
            # Eliminar banners
            if s.startswith("# ═") or s.startswith("## ═"):
                continue
            cleaned.append(line)

        return "\n".join(cleaned)

    def get_cover_title(self, filename: str) -> str:
        """Obtiene el título para la portada basado en el nombre del archivo."""
        return FILE_TITLES.get(filename, filename.replace(".md", "").replace("_", " ").upper())

    def group_sections(self, html: str) -> str:
        """Agrupa títulos con contenido siguiente."""
        soup = BeautifulSoup(html, "html.parser")

        for h in soup.find_all(["h2", "h3", "h4"]):
            wrap = soup.new_tag("div")
            wrap["class"] = "section-block"
            h.insert_before(wrap)
            wrap.append(h.extract())

            count = 0
            cur = wrap.next_sibling
            while cur and count < 3:
                if isinstance(cur, str):
                    if not cur.strip():
                        tmp = cur.next_sibling
                        cur.extract()
                        cur = tmp
                        continue
                    break
                if hasattr(cur, "name") and cur.name in ["h1", "h2", "h3", "h4"]:
                    break
                if hasattr(cur, "name"):
                    tmp = cur.next_sibling
                    wrap.append(cur.extract())
                    cur = tmp
                    count += 1
                else:
                    cur = cur.next_sibling

        return str(soup)

    def generate_cover_pdf(self, title: str, stem: str) -> Path:
        """Genera portada con título basado en archivo."""
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;600;800&display=swap');

html, body {{
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}}

body {{
    background: linear-gradient(160deg, #1e3a8a 0%, #312e81 50%, #1e1b4b 100%);
    font-family: 'Inter', Arial, sans-serif;
    position: relative;
}}

.center-box {{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    width: 85%;
}}

.diamond {{
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    transform: rotate(45deg);
    margin: 0 auto 30px auto;
}}

h1 {{
    font-size: 28px;
    font-weight: 800;
    color: white;
    text-transform: uppercase;
    letter-spacing: 1px;
    line-height: 1.3;
    margin-bottom: 12px;
}}

.subtitle {{
    font-size: 13px;
    font-weight: 300;
    color: #93c5fd;
    letter-spacing: 3px;
    margin-bottom: 35px;
    text-transform: uppercase;
}}

.badge {{
    display: inline-block;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.25);
    color: white;
    padding: 10px 28px;
    border-radius: 25px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
}}

.footer {{
    position: absolute;
    bottom: 30px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 10px;
    color: rgba(255,255,255,0.4);
    letter-spacing: 1px;
}}
</style>
</head>
<body>
<div class="center-box">
    <div class="diamond"></div>
    <h1>{title}</h1>
    <div class="subtitle">Guía MLOps v5.0 — Senior Edition</div>
    <div class="badge">PORTFOLIO EDITION</div>
</div>
<div class="footer">DUQUEOM | 2025</div>
</body>
</html>"""

        tmp = OUTPUT_DIR / f"_c_{stem}.html"
        tmp.write_text(html, encoding="utf-8")

        pdf = OUTPUT_DIR / f"_c_{stem}.pdf"
        cmd = [
            "wkhtmltopdf",
            "--page-size",
            "Letter",
            "--margin-top",
            "0mm",
            "--margin-bottom",
            "0mm",
            "--margin-left",
            "0mm",
            "--margin-right",
            "0mm",
            "--quiet",
            str(tmp),
            str(pdf),
        ]
        subprocess.run(cmd, capture_output=True)
        tmp.unlink()
        return pdf

    def generate_content_pdf(self, html: str, stem: str) -> Path:
        """Genera PDF de contenido."""
        full = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<link rel="stylesheet" href="_style.css">
</head><body>{html}</body></html>"""

        tmp = OUTPUT_DIR / f"_t_{stem}.html"
        tmp.write_text(full, encoding="utf-8")

        pdf = OUTPUT_DIR / f"_t_{stem}.pdf"
        cmd = [
            "wkhtmltopdf",
            "--page-size",
            "Letter",
            "--margin-top",
            "15mm",
            "--margin-bottom",
            "15mm",
            "--margin-left",
            "15mm",
            "--margin-right",
            "15mm",
            "--enable-local-file-access",
            "--quiet",
            str(tmp),
            str(pdf),
        ]
        subprocess.run(cmd, capture_output=True)
        tmp.unlink()
        return pdf

    def merge_pdfs(self, p1: Path, p2: Path, out: Path):
        """Une dos PDFs."""
        from PyPDF2 import PdfMerger

        m = PdfMerger()
        m.append(str(p1))
        m.append(str(p2))
        m.write(str(out))
        m.close()

    def process_module(self, md_file: str) -> Optional[Path]:
        """Procesa un módulo completo."""
        path = BASE_DIR / md_file
        if not path.exists():
            return None

        print(f"  > {md_file}")

        raw = path.read_text(encoding="utf-8")
        clean = self.clean_markdown(raw)

        # Título para portada = nombre del archivo (no del contenido)
        cover_title = self.get_cover_title(md_file)

        html = markdown.markdown(clean, extensions=["tables", "fenced_code", "nl2br"])
        html = self.group_sections(html)

        stem = md_file.replace(".md", "")
        cover = self.generate_cover_pdf(cover_title, stem)
        content = self.generate_content_pdf(html, stem)

        final = OUTPUT_DIR / f"{stem}.pdf"
        self.merge_pdfs(cover, content, final)

        cover.unlink()
        content.unlink()
        return final

    def generate_global_cover(self) -> Path:
        """Portada principal."""
        html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;600;900&display=swap');

html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}

body {
    background: linear-gradient(180deg, #0c0f1a 0%, #1a1f3a 50%, #0f172a 100%);
    font-family: 'Inter', Arial, sans-serif;
    position: relative;
}

.center-box {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    width: 90%;
}

.logo {
    width: 70px;
    height: 70px;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    border-radius: 16px;
    margin: 0 auto 35px auto;
}

h1 {
    font-size: 42px;
    font-weight: 900;
    color: #60a5fa;
    letter-spacing: 5px;
    margin-bottom: 8px;
}

h2 {
    font-size: 18px;
    font-weight: 300;
    color: #94a3b8;
    letter-spacing: 4px;
    margin-bottom: 40px;
    text-transform: uppercase;
}

.badge {
    display: inline-block;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: white;
    padding: 12px 32px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 2px;
    margin-bottom: 45px;
}

.stats {
    margin-bottom: 30px;
}

.stat {
    display: inline-block;
    margin: 0 25px;
    text-align: center;
}

.stat-num {
    font-size: 32px;
    font-weight: 700;
    color: #60a5fa;
    display: block;
}

.stat-label {
    font-size: 10px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.footer {
    position: absolute;
    bottom: 30px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 12px;
    color: #475569;
    letter-spacing: 1px;
}
</style>
</head>
<body>
<div class="center-box">
    <div class="logo"></div>
    <h1>GUÍA MLOPS</h1>
    <h2>De Cero a Senior / Staff</h2>
    <div class="badge">VERSION 5.0 — PORTFOLIO EDITION</div>
    <div class="stats">
        <div class="stat"><span class="stat-num">23</span><span class="stat-label">Módulos</span></div>
        <div class="stat"><span class="stat-num">86</span><span class="stat-label">Horas</span></div>
        <div class="stat"><span class="stat-num">8</span><span class="stat-label">Semanas</span></div>
    </div>
</div>
<div class="footer">DUQUEOM | 2025</div>
</body>
</html>"""

        tmp = OUTPUT_DIR / "_global.html"
        tmp.write_text(html, encoding="utf-8")

        out = OUTPUT_DIR / "_000_COVER.pdf"
        cmd = [
            "wkhtmltopdf",
            "--page-size",
            "Letter",
            "--margin-top",
            "0mm",
            "--margin-bottom",
            "0mm",
            "--margin-left",
            "0mm",
            "--margin-right",
            "0mm",
            "--quiet",
            str(tmp),
            str(out),
        ]
        subprocess.run(cmd, capture_output=True)
        tmp.unlink()
        return out

    def merge_all(self, pdfs: List[Path]):
        """Combina todos los PDFs."""
        from PyPDF2 import PdfMerger

        final = OUTPUT_DIR / FINAL_FILENAME
        print(f"\n[*] Combinando {len(pdfs)} PDFs...")

        m = PdfMerger()
        for p in pdfs:
            if p.exists():
                m.append(str(p))
        m.write(str(final))
        m.close()

        mb = final.stat().st_size / (1024 * 1024)
        print(f"[OK] {final.name} ({mb:.1f} MB)")


def main():
    print("=" * 50)
    print("  GENERADOR PDF PRO v8.0")
    print("=" * 50)

    gen = PDFGenerator()

    print("\n[1] Portada global...")
    cover = gen.generate_global_cover()

    print("\n[2] Módulos:")
    pdfs = [cover]
    for f in ORDERED_FILES:
        p = gen.process_module(f)
        if p:
            pdfs.append(p)

    gen.merge_all(pdfs)
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
    main()
