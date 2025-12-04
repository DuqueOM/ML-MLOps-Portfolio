#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
GENERADOR DE PDFs - GUÍA MLOps
═══════════════════════════════════════════════════════════════════════════════

Métodos de generación:
1. Pandoc + XeLaTeX (mejor calidad) - sudo apt install pandoc texlive-xetex
2. Pandoc + wkhtmltopdf             - sudo apt install pandoc wkhtmltopdf
3. Python weasyprint                - pip install markdown weasyprint

Uso:
    python generate_pdfs.py                    # Genera todos los PDFs
    python generate_pdfs.py 01_FUNDAMENTOS.md  # Genera un PDF específico
    python generate_pdfs.py --install          # Muestra instrucciones de instalación
"""

import subprocess
from pathlib import Path

# Configuración
GUIDE_DIR = Path(__file__).parent
OUTPUT_DIR = GUIDE_DIR / "pdf"

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_banner():
    """Mostrar banner."""
    print(
        f"""
{BLUE}═══════════════════════════════════════════════════════════════════════════════{RESET}
{BOLD}                    📚 GENERADOR DE PDFs - GUÍA MLOps                          {RESET}
{BLUE}═══════════════════════════════════════════════════════════════════════════════{RESET}
"""
    )


def print_install_instructions():
    """Mostrar instrucciones de instalación."""
    print(
        f"""
{YELLOW}📦 INSTRUCCIONES DE INSTALACIÓN{RESET}

{BOLD}Opción 1: Pandoc + XeLaTeX (Recomendado - Mejor calidad){RESET}
{GREEN}sudo apt update
sudo apt install pandoc texlive-xetex texlive-fonts-recommended{RESET}

{BOLD}Opción 2: Pandoc + wkhtmltopdf (Más rápido){RESET}
{GREEN}sudo apt install pandoc wkhtmltopdf{RESET}

{BOLD}Opción 3: Python weasyprint (Sin sudo){RESET}
{GREEN}python -m venv venv
source venv/bin/activate
pip install markdown weasyprint{RESET}

{BOLD}Opción 4: Usar VS Code / Obsidian{RESET}
- VS Code: Extensión "Markdown PDF"
- Obsidian: Export to PDF plugin

{BOLD}Opción 5: Online{RESET}
- https://md2pdf.netlify.app/
- https://www.markdowntopdf.com/
"""
    )


def check_pandoc():
    """Verificar si pandoc está instalado."""
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
        version = result.stdout.decode().split("\n")[0]
        return True, version
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, None


def check_xelatex():
    """Verificar si xelatex está instalado."""
    try:
        subprocess.run(["xelatex", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_wkhtmltopdf():
    """Verificar si wkhtmltopdf está instalado."""
    try:
        subprocess.run(["wkhtmltopdf", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def generate_pdf_pandoc_xelatex(md_file: Path, output_dir: Path):
    """Generar PDF usando pandoc + xelatex con estilo libro universitario."""
    pdf_file = output_dir / f"{md_file.stem}.pdf"

    # Header LaTeX para evitar títulos huérfanos y mejorar presentación
    latex_header = r"""
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{float}

% Estilo de página
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\leftmark}
\fancyhead[R]{\thepage}
\fancyfoot[C]{Guía MLOps v5.0: Senior Edition}

% CRÍTICO: Evitar títulos huérfanos (solos al final de página)
\widowpenalty=10000
\clubpenalty=10000
\brokenpenalty=10000

% Mantener títulos con su contenido
\titlespacing*{\section}{0pt}{12pt plus 4pt minus 2pt}{6pt plus 2pt minus 2pt}
\titlespacing*{\subsection}{0pt}{10pt plus 4pt minus 2pt}{4pt plus 2pt minus 2pt}
\titlespacing*{\subsubsection}{0pt}{8pt plus 4pt minus 2pt}{4pt plus 2pt minus 2pt}

% Evitar que títulos queden solos
\makeatletter
    \def\@seccntformat#1{\csname the#1\endcsname\quad}
    \renewcommand{\section}{%
        \@startsection{section}{1}{0pt}{-3.5ex plus -1ex minus -.2ex}{%
        2.3ex plus .2ex}{\normalfont\Large\bfseries}}
    \renewcommand{\subsection}{%
        \@startsection{subsection}{2}{0pt}{-3.25ex plus -1ex minus -.2ex}{%
        1.5ex plus .2ex}{\normalfont\large\bfseries}}
\makeatother

% Tablas mejoradas
\renewcommand{\arraystretch}{1.3}

