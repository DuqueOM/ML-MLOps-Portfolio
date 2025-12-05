#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# validate_guide.sh - Script de validación para guia_mlops
# Verifica integridad de la guía: links, YAML, archivos requeridos
# ═══════════════════════════════════════════════════════════════════════════════

set -e

GUIDE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🔍 VALIDACIÓN DE GUÍA MLOps"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Directorio: $GUIDE_DIR"
echo ""

# Contadores
ERRORS=0
WARNINGS=0

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Verificar archivos requeridos
# ═══════════════════════════════════════════════════════════════════════════════
echo "📁 [1/5] Verificando archivos requeridos..."

REQUIRED_FILES=(
    "00_INDICE.md"
    "01_PYTHON_MODERNO.md"
    "07_SKLEARN_PIPELINES.md"
    "11_TESTING_ML.md"
    "12_CI_CD.md"
    "14_FASTAPI.md"
    "21_GLOSARIO.md"
    "EJERCICIOS.md"
    "EJERCICIOS_SOLUCIONES.md"
    "RECURSOS_POR_MODULO.md"
    "RUBRICA_EVALUACION.md"
    "DECISIONES_TECH.md"
    "MAINTENANCE_GUIDE.md"
    "mkdocs.yml"
    "requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$GUIDE_DIR/$file" ]]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file - NO ENCONTRADO"
        ((ERRORS++))
    fi
done

# Verificar 23 módulos
echo ""
echo "  Verificando 23 módulos..."
for i in $(seq -w 1 23); do
    # Buscar archivo que empiece con el número
    if ls "$GUIDE_DIR"/${i}_*.md 1> /dev/null 2>&1; then
        MODULE=$(ls "$GUIDE_DIR"/${i}_*.md 2>/dev/null | head -1 | xargs basename)
        echo -e "  ${GREEN}✓${NC} $MODULE"
    else
        echo -e "  ${RED}✗${NC} Módulo $i - NO ENCONTRADO"
        ((ERRORS++))
    fi
done

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Validar sintaxis YAML
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "📋 [2/5] Validando sintaxis YAML..."

YAML_FILES=(
    "mkdocs.yml"
)

for file in "${YAML_FILES[@]}"; do
    if [[ -f "$GUIDE_DIR/$file" ]]; then
        if python3 -c "import yaml; yaml.safe_load(open('$GUIDE_DIR/$file'))" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $file - Sintaxis válida"
        else
            echo -e "  ${RED}✗${NC} $file - Error de sintaxis YAML"
            ((ERRORS++))
        fi
    fi
done

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Verificar links internos en Markdown
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "🔗 [3/5] Verificando links internos..."

# Extraer todos los links .md y verificar que existen
BROKEN_LINKS=0
for mdfile in "$GUIDE_DIR"/*.md; do
    # Extraer links tipo [texto](archivo.md) o [texto](archivo.md#anchor)
    links=$(grep -oE '\]\([^)]+\.md[^)]*\)' "$mdfile" 2>/dev/null | sed 's/](\([^)#]*\).*/\1/' | sort -u)
    
    for link in $links; do
        # Ignorar links externos (http/https)
        if [[ "$link" == http* ]]; then
            continue
        fi
        
        # Verificar si el archivo existe
        target="$GUIDE_DIR/$link"
        if [[ ! -f "$target" ]]; then
            echo -e "  ${YELLOW}⚠${NC} $(basename $mdfile): Link roto → $link"
            ((BROKEN_LINKS++))
            ((WARNINGS++))
        fi
    done
done

if [[ $BROKEN_LINKS -eq 0 ]]; then
    echo -e "  ${GREEN}✓${NC} Todos los links internos son válidos"
else
    echo -e "  ${YELLOW}⚠${NC} $BROKEN_LINKS links potencialmente rotos"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Verificar referencias cruzadas
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "🔀 [4/5] Verificando referencias cruzadas..."

# Verificar que archivos clave están referenciados
check_reference() {
    local file=$1
    local min_refs=$2
    local count=$(grep -r "$file" "$GUIDE_DIR"/*.md 2>/dev/null | wc -l)
    
    if [[ $count -ge $min_refs ]]; then
        echo -e "  ${GREEN}✓${NC} $file referenciado $count veces"
    else
        echo -e "  ${YELLOW}⚠${NC} $file solo referenciado $count veces (esperado: $min_refs+)"
        ((WARNINGS++))
    fi
}

check_reference "EJERCICIOS.md" 5
check_reference "RECURSOS_POR_MODULO.md" 5
check_reference "21_GLOSARIO.md" 5
check_reference "RUBRICA_EVALUACION.md" 3
check_reference "DECISIONES_TECH.md" 3

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Verificar tamaño de módulos
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "📊 [5/5] Verificando tamaño de módulos..."

MIN_SIZE=5000  # 5KB mínimo esperado

for i in $(seq -w 1 23); do
    if ls "$GUIDE_DIR"/${i}_*.md 1> /dev/null 2>&1; then
        MODULE=$(ls "$GUIDE_DIR"/${i}_*.md 2>/dev/null | head -1)
        SIZE=$(stat -f%z "$MODULE" 2>/dev/null || stat -c%s "$MODULE" 2>/dev/null)
        
        if [[ $SIZE -lt $MIN_SIZE ]]; then
            echo -e "  ${YELLOW}⚠${NC} $(basename $MODULE): ${SIZE} bytes (< ${MIN_SIZE} bytes)"
            ((WARNINGS++))
        fi
    fi
done

if [[ $WARNINGS -eq 0 ]]; then
    echo -e "  ${GREEN}✓${NC} Todos los módulos tienen tamaño adecuado"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Resumen
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "📊 RESUMEN"
echo "═══════════════════════════════════════════════════════════════════════════"

if [[ $ERRORS -eq 0 && $WARNINGS -eq 0 ]]; then
    echo -e "${GREEN}✅ VALIDACIÓN EXITOSA - Sin errores ni advertencias${NC}"
    exit 0
elif [[ $ERRORS -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  VALIDACIÓN CON ADVERTENCIAS${NC}"
    echo "   Errores: $ERRORS"
    echo "   Advertencias: $WARNINGS"
    exit 0
else
    echo -e "${RED}❌ VALIDACIÓN FALLIDA${NC}"
    echo "   Errores: $ERRORS"
    echo "   Advertencias: $WARNINGS"
    exit 1
fi
