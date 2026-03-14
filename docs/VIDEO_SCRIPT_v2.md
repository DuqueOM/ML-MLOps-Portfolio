# Portfolio Demo Video Script v2 — 3:30 min

> **Objetivo**: Impresionar en los primeros 5 segundos. Cada toma demuestra una habilidad real.
> **Formato**: 1920×1080, 30fps, subtítulos blancos abajo, música lo-fi suave, sin narración de voz.
> **Herramienta**: OBS Studio → DaVinci Resolve / kdenlive para edición.

---

## Pre-producción (ANTES de grabar)

### Pestañas del navegador pre-abiertas (en orden)
1. GitHub repo README (scroll a badges y tabla de métricas)
2. GKE Console → Workloads (6 verdes)
3. AWS EKS Console → Workloads (6 verdes)
4. Grafana → ML Portfolio Metrics dashboard
5. Prometheus → Targets (4/4 UP)
6. MLflow → Experiments table
7. GitHub Actions → CI pipeline completado (10 jobs verdes)
8. Codecov → Sunburst chart
9. GitHub → Secrets page

### Terminales pre-configuradas (fuente 18px, fondo oscuro)
- **Terminal 1**: GKE context activo
- **Terminal 2**: EKS context activo
- **Terminal 3**: Para curl commands

### Script de comandos (copiar/pegar rápido)
```bash
# Guardar como ~/video-commands.sh — NO ejecutar, solo copiar líneas individuales

# GKE
kubectl get pods -n ml-portfolio -o wide
kubectl top pods -n ml-portfolio

# EKS
kubectl get pods -n ml-portfolio -o wide

# Health checks GKE (Ingress IP)
curl -s http://136.111.152.72/bankchurn/health | python3 -m json.tool
curl -s http://136.111.152.72/nlpinsight/health | python3 -m json.tool
curl -s http://136.111.152.72/chicagotaxi/health | python3 -m json.tool

# BankChurn prediction + SHAP
curl -s -X POST "http://136.111.152.72/bankchurn/predict?explain=true" \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":619,"Geography":"France","Gender":"Female","Age":42,"Tenure":2,"Balance":0,"NumOfProducts":1,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":101348.88}' | python3 -m json.tool

# NLPInsight sentiment
curl -s -X POST "http://136.111.152.72/nlpinsight/predict" \
  -H "Content-Type: application/json" \
  -d '{"text":"The company reported massive losses and the CEO resigned immediately"}' | python3 -m json.tool

# ChicagoTaxi demand
curl -s -X POST "http://136.111.152.72/chicagotaxi/demand" \
  -H "Content-Type: application/json" \
  -d '{"pickup_community_area":8,"hour":17,"day_of_week":4,"month":3}' | python3 -m json.tool

# Side-by-side (split terminal)
# LEFT: kubectl get pods -n ml-portfolio (GKE context)
# RIGHT: kubectl get pods -n ml-portfolio (EKS context)
```

### Port-forwards activos antes de grabar
```bash
kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio &
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio &
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio &
```

### Checklist pre-grabación
- [ ] Practicar la secuencia **2 veces** completa antes de grabar
- [ ] Cerrar notificaciones del sistema, Slack, email
- [ ] Modo "Do Not Disturb" activado
- [ ] Resolución del monitor confirmada en 1920×1080
- [ ] OBS configurado: pantalla completa, 30fps, encoding H.264

---

## Guión Detallado — Toma por Toma

### 🎬 0:00–0:05 | HOOK — Impacto Inmediato

**Qué mostrar**: Pantalla dividida en 2: GKE Console (6 workloads verdes) a la izquierda, EKS Console (6 workloads verdes) a la derecha. Ambos visibles simultáneamente.

**Cómo**: Capturas de pantalla pre-armadas en un editor, o dos ventanas del navegador side-by-side.

**Subtítulo**: `"3 ML Services · 2 Clouds · Zero Downtime"`

**Voz de fondo (texto para TTS o narración)**: *"Three machine learning services. Two clouds. One infrastructure."*

> 💡 **Por qué funciona**: El reclutador ve inmediatamente que esto NO es un notebook de Kaggle. Es infraestructura real en producción.

---

### 🎬 0:05–0:20 | README — El Elevator Pitch Visual

**Qué mostrar**: GitHub repo README.md — scroll lento mostrando:
1. Badges (CI ✅, coverage 90%+, Python 3.11+, K8s, Terraform)
2. Tabla de métricas (3 proyectos con AUC, Acc, R²)
3. Tabla de equivalencia multi-cloud (GCP vs AWS)
4. Screenshots de producción (multi-cloud hero, Grafana, SHAP)