% Bloques de código sin cortar
\usepackage{listings}
\lstset{
    breaklines=true,
    breakatwhitespace=true,
    basicstyle=\small\ttfamily,
    frame=single,
    framesep=5pt
}
"""

    # Escribir header temporal
    header_file = output_dir / "_header.tex"
    header_file.write_text(latex_header)

    cmd = [
        "pandoc",
        str(md_file),
        "-o",
        str(pdf_file),
        "--pdf-engine=xelatex",
        "-V",
        "geometry:margin=2.5cm",
        "-V",
        "geometry:top=3cm",
        "-V",
        "geometry:bottom=3cm",
        "-V",
        "fontsize=11pt",
        "-V",
        "documentclass=article",
        "-V",
        "mainfont=DejaVu Sans",
        "-V",
        "monofont=DejaVu Sans Mono",
        "--toc",
        "--toc-depth=3",
        "-V",
        "colorlinks=true",
        "-V",
        "linkcolor=blue",
        "-V",
        "urlcolor=blue",
        "-V",
        "toccolor=gray",
        "--highlight-style=tango",
        f"--include-in-header={header_file}",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()
    except subprocess.TimeoutExpired:
        return False, "Timeout - archivo muy grande"


def generate_pdf_pandoc_html(md_file: Path, output_dir: Path):
    """Generar PDF usando pandoc + wkhtmltopdf con márgenes de 0.5 pulgadas."""
    pdf_file = output_dir / f"{md_file.stem}.pdf"

    # Márgenes de 0.5 pulgadas = 12.7mm
    margin = "12.7mm"

    # Crear archivo CSS optimizado para PDF estilo libro universitario
    css_file = output_dir / "_style.css"
    css_content = """
/* ═══════════════════════════════════════════════════════════════
   ESTILOS PDF - GUÍA MLOPS v5.0: Senior Edition
   Estilo: Libro Educativo Universitario
   ═══════════════════════════════════════════════════════════════ */

/* Layout general */
body {
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #2d3748;
    max-width: 100% !important;
    width: 100% !important;
    text-align: justify;
}

/* ═══════════════════════════════════════════════════════════════
   CONTROL DE TÍTULOS HUÉRFANOS (CRÍTICO)
   ═══════════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 {
    color: #1a365d;
    page-break-after: avoid !important;
    break-after: avoid !important;
    page-break-inside: avoid !important;
}

/* Forzar que el contenido siga al título */
h1 + *, h2 + *, h3 + *, h4 + * {
    page-break-before: avoid !important;
}

/* Encabezados con espacio adecuado */
h1 {
    font-size: 1.8em;
    border-bottom: 3px solid #3182ce;
    padding-bottom: 10px;
    margin-top: 1.5em;
    margin-bottom: 0.8em;
}

h2 {
    font-size: 1.4em;
    border-bottom: 1.5px solid #90cdf4;
    padding-bottom: 6px;
    margin-top: 1.3em;
    margin-bottom: 0.6em;
}

h3 {
    font-size: 1.15em;
    margin-top: 1.1em;
    margin-bottom: 0.5em;
    color: #2c5282;
}

h4 {
    font-size: 1.05em;
    margin-top: 1em;
    margin-bottom: 0.4em;
    color: #3182ce;
}

/* ═══════════════════════════════════════════════════════════════
   CÓDIGO Y BLOQUES
   ═══════════════════════════════════════════════════════════════ */
code {
    background: #edf2f7;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 0.88em;
    font-family: 'Consolas', 'Monaco', monospace;
    color: #d53f8c;
}

pre {
    background: #1a202c;
    color: #e2e8f0;
    padding: 14px 18px;
    border-radius: 6px;
    font-size: 0.82em;
    line-height: 1.45;
    white-space: pre-wrap;
    word-wrap: break-word;
    page-break-inside: avoid !important;
    break-inside: avoid !important;
    margin: 14px 0;
}

pre code {
    background: transparent;
    color: inherit;
    padding: 0;
    font-size: 1em;
}

/* ═══════════════════════════════════════════════════════════════
   TABLAS ESTILO LIBRO
   ═══════════════════════════════════════════════════════════════ */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 0.9em;
    page-break-inside: avoid !important;
    break-inside: avoid !important;
}

thead {
    display: table-header-group;
}

tr {
    page-break-inside: avoid;
    page-break-after: auto;
}

