#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
GENERADOR DE AUDIO - GUÍA MLOps
Convierte módulos Markdown a archivos MP3 usando gTTS (Google Text-to-Speech)
═══════════════════════════════════════════════════════════════════════════════

Uso:
    python generate_audio.py                    # Genera todos los módulos
    python generate_audio.py 01_FUNDAMENTOS.md  # Genera un módulo específico
    python generate_audio.py --install          # Muestra instrucciones de instalación

Instalación:
    pip install gtts
"""

import re
import sys
import time
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

# Idioma para gTTS (español)
LANG = "es"

# Usar velocidad lenta (más clara para educación)
SLOW = False

# Directorio de salida
OUTPUT_DIR = "audio"

# Archivos a procesar (orden correcto) - v5.0 Senior Edition
MODULE_FILES = [
    # === ÍNDICE Y NAVEGACIÓN ===
    "00_INDICE.md",
    "SYLLABUS.md",
    # === FASE 1: FUNDAMENTOS ===
    "01_PYTHON_MODERNO.md",
    "02_DISENO_SISTEMAS.md",
    "03_ESTRUCTURA_PROYECTO.md",
    "04_ENTORNOS.md",
    "05_GIT_PROFESIONAL.md",
    "06_VERSIONADO_DATOS.md",
    # === FASE 2: ML ENGINEERING ===
    "07_SKLEARN_PIPELINES.md",
    "08_INGENIERIA_FEATURES.md",
    "09_TRAINING_PROFESIONAL.md",
    "10_EXPERIMENT_TRACKING.md",
    # === FASE 3: MLOps CORE ===
    "11_TESTING_ML.md",
    "12_CI_CD.md",
    "13_DOCKER.md",
    "14_FASTAPI.md",
    "15_STREAMLIT.md",
    # === FASE 4: PRODUCCIÓN ===
    "16_OBSERVABILIDAD.md",
    "17_DESPLIEGUE.md",
    "18_INFRAESTRUCTURA.md",
    # === FASE 5: ESPECIALIZACIÓN ===
    "19_DOCUMENTACION.md",
    "20_PROYECTO_INTEGRADOR.md",
    # === REFERENCIAS ===
    "21_GLOSARIO.md",
    "22_CHECKLIST.md",
    "23_RECURSOS.md",
]


# ═══════════════════════════════════════════════════════════════════════════════
# LIMPIEZA DE TEXTO
# ═══════════════════════════════════════════════════════════════════════════════


def clean_cell_for_speech(text: str) -> str:
    """
    Limpia una celda de tabla para que sea legible sin signos de puntuación.
    """
    # Eliminar comillas, puntos, comas y otros signos de puntuación
    text = re.sub(r'["""\'\'`.,;:!?¿¡()[\]{}*#@&%$~^<>]', "", text)
    # Eliminar guiones sueltos pero mantener palabras compuestas
    text = re.sub(r"\s-\s", " ", text)
    text = re.sub(r"^-\s", "", text)
    text = re.sub(r"\s-$", "", text)
    # Limpiar espacios múltiples
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def convert_table_to_speech(table_text: str) -> str:
    """
    Convierte una tabla Markdown a texto legible para speech.
    Solo lee las filas de datos con formato "Columna: valor".
    No repite los encabezados innecesariamente.
    Limpia signos de puntuación.
    """
    lines = table_text.strip().split("\n")
    result = []
    headers = []
    header_found = False

    for line in lines:
        # Saltar líneas separadoras (|---|---|---| o |:---:|:---:|)
        cells_raw = []
        for cell in line.split("|"):
            c = cell.strip()
            # Quitar enlaces markdown dentro de la celda: [Texto](archivo.md) -> Texto
            c = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", c)
            cells_raw.append(c)
        cells = [c for c in cells_raw if c]  # Eliminar vacíos

        # Si todas las celdas son solo guiones, espacios o dos puntos, es separador
        if all(re.match(r"^[\s\-:]+$", cell) for cell in cells):
            continue

        if not header_found:
            # Primera línea con contenido real = headers (limpiar puntuación)
            headers = [clean_cell_for_speech(c) for c in cells]
            header_found = True
        else:
            # Filas de datos: leer como "Columna valor" (sin signos)
            cleaned_cells = [clean_cell_for_speech(c) for c in cells]
            if len(cleaned_cells) == len(headers):
                row_text = ", ".join([f"{headers[j]} {cleaned_cells[j]}" for j in range(len(cleaned_cells))])
                result.append(row_text + ".")
            elif cleaned_cells:
                result.append(", ".join(cleaned_cells) + ".")

    return "\n".join(result)


