# Portfolio Demo Video Script v2 — 3:30 min

> **Objetivo**: Impresionar en los primeros 5 segundos. Cada toma demuestra una habilidad real de MLOps.
> **Audiencia**: Reclutadores técnicos, Engineering Managers, MLOps Leads.
> **Filosofía**: *Terminal para infraestructura, UI para el negocio*. El balance perfecto entre "sé usar Linux" y "entiendo el producto".

---

## 🛠️ Pre-producción: Preparación del Entorno (Guía Paso a Paso)

Para que el video fluya sin pausas, **todo debe estar abierto y listo antes de presionar grabar**. Sigue este checklist al pie de la letra.

### 1. Variables de entorno globales (Copiar a la terminal)
*Define ambas nubes antes de empezar:*
```bash
# GCP — nginx-ingress LoadBalancer
export GKE_URL="http://136.111.152.72"

# AWS — NodePort directo (NLB pendiente de cuota de servicio)
# Una vez aprobada la cuota, reemplaza con: export EKS_URL="http://<nlb-hostname>"
export EKS_URL="http://100.48.81.16:31963"
```

### 2. Pestañas del navegador pre-abiertas (Abre todas en orden, en una ventana nueva)
Abre una ventana limpia de tu navegador (sin extensiones que distraigan) y prepara estas pestañas:

**GCP (GKE — nginx-ingress IP pública: `136.111.152.72`)**
1. **GitHub Repo**: `https://github.com/DuqueOM/ML-MLOps-Portfolio`
2. **BankChurn UI (GCP)**: `http://136.111.152.72/bankchurn/docs`
3. **NLPInsight UI (GCP)**: `http://136.111.152.72/nlpinsight/docs`
4. **ChicagoTaxi UI (GCP)**: `http://136.111.152.72/chicagotaxi/docs`
5. **Grafana (GCP)**: `http://136.111.152.72/grafana/dashboards`
6. **MLflow (GCP)**: `http://136.111.152.72/mlflow`
7. **Prometheus (GCP — port-forward)**: Ejecuta en terminal oculta: `kubectl config use-context ml-portfolio-gke-production && kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio &` → abre `http://localhost:9090/targets`

**AWS (EKS — NodePort IP pública: `100.48.81.16:31963`)**
8. **BankChurn UI (AWS)**: `http://100.48.81.16:31963/bankchurn/docs`
9. **NLPInsight UI (AWS)**: `http://100.48.81.16:31963/nlpinsight/docs`
10. **ChicagoTaxi UI (AWS)**: `http://100.48.81.16:31963/chicagotaxi/docs`
11. **Grafana (AWS)**: `http://100.48.81.16:31963/grafana/dashboards`
12. **MLflow (AWS)**: `http://100.48.81.16:31963/mlflow`

> 📝 **Nota AWS**: Actualmente se accede vía NodePort mientras se aprueba la cuota de NLB en AWS Service Quotas. Una vez aprobada (`Network Load Balancers per Region`), el NLB se provisiona automáticamente y reemplaza esta IP por un hostname `*.elb.amazonaws.com`.

**CI/CD y calidad**
13. **GitHub Actions**: `https://github.com/DuqueOM/ML-MLOps-Portfolio/actions`
14. **Codecov**: `https://app.codecov.io/gh/DuqueOM/ML-MLOps-Portfolio`

### 3. Preparación de payloads (Tenlos listos en un block de notas)

**Para BankChurn Swagger UI (/predict):**
```json
{
  "CreditScore": 619,
  "Geography": "France",
  "Gender": "Female",
  "Age": 42,
  "Tenure": 2,
  "Balance": 0,
  "NumOfProducts": 1,
  "HasCrCard": 1,
  "IsActiveMember": 1,
  "EstimatedSalary": 101348.88
}
```
> ⚠️ **IMPORTANTE PARA SHAP**: El JSON de arriba es solo el cuerpo de los datos. Para activar SHAP, en la misma interfaz de Swagger debes **cambiar el campo `explain` de `false` a `true`** (es un parámetro de query, no va dentro del JSON).

