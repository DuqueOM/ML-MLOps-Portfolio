# 13. CI/CD con GitHub Actions

## 🎯 Objetivo del Módulo

Implementar un pipeline CI/CD profesional que valide automáticamente tu código en cada push, como el workflow `ci-mlops.yml` del portafolio.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🔄 CI/CD = Tu Guardián Automático                                          ║
║                                                                              ║
║  ANTES (sin CI/CD):                                                          ║
║  • "Olvidé correr los tests antes de mergear"                                ║
║  • "Rompí producción con un cambio pequeño"                                  ║
║  • "No sabía que mi código no pasaba linting"                                ║
║                                                                              ║
║  DESPUÉS (con CI/CD):                                                        ║
║  • Cada push ejecuta tests automáticamente                                   ║
║  • No puedes mergear si los tests fallan                                     ║
║  • Coverage, linting, y seguridad verificados siempre                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Contenido

1. [Anatomía de un Workflow](#131-anatomía-de-un-workflow)
2. [Matrix Testing: Múltiples Versiones](#132-matrix-testing-múltiples-versiones)
3. [Coverage Enforcement](#133-coverage-enforcement)
4. [Security Scanning](#134-security-scanning)
5. [Docker Build y Push](#135-docker-build-y-push)
6. [El Workflow Completo del Portafolio](#136-el-workflow-completo)

---

## 13.1 Anatomía de un Workflow

### Estructura Básica

```yaml
# .github/workflows/ci.yml

name: CI Pipeline                    # Nombre visible en GitHub

on:                                   # ¿Cuándo ejecutar?
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:                                 # ¿Qué ejecutar?
  test:
    runs-on: ubuntu-latest           # Sistema operativo
    steps:                           # Pasos secuenciales
      - uses: actions/checkout@v4    # Paso 1: Descargar código
      - uses: actions/setup-python@v5 # Paso 2: Configurar Python
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt  # Paso 3: Instalar deps
      - run: pytest                           # Paso 4: Correr tests
```

### Analogía: La Línea de Inspección de Calidad

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  🏭 IMAGINA UNA FÁBRICA DE AUTOS:                                         ║
║                                                                           ║
║  Workflow = Línea de inspección de calidad                                ║
║                                                                           ║
║  on (trigger):                                                            ║
║  → "Cada vez que un auto nuevo llega a la línea"                          ║
║                                                                           ║
║  jobs:                                                                    ║
║  → Diferentes estaciones de inspección                                    ║
║                                                                           ║
║  steps:                                                                   ║
║  → Tareas específicas en cada estación                                    ║
║                                                                           ║
║  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐                    ║
║  │ Checkout│──►│ Install │──►│  Test   │──►│  Build  │                    ║
║  │  (get   │   │  (prep  │   │  (run   │   │ (create │                    ║
║  │  code)  │   │  tools) │   │  tests) │   │ Docker) │                    ║
║  └─────────┘   └─────────┘   └─────────┘   └─────────┘                    ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## 13.2 Matrix Testing: Múltiples Versiones

### El Problema: "Funciona en mi versión de Python"

```yaml
# ❌ ANTES: Solo pruebas con una versión
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'  # ¿Y si alguien usa 3.12?
```

### La Solución: Matrix Strategy

```yaml
# ✅ DESPUÉS: Pruebas con múltiples versiones
# Código REAL de ci-mlops.yml del portafolio

jobs:
  tests:
    name: Tests & Coverage
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false                  # No cancelar otros si uno falla
      matrix:
        python-version: ['3.11', '3.12']  # 2 versiones de Python
        project:                           # 3 proyectos
          - BankChurn-Predictor
          - CarVision-Market-Intelligence
          - TelecomAI-Customer-Intelligence
    
    # Esto crea 2 x 3 = 6 jobs paralelos:
    # - BankChurn con Python 3.11
    # - BankChurn con Python 3.12
    # - CarVision con Python 3.11
    # - CarVision con Python 3.12
    # - TelecomAI con Python 3.11
    # - TelecomAI con Python 3.12
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'  # Cache de dependencias para velocidad
      
      - name: Install dependencies
        working-directory: ${{ matrix.project }}
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        working-directory: ${{ matrix.project }}
        run: pytest --cov=src/ --cov-fail-under=80
```

### Visualización del Matrix

```
                    Python 3.11          Python 3.12
                  ┌─────────────┐      ┌─────────────┐
BankChurn         │   Job 1     │      │   Job 2     │
                  │   ✅ Pass   │      │   ✅ Pass  │
                  └─────────────┘      └─────────────┘

                  ┌─────────────┐      ┌─────────────┐
CarVision         │   Job 3     │      │   Job 4     │
                  │   ✅ Pass   │      │   ✅ Pass  │
                  └─────────────┘      └─────────────┘

                  ┌─────────────┐      ┌─────────────┐
TelecomAI         │   Job 5     │      │   Job 6     │
                  │   ✅ Pass   │      │   ✅ Pass  │
                  └─────────────┘      └─────────────┘

Total: 6 jobs ejecutándose EN PARALELO
```

---

## 13.3 Coverage Enforcement

### Thresholds por Proyecto

```yaml
# Código REAL de ci-mlops.yml

- name: Run tests with coverage
  working-directory: ${{ matrix.project }}
  run: |
    # Cada proyecto puede tener diferente threshold
    if [ "${{ matrix.project }}" = "BankChurn-Predictor" ]; then
      COV_TARGET="src"
      THRESHOLD=79
    elif [ "${{ matrix.project }}" = "CarVision-Market-Intelligence" ]; then
      COV_TARGET="src/carvision"
      THRESHOLD=80
    else
      COV_TARGET="src/telecom"
      THRESHOLD=80
    fi
    
    pytest --maxfail=1 --disable-warnings -q \
      -m "not slow" \
      --cov=$COV_TARGET \
      --cov-report=xml \
      --cov-report=term-missing \
      --cov-fail-under=$THRESHOLD  # ← FALLA si está por debajo
```

### Upload de Coverage a Codecov

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v5
  with:
    files: ${{ matrix.project }}/coverage.xml
    flags: ${{ matrix.project }}
    name: ${{ matrix.project }}-coverage-${{ matrix.python-version }}
    fail_ci_if_error: false  # No fallar si Codecov tiene problemas

- name: Upload coverage artifact
  uses: actions/upload-artifact@v5
  with:
    name: coverage-${{ matrix.project }}-py${{ matrix.python-version }}
    path: ${{ matrix.project }}/coverage.xml
    retention-days: 30
```

---

## 13.4 Security Scanning

### Múltiples Capas de Seguridad

```yaml
# Job de seguridad - Código REAL del portafolio

security-scan:
  name: Security Scan
  runs-on: ubuntu-latest
  needs: [tests]  # Solo corre si tests pasan
  
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Necesario para gitleaks (analiza historial)
    
    # 1. GITLEAKS: Detecta secretos en el código
    - name: Gitleaks (Secret Detection)
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    # 2. BANDIT: Análisis de seguridad de Python
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    
    - name: Run Bandit
      run: |
        pip install bandit
        for project in BankChurn-Predictor CarVision-Market-Intelligence TelecomAI-Customer-Intelligence; do
          echo "Scanning $project..."
          bandit -r "$project/src" -f json -o "bandit-$project.json" || true
        done
    
    # 3. PIP-AUDIT: Vulnerabilidades en dependencias
    - name: Run pip-audit
      run: |
        pip install pip-audit
        for project in BankChurn-Predictor CarVision-Market-Intelligence TelecomAI-Customer-Intelligence; do
          echo "Auditing $project..."
          pip-audit -r "$project/requirements.txt" --format json || true
        done
```

### TRIVY: Escaneo de Imágenes Docker

```yaml
docker-security:
  name: Docker Security Scan
  runs-on: ubuntu-latest
  needs: [docker-build]
  
  steps:
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'ml-portfolio-bankchurn:latest'
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: 'trivy-results.sarif'
```

---

## 13.5 Docker Build y Push

### Build Multi-Proyecto

```yaml
docker-build:
  name: Docker Build
  runs-on: ubuntu-latest
  needs: [tests, quality-gates]
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  
  strategy:
    matrix:
      include:
        - project: BankChurn-Predictor
          image: ml-portfolio-bankchurn
        - project: CarVision-Market-Intelligence
          image: ml-portfolio-carvision
        - project: TelecomAI-Customer-Intelligence
          image: ml-portfolio-telecom
  
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: ./${{ matrix.project }}
        push: true
        tags: |
          ghcr.io/${{ github.repository_owner }}/${{ matrix.image }}:latest
          ghcr.io/${{ github.repository_owner }}/${{ matrix.image }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

---

## 13.6 El Workflow Completo del Portafolio

### Diagrama del Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CI/CD Pipeline: ci-mlops.yml                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TRIGGER: push to main/develop OR pull_request to main                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         JOB 1: tests                                │    │
│  │  Matrix: Python 3.11/3.12 × 3 proyectos = 6 jobs paralelos          │    │
│  │                                                                     │    │
│  │  Steps:                                                             │    │
│  │  1. Checkout code                                                   │    │
│  │  2. Setup Python (con cache)                                        │    │
│  │  3. Install dependencies                                            │    │
│  │  4. Run linting (flake8, black, isort)                              │    │
│  │  5. Run tests with coverage                                         │    │
│  │  6. Upload coverage to Codecov                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      JOB 2: quality-gates                           │    │
│  │  needs: [tests]                                                     │    │
│  │                                                                     │    │
│  │  Steps:                                                             │    │
│  │  1. Check Black formatting                                          │    │
│  │  2. Check import sorting (isort)                                    │    │
│  │  3. Run flake8 strict                                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      JOB 3: security-scan                           │    │
│  │  needs: [tests]                                                     │    │
│  │                                                                     │    │
│  │  Steps:                                                             │    │
│  │  1. Gitleaks (secretos)                                             │    │
│  │  2. Bandit (código Python)                                          │    │
│  │  3. pip-audit (dependencias)                                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      JOB 4: docker-build                            │    │
│  │  needs: [tests, quality-gates]                                      │    │
│  │  if: push to main                                                   │    │
│  │                                                                     │    │
│  │  Steps:                                                             │    │
│  │  1. Setup Docker Buildx                                             │    │
│  │  2. Login to GHCR                                                   │    │
│  │  3. Build multi-stage images                                        │    │
│  │  4. Push to registry                                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                              │
│                              ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        JOB 5: e2e-test                              │    │
│  │  needs: [docker-build]                                              │    │
│  │                                                                     │    │
│  │  Steps:                                                             │    │
│  │  1. Start Docker Compose stack                                      │    │
│  │  2. Wait for services                                               │    │
│  │  3. Run API health checks                                           │    │
│  │  4. Run integration tests                                           │    │
│  │  5. Cleanup                                                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### El Archivo Completo

```yaml
# .github/workflows/ci-mlops.yml - Versión simplificada del portafolio

name: CI/CD MLOps Portfolio

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

permissions:
  actions: read
  contents: read
  security-events: write
  packages: write

env:
  PYTHON_VERSION: '3.12'

jobs:
  # ═══════════════════════════════════════════════════════════════════════════
  # JOB 1: Tests con Coverage
  # ═══════════════════════════════════════════════════════════════════════════
  tests:
    name: Tests & Coverage
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.11', '3.12']
        project:
          - BankChurn-Predictor
          - CarVision-Market-Intelligence
          - TelecomAI-Customer-Intelligence
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      
      - name: Install dependencies
        working-directory: ${{ matrix.project }}
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt 2>/dev/null || pip install -e .
          pip install pytest pytest-cov flake8 black isort mypy
      
      - name: Run linting
        working-directory: ${{ matrix.project }}
        run: |
          flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics || true
          black --check src/ || true
      
      - name: Run tests with coverage
        working-directory: ${{ matrix.project }}
        run: |
          # Determinar threshold por proyecto
          if [ "${{ matrix.project }}" = "BankChurn-Predictor" ]; then
            THRESHOLD=79
          else
            THRESHOLD=80
          fi
          
          pytest -m "not slow" \
            --cov=src/ \
            --cov-report=xml \
            --cov-report=term-missing \
            --cov-fail-under=$THRESHOLD
      
      - name: Upload coverage
        uses: codecov/codecov-action@v5
        with:
          files: ${{ matrix.project }}/coverage.xml
          flags: ${{ matrix.project }}
  
  # ═══════════════════════════════════════════════════════════════════════════
  # JOB 2: Quality Gates
  # ═══════════════════════════════════════════════════════════════════════════
  quality-gates:
    name: Quality Gates
    runs-on: ubuntu-latest
    needs: [tests]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install tools
        run: pip install black flake8 isort
      
      - name: Check formatting
        run: |
          for project in BankChurn-Predictor CarVision-Market-Intelligence TelecomAI-Customer-Intelligence; do
            echo "Checking $project..."
            black --check "$project/src" "$project/app" 2>/dev/null || true
            isort --check-only "$project/src" 2>/dev/null || true
          done
  
  # ═══════════════════════════════════════════════════════════════════════════
  # JOB 3: Security Scan
  # ═══════════════════════════════════════════════════════════════════════════
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: [tests]
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r */src/ -f json -o bandit-report.json || true
      
      - name: Upload security report
        uses: actions/upload-artifact@v5
        with:
          name: security-reports
          path: bandit-report.json
  
  # ═══════════════════════════════════════════════════════════════════════════
  # JOB 4: Docker Build (solo en main)
  # ═══════════════════════════════════════════════════════════════════════════
  docker-build:
    name: Docker Build
    runs-on: ubuntu-latest
    needs: [tests, quality-gates]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    strategy:
      matrix:
        include:
          - project: BankChurn-Predictor
            image: ml-portfolio-bankchurn
          - project: CarVision-Market-Intelligence
            image: ml-portfolio-carvision
          - project: TelecomAI-Customer-Intelligence
            image: ml-portfolio-telecom
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./${{ matrix.project }}
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/${{ matrix.image }}:latest
            ghcr.io/${{ github.repository_owner }}/${{ matrix.image }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## 🧨 Errores habituales y cómo depurarlos en CI/CD

En este módulo los problemas suelen venir de **triggers mal configurados**, **rutas incorrectas** o **jobs mal encadenados**.

### 1) El workflow no se dispara

**Síntomas típicos**

- Haces push o abres un PR y GitHub no muestra ningún run nuevo.

**Cómo identificarlo**

- Revisa la sección `on:` del workflow:
  - ¿Incluye las ramas correctas (`main`, `develop`, feature branches)?
  - ¿Estás haciendo push a una rama no contemplada?

**Cómo corregirlo**

- Ajusta los triggers a tu flujo real:
  ```yaml
  on:
    push:
      branches: [main, develop, "feature/*"]
    pull_request:
      branches: [main]
  ```

---

### 2) Falla solo en un proyecto o en una versión de Python

**Síntomas típicos**

- En la matrix, solo falla `CarVision` en Python 3.12, el resto pasa.

**Cómo identificarlo**

- Mira los logs filtrando por `matrix.project` y `matrix.python-version`.

**Cómo corregirlo**

- Ejecuta localmente con la misma versión de Python y el mismo directorio (`working-directory`) que en el job.
- Asegúrate de que los paths (`src/`, `app/`, `requirements.txt`) sean correctos para cada proyecto en la matrix.

---

### 3) Coverage o linting no respetan el threshold esperado

**Síntomas típicos**

- Crees haber configurado `--cov-fail-under`, pero el job pasa aunque el coverage sea bajo.

**Cómo identificarlo**

- Verifica la línea exacta del comando `pytest` en el workflow.

**Cómo corregirlo**

- Asegúrate de que el parámetro `--cov-fail-under` se pase realmente al comando que se ejecuta (no a un alias intermedio).
- Diferencia claramente entre thresholds por proyecto usando condiciones `if` en el script del job.

---

### 4) Jobs que fallan por falta de dependencias o rutas

**Síntomas típicos**

- Errores como `ModuleNotFoundError` en CI pero no en local.
- `pip install -r requirements.txt` falla porque el archivo no existe en ese directorio.

**Cómo identificarlo**

- Verifica el `working-directory` de cada `step`.
- Revisa la estructura real del repo y compara con las rutas usadas en el workflow.

**Cómo corregirlo**

- Ajusta `working-directory` para que apunte al proyecto correcto (`BankChurn-Predictor`, etc.).
- Si un proyecto no tiene `requirements.txt`, instala en modo editable con `pip install -e .` como fallback.

---

### 5) Patrón general de debugging en GitHub Actions

1. Reproduce localmente el comando exacto que falla (`pytest`, `docker build`, etc.).
2. Verifica `on:` y `matrix` para asegurarte de que el job se ejecuta en los contextos esperados.
3. Usa `working-directory` y rutas relativas coherentes con la estructura del repo.
4. Encadena bien los jobs usando `needs` para que la lógica del pipeline sea clara.

Con este enfoque, CI/CD pasa de ser una caja negra “que a veces falla” a un pipeline confiable que te protege al hacer cambios en el portafolio.

---

## ✅ Ejercicio: Crear Tu Propio Workflow

### Paso 1: Workflow Mínimo

Crea `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pytest
      - run: pytest
```

### Paso 2: Añadir Coverage

```yaml
      - run: pip install pytest pytest-cov
      - run: pytest --cov=src/ --cov-fail-under=80
```

### Paso 3: Añadir Matrix

```yaml
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
```

### Paso 4: Añadir Security

Añade un job nuevo con Bandit y Gitleaks.

---

## ✅ Checkpoint

- [ ] Tienes un workflow básico que ejecuta tests
- [ ] El workflow usa matrix testing (múltiples versiones Python)
- [ ] Coverage está enforced con threshold
- [ ] Tienes al menos un scan de seguridad
- [ ] Los artifacts se suben correctamente

---

## 📦 Cómo se Usó en el Portafolio

El portafolio tiene un workflow CI/CD real en `.github/workflows/ci-mlops.yml`:

### Workflow Real del Portafolio

```yaml
# .github/workflows/ci-mlops.yml (extracto)
name: CI/CD MLOps Portfolio

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        project: [BankChurn-Predictor, CarVision-Market-Intelligence, TelecomAI-Customer-Intelligence]
        python-version: ['3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          cd ${{ matrix.project }}
          pip install -e ".[dev]"
      
      - name: Run tests with coverage
        run: |
          cd ${{ matrix.project }}
          pytest tests/ --cov=src/ --cov-fail-under=79
```

### Features del CI/CD

| Feature | Implementación |
|---------|----------------|
| Matrix Testing | 3 proyectos × 2 versiones Python |
| Coverage Gate | `--cov-fail-under=79` |
| Security Scan | gitleaks en pre-commit |
| Artifacts | Coverage reports |

### 🔧 Ejercicio: Revisa el CI Real

```bash
# 1. Ve el workflow real
cat .github/workflows/ci-mlops.yml

# 2. Simula localmente con act (opcional)
act -j test --matrix project:BankChurn-Predictor

# 3. Ve los runs en GitHub
# https://github.com/DuqueOM/ML-MLOps-Portfolio/actions
```

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **CI vs CD**: CI = integrar código frecuentemente, CD = desplegar automáticamente.

2. **GitHub Actions vs Jenkins vs GitLab CI**: Trade-offs de cada uno.

3. **ML-specific CI**: Explica cómo CI para ML incluye validación de datos y modelos.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Secrets | Usa GitHub Secrets, nunca hardcodees |
| Caching | Cachea dependencias y datos para velocidad |
| Paralelización | Matriz de tests para múltiples versiones |
| Rollback | Siempre ten estrategia de rollback |

### Pipeline CI/CD para ML

```yaml
1. Lint + Format (ruff, black)
2. Unit Tests (pytest)
3. Integration Tests
4. Security Scan (gitleaks, bandit)
5. Build Docker Image
6. Model Validation
7. Deploy to Staging
8. Smoke Tests
9. Deploy to Production
```


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [GitHub Actions Tutorial - TechWorld Nana](https://www.youtube.com/watch?v=R8_veQiYBjI) | Video |
| 🟡 | [CI/CD for ML - Made With ML](https://madewithml.com/courses/mlops/cicd/) | Tutorial |

**Documentación oficial:**
- [GitHub Actions](https://docs.github.com/en/actions)
- [pre-commit](https://pre-commit.com/)

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **CI/CD**: Integración y despliegue continuo
- **GitHub Actions**: Automatización de workflows
- **pre-commit**: Hooks de validación antes de commit

---

## 📋 Plantillas Relacionadas

Ver [templates/](templates/index.md) para plantillas listas:
- [ci_github_actions.yml](templates/ci_github_actions.yml) — Pipeline CI/CD completo
- [ci_template.yml](templates/ci_template.yml) — Versión mínima para quick start

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 12:
- **12.1**: GitHub Actions workflow básico

---

<div align="center">

[← Volver al Índice](00_INDICE.md) | [Siguiente: Docker Avanzado →](13_DOCKER.md)

</div>