th {
    background: linear-gradient(180deg, #3182ce 0%, #2c5282 100%);
    color: white;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    font-size: 0.95em;
    border: none;
}

td {
    border-bottom: 1px solid #e2e8f0;
    padding: 10px 14px;
    vertical-align: top;
}

tr:nth-child(even) {
    background: #f7fafc;
}

/* ═══════════════════════════════════════════════════════════════
   OTROS ELEMENTOS
   ═══════════════════════════════════════════════════════════════ */
blockquote {
    border-left: 4px solid #3182ce;
    margin: 18px 0;
    padding: 12px 18px;
    background: linear-gradient(90deg, #ebf8ff 0%, #ffffff 100%);
    border-radius: 0 6px 6px 0;
    page-break-inside: avoid;
    font-style: italic;
}

blockquote p {
    margin: 0;
}

a {
    color: #3182ce;
    text-decoration: none;
}

p {
    margin: 0.6em 0;
    orphans: 3;
    widows: 3;
}

/* Listas mejoradas */
ul, ol {
    margin: 0.6em 0;
    padding-left: 2em;
}

li {
    margin: 0.35em 0;
    line-height: 1.55;
}

/* Separadores */
hr {
    border: none;
    border-top: 2px solid #e2e8f0;
    margin: 28px 0;
}

/* ═══════════════════════════════════════════════════════════════
   ASCII ART Y DIAGRAMAS
   ═══════════════════════════════════════════════════════════════ */
pre.sourceCode, .ascii-diagram {
    page-break-inside: avoid !important;
    font-size: 0.72em;
    line-height: 1.25;
    background: #f8f9fa;
    color: #1a202c;
    border: 1px solid #e2e8f0;
}
"""
    css_file.write_text(css_content)

    cmd = [
        "pandoc",
        str(md_file),
        "-o",
        str(pdf_file),
        "--pdf-engine=wkhtmltopdf",
        f"--css={css_file}",
        "-V",
        f"margin-top={margin}",
        "-V",
        f"margin-bottom={margin}",
        "-V",
        f"margin-left={margin}",
        "-V",
        f"margin-right={margin}",
        "-V",
        "papersize=letter",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=90)
        if result.returncode == 0:
            return True, None
        return False, result.stderr.decode()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.decode()
    except subprocess.TimeoutExpired:
        return False, "Timeout"


def generate_pdf_weasyprint(md_file: Path, output_dir: Path):
    """Generar PDF usando markdown + weasyprint."""
    try:
        import markdown
        from weasyprint import CSS, HTML
    except ImportError:
        print("❌ Instala: pip install markdown weasyprint")
        return False

    pdf_file = output_dir / f"{md_file.stem}.pdf"

    # Leer markdown
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Convertir a HTML
    html_content = markdown.markdown(md_content, extensions=["tables", "fenced_code", "codehilite", "toc"])

    # CSS profesional estilo libro universitario
    css = CSS(
        string="""
        @page {
            size: A4;
            margin: 2.5cm 2cm 2.5cm 2cm;

            @top-center {
                content: "Guía MLOps v4.0";
                font-size: 9pt;
                color: #666;
            }
            @bottom-center {
                content: counter(page);
                font-size: 9pt;
            }
        }

        /* Evitar títulos huérfanos */
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
            break-after: avoid;
        }

        /* Mantener párrafos unidos */
        p {
            orphans: 3;
            widows: 3;
        }

        body {
            font-family: "Georgia", "Times New Roman", serif;
            font-size: 11pt;
            line-height: 1.7;
            color: #2d3748;
            text-align: justify;
            hyphens: auto;
        }

        h1 {
            color: #1a365d;
            font-size: 24pt;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 12px;
            margin-top: 40px;
            margin-bottom: 20px;
            page-break-before: always;
        }
        h1:first-of-type {
            page-break-before: avoid;
        }

        h2 {
            color: #2c5282;
            font-size: 18pt;
            border-bottom: 1.5px solid #90cdf4;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 15px;
        }

        h3 {
            color: #2b6cb0;
            font-size: 14pt;
            margin-top: 25px;
            margin-bottom: 12px;
        }

        h4 {
            color: #3182ce;
            font-size: 12pt;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        code {
            background: #edf2f7;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 9.5pt;
            color: #d53f8c;
        }

        pre {
            background: #1a202c;
            color: #e2e8f0;
            padding: 16px 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 9pt;
            line-height: 1.5;
            margin: 16px 0;
            page-break-inside: avoid;
            break-inside: avoid;
        }

        pre code {
            background: transparent;
            color: inherit;
            padding: 0;
        }

        /* Tablas estilo libro */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 10pt;
            page-break-inside: avoid;
            break-inside: avoid;
        }

        th {
            background: linear-gradient(180deg, #3182ce 0%, #2c5282 100%);
            color: white;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            border: none;
        }

        td {
            border-bottom: 1px solid #e2e8f0;
            padding: 10px 16px;
            vertical-align: top;
        }

        tr:nth-child(even) {
            background: #f7fafc;
        }

        tr:hover {
            background: #edf2f7;
        }

        /* Blockquotes estilo nota */
        blockquote {
            border-left: 4px solid #3182ce;
            margin: 24px 0;
            padding: 16px 24px;
            background: linear-gradient(90deg, #ebf8ff 0%, #ffffff 100%);
            font-style: italic;
            color: #2d3748;
            border-radius: 0 8px 8px 0;
            page-break-inside: avoid;
        }

        blockquote p {
            margin: 0;
        }

        a {
            color: #3182ce;
            text-decoration: none;
        }

        /* Listas mejoradas */
        ul, ol {
            margin: 12px 0;
            padding-left: 2em;
        }

        li {
            margin: 6px 0;
            line-height: 1.6;
        }

        /* TOC estilo libro */
        .toc {
            background: #f7fafc;
            padding: 24px 32px;
            border-radius: 8px;
            margin-bottom: 40px;
            border: 1px solid #e2e8f0;
        }

        .toc h2 {
            border: none;
            margin-top: 0;
        }

        /* Separadores */
        hr {
            border: none;
            border-top: 2px solid #e2e8f0;
            margin: 32px 0;
        }

        /* ASCII diagrams */
        .ascii-art, pre.ascii {
            font-family: "Courier New", monospace;
            font-size: 8pt;
            line-height: 1.2;
            background: #f8f9fa;
            color: #1a202c;
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
        }
    """
    )

    # HTML completo
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{md_file.stem}</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Generar PDF
    try:
        HTML(string=full_html).write_pdf(str(pdf_file), stylesheets=[css])
        print(f"✅ Generado: {pdf_file.name}")
        return True
    except Exception as e:
        print(f"❌ Error en {md_file.name}: {e}")
        return False


def main():
    """Función principal."""
    import sys

    # Manejar argumentos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install":
            print_banner()
            print_install_instructions()
            return
        elif sys.argv[1] == "--help":
            print(__doc__)
            return

    print_banner()

    # Crear directorio de salida
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Determinar archivos a procesar
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Archivo específico
        md_files = [GUIDE_DIR / sys.argv[1]]
        if not md_files[0].exists():
            print(f"{RED}❌ Archivo no encontrado: {sys.argv[1]}{RESET}")
            return
    else:
        # Todos los archivos
        md_files = sorted(GUIDE_DIR.glob("*.md"))
        md_files = [f for f in md_files if not f.name.startswith("generate")]

    print(f"📁 Archivos a procesar: {len(md_files)}")
    print(f"📂 Output: {OUTPUT_DIR}\n")

    # Detectar herramientas disponibles
    has_pandoc, pandoc_version = check_pandoc()
    has_xelatex = check_xelatex()
    has_wkhtmltopdf = check_wkhtmltopdf()

    # Seleccionar método de generación
    if has_pandoc and has_xelatex:
        print(f"{GREEN}✅ Usando: Pandoc + XeLaTeX (mejor calidad){RESET}")
        print(f"   {pandoc_version}\n")

        def generate_func(md, out):
            success, err = generate_pdf_pandoc_xelatex(md, out)
            return success

    elif has_pandoc and has_wkhtmltopdf:
        print(f"{YELLOW}⚠️ Usando: Pandoc + wkhtmltopdf{RESET}\n")

        def generate_func(md, out):
            success, err = generate_pdf_pandoc_html(md, out)
            return success

    else:
        print(f"{YELLOW}⚠️ Pandoc no disponible. Intentando weasyprint...{RESET}\n")
        generate_func = generate_pdf_weasyprint

    # Generar PDFs
    success = 0
    failed = 0

    for md_file in md_files:
        print(f"📄 Procesando: {md_file.name}...", end=" ")
        try:
            if generate_func(md_file, OUTPUT_DIR):
                print(f"{GREEN}✅{RESET}")
                success += 1
            else:
                print(f"{RED}❌{RESET}")
                failed += 1
        except Exception as e:
            print(f"{RED}❌ Error: {e}{RESET}")
            failed += 1

    # Resumen
    print(f"\n{BLUE}{'═' * 60}{RESET}")
    print(f"{BOLD}📊 RESUMEN: {GREEN}{success} exitosos{RESET}, {RED}{failed} fallidos{RESET}")
    print(f"{BLUE}{'═' * 60}{RESET}")

    if success > 0:
        print(f"\n✅ PDFs generados en: {OUTPUT_DIR}")

    if failed > 0:
        print(f"\n{YELLOW}💡 Tip: Ejecuta 'python generate_pdfs.py --install' para ver opciones de instalación{RESET}")


if __name__ == "__main__":
    main()
