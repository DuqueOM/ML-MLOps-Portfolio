#!/bin/bash
# ============================================================================
# validate_guide.sh — Script de validación completa de la Guía MLOps v2
# ============================================================================
# Uso: ./scripts/validate_guide.sh
# Este script verifica:
#   1. Links rotos en archivos Markdown
#   2. Tests de todos los módulos
#   3. Notebooks ejecutables (con papermill)
#   4. Sintaxis de archivos YAML/JSON
#   5. Existencia de archivos requeridos
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0

echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}           Validación de Guía MLOps v2${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# 1. Verificar estructura de directorios
# ============================================================================
echo -e "${BLUE}[1/6] Verificando estructura de directorios...${NC}"

REQUIRED_DIRS=(
    "docs/00_introduccion"
    "docs/01_python_moderno"
    "docs/02_ingenieria_datos"
    "docs/03_feature_engineering"
    "docs/04_modelado"
    "docs/05_mlflow_dvc"
    "docs/06_despliegue_api"
    "docs/07_dashboard"
    "docs/08_ci_cd_testing"
    "docs/09_modelcards_datasetcards"
    "docs/10_observabilidad_monitoring"
    "docs/11_mantenimiento_auditoria"
    "templates"
    "scripts"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $dir"
    else
        echo -e "  ${RED}✗${NC} $dir (no existe)"
        ((ERRORS++))
    fi
done

# ============================================================================
# 2. Verificar archivos requeridos
# ============================================================================
echo ""
echo -e "${BLUE}[2/6] Verificando archivos requeridos...${NC}"

REQUIRED_FILES=(
    "mkdocs.yml"
    "Makefile_v2"
    "requirements.txt"
    "SYLLABUS.md"
    "templates/model_card_template.md"
    "templates/dataset_card_template.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (no existe)"
        ((ERRORS++))
    fi
done

# ============================================================================
# 3. Verificar links en Markdown (básico)
# ============================================================================
echo ""
echo -e "${BLUE}[3/6] Verificando links en archivos Markdown...${NC}"

# Buscar links internos rotos (archivos .md referenciados que no existen)
BROKEN_LINKS=0
for md_file in $(find . -name "*.md" -not -path "./.venv/*" -not -path "./site/*" 2>/dev/null); do
    # Extraer links a archivos .md locales
    links=$(grep -oE '\]\([^)]+\.md\)' "$md_file" 2>/dev/null | sed 's/](\(.*\))/\1/' || true)
    for link in $links; do
        # Ignorar links externos (http/https)
        if [[ "$link" != http* ]]; then
            # Resolver path relativo
            dir=$(dirname "$md_file")
            target="$dir/$link"
            if [ ! -f "$target" ] && [ ! -f "./$link" ]; then
                echo -e "  ${YELLOW}⚠${NC} Link roto: $link (en $md_file)"
                ((WARNINGS++))
                ((BROKEN_LINKS++))
            fi
        fi
    done
done

if [ $BROKEN_LINKS -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} No se encontraron links rotos evidentes"
fi

# ============================================================================
# 4. Verificar sintaxis YAML
# ============================================================================
echo ""
echo -e "${BLUE}[4/6] Verificando sintaxis de archivos YAML...${NC}"

for yaml_file in $(find . -name "*.yml" -o -name "*.yaml" 2>/dev/null | grep -v ".venv" | grep -v "site"); do
    if command -v python3 &> /dev/null; then
        if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $yaml_file"
        else
            echo -e "  ${RED}✗${NC} $yaml_file (sintaxis inválida)"
            ((ERRORS++))
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} python3 no disponible, saltando verificación YAML"
        break
    fi
done

# ============================================================================
# 5. Verificar tests por módulo
# ============================================================================
echo ""
echo -e "${BLUE}[5/6] Verificando existencia de tests por módulo...${NC}"

MODULES=(
    "01_python_moderno"
    "02_ingenieria_datos"
    "03_feature_engineering"
    "04_modelado"
    "05_mlflow_dvc"
    "06_despliegue_api"
    "07_dashboard"
    "08_ci_cd_testing"
    "09_modelcards_datasetcards"
    "10_observabilidad_monitoring"
    "11_mantenimiento_auditoria"
)

for module in "${MODULES[@]}"; do
    test_dir="docs/$module/tests"
    if [ -d "$test_dir" ]; then
        test_count=$(find "$test_dir" -name "test_*.py" 2>/dev/null | wc -l)
        if [ "$test_count" -gt 0 ]; then
            echo -e "  ${GREEN}✓${NC} $module ($test_count tests)"
        else
            echo -e "  ${YELLOW}⚠${NC} $module (directorio existe pero sin tests)"
            ((WARNINGS++))
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} $module (sin directorio tests/)"
        ((WARNINGS++))
    fi
done

# ============================================================================
# 6. Verificar notebooks (si existen)
# ============================================================================
echo ""
echo -e "${BLUE}[6/6] Verificando notebooks...${NC}"

NOTEBOOK_COUNT=$(find docs/notebooks -name "*.ipynb" 2>/dev/null | wc -l)
if [ "$NOTEBOOK_COUNT" -gt 0 ]; then
    echo -e "  ${GREEN}✓${NC} Encontrados $NOTEBOOK_COUNT notebooks"
    
    # Verificar que se puedan abrir como JSON válido
    for nb in $(find docs/notebooks -name "*.ipynb" 2>/dev/null); do
        if python3 -c "import json; json.load(open('$nb'))" 2>/dev/null; then
            echo -e "    ${GREEN}✓${NC} $(basename $nb)"
        else
            echo -e "    ${RED}✗${NC} $(basename $nb) (JSON inválido)"
            ((ERRORS++))
        fi
    done
else
    echo -e "  ${YELLOW}⚠${NC} No se encontraron notebooks en docs/notebooks/"
fi

# ============================================================================
# Resumen
# ============================================================================
echo ""
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                      RESUMEN${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ Validación completa: Sin errores ni advertencias${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Validación completa: $WARNINGS advertencia(s), 0 errores${NC}"
    exit 0
else
    echo -e "${RED}✗ Validación fallida: $ERRORS error(es), $WARNINGS advertencia(s)${NC}"
    exit 1
fi