**Para NLPInsight Swagger UI (/predict):**
```json
{
  "text": "The company reported massive unexpected losses, causing the stock to plummet and the CEO to resign immediately."
}
```

**Para ChicagoTaxi Swagger UI (/demand):**
```json
{
  "pickup_community_area": 8,
  "hour": 17,
  "day_of_week": 4,
  "month": 3
}
```

### 4. Configuración de Terminales (Split Screen con tmux)
El impacto visual del video depende de mostrar que tienes control absoluto sobre ambas nubes **al mismo tiempo**.

**Paso 1: Preparar la pantalla dividida (Antes de grabar)**
1. Abre tu terminal maximizada.
2. Ejecuta `tmux`.
3. Presiona `Ctrl+b` y luego `%` (divide la pantalla verticalmente en dos paneles).
4. **Panel Izquierdo (GCP)**: Conéctate al clúster de GKE y limpia la pantalla:
   ```bash
   kubectl config use-context gke-production
   clear
   ```
5. **Panel Derecho (AWS)**: Presiona `Ctrl+b` y flecha derecha para saltar a este panel. Conéctate al clúster de EKS y limpia:
   ```bash
   kubectl config use-context eks-production
   clear
   ```
6. Ahora tienes la terminal dividida, apuntando a GCP a la izquierda y a AWS a la derecha, con nombres de contexto perfectamente simétricos.

**Paso 2: Comandos rápidos listos para copiar/pegar**
*(Guárdalos en un block de notas aparte. Durante la grabación, solo harás copiar/pegar para que se vea rápido y fluido).*

```bash
# ----- PARA EL MINUTO 0:00 (El Hook) -----
# Copia este primero en el panel GKE, luego en el panel EKS. 
# La idea es que ambos lados muestren EXACTAMENTE los mismos pods corriendo.
kubectl get pods -n ml-portfolio -o wide

# ----- PARA EL MINUTO 1:10 (Load Testing) -----
# Este va en CUALQUIER panel, cuando minimices la terminal a la mitad de la pantalla
locust -f tests/load/locustfile.py --headless -u 50 -r 10 --run-time 1m --host http://136.111.152.72

# ----- PARA EL MINUTO 2:15 (Multi-Cloud Parity) -----
# Si quieres mostrar que los Ingress existen en ambos clouds
kubectl get ingress,svc -n ml-portfolio
```

---

## 🎬 Guión Detallado — Toma por Toma

### 🎬 0:00–0:10 | HOOK — Infraestructura Multi-Cloud (Impacto Inmediato)
*¿Qué impresiona más? Ver infraestructura real corriendo en ambos clouds simultáneamente.*

**Qué mostrar en pantalla**: La terminal con el "Split Screen" (tmux) activo.
1. La terminal ya debe mostrar tu prompt en el lado izquierdo con `gke-production` y en el derecho con `eks-production`.
2. Haz click en el panel izquierdo (GCP) y pega: `kubectl get pods -n ml-portfolio -o wide`
3. Haz click en el panel derecho (AWS) y pega: `kubectl get pods -n ml-portfolio -o wide`
4. Pausa 2 segundos. **Este es el efecto "Wow"**: El reclutador ve que tienes exactamente la misma infraestructura (6 microservicios) viva y en estado `Running` en dos nubes competidoras simultáneamente. Esto prueba que tu IaC y GitOps son reales.

**Subtítulo en video**: `"3 ML Services · Deployed simultaneously on GCP (GKE) & AWS (EKS)"`

**Voz de fondo**: *"Three machine learning services. Two clouds. One identical infrastructure. Provisioned with Terraform and Kustomize overlays."*

---

### 🎬 0:10–0:40 | ML Predictions — El Valor de Negocio (Swagger UI > curl)
*Mostramos la UI interactiva (Swagger) para demostrar que entregamos un producto consumible por Frontend/Backend devs.*

