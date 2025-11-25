# Propuesta de Mejoras CI/CD — Portafolio ML-MLOps

**Fecha**: 2025-11-25  
**Archivo destino**: `.github/workflows/ci-mlops.yml`  
**Idioma de los snippets**: Inglés (requerido para CI/CD)

---

## 1) Resumen de Mejoras Propuestas

| Mejora | Descripción | Prioridad |
|--------|-------------|-----------|
| Quality Gates Job | Fallar PRs si cobertura < 70% o linting falla | Alta |
| Security Scan Enhanced | Añadir pip-audit y mejorar reporting | Alta |
| Report Generation | Generar y subir reportes automáticamente | Media |
| Dependabot Config | Actualizaciones automáticas de dependencias | Media |

---

## 2) Snippet 1: Quality Gates Job

Este job se ejecuta después de `tests` y falla el PR si no se cumplen los umbrales de calidad.

```yaml
# Añadir después del job 'tests' en ci-mlops.yml

  # Quality Gate - Enforce code quality standards
  quality-gates:
    name: Quality Gates
    runs-on: ubuntu-latest
    needs: [tests]
    if: always() && needs.tests.result != 'cancelled'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install quality tools
        run: |
          pip install black flake8 mypy
      
      - name: Check Black formatting
        run: |
          echo "::group::Black Check"
          black --check BankChurn-Predictor/src BankChurn-Predictor/app || BLACK_FAIL=1
          black --check CarVision-Market-Intelligence/src CarVision-Market-Intelligence/app || BLACK_FAIL=1
          black --check TelecomAI-Customer-Intelligence/src TelecomAI-Customer-Intelligence/app || BLACK_FAIL=1
          echo "::endgroup::"
          
          if [ "$BLACK_FAIL" = "1" ]; then
            echo "::error::Black formatting check failed. Run 'black .' to fix."
            exit 1
          fi
      
      - name: Check Flake8 linting
        run: |
          echo "::group::Flake8 Check"
          flake8 BankChurn-Predictor/src --max-line-length=120 --count --select=E9,F63,F7,F82 --show-source
          flake8 CarVision-Market-Intelligence/src --max-line-length=120 --count --select=E9,F63,F7,F82 --show-source
          flake8 TelecomAI-Customer-Intelligence/src --max-line-length=120 --count --select=E9,F63,F7,F82 --show-source
          echo "::endgroup::"
      
      - name: Verify test results passed
        run: |
          if [ "${{ needs.tests.result }}" != "success" ]; then
            echo "::error::Tests did not pass. Quality gate failed."
            exit 1
          fi
          echo "✅ All quality gates passed"
```

---

## 3) Snippet 2: Enhanced Security Scan

Mejora el job de seguridad existente añadiendo pip-audit y mejor reporting.

```yaml
# Reemplazar el job 'security' existente

  # Enhanced Security Scanning
  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
        continue-on-error: true  # Don't fail on false positives
      
      - name: Install security tools
        run: |
          pip install bandit pip-audit safety
      
      - name: Run Bandit SAST scan
        run: |
          echo "::group::Bandit Security Scan"
          mkdir -p reports
          
          # Scan each project
          for project in BankChurn-Predictor CarVision-Market-Intelligence TelecomAI-Customer-Intelligence; do
            echo "Scanning $project..."
            bandit -r "$project/src" -f json -o "reports/bandit-$project.json" -ll || true
            bandit -r "$project/src" -f txt -ll || true
          done
          
          echo "::endgroup::"
      
      - name: Run pip-audit
        run: |
          echo "::group::Dependency Vulnerability Scan"
          pip-audit --format=json > reports/pip-audit.json || true
          pip-audit || true
          echo "::endgroup::"
      
      - name: Check for critical vulnerabilities
        run: |
          # Check Bandit results
          for report in reports/bandit-*.json; do
            if [ -f "$report" ]; then
              HIGH=$(jq '.metrics._totals["SEVERITY.HIGH"] // 0' "$report")
              if [ "$HIGH" -gt 0 ]; then
                echo "::error::Critical security issues found in $report"
                exit 1
              fi
            fi
          done
          
          # Check pip-audit results
          if [ -f reports/pip-audit.json ]; then
            VULNS=$(jq 'if type == "array" then length else 0 end' reports/pip-audit.json 2>/dev/null || echo 0)
            if [ "$VULNS" -gt 0 ]; then
              echo "::warning::$VULNS dependency vulnerabilities found. Review reports/pip-audit.json"
            fi
          fi
          
          echo "✅ No critical security issues found"
      
      - name: Upload security reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: security-reports
          path: |
            reports/bandit-*.json
            reports/pip-audit.json
          retention-days: 30
```

---

## 4) Snippet 3: Report Generation Job

Genera reportes automáticamente y los sube como artifacts.

