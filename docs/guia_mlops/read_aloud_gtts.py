#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
READ ALOUD - Lee texto del portapapeles usando gTTS (voz natural)
Para Windows 10 + WSL
═══════════════════════════════════════════════════════════════════════════════

Uso:
    python read_aloud_gtts.py          # Lee el portapapeles
    python read_aloud_gtts.py --stop   # Detiene la reproducción actual

Requisitos:
    pip install gtts

Configurar atajo en Windows:
    wsl.exe -e bash -c "source ~/.venv-voice/bin/activate && python ~/read_aloud_gtts.py"
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

LANG = "es"  # Idioma para gTTS
SLOW = False  # Velocidad normal
TEMP_DIR = Path(tempfile.gettempdir())
AUDIO_FILE = TEMP_DIR / "read_aloud_temp.mp3"
PID_FILE = TEMP_DIR / "read_aloud_pid.txt"


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════════════════════════


def get_clipboard_from_windows() -> str:
    """Obtiene el contenido del portapapeles de Windows desde WSL.

    Maneja correctamente distintas codificaciones (UTF-8, UTF-16, cp1252)
    para evitar errores con caracteres como "¡", acentos, etc.
    """
    try:
        # Leemos la salida en binario y la decodificamos manualmente
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", "Get-Clipboard"],
            capture_output=True,
            text=False,
            timeout=5,
        )

        data = result.stdout
        if not data:
            return ""

        # 1) Intentar UTF-8
        for encoding in ("utf-8", "utf-16-le", "cp1252"):
            try:
                return data.decode(encoding).strip()
            except UnicodeDecodeError:
                continue

        # Último recurso: decodificar reemplazando caracteres inválidos
        return data.decode("utf-8", errors="replace").strip()

    except Exception as e:
        print(f"Error al leer portapapeles: {e}")
        return ""


def clean_text_for_speech(text: str) -> str:
    """Limpia el texto para que suene natural al leerlo."""
    # Eliminar bloques de código
    text = re.sub(r"```[\s\S]*?```", " código omitido ", text)
    text = re.sub(r"`[^`]+`", "", text)

    # Eliminar markdown
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)  # Headers
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # Bold
    text = re.sub(r"\*([^*]+)\*", r"\1", text)  # Italic
    text = re.sub(r"__([^_]+)__", r"\1", text)  # Bold alt
    text = re.sub(r"_([^_]+)_", r"\1", text)  # Italic alt

    # Eliminar URLs
    text = re.sub(r"https?://\S+", " enlace ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [text](url)

    # Eliminar caracteres especiales
    text = re.sub(r"[═╔╗╚╝║─│┌┐└┘├┤┬┴┼▶▼►◀●○◆◇★☆→←↑↓]", "", text)
    text = re.sub(r"[\[\]{}|<>]", "", text)

    # Limpiar tablas markdown (simplificado)
    text = re.sub(r"^\|.*\|$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\s\-:]+$", "", text, flags=re.MULTILINE)

    # Limpiar emojis comunes de documentación
    text = re.sub(r"[📚📋📁📦🔧⚙️✅❌⚠️💡🎯🚀📝🔄▶️]", "", text)

    # Limpiar espacios múltiples y líneas vacías
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)

    return text.strip()


def stop_playback():
    """Detiene cualquier reproducción en curso."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            subprocess.run(["kill", str(pid)], capture_output=True)
            PID_FILE.unlink()
            print("Reproduccion detenida.")
        except Exception:
            pass

    # También intentar matar cualquier proceso de reproducción
    subprocess.run(["pkill", "-f", "ffplay.*read_aloud_temp"], capture_output=True)
    subprocess.run(
        [
            "powershell.exe",
            "-Command",
            "Stop-Process -Name 'wmplayer' -ErrorAction SilentlyContinue",
        ],
        capture_output=True,
    )


def play_audio_windows(audio_path: Path):
    """Reproduce el audio usando Windows Media Player o similar."""
    # Convertir ruta WSL a Windows
    wsl_path = str(audio_path)

    # Usar PowerShell para reproducir
    # Opción 1: Usar Start-Process con el reproductor por defecto
    windows_path = subprocess.run(
        ["wslpath", "-w", wsl_path],
        capture_output=True,
        text=True,
    ).stdout.strip()

    print(f"Reproduciendo: {windows_path}")

    # Reproducir con el programa por defecto de Windows
    process = subprocess.Popen(
        [
            "powershell.exe",
            "-Command",
            f'Start-Process "{windows_path}"',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Guardar PID para poder detenerlo después
    PID_FILE.write_text(str(process.pid))


def generate_and_play(text: str):
    """Genera audio con gTTS y lo reproduce."""
    from gtts import gTTS

    # Limpiar texto
    clean_text = clean_text_for_speech(text)

    if len(clean_text) < 10:
        print("Texto muy corto para leer.")
        return

    # Mostrar preview
    preview = clean_text[:100] + "..." if len(clean_text) > 100 else clean_text
    print(f"Leyendo: {preview}")
    print("-" * 60)

    # Generar audio
    print("Generando audio...")
    tts = gTTS(text=clean_text, lang=LANG, slow=SLOW)
    tts.save(str(AUDIO_FILE))

    print("Reproduciendo...")
    play_audio_windows(AUDIO_FILE)
    print("Listo. El audio se reproduce en segundo plano.")


def main():
    """Punto de entrada principal."""
    # Verificar argumentos
    if "--stop" in sys.argv:
        stop_playback()
        return

    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return

    # Detener reproducción anterior si existe
    stop_playback()

    # Obtener texto del portapapeles
    text = get_clipboard_from_windows()

    if not text:
        print("No hay texto en el portapapeles.")
        return

    # Generar y reproducir
    generate_and_play(text)


if __name__ == "__main__":
    main()