**Qué mostrar en pantalla**: Navegador web, cambiando rápido entre pestañas. **Usa las URLs de GCP para las predicciones** (IP pública estable).
1. **Ve a la pestaña de BankChurn Swagger** (`http://136.111.152.72/bankchurn/docs`):
   - Expande `POST /predict`. Click en "Try it out".
   - Cambia `explain` de `false` a `true` (en el dropdown/checkbox de query params).
   - Pega el JSON del block de notas en el `Request body`.
   - Click grande en **"Execute"**.
   - Haz scroll lento al "Server response". Resalta con el cursor: `"churn_probability": 0.73` y los valores dentro del objeto `"feature_contributions"` (especialmente `NumOfProducts: +0.28`).
2. **Ve a la pestaña de NLPInsight Swagger** (`http://136.111.152.72/nlpinsight/docs`):
   - Expande `POST /predict`. Click en "Try it out".
   - Pega el texto negativo del block de notas.
   - Click en **"Execute"**.
   - Resalta el resultado `"sentiment": "negative", "confidence": 0.99`.
3. **Ve a la pestaña de ChicagoTaxi Swagger** (`http://136.111.152.72/chicagotaxi/docs`):
   - Expande `POST /demand`. Click en "Try it out".
   - Pega el JSON de prueba del block de notas.
   - Click en **"Execute"**.
   - Resalta `"predicted_demand": 45.2` (u otro valor que arroje).

**Subtítulo en video**: `"Production APIs: 3 Models · Live Explainability · Sub-150ms Latency"`

**Voz de fondo**: *"The APIs are built with FastAPI. BankChurn returns predictions with live SHAP explainability in under 150 milliseconds. NLPInsight provides financial sentiment classification via a fine-tuned FinBERT transformer, and ChicagoTaxi forecasts ride demand based on 6.3 million historical trips processed with PySpark."*

---

### 🎬 0:40–1:10 | Experiment Tracking — El Estándar Enterprise (UI)
*MLflow en UI demuestra trazabilidad real, lo cual es crítico para reclutadores MLOps.*

**Qué mostrar en pantalla**: Pestaña de MLflow GCP (`http://136.111.152.72/mlflow`).
1. Selecciona el experimento `BankChurn` en la barra lateral izquierda.
2. En la tabla principal, selecciona con los checkboxes 3 o 4 runs (ej. `LR-baseline`, `RF-v1`, `StackingClassifier`).
3. Haz click en el botón azul **"Compare"**.
4. Haz scroll en la vista de comparación para mostrar el *Parallel coordinates plot* (el gráfico de líneas de colores) o la tabla comparativa de `test_auc`.

**Subtítulo en video**: `"MLflow Tracking Server: SQLite + PVC persistence · Auto-logged via Ingress"`

**Voz de fondo**: *"Every model version is tracked in a centralized MLflow server running in the cluster. Persistent volumes ensure data safety, while the Nginx Ingress handles sub-path routing automatically so the SDK connects natively."*

---

### 🎬 1:10–1:45 | Observabilidad & Load Testing (Split Screen Horizontal)
*El momento cumbre: Mostrar tráfico generándose en la terminal y Grafana reaccionando en vivo.*

**Qué mostrar en pantalla**: Ajusta las ventanas para que el Navegador ocupe la mitad superior de la pantalla y la Terminal la mitad inferior.
1. **Navegador (Arriba)**: Grafana Dashboard (`ML Portfolio Metrics`). Asegúrate de que se vean los paneles de "Request Rate" y "P95 Latency".
2. **Terminal (Abajo)**: Pega y ejecuta el comando de Locust apuntando a GCP:
   `locust -f tests/load/locustfile.py --headless -u 50 -r 10 --run-time 1m --host http://136.111.152.72`
3. **Acción**: Tras dar 'Enter' a Locust, deja el cursor quieto. Mira cómo las líneas en Grafana (arriba) empiezan a subir dramáticamente indicando el tráfico real entrante. La latencia debe mantenerse plana y baja.
4. **Cambio rápido (opcional)**: Ve a la pestaña de Prometheus y muestra que los 4 Targets dicen `UP` (en verde).

**Subtítulo en video**: `"Full Observability: Locust load test driving traffic to Grafana & Prometheus"`

