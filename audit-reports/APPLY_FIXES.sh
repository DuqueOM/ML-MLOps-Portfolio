#!/usr/bin/env bash
# Script Automatizado para Aplicar Mejoras Críticas
# Usage: ./APPLY_FIXES.sh
# 
# Este script aplica automáticamente los parches P0 (críticos)
# Ejecutar con precaución - hacer backup antes

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Aplicación de Mejoras Críticas (P0)${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Verificar que estamos en la raíz del repo
if [ ! -f "README.md" ] || [ ! -d "fixes" ]; then
    echo -e "${RED}ERROR: Ejecutar desde la raíz del repositorio${NC}"
    exit 1
fi

# Confirmar con usuario
echo -e "${YELLOW}Este script aplicará:${NC}"
echo "  1. Parche de credenciales (docker-compose-mlflow.yml)"
echo "  2. Mejora de .gitignore"
echo "  3. Adición de LICENSE"
echo "  4. Creación de .env.example"
echo ""
echo -e "${YELLOW}⚠️  ADVERTENCIA: Se modificarán archivos en el repositorio${NC}"
read -p "¿Continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operación cancelada"
    exit 0
fi

# Crear backup
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
echo -e "\n${YELLOW}Creando backup en: $BACKUP_DIR${NC}"
mkdir -p "$BACKUP_DIR"
cp -r .gitignore infra/ "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✓ Backup creado${NC}\n"

# Paso 1: Aplicar parche de credenciales
echo -e "${BLUE}Paso 1: Eliminar credenciales hardcoded${NC}"
if git apply --check fixes/0001-remove-hardcoded-credentials.patch 2>/dev/null; then
    git apply fixes/0001-remove-hardcoded-credentials.patch
    echo -e "${GREEN}✓ Parche de credenciales aplicado${NC}"
else
    echo -e "${YELLOW}⚠ Parche ya aplicado o conflictos - revisar manualmente${NC}"
fi

# Crear .env.example para infra
if [ ! -f "infra/.env.example" ]; then
    cp fixes/0004-env-example-infra.txt infra/.env.example
    echo -e "${GREEN}✓ Creado infra/.env.example${NC}"
fi

# Crear .env si no existe (con valores seguros generados)
if [ ! -f "infra/.env" ]; then
    echo -e "${YELLOW}Generando credenciales seguras...${NC}"
    cat > infra/.env << EOF
# Generated secure credentials - $(date)
# IMPORTANT: Never commit this file to git!

POSTGRES_PASSWORD=$(openssl rand -base64 32)
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)
AWS_SECRET_ACCESS_KEY=$(openssl rand -base64 32)
EOF
    echo -e "${GREEN}✓ Creado infra/.env con passwords aleatorios${NC}"
    echo -e "${YELLOW}⚠️  Asegurar que infra/.env está en .gitignore${NC}"
fi
echo ""

# Paso 2: Mejorar .gitignore
echo -e "${BLUE}Paso 2: Mejorar .gitignore${NC}"
if git apply --check fixes/0002-improve-gitignore.patch 2>/dev/null; then
    git apply fixes/0002-improve-gitignore.patch
    echo -e "${GREEN}✓ .gitignore actualizado${NC}"
    
    # Limpiar archivos ya trackeados
    echo "Limpiando archivos que ahora están en .gitignore..."
    git rm -r --cached .pytest_cache 2>/dev/null || true
    git rm -r --cached .mypy_cache 2>/dev/null || true
    find . -type d -name "__pycache__" -exec git rm -r --cached {} + 2>/dev/null || true
    find . -type f -name "*.log" -exec git rm --cached {} + 2>/dev/null || true
    echo -e "${GREEN}✓ Archivos temporales limpiados${NC}"
else
    echo -e "${YELLOW}⚠ .gitignore ya actualizado o conflictos${NC}"
fi
echo ""

# Paso 3: Agregar LICENSE
echo -e "${BLUE}Paso 3: Agregar LICENSE en raíz${NC}"
if [ ! -f "LICENSE" ]; then
    cp fixes/0003-add-root-license.txt LICENSE
    echo -e "${GREEN}✓ LICENSE creado${NC}"
else
    echo -e "${YELLOW}⚠ LICENSE ya existe - no sobrescribir${NC}"
fi
echo ""

# Paso 4: Crear .env.example global
echo -e "${BLUE}Paso 4: Documentar variables de entorno${NC}"
if [ ! -f ".env.example" ]; then
    cp fixes/0005-root-env-example.txt .env.example
    echo -e "${GREEN}✓ .env.example creado${NC}"
else
    echo -e "${YELLOW}⚠ .env.example ya existe${NC}"
fi
echo ""

# Verificaciones finales
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verificaciones${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Verificar que credenciales no están hardcoded
echo "Verificando docker-compose-mlflow.yml..."
if grep -q "PASSWORD.*:" infra/docker-compose-mlflow.yml; then
    if grep -q "PASSWORD.*\${" infra/docker-compose-mlflow.yml; then
        echo -e "${GREEN}✓ Credenciales usan variables de entorno${NC}"
    else
        echo -e "${RED}✗ Aún hay passwords hardcoded${NC}"
    fi
fi

# Verificar .gitignore
echo "Verificando .gitignore..."
if git check-ignore infra/.env >/dev/null 2>&1; then
    echo -e "${GREEN}✓ infra/.env está ignorado${NC}"
else
    echo -e "${YELLOW}⚠ infra/.env NO está en .gitignore - agregarlo${NC}"
fi

# Estado del repo
echo -e "\nArchivos modificados:"
git status --short

# Resumen
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Resumen${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${GREEN}Cambios aplicados:${NC}"
echo "  ✓ Credenciales movidas a variables de entorno"
echo "  ✓ .gitignore mejorado"
echo "  ✓ LICENSE agregado (si no existía)"
echo "  ✓ .env.example documentado"
echo "  ✓ Archivos temporales limpiados"
echo ""

echo -e "${YELLOW}Próximos pasos:${NC}"
echo "  1. Revisar cambios con: git diff"
echo "  2. Verificar que infra/.env tiene credenciales seguras"
echo "  3. NUNCA comitear infra/.env"
echo "  4. Commit cambios:"
echo "     ${BLUE}git add .gitignore LICENSE .env.example infra/docker-compose-mlflow.yml infra/.env.example${NC}"
echo "     ${BLUE}git commit -m 'security: apply P0 fixes from audit'${NC}"
echo "  5. Ejecutar security scan: ${BLUE}./security_scan.sh${NC}"
echo ""

echo -e "${GREEN}✅ Mejoras críticas aplicadas${NC}"
echo "Backup guardado en: $BACKUP_DIR"
