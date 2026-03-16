# Portfolio Demo Video Script v2 — 3:30 min

> **Objetivo**: Impresionar en los primeros 5 segundos. Cada toma demuestra una habilidad real de MLOps.
> **Audiencia**: Reclutadores técnicos, Engineering Managers, MLOps Leads.
> **Filosofía**: *Terminal para infraestructura, UI para el negocio*. El balance perfecto entre "sé usar Linux" y "entiendo el producto".

---

## Pre-producción (ANTES de grabar)

### Pestañas del navegador pre-abiertas (en orden)
1. GitHub repo README (scroll a badges y arquitectura)
2. FastAPI Swagger UI (BankChurn `http://136.111.152.72/bankchurn/docs`)
3. FastAPI Swagger UI (NLPInsight `http://136.111.152.72/nlpinsight/docs`)
4. Grafana → ML Portfolio Metrics dashboard
5. Prometheus → Targets (4/4 UP)
6. MLflow → Experiments table (http://136.111.152.72/mlflow)
7. GitHub Actions → CI pipeline completado
8. Codecov → Sunburst chart

### Terminales pre-configuradas (fuente 18px, fondo oscuro)
- **Pantalla dividida (Split Screen)**:
  - **Terminal Izquierda**: GKE context (`kubectl config use-context ml-portfolio-gke-production`)
  - **Terminal Derecha**: EKS context (`kubectl config use-context ml-portfolio-eks`)

### Script de comandos (copiar/pegar rápido)
```bash
# LADO IZQUIERDO (GKE)
kubectl get pods -n ml-portfolio -o wide
kubectl top pods -n ml-portfolio

# LADO DERECHO (EKS)
kubectl get pods -n ml-portfolio -o wide
kubectl get ingress -n ml-portfolio

# PRUEBA DE CARGA (Locust - terminal separada abajo)
locust -f tests/load/locustfile.py --headless -u 50 -r 10 --run-time 1m --host http://136.111.152.72
```

---

## Guión Detallado — Toma por Toma

### 🎬 0:00–0:10 | HOOK — Infraestructura Multi-Cloud (Impacto Inmediato)
*¿Qué impresiona más? Ver infraestructura real corriendo en ambos clouds simultáneamente.*

**Qué mostrar**: Terminal en pantalla completa dividida en dos paneles verticales (tmux o terminator).
- **Izquierda**: GKE. Ejecutar `kubectl get pods -n ml-portfolio`
- **Derecha**: EKS. Ejecutar `kubectl get pods -n ml-portfolio`
- Ambos lados muestran exactamente los mismos 6 servicios en estado `Running`.

**Subtítulo**: `"3 ML Services · Deployed simultaneously on GCP (GKE) & AWS (EKS)"`

**Voz de fondo**: *"Three machine learning services. Two clouds. One identical infrastructure. Provisioned with Terraform and Kustomize overlays."*

---

### 🎬 0:10–0:40 | ML Predictions — El Valor de Negocio (Swagger UI > curl)
*¿Terminal o UI? Para predicciones, la UI (Swagger) es mucho más visual y demuestra que entregas un producto consumible por Frontend/Backend devs, no solo un script.*

**Qué mostrar** (secuencia rápida):
1. **BankChurn Swagger UI**: Expandir el endpoint `/predict`, hacer click en "Try it out", poner `explain: true`, click "Execute".
   - Mostrar el Response JSON resaltando `"churn_probability"` y el array de SHAP values (`"feature_contributions"`).
2. **NLPInsight Swagger UI**: Ejecutar inferencia rápida. Resaltar `"sentiment": "negative", "confidence": 0.94`.

**Subtítulo**: `"Production APIs: FastAPI endpoints with live SHAP explainability"`

**Voz de fondo**: *"The APIs are built with FastAPI. BankChurn returns predictions with live SHAP explainability in under 150 milliseconds. NLPInsight provides financial sentiment classification via a fine-tuned transformer."*

---

### 🎬 0:40–1:10 | Experiment Tracking — El Estándar Enterprise (UI)
*MLflow en terminal no se ve bien. La UI demuestra trazabilidad real.*

**Qué mostrar**:
1. Pestaña de **MLflow** (`http://136.111.152.72/mlflow`).
2. Mostrar los 3 experimentos a la izquierda.
3. Hacer click en "BankChurn", mostrar las 5 runs (LR, RF, GBM, Stacking).
4. Seleccionar 2 runs y hacer click en "Compare" → mostrar el parallel coordinates plot o la tabla de métricas (test_auc).

**Subtítulo**: `"MLflow Tracking Server: SQLite + PVC persistence · Auto-logged via Ingress"`

**Voz de fondo**: *"Every model version is tracked in a centralized MLflow server running in the cluster. Persistent volumes ensure data safety, while the Nginx Ingress handles sub-path routing automatically."*

---

### 🎬 1:10–1:45 | Observabilidad & Load Testing (Split Screen)
*El momento más impresionante: Mostrar el tráfico generándose en la terminal y Grafana reaccionando en vivo.*

**Qué mostrar**: Pantalla dividida Horizontal.
- **Arriba (Navegador)**: Dashboard de Grafana "ML Portfolio Metrics" (paneles de RPS y Latencia).
- **Abajo (Terminal)**: Ejecutando el comando headless de Locust (`locust -f ...`).

1. Lanzar el comando Locust abajo.
2. Esperar 5 segundos → ver cómo los gráficos de Grafana arriba empiezan a dibujar los picos de tráfico (RPS subiendo, Latencia estable).
3. Cambiar rápido a la pestaña de **Prometheus** → Targets (todos verdes).

**Subtítulo**: `"Full Observability: Locust load test driving traffic to Grafana & Prometheus"`

**Voz de fondo**: *"We generate headless load with Locust. Prometheus scrapes metrics every 15 seconds, and Grafana visualizes the traffic in real-time. Even at 50 concurrent users, latency stays well below the 500 millisecond SLA."*

---

### 🎬 1:45–2:15 | CI/CD Pipeline & Code Quality (Navegador)

**Qué mostrar** (secuencia rápida):
1. **GitHub Actions**: El workflow `ci-mlops.yml` completado. Abrir la matriz de Python 3.11/3.12 y mostrar los jobs (Test, Lint, Trivy Security Scan).
2. **Codecov**: El Sunburst chart mostrando >90% de cobertura.
3. **GitHub Repo**: El README con la arquitectura (Mermaid diagram).

**Subtítulo**: `"Enterprise CI/CD: 10 jobs · Trivy Security Scans · 90%+ Coverage · Kustomize"`

**Voz de fondo**: *"Every push triggers an enterprise CI/CD pipeline. Matrix testing across Python versions, security scanning with Trivy, and Codecov verification ensuring over 90 percent coverage across all three projects."*

---

### 🎬 2:15–2:30 | DevSecOps & IaC (Terminal + IDE)

**Qué mostrar**:
1. **IDE (VSCode/Windsurf)**: Abrir `k8s/overlays/` y mostrar la estructura lado a lado de `gcp/ingress-gcp.yaml` vs `aws/ingress-aws.yaml`. (Muestra el patrón "Base + Overlays").
2. **Terminal**: Ejecutar `kubectl get networkpolicies -n ml-portfolio` (Muestra seguridad zero-trust en K8s).

**Subtítulo**: `"DevSecOps: Kustomize Overlays · Network Policies · Zero-Trust"`

**Voz de fondo**: *"Infrastructure follows a GitOps approach. Kustomize manages base manifests and cloud-specific overlays. Network policies enforce zero-trust security between pods."*

---

### 🎬 2:30–2:50 | Cierre — Call to Action

**Qué mostrar**:
1. **GitHub Pages Docs**: Navegar rápido por la documentación estática generada con MkDocs.
2. **Pantalla final (Estática)**:

```
┌──────────────────────────────────────────────────┐
│                                                  │
│   ML-MLOps Portfolio                             │
│   Production-Grade · Multi-Cloud · 395+ Tests    │
│                                                  │
│   github.com/DuqueOM/ML-MLOps-Portfolio          │
│   duqueom.github.io/ML-MLOps-Portfolio           │
│                                                  │
│   Duque Ortega Mutis                             │
│   ML Engineer | MLOps & Cloud Infrastructure     │
│   linkedin.com/in/DuqueOM                        │
│   DuqueOrtegaMutis@gmail.com                     │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Subtítulo**: `"github.com/DuqueOM"`

**Voz de fondo**: *"Production-grade MLOps. Three services, two clouds, full observability, enterprise CI/CD. Everything is open-source, documented, and live. I'm Duque Ortega Mutis. Let's connect."*
- **Título**: `ML-MLOps Portfolio Demo — 3 ML Services on GCP + AWS | Production Infrastructure`
- **Descripción**:
  ```
  Production multi-cloud MLOps portfolio: 3 ML services deployed on GCP (GKE) and AWS (EKS).

  🔗 Repository: https://github.com/DuqueOM/ML-MLOps-Portfolio
  📄 Documentation: https://duqueom.github.io/ML-MLOps-Portfolio/
  💼 LinkedIn: https://linkedin.com/in/DuqueOM

  Stack: Python 3.11 · FastAPI · Docker · Kubernetes (GKE + EKS) · Terraform · GitHub Actions · MLflow · Prometheus · Grafana · SHAP · 395+ tests · 90-98% coverage

  Timestamps:
  0:00 - Multi-Cloud Overview
  0:05 - Repository & Badges
  0:20 - GCP Deployment (GKE)
  0:45 - Live ML Predictions (SHAP, Sentiment, Demand)
  1:20 - Monitoring Stack (Grafana, Prometheus, MLflow)
  1:45 - Load Testing & SLA
  2:05 - CI/CD Pipeline & Security
  2:25 - AWS Deployment (EKS) — Multi-Cloud Parity
  2:50 - Infrastructure as Code & DevSecOps
  3:10 - Summary & Contact
  ```
- **Tags**: `MLOps, Machine Learning, Kubernetes, GKE, EKS, Terraform, Portfolio, CI/CD, Prometheus, Grafana, FastAPI, SHAP, Multi-Cloud`

---

## Resumen de tiempos

| Sección | Duración | Contenido principal |
|---------|----------|-------------------|
| Hook | 0:00–0:05 (5s) | Split GKE/EKS — impacto inmediato |
| README | 0:05–0:20 (15s) | Badges, métricas, screenshots |
| GCP | 0:20–0:45 (25s) | Console, pods, health check |
| Predictions | 0:45–1:20 (35s) | 3 API calls live (SHAP, sentiment, demand) |
| Monitoring | 1:20–1:45 (25s) | Grafana, Prometheus, MLflow |
| Load Test | 1:45–2:05 (20s) | Locust results, SLA proof |
| CI/CD | 2:05–2:25 (20s) | Pipeline, Codecov, secrets |
| Multi-Cloud | 2:25–2:50 (25s) | EKS pods, split-screen parity |
| IaC/Security | 2:50–3:10 (20s) | Terraform, tfsec, overlays, ADRs |
| Cierre | 3:10–3:30 (20s) | GitHub Pages, contact info |
| **Total** | **3:30** | |

---

## Tips finales

1. **Regla de los 3 segundos**: Ninguna toma debe quedarse estática más de 3-4 segundos. Siempre debe haber movimiento (scroll, click, nuevo comando, cambio de pestaña).
2. **El cursor es tu puntero**: Úsalo para guiar la atención del viewer. Mueve el cursor hacia lo que quieres que miren ANTES de que aparezca el subtítulo.
3. **Practica el timing**: Graba un "ensayo" completo sin editar. Revisa que las transiciones fluyan. Ajusta el orden si algo se siente lento.
4. **Audio sync**: Si usas voz (TTS o narración), sincroniza la voz con la acción en pantalla. La voz debe describir lo que se VE en ese momento, no lo que viene después.
5. **No expliques de más**: El video es un teaser. El reclutador que quiera profundidad irá al repo y a la documentación. El video solo debe generar la reacción: *"This person knows what they're doing."*