**Cómo**: Scroll suave y controlado en el navegador. NO hacer scroll rápido.

**Subtítulo**: `"ML-MLOps Portfolio — Production-Grade · Multi-Cloud · 294+ Tests · 90-98% Coverage"`

**Voz de fondo**: *"This is my ML-MLOps Portfolio. Three end-to-end machine learning projects, deployed on both Google Cloud and Amazon Web Services. Over 294 tests, 90 to 98 percent coverage, verified by Codecov. Let me show you."*

---

### 🎬 0:20–0:45 | GCP Deployment — Pods Running

**Qué mostrar** (secuencia):
1. **GKE Console** (3 seg): 6 workloads con status verde → hacer click en bankchurn-predictor para ver detalle
2. **Terminal 1** (5 seg): `kubectl get pods -n ml-portfolio -o wide` → 6 pods Running, 0 restarts
3. **Terminal 1** (3 seg): `kubectl top pods -n ml-portfolio` → CPU/RAM real de cada pod
4. **Terminal 1** (4 seg): `curl -s http://136.111.152.72/bankchurn/health | python3 -m json.tool` → `{"status":"healthy"}`

**Cómo**: Terminal con fuente 18px. Pegar comandos (NO escribir). Pausar 2 seg en cada resultado.

**Subtítulo**: `"GCP: 6 workloads on GKE — zero restarts · HPA autoscaling enabled"`

**Voz de fondo**: *"On Google Cloud, six services are running on GKE — three ML APIs, plus MLflow, Prometheus, and Grafana. Zero restarts. CPU-based autoscaling is active. Let's hit the health endpoint via the production Ingress IP — healthy."*

---

### 🎬 0:45–1:20 | ML Predictions — Live API Calls

**Qué mostrar** (secuencia rápida, 3 calls):

**Call 1 — BankChurn con SHAP (12 seg)**:
1. Pegar curl con `?explain=true` → mostrar respuesta JSON
2. Resaltar (con el cursor) `"churn_probability": 0.73` y `"feature_contributions"` con valores reales
3. Pausar en `NumOfProducts: +0.28` y `Age: +0.15` (los mayores contribuidores)

**Subtítulo**: `"BankChurn: Churn prediction with SHAP explainability — real feature contributions"`

**Voz de fondo**: *"BankChurn Predictor — a stacking classifier with four base models. This customer has 73% churn probability. SHAP explains why: having only one product is the biggest risk factor, followed by age. This runs in 103 milliseconds."*

**Call 2 — NLPInsight (8 seg)**:
1. Pegar curl con texto negativo → `"sentiment": "negative", "confidence": 0.94`
2. Mostrar las probabilities de las 3 clases

**Subtítulo**: `"NLPInsight: Financial sentiment analysis — negative with 94% confidence"`

**Voz de fondo**: *"NLPInsight Analyzer — financial sentiment classification. The model correctly identifies this as negative sentiment with 94% confidence. Five milliseconds inference."*

**Call 3 — ChicagoTaxi (8 seg)**:
1. Pegar curl → `"predicted_demand": 45.2, "pickup_area": "Near North Side"`
2. Mostrar rápido el response

**Subtítulo**: `"ChicagoTaxi: Demand forecasting from 6.3M taxi trips — PySpark ETL"`

**Voz de fondo**: *"ChicagoTaxi Pipeline — demand forecasting built from 6.3 million taxi trips processed with PySpark. R-squared 0.96."*

---

### 🎬 1:20–1:45 | Monitoring Stack — Observabilidad Completa

**Qué mostrar** (secuencia):
1. **Grafana** (8 seg): Dashboard "ML Portfolio Metrics" — mostrar paneles de Request Rate, P95 Latency, Prediction Count. Si hay datos de load test reciente, los gráficos tendrán picos visibles.
2. **Prometheus** (4 seg): Targets page → 4/4 UP (verde). Hover sobre uno para mostrar el scrape interval.
3. **MLflow** (5 seg): Experiments table → 3 experiments, mostrar la lista de runs con métricas.
4. **Grafana otra vez** (3 seg): Volver al panel de Latency Distribution P99/P95/P50

**Cómo**: Navegador maximizado. Click suave entre pestañas. NO hacer scroll innecesario.