**Voz de fondo**: *"We generate headless load with Locust. Prometheus scrapes metrics every 15 seconds, and Grafana visualizes the traffic in real-time. Even at 50 concurrent users, latency stays well below the 500 millisecond SLA."*

---

### 🎬 1:45–2:15 | CI/CD Pipeline & Calidad de Código (Navegador)

**Qué mostrar en pantalla**: Pestañas de GitHub a pantalla completa.
1. **Pestaña GitHub Actions**: Muestra el workflow `CI / MLOps Pipeline` en verde. Expande la matriz para mostrar los jobs ejecutados (`Test (3.11)`, `Test (3.12)`, `Trivy Vulnerability Scanner`, `Gitleaks`, `Bandit`).
2. **Pestaña Codecov**: Muestra el gráfico "Sunburst" (el círculo de colores). Pon el mouse (hover) sobre la sección más grande (el 90%+ total) y luego sobre `src/bankchurn` o `src/nlpinsight`.

**Subtítulo en video**: `"Enterprise CI/CD: 10 jobs · Trivy Security Scans · 90%+ Coverage · Multi-Python"`

**Voz de fondo**: *"Every push triggers an enterprise CI/CD pipeline. Matrix testing across Python versions, security scanning with Trivy, and Codecov verification ensuring over 90 percent coverage across all three projects."*

---

### 🎬 2:15–2:30 | Multi-Cloud Parity (Split Screen — Navegador)
*El momento que demuestra que ambas nubes son production-grade.*

**Qué mostrar en pantalla**: Divide el navegador o usa dos ventanas lado a lado.
1. **Izquierda — GCP**: `http://136.111.152.72/bankchurn/docs` (nginx-ingress, IP pública)
2. **Derecha — AWS**: `http://100.48.81.16:31963/bankchurn/docs` (nginx-ingress vía NodePort)
3. En el panel derecho (AWS), ejecuta la misma predicción de BankChurn. El resultado debe ser **idéntico** al de GCP — mismo modelo, misma lógica, misma respuesta JSON.
4. Zoom out para que el viewer vea los dos Swagger UI al mismo tiempo.

**Subtítulo en video**: `"Multi-Cloud Parity: Same API · Same Model · GKE + EKS"`

**Voz de fondo**: *"Both clouds serve the exact same model, the same API contract, deployed from the same Kustomize base. The only difference is the overlay file — 12 lines of YAML. This is real multi-cloud, not a marketing slide."*

---

### 🎬 2:30–2:45 | DevSecOps & IaC (Terminal + IDE)

**Qué mostrar en pantalla**: Tu editor de código (VSCode o Cursor/Windsurf).
1. Abre el árbol de archivos a la izquierda.
2. Navega a `infra/terraform/` y expande las carpetas `aws` y `gcp` (demostrando que existe código Terraform para ambos).
3. Navega a `k8s/overlays/` y abre dos archivos lado a lado en el editor: `overlays/gcp/ingress-gcp.yaml` y `overlays/aws/ingress-aws.yaml`. Haz un leve scroll para mostrar cómo la base se parchea por cada nube.
4. En la terminal integrada del IDE, ejecuta `kubectl get networkpolicies -n ml-portfolio` para mostrar las reglas de denegación por defecto.

**Subtítulo en video**: `"DevSecOps: Terraform IaC · Kustomize Overlays · Network Policies"`

**Voz de fondo**: *"Infrastructure follows a GitOps approach. Kustomize manages base manifests and cloud-specific overlays. Network policies enforce zero-trust security between pods. Terraform provisions the clusters."`

---

### 🎬 2:30–2:50 | Cierre — Call to Action

**Qué mostrar en pantalla**: Navegador web.
1. **GitHub Repo (README)**: Haz un scroll suave hacia la parte superior. Pausa un segundo mostrando la insignia de versión y el diagrama arquitectónico.
2. **Pantalla final estática**: Corta (en post-producción) a una imagen de fondo oscuro con este texto blanco centrado:

```text
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

**Subtítulo en video**: `"github.com/DuqueOM"`

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
