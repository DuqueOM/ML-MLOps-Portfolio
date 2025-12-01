#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SETUP: Voice Tools con gTTS (voz natural de Google)
# Para Windows 10 + WSL
# ═══════════════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "           🎙️ CONFIGURACIÓN DE VOZ NATURAL (gTTS)"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/.venv-voice"
SCRIPT_NAME="read_aloud_gtts.py"

# 1. Crear entorno virtual
echo "📦 Creando entorno virtual en $VENV_DIR..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# 2. Instalar gTTS
echo ""
echo "🔧 Instalando gTTS..."
pip install --upgrade pip
pip install gtts

# 3. Copiar script a ubicación fija
echo ""
echo "📝 Instalando script..."
cp "$SCRIPT_DIR/$SCRIPT_NAME" "$HOME/$SCRIPT_NAME"
chmod +x "$HOME/$SCRIPT_NAME"

# 4. Crear wrapper script
echo ""
echo "🔗 Creando wrapper..."
cat > "$HOME/read_aloud.sh" << 'EOF'
#!/bin/bash
source ~/.venv-voice/bin/activate
python ~/read_aloud_gtts.py "$@"
EOF
chmod +x "$HOME/read_aloud.sh"

# 5. Crear script PowerShell para Windows
WINDOWS_SCRIPT="$HOME/ReadAloudGTTS.ps1"
cat > "$WINDOWS_SCRIPT" << 'EOF'
# Read Aloud usando gTTS (voz natural de Google)
# Ejecuta el script de Python en WSL

param(
    [switch]$Stop
)

if ($Stop) {
    wsl.exe -e bash -c "source ~/.venv-voice/bin/activate && python ~/read_aloud_gtts.py --stop"
} else {
    wsl.exe -e bash -c "source ~/.venv-voice/bin/activate && python ~/read_aloud_gtts.py"
}
EOF

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                          ✅ INSTALACIÓN COMPLETA"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📍 ARCHIVOS INSTALADOS:"
echo "   • $HOME/read_aloud_gtts.py    → Script principal (Python)"
echo "   • $HOME/read_aloud.sh         → Wrapper bash"
echo "   • $WINDOWS_SCRIPT             → Script PowerShell"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                    🔧 CONFIGURAR ATAJO EN WINDOWS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "OPCIÓN A: Crear acceso directo"
echo ""
echo "   1. Clic derecho en Escritorio → Nuevo → Acceso directo"
echo ""
echo "   2. Ubicación del elemento:"
echo '      powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "wsl.exe -e bash -c \"source ~/.venv-voice/bin/activate && python ~/read_aloud_gtts.py\""'
echo ""
echo "   3. Nombre: Read Aloud (gTTS)"
echo ""
echo "   4. Clic derecho → Propiedades → Tecla de método abreviado:"
echo "      Ctrl + Alt + R"
echo ""
echo "OPCIÓN B: Para DETENER la reproducción"
echo ""
echo "   1. Crear otro acceso directo con:"
echo '      powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -Command "wsl.exe -e bash -c \"source ~/.venv-voice/bin/activate && python ~/read_aloud_gtts.py --stop\""'
echo ""
echo "   2. Asignar atajo: Ctrl + Alt + S (Stop)"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "🎤 USO:"
echo "   1. Selecciona texto en cualquier app (Windsurf, navegador, etc.)"
echo "   2. Ctrl + C para copiar"
echo "   3. Ctrl + Alt + R para escuchar (voz natural de Google)"
echo "   4. Ctrl + Alt + S para detener"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