def convert_ascii_box_to_speech(box_text: str) -> str:
    """
    Convierte un cuadro ASCII a texto legible para speech.
    Extrae el contenido significativo ignorando los bordes.
    """
    lines = box_text.strip().split("\n")
    content_lines = []

    for line in lines:
        # Eliminar caracteres de borde y espacios extra
        clean = re.sub(r"[╔╗╚╝═║┌┐└┘─│├┤┬┴┼▶▼►◀●○◆◇★☆→←↑↓⟶⟵█░▓\[\]]", "", line)
        clean = clean.strip()
        if clean and len(clean) > 2:  # Solo líneas con contenido significativo
            content_lines.append(clean)

    return "\n".join(content_lines)


def clean_markdown_for_speech(content: str) -> str:
    """
    Limpia el contenido Markdown para que sea legible en voz alta.
    AHORA LEE TABLAS Y CUADROS ASCII convirtiéndolos a texto.
    """
    text = content

    # 1. Convertir tablas Markdown a texto ANTES de eliminarlas
    # Buscar tablas (líneas consecutivas con |)
    table_pattern = r"((?:^\|.+\|$\n?)+)"
    tables = re.findall(table_pattern, text, flags=re.MULTILINE)
    for table in tables:
        speech_table = convert_table_to_speech(table)
        text = text.replace(table, f"\n{speech_table}\n")

    # 2. Convertir cuadros ASCII a texto ANTES de eliminarlos
    # Buscar bloques que empiezan con ╔ o ┌
    box_pattern = r"((?:^[╔┌].*$\n?)(?:^[║│].*$\n?)*(?:^[╚└].*$\n?))"
    boxes = re.findall(box_pattern, text, flags=re.MULTILINE)
    for box in boxes:
        speech_box = convert_ascii_box_to_speech(box)
        if speech_box.strip():
            text = text.replace(box, f"\nRecuadro: {speech_box}\n")
        else:
            text = text.replace(box, "")

    # 3. Eliminar bloques de código completos (```...```)
    text = re.sub(r"```[\s\S]*?```", " Bloque de código omitido. ", text)

    # 4. Eliminar código inline (`...`) pero indicar que había código
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # 5. Eliminar líneas que son solo símbolos decorativos restantes
    text = re.sub(r"^[╔╗╚╝═║┌┐└┘─│├┤┬┴┼▶▼\[\]█░▓ ]+$", "", text, flags=re.MULTILINE)

    # 6. Eliminar líneas que son solo símbolos decorativos
    text = re.sub(r"^[#═─\-\*\s]+$", "", text, flags=re.MULTILINE)

    # 7. Eliminar HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # 8. Eliminar links markdown pero mantener el texto
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    # 9. Eliminar imágenes markdown
    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", text)

    # 10. Convertir headers a texto con pausas
    text = re.sub(r"^#{1,6}\s*(.+)$", r"\n\1.\n", text, flags=re.MULTILINE)

    # 11. Eliminar formato bold/italic pero mantener texto
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # 12. Convertir listas a texto natural
    text = re.sub(r"^\s*[-*+]\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # 12. Limpiar emojis comunes (convertir a texto o eliminar)
    emoji_map = {
        "🚀": "rocket",
        "📊": "",
        "🎯": "",
        "⚡": "",
        "✅": "",
        "❌": "",
        "📝": "",
        "🔄": "",
        "📁": "",
        "🐳": "Docker",
        "☸️": "Kubernetes",
        "🏗️": "",
        "📈": "",
        "🧪": "",
        "⚙️": "",
        "🔧": "",
        "💡": "",
        "⚠️": "Atención:",
        "🔜": "",
        "📖": "",
        "🏠": "",
        "🏨": "",
        "🍽️": "",
        "🔴": "",
        "🟡": "",
        "🟢": "",
        "🔵": "",
        "📦": "",
        "🤖": "",
        "🌐": "",
        "📋": "",
        "🌟": "",
    }
    for emoji, replacement in emoji_map.items():
        text = text.replace(emoji, replacement)

    # 13. Eliminar caracteres especiales restantes
    text = re.sub(r"[╔╗╚╝═║┌┐└┘─│├┤┬┴┼▶▼►◀●○◆◇★☆→←↑↓⟶⟵]", "", text)

    # 14. Normalizar unidades y siglas problemáticas para TTS en español
    #    - "8h" / "8 h" -> "8 horas"
    #    - "18 min" -> "18 minutos"
    #    - "ML" / "ml" -> "eme ele"
    text = re.sub(r"\b(\d+)\s*h\b", r"\1 horas", text)
    text = re.sub(r"\b(\d+)h\b", r"\1 horas", text)
    text = re.sub(r"\b(\d+)\s*min\b", r"\1 minutos", text)
    text = re.sub(r"\b[Mm][Ll]\b", "eme ele", text)

    # 15. Limpiar múltiples espacios y líneas vacías
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    # 16. Limpiar líneas que quedaron con solo espacios
    text = re.sub(r"^\s+$", "", text, flags=re.MULTILINE)

    # 17. Agregar pausas naturales
    text = text.replace("---", "\n")
    text = text.replace(">", "")

    # 18. Limpiar inicio/fin
    text = text.strip()
    # 19. Eliminar cualquier asterisco residual que quede del markdown
    text = text.replace("*", "")

    return text


def extract_module_title(content: str) -> str:
    """Extrae el título del módulo para anunciarlo."""
    # Buscar el primer header nivel 1
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if match:
        title = match.group(1)
        # Limpiar emojis y formato
        title = re.sub(r"[^\w\s:]", "", title)
        return title.strip()
    return "Módulo"


# ═══════════════════════════════════════════════════════════════════════════════
# GENERACIÓN DE AUDIO
# ═══════════════════════════════════════════════════════════════════════════════


def generate_audio(text: str, output_path: Path):
    """Genera audio MP3 usando gTTS (Google Text-to-Speech)."""
    from gtts import gTTS

    tts = gTTS(text=text, lang=LANG, slow=SLOW)
    tts.save(str(output_path))


def process_file(md_path: Path, output_dir: Path) -> bool:
    """Procesa un archivo Markdown y genera el audio."""
    try:
        # Leer contenido
        content = md_path.read_text(encoding="utf-8")

        # Extraer título
        title = extract_module_title(content)

        # Limpiar para speech
        clean_text = clean_markdown_for_speech(content)

        # Agregar introducción
        intro = f"Bienvenido al {title}.\n\n"
        full_text = intro + clean_text

        # Verificar que hay contenido
        if len(full_text.strip()) < 100:
            print("  ⚠️ Contenido muy corto, saltando...")
            return False

        # Generar audio
        output_path = output_dir / f"{md_path.stem}.mp3"
        generate_audio(full_text, output_path)

        # Obtener tamaño del archivo
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ {output_path.name} ({size_mb:.1f} MB)")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def process_all_files(files_to_process: list, output_dir: Path, skip_existing: bool = True):
    """Procesa todos los archivos con delay para evitar rate limiting."""

    success = 0
    failed = 0
    skipped = 0

    for i, md_path in enumerate(files_to_process):
        # Verificar si ya existe el audio
        output_path = output_dir / f"{md_path.stem}.mp3"
        if skip_existing and output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"⏭️ Saltando: {md_path.name} (ya existe: {size_mb:.1f} MB)")
            skipped += 1
            continue

        print(f"🎙️ Procesando: {md_path.name}...")
        if process_file(md_path, output_dir):
            success += 1
            # Delay de 30 segundos entre archivos para evitar rate limiting
            if i < len(files_to_process) - 1:
                remaining = len(files_to_process) - i - 1
                print(f"  ⏳ Esperando 30s antes del siguiente ({remaining} restantes)...")
                time.sleep(30)
        else:
            failed += 1
            # Delay más largo después de un error (posible rate limit)
            print("  ⏳ Esperando 120s después del error...")
            time.sleep(120)

    return success, failed, skipped


