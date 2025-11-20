# Fixes - Parches Priorizados

Este directorio contiene parches y archivos de configuración para mejorar el repositorio.

## Aplicación de Parches

### P0 - Crítico (aplicar inmediatamente)

#### 1. Eliminar credenciales hardcoded

```bash
# Aplicar parche
git apply fixes/0001-remove-hardcoded-credentials.patch

# Crear archivo de credenciales
cp fixes/0004-env-example-infra.txt infra/.env.example
cd infra
cp .env.example .env

# Generar passwords seguros
openssl rand -base64 32  # Copiar a POSTGRES_PASSWORD
openssl rand -base64 32  # Copiar a MINIO_ROOT_PASSWORD (y AWS_SECRET_ACCESS_KEY)

# Editar infra/.env con los valores generados

# Verificar que .env está en .gitignore
git check-ignore infra/.env  # Debe decir "infra/.env"
```

#### 2. Mejorar .gitignore

```bash
git apply fixes/0002-improve-gitignore.patch

# Limpiar archivos ya trackeados que deberían ser ignorados
git rm -r --cached .pytest_cache
git rm -r --cached **/__pycache__
git rm --cached **/*.log

# Commit
git add .gitignore
git commit -m "chore: improve .gitignore with Python best practices"
```

#### 3. Agregar LICENSE en raíz

```bash
cp fixes/0003-add-root-license.txt LICENSE
git add LICENSE
git commit -m "docs: add MIT LICENSE to repository root"
```

### P1 - Alta (aplicar esta semana)

#### 4. Documentar variables de entorno

```bash
# Raíz del proyecto
cp fixes/0005-root-env-example.txt .env.example
git add .env.example
git commit -m "docs: add .env.example with documented environment variables"
```

#### 5. Configurar Dependabot

```bash
mkdir -p .github
cp fixes/0006-dependabot.yml .github/dependabot.yml
git add .github/dependabot.yml
git commit -m "ci: add Dependabot for automated dependency updates"
```

### P2 - Media (aplicar próximamente)

Otros parches y mejoras están documentados en el `review-report.md` principal.

## Verificación Post-Aplicación

```bash
# Verificar que no hay secretos expuestos
grep -r "password\|secret" infra/docker-compose-mlflow.yml
# Debe mostrar solo ${VARIABLE} referencias

# Verificar .gitignore
git status --ignored
# No debe listar .pytest_cache, __pycache__, etc.

# Verificar que el repositorio está limpio
git status
```

## Notas Importantes

- **NUNCA** comitear archivos `.env` con credenciales reales
- Siempre usar `.env.example` como plantilla con valores de ejemplo
- Generar passwords seguros con `openssl rand -base64 32`
- Rotar credenciales si fueron expuestas públicamente