**Subtítulo**: `"Full Observability: Grafana (26 panels) · Prometheus · MLflow (3 experiments, 14 runs)"`

**Voz de fondo**: *"The monitoring stack runs on the same cluster. Grafana has 26 auto-provisioned panels tracking request rates, latency percentiles, and error rates. Prometheus scrapes all three services every 15 seconds. MLflow tracks three experiments with 14 runs — every model version is reproducible."*

---

### 🎬 1:45–2:05 | Load Test Results — Production Proof

**Qué mostrar** (secuencia):
1. **Terminal** (5 seg): Mostrar output de Locust (tabla de resultados): 2,675 requests, 22 RPS, 0% errors
2. **Grafana** (8 seg): Dashboard con los picos del load test visible — Request Rate subiendo, Latency manteniéndose estable
3. **Terminal** (5 seg): Mostrar rápidamente la tabla de SLA compliance: Error rate < 1% ✅, P95 < 500ms ✅

**Cómo**: Si no tienes el output de Locust guardado, muestra el screenshot `38c-load-test-results.png`.

**Subtítulo**: `"Load Test: 10 users · 2,675 requests · 0% errors · P95 210ms — SLA met ✅"`

**Voz de fondo**: *"Under load — ten concurrent users for two minutes. Over 2,600 requests, zero percent error rate, P95 latency at 210 milliseconds. All SLA thresholds met. The same test runs on AWS with comparable results."*

---

### 🎬 2:05–2:25 | CI/CD Pipeline — Security & Quality

**Qué mostrar** (secuencia):
1. **GitHub Actions** (6 seg): CI pipeline completado — 10 jobs verdes en la matrix. Hacer click para expandir y mostrar los job names (test, lint, security, docker, integration).
2. **Codecov** (5 seg): Sunburst chart mostrando 90-98% coverage. Hover sobre un proyecto para ver el porcentaje.
3. **GitHub Secrets** (4 seg): Página de secrets mostrando GCP_SA_KEY, AWS credentials, CODECOV_TOKEN — demostrar que es multi-cloud real.

**Cómo**: Pestañas pre-abiertas. Click entre ellas sin delay.

**Subtítulo**: `"CI/CD: 10 jobs · Security scanning · 294+ tests · 90-98% coverage · Codecov verified"`

**Voz de fondo**: *"Every push triggers a 10-job CI pipeline: matrix testing across Python 3.11 and 3.12, security scanning with Trivy, Bandit, and Gitleaks — blocking on high severity. 294 tests, coverage verified by Codecov. Two separate deploy workflows push to GCP and AWS automatically."*

---

### 🎬 2:25–2:50 | Multi-Cloud AWS — Parity Proof

**Qué mostrar** (secuencia):
1. **AWS EKS Console** (5 seg): Cluster activo → 6 workloads verdes. Highlight que es IGUAL que GKE.
2. **Terminal 2** (5 seg): `kubectl get pods -n ml-portfolio` (EKS context) → 6 pods Running.
3. **Split-screen terminal** (8 seg): **IZQUIERDA** = GKE pods, **DERECHA** = EKS pods. Mismos 6 servicios, diferente cloud.
4. **Terminal 2** (5 seg): `curl` health check vía ELB DNS → `{"status":"healthy"}` — misma respuesta que GCP.

**Cómo**:
- Para el split-screen: usar `tmux` con dos panes verticales, o dos terminales lado a lado.
- Resaltar con el cursor que los mismos 6 pods aparecen en ambos clouds.

**Subtítulo**: `"Multi-Cloud Parity: Same 6 services on GCP (GKE) + AWS (EKS) — Terraform + Kustomize"`

**Voz de fondo**: *"Now the same stack on Amazon Web Services. Six pods on EKS — identical services, different cloud. Side by side: GKE on the left, EKS on the right. Same pods, same health responses, same monitoring. Provisioned with Terraform, configured with Kustomize overlays — base manifests shared, cloud-specific patches applied per environment."*

---

### 🎬 2:50–3:10 | Infrastructure as Code & Security — DevSecOps

**Qué mostrar** (secuencia):
1. **Terminal** (5 seg): `tree infra/terraform/ -L 2` → mostrar estructura GCP + AWS side-by-side (o `ls -la infra/terraform/gcp/ infra/terraform/aws/`)
2. **Terminal** (5 seg): Mostrar output de `test_terraform.sh all` (tfsec + checkov results) — o usar el screenshot `55-tfsec-results.png`
3. **IDE/Editor** (5 seg): Abrir rápidamente `k8s/overlays/` → mostrar `gcp/` y `aws/` carpetas con los overlays. Mostrar un diff visual: base deployment vs cloud-specific patch.
4. **Terminal** (3 seg): `kubectl get networkpolicies -n ml-portfolio` → mostrar las políticas de red aplicadas.

