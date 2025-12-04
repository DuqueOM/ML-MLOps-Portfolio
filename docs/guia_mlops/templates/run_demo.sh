#!/bin/bash
# ════════════════════════════════════════════════════════════════════════════════
# RUN_DEMO.SH - Script para demostración del proyecto MLOps
# Ejecuta el pipeline completo y muestra resultados
# ════════════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────────────────────────
# Funciones de utilidad
# ─────────────────────────────────────────────────────────────────────────────────

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 no está instalado"
        exit 1
    fi
}

# ─────────────────────────────────────────────────────────────────────────────────
# Verificar prerrequisitos
# ─────────────────────────────────────────────────────────────────────────────────

print_header "🔍 VERIFICANDO PRERREQUISITOS"

print_step "Verificando Python..."
check_command python3
python3 --version

print_step "Verificando pip..."
check_command pip

print_step "Verificando Git..."
check_command git
git --version

# Opcional: Docker
if command -v docker &> /dev/null; then
    print_step "Docker disponible"
    docker --version
else
    print_warning "Docker no disponible - saltando pasos de containerización"
fi

print_success "Prerrequisitos verificados"

# ─────────────────────────────────────────────────────────────────────────────────
# Setup del entorno
# ─────────────────────────────────────────────────────────────────────────────────

print_header "📦 CONFIGURANDO ENTORNO"

if [ ! -d "venv" ]; then
    print_step "Creando entorno virtual..."
    python3 -m venv venv
fi

print_step "Activando entorno virtual..."
source venv/bin/activate

print_step "Instalando dependencias..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

print_success "Entorno configurado"

# ─────────────────────────────────────────────────────────────────────────────────
# Pipeline ML
# ─────────────────────────────────────────────────────────────────────────────────

print_header "🔄 EJECUTANDO PIPELINE ML"

# Datos
print_step "Preparando datos..."
if [ -f "src/data/prepare.py" ]; then
    python src/data/prepare.py
    print_success "Datos preparados"
else
    print_warning "Script de preparación no encontrado"
fi

# Entrenamiento
print_step "Entrenando modelo..."
if [ -f "src/models/train.py" ]; then
    python src/models/train.py
    print_success "Modelo entrenado"
else
    print_warning "Script de entrenamiento no encontrado"
fi

# Evaluación
print_step "Evaluando modelo..."
if [ -f "src/models/evaluate.py" ]; then
    python src/models/evaluate.py
    print_success "Modelo evaluado"
fi

# ─────────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────────

print_header "🧪 EJECUTANDO TESTS"

if [ -d "tests" ]; then
    print_step "Ejecutando pytest..."
    pytest tests/ -v --tb=short || print_warning "Algunos tests fallaron"
else
    print_warning "Directorio tests/ no encontrado"
fi

# ─────────────────────────────────────────────────────────────────────────────────
# Métricas
# ─────────────────────────────────────────────────────────────────────────────────

print_header "📊 MÉTRICAS DEL MODELO"

if [ -f "metrics/scores.json" ]; then
    print_step "Métricas guardadas:"
    cat metrics/scores.json | python -m json.tool
elif command -v dvc &> /dev/null; then
    print_step "Métricas DVC:"
    dvc metrics show 2>/dev/null || print_warning "No hay métricas DVC"
fi

# ─────────────────────────────────────────────────────────────────────────────────
# API Demo
# ─────────────────────────────────────────────────────────────────────────────────

print_header "🚀 DEMO DE API"

if [ -f "src/api/main.py" ]; then
    print_step "Iniciando servidor API..."
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    
    # Esperar a que el servidor inicie
    sleep 3
    
    print_step "Verificando health endpoint..."
    curl -s http://localhost:8000/health | python -m json.tool
    
    print_step "Probando predicción..."
    curl -s -X POST "http://localhost:8000/predict" \
        -H "Content-Type: application/json" \
        -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}' \
        | python -m json.tool
    
    print_step "Deteniendo servidor..."
    kill $API_PID 2>/dev/null
    
    print_success "Demo de API completado"
else
    print_warning "API no encontrada en src/api/main.py"
fi

# ─────────────────────────────────────────────────────────────────────────────────
# Docker Demo (opcional)
# ─────────────────────────────────────────────────────────────────────────────────

if command -v docker &> /dev/null && [ -f "Dockerfile" ]; then
    print_header "🐳 DEMO DOCKER"
    
    print_step "Construyendo imagen..."
    docker build -t ml-demo:latest . -q
    
    print_step "Verificando tamaño de imagen..."
    docker images ml-demo:latest --format "Tamaño: {{.Size}}"
    
    print_step "Ejecutando contenedor..."
    docker run -d -p 8001:8000 --name ml-demo-container ml-demo:latest
    
    sleep 3
    
    print_step "Verificando contenedor..."
    curl -s http://localhost:8001/health | python -m json.tool
    
    print_step "Limpiando..."
    docker stop ml-demo-container
    docker rm ml-demo-container
    
    print_success "Demo Docker completado"
fi

# ─────────────────────────────────────────────────────────────────────────────────
# Resumen
# ─────────────────────────────────────────────────────────────────────────────────

print_header "📋 RESUMEN DE LA DEMO"

echo "
┌─────────────────────────────────────────────────────────────────────┐
│                        DEMO COMPLETADO                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ✅ Entorno configurado                                            │
│   ✅ Pipeline ML ejecutado                                          │
│   ✅ Tests ejecutados                                               │
│   ✅ API verificada                                                 │
│                                                                     │
│   Próximos pasos:                                                   │
│   • Revisar métricas en metrics/                                    │
│   • Ver experimentos: mlflow ui                                     │
│   • Documentación en README.md                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
"

print_success "¡Demo completado exitosamente!"

# Cleanup
deactivate 2>/dev/null || true
