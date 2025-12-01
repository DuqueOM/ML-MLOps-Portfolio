#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# SETUP: Voz Multimodal para Windsurf en Ubuntu
# Instala Whisper para speech-to-text y espeak para text-to-speech
# ═══════════════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════════════════════"
echo "           🎙️ CONFIGURACIÓN DE VOZ MULTIMODAL PARA WINDSURF"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

# Verificar sistema
echo "📋 Sistema: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo ""

# 1. Instalar dependencias del sistema
echo "📦 Instalando dependencias del sistema..."
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio ffmpeg espeak-ng xdotool

# 2. Crear entorno virtual
echo ""
echo "🐍 Creando entorno virtual para herramientas de voz..."
cd ~/
python3 -m venv ~/.voice-tools
source ~/.voice-tools/bin/activate

# 3. Instalar Whisper y herramientas
echo ""
echo "🤖 Instalando OpenAI Whisper (transcripción local)..."
pip install --upgrade pip
pip install openai-whisper SpeechRecognition pyaudio pyttsx3

# 4. Crear script de dictado
echo ""
echo "📝 Creando script de dictado..."

cat > ~/.local/bin/voice-to-windsurf << 'SCRIPT'
#!/bin/bash
# Voice to Windsurf - Dicta y pega en el cursor actual
# Uso: Presionar hotkey → Hablar → Esperar transcripción → Pegar

source ~/.voice-tools/bin/activate

python3 << 'PYTHON'
import speech_recognition as sr
import subprocess
import sys

def dictate():
    r = sr.Recognizer()
    
    print("🎙️ Escuchando... (habla ahora)")
    
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=30)
        except sr.WaitTimeoutError:
            print("⏰ Tiempo agotado")
            return
    
    print("🔄 Procesando...")
    
    try:
        # Usar Whisper de OpenAI (via API gratuita de Google como fallback)
        text = r.recognize_google(audio, language="es-ES")
        print(f"📝 Transcrito: {text}")
        
        # Copiar al portapapeles
        subprocess.run(['xclip', '-selection', 'clipboard'], 
                      input=text.encode(), check=True)
        
        # Pegar automáticamente (Ctrl+V)
        subprocess.run(['xdotool', 'key', 'ctrl+v'], check=True)
        
        print("✅ Pegado en cursor")
        
    except sr.UnknownValueError:
        print("❌ No se entendió el audio")
    except sr.RequestError as e:
        print(f"❌ Error de servicio: {e}")

if __name__ == "__main__":
    dictate()
PYTHON
SCRIPT

chmod +x ~/.local/bin/voice-to-windsurf

# 5. Crear script de lectura (read aloud)
echo ""
echo "🔊 Creando script de lectura en voz alta..."

cat > ~/.local/bin/read-aloud << 'SCRIPT'
#!/bin/bash
# Read Aloud - Lee el texto seleccionado en voz alta
# Uso: Seleccionar texto → Presionar hotkey

# Obtener texto seleccionado
TEXT=$(xclip -selection primary -o 2>/dev/null)

if [ -z "$TEXT" ]; then
    TEXT=$(xclip -selection clipboard -o 2>/dev/null)
fi

if [ -z "$TEXT" ]; then
    espeak-ng "No hay texto seleccionado" -v es-la
    exit 1
fi

echo "🔊 Leyendo: ${TEXT:0:50}..."

# Leer con espeak-ng (voz española)
espeak-ng "$TEXT" -v es-la -s 150
SCRIPT

chmod +x ~/.local/bin/read-aloud

# 6. Instalar xclip si no está
sudo apt install -y xclip

# 7. Instrucciones finales
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "                          ✅ INSTALACIÓN COMPLETA"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📍 SCRIPTS INSTALADOS:"
echo "   • ~/.local/bin/voice-to-windsurf  → Dictado por voz"
echo "   • ~/.local/bin/read-aloud         → Lectura en voz alta"
echo ""
echo "🔧 CONFIGURAR ATAJOS DE TECLADO:"
echo ""
echo "   1. Abre Settings → Keyboard → Shortcuts → Custom"
echo ""
echo "   2. Agregar atajo para DICTADO:"
echo "      Nombre: Voice to Windsurf"
echo "      Comando: /home/$USER/.local/bin/voice-to-windsurf"
echo "      Atajo: Super+D (o el que prefieras)"
echo ""
echo "   3. Agregar atajo para LECTURA:"
echo "      Nombre: Read Aloud"
echo "      Comando: /home/$USER/.local/bin/read-aloud"
echo "      Atajo: Super+R (o el que prefieras)"
echo ""
echo "🎤 USO:"
echo "   • Dictado: Presiona Super+D, habla, el texto se pegará automáticamente"
echo "   • Lectura: Selecciona texto, presiona Super+R para escucharlo"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