**Cómo**: Terminal + editor de código. Transición rápida (fade 0.3s entre cada toma).

**Subtítulo**: `"DevSecOps: Terraform IaC · tfsec + checkov · Network Policies · Non-root containers · 13 ADRs"`

**Voz de fondo**: *"Infrastructure is code. Terraform manages both clouds — GCP and AWS — with separate state files and modules. Security scanning with tfsec and checkov runs on every commit. Kubernetes manifests use Kustomize: one base, two overlays. Network policies restrict pod communication. All containers run as non-root. Thirteen Architectural Decision Records document every trade-off."*

---

### 🎬 3:10–3:30 | Cierre — Call to Action

**Qué mostrar** (secuencia):
1. **GitHub README** (5 seg): Scroll rápido de vuelta al top — badges, tabla de métricas, screenshots. El reclutador ya vio todo en vivo, ahora lo reconoce.
2. **GitHub Pages** (5 seg): Abrir `https://duqueom.github.io/ML-MLOps-Portfolio/` → mostrar la landing page con navegación profesional, screenshots, y tabla de proyectos.
3. **Pantalla final** (10 seg): Fondo oscuro con texto centrado en blanco:

```
┌──────────────────────────────────────────────────┐
│                                                  │
│   ML-MLOps Portfolio                             │
│   Production-Grade · Multi-Cloud · 294+ Tests    │
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

**Cómo**: La pantalla final puede ser una imagen estática creada en Canva/Figma, o un slide negro con texto blanco en DaVinci Resolve.

**Subtítulo**: `"Production-grade MLOps — multi-cloud deployed · github.com/DuqueOM"`

**Voz de fondo**: *"Production-grade MLOps. Three services, two clouds, full observability, enterprise CI/CD. Everything is open-source, documented, and live. I'm Duque Ortega Mutis — ML Engineer. Let's connect."*

---

## Post-producción

### Edición
| Paso | Herramienta | Detalle |
|------|-------------|---------|
| 1. Cortar pausas | DaVinci Resolve / kdenlive | Eliminar cualquier pausa >2 seg. El ritmo debe ser constante. |
| 2. Agregar subtítulos | Misma herramienta | Fuente: **Inter** o **Roboto**, tamaño 36px, blanco con sombra negra sutil, alineados abajo-centro |
| 3. Agregar voz (opcional) | ElevenLabs / Google TTS / narración propia | Si usas TTS: voz masculina, acento neutro inglés, velocidad 1.1x. Si narras tú: practica 3 veces, habla lento y claro. |
| 4. Música de fondo | YouTube Audio Library → buscar "coding lo-fi" o "ambient tech" | Volumen al **15-20%** — debe ser apenas perceptible, no competir con la voz/subtítulos |
| 5. Transiciones | Fade 0.3-0.5s entre secciones | Sin efectos llamativos. Profesional = simple. |
| 6. Color correction | Sutil, si es necesario | Asegurar que las terminales se lean bien (contraste alto) |

### Exportación
- **Formato**: MP4, codec H.264, 1080p, 30fps
- **Bitrate**: 8-12 Mbps (calidad alta sin exceso de tamaño)
- **Tamaño objetivo**: < 80 MB
- **Thumbnail**: Captura del README con texto overlay: "ML-MLOps Portfolio Demo — 3 Services · 2 Clouds"

### Publicación
- Subir a YouTube como **no listado** (Unlisted)
- **Título**: `ML-MLOps Portfolio Demo — 3 ML Services on GCP + AWS | Production Infrastructure`
- **Descripción**:
  ```
  Production multi-cloud MLOps portfolio: 3 ML services deployed on GCP (GKE) and AWS (EKS).

  🔗 Repository: https://github.com/DuqueOM/ML-MLOps-Portfolio
  📄 Documentation: https://duqueom.github.io/ML-MLOps-Portfolio/
  💼 LinkedIn: https://linkedin.com/in/DuqueOM

  Stack: Python 3.11 · FastAPI · Docker · Kubernetes (GKE + EKS) · Terraform · GitHub Actions · MLflow · Prometheus · Grafana · SHAP · 294+ tests · 90-98% coverage

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