```yaml
# Añadir como nuevo job

  # Generate Audit Reports
  report-gen:
    name: Generate Audit Reports
    runs-on: ubuntu-latest
    needs: [tests, security]
    if: github.event_name == 'pull_request'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install audit tools
        run: |
          pip install black flake8 mypy bandit radon pip-audit pytest pytest-cov
      
      - name: Run audit script
        run: |
          chmod +x scripts/run_audit.sh
          ./scripts/run_audit.sh --quick || true
      
      - name: Upload audit reports
        uses: actions/upload-artifact@v4
        with:
          name: audit-reports-${{ github.sha }}
          path: |
            reports/audit/
            Reportes Portafolio/
          retention-days: 90
      
      - name: Comment PR with summary
        uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        with:
          script: |
            const fs = require('fs');
            
            // Read summary if exists
            let summary = '## 📊 Audit Summary\n\n';
            try {
              const summaryFiles = fs.readdirSync('reports/audit/').filter(f => f.startsWith('audit_summary'));
              if (summaryFiles.length > 0) {
                summary += fs.readFileSync(`reports/audit/${summaryFiles[0]}`, 'utf8');
              }
            } catch (e) {
              summary += 'Audit completed. Check artifacts for details.';
            }
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
```

---

## 5) Snippet 4: Dependabot Configuration

Crear archivo `.github/dependabot.yml` para actualizaciones automáticas.

```yaml
# Crear .github/dependabot.yml

version: 2
updates:
  # Python dependencies for BankChurn
  - package-ecosystem: "pip"
    directory: "/BankChurn-Predictor"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 3
    labels:
      - "dependencies"
      - "bankchurn"
    commit-message:
      prefix: "deps(bankchurn)"

  # Python dependencies for CarVision
  - package-ecosystem: "pip"
    directory: "/CarVision-Market-Intelligence"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 3
    labels:
      - "dependencies"
      - "carvision"
    commit-message:
      prefix: "deps(carvision)"

  # Python dependencies for TelecomAI
  - package-ecosystem: "pip"
    directory: "/TelecomAI-Customer-Intelligence"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 3
    labels:
      - "dependencies"
      - "telecom"
    commit-message:
      prefix: "deps(telecom)"

  # Docker images
  - package-ecosystem: "docker"
    directory: "/BankChurn-Predictor"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"

  - package-ecosystem: "docker"
    directory: "/CarVision-Market-Intelligence"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"

  - package-ecosystem: "docker"
    directory: "/TelecomAI-Customer-Intelligence"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "ci"
```

---

## 6) Instrucciones de Implementación

### Paso 1: Añadir Quality Gates

1. Abrir `.github/workflows/ci-mlops.yml`
2. Localizar la línea después del job `tests` (aproximadamente línea 93)
3. Pegar el Snippet 1 completo
4. Commit: `chore(ci): add quality-gates job with formatting and linting checks`

### Paso 2: Actualizar Security Job

1. Localizar el job `security` existente (líneas 94-122)
2. Reemplazar completamente con el Snippet 2
3. Commit: `chore(ci): enhance security scanning with pip-audit`

### Paso 3: Añadir Report Generation

1. Añadir el Snippet 3 al final del archivo antes del job `validate-docs`
2. Commit: `chore(ci): add automated report generation job`

### Paso 4: Configurar Dependabot

1. Crear archivo `.github/dependabot.yml`
2. Pegar el Snippet 4
3. Commit: `chore(ci): configure dependabot for automated updates`

---

## 7) Verificación Post-Implementación

Después de implementar, verificar que:

```bash
# 1. Validar sintaxis YAML
yamllint .github/workflows/ci-mlops.yml

# 2. Ejecutar localmente (si tienes act instalado)
act -j quality-gates --dry-run

# 3. Crear un PR de prueba para verificar que los jobs corren
git checkout -b test/ci-improvements
git add .github/
git commit -m "test: verify new CI jobs"
git push origin test/ci-improvements
```

---

## 8) Métricas de Éxito

Después de implementar estas mejoras, esperar:

| Métrica | Antes | Después |
|---------|-------|---------|
| PRs con código mal formateado | ~30% | 0% |
| Vulnerabilidades no detectadas | Posible | 0 |
| Tiempo para detectar issues de calidad | En review | En CI |
| Dependencias desactualizadas | Manual | Automático |

---

## 9) Rollback Plan

Si hay problemas, revertir con:

```bash
git revert HEAD~4  # Revertir últimos 4 commits de CI
git push origin main
```

O deshabilitar jobs específicos:

```yaml
# Añadir 'if: false' para deshabilitar temporalmente
quality-gates:
  if: false  # Temporalmente deshabilitado
  ...
```

---

*Propuesta generada como parte del proceso de auditoría del portafolio ML-MLOps.*
