# ═══════════════════════════════════════════════════════════════════════════════
# READ ALOUD - Lee texto del portapapeles en voz alta (Windows 10)
# Uso: Copiar texto, ejecutar script y escuchar
# ═══════════════════════════════════════════════════════════════════════════════

Add-Type -AssemblyName System.Speech

# Obtener texto del portapapeles
$text = Get-Clipboard

if ([string]::IsNullOrEmpty($text)) {
    Write-Host "No hay texto en el portapapeles." -ForegroundColor Red
    exit
}

Write-Host "Leyendo en voz alta..." -ForegroundColor Cyan
Write-Host "-------------------------------------------------------------------" -ForegroundColor Gray
Write-Host $text -ForegroundColor White
Write-Host "-------------------------------------------------------------------" -ForegroundColor Gray

# Crear sintetizador de voz
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

# Configurar voz española si está disponible
$voices = $synth.GetInstalledVoices()
$spanishVoice = $voices | Where-Object { $_.VoiceInfo.Culture.Name -like "es-*" } | Select-Object -First 1

if ($spanishVoice) {
    $synth.SelectVoice($spanishVoice.VoiceInfo.Name)
    Write-Host "Voz seleccionada: $($spanishVoice.VoiceInfo.Name)" -ForegroundColor Green
} else {
    Write-Host "Usando voz por defecto (instalar voz española recomendado)." -ForegroundColor Yellow
}

# Configurar velocidad (0 = normal, -2 = lento, 2 = rápido)
$synth.Rate = 0

# Hablar
$synth.Speak($text)

Write-Host "Lectura completada." -ForegroundColor Green