def show_install_instructions():
    """Muestra instrucciones de instalación."""
    print(
        """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🎙️ GENERADOR DE AUDIO - INSTALACIÓN                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   1. Instalar gTTS:                                                           ║
║      pip install gtts                                                         ║
║                                                                               ║
║   2. Ejecutar el generador:                                                   ║
║      python generate_audio.py                                                 ║
║                                                                               ║
║   3. Los archivos MP3 se guardarán en: ./audio/                               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
    )


def main():
    """Punto de entrada principal."""
    print("\n" + "═" * 79)
    print("                    🎙️ GENERADOR DE AUDIO - GUÍA MLOps")
    print("═" * 79 + "\n")

    # Verificar argumentos
    if "--install" in sys.argv:
        show_install_instructions()
        return

    # Verificar que gTTS está instalado
    try:
        from gtts import gTTS  # noqa: F401
    except ImportError:
        print("❌ gTTS no está instalado.\n")
        show_install_instructions()
        return

    # Directorio actual
    script_dir = Path(__file__).parent
    output_dir = script_dir / OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)

    # Determinar archivos a procesar
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # Archivo específico
        files_to_process = [script_dir / sys.argv[1]]
    else:
        # Todos los .md actuales en la carpeta (excepto scripts auxiliares)
        files_to_process = sorted(p for p in script_dir.glob("*.md") if not p.name.startswith("generate"))

    print(f"📁 Archivos a procesar: {len(files_to_process)}")
    print("🗣️ Motor: Google Text-to-Speech (español)")
    print(f"📂 Output: {output_dir}\n")

    # Procesar
    force = "--force" in sys.argv
    success, failed, skipped = process_all_files(files_to_process, output_dir, skip_existing=not force)

    print("\n" + "═" * 60)
    print(f"📊 RESUMEN: ✅ {success} exitosos, ⏭️ {skipped} saltados, ❌ {failed} fallidos")
    print("═" * 60)

    if success > 0:
        print(f"\n✅ Audios generados en: {output_dir}")

        # Calcular tamaño total
        total_size = sum(f.stat().st_size for f in output_dir.glob("*.mp3"))
        print(f"📦 Tamaño total: {total_size / (1024*1024):.1f} MB")


if __name__ == "__main__":
    main()
