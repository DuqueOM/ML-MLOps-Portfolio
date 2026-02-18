# GCP Deployment Evidence — Portfolio Documentation Plan

Plan de acción detallado para documentar la ejecución del proyecto en GCP con recopilación audiovisual y documental profesional.

---

## 1. Screenshots Obligatorios (Evidencia Visual)

Capturar cada screenshot con timestamp visible y guardar en `docs/evidence/screenshots/`.

### 1.1 GCP Console

| # | Screenshot | Ruta Sugerida | Descripción |
|---|-----------|---------------|-------------|
| 1 | GCP Project Dashboard | `gcp-project-dashboard.png` | Vista general del proyecto con APIs habilitadas |
| 2 | GKE Cluster Overview | `gke-cluster-overview.png` | Cluster con nodos, zona, versión de K8s |
| 3 | GKE Workloads | `gke-workloads-running.png` | Todos los deployments en estado Running |
| 4 | GKE Services & Ingress | `gke-services-ingress.png` | Servicios NodePort + Ingress con IP externa |
| 5 | Artifact Registry | `artifact-registry-images.png` | 3 imágenes Docker con tags latest + v1.0.0 |
| 6 | Cloud Storage Buckets | `gcs-buckets-models.png` | Bucket de modelos con archivos subidos |
| 7 | Cloud Build History | `cloud-build-history.png` | Builds exitosos (CarVision 4m37s) |
| 8 | IAM Service Account | `iam-service-account.png` | Roles asignados al deployer |
| 9 | VPC Network | `vpc-network-topology.png` | Red VPC con subnets y firewall rules |
| 10 | Cloud SQL Instance | `cloud-sql-instance.png` | Instancia PostgreSQL db-f1-micro |
| 11 | Billing Dashboard | `billing-dashboard.png` | Costos reales del deployment |
| 12 | Cloud Monitoring | `cloud-monitoring-metrics.png` | Métricas de CPU/memory de los pods |

### 1.2 Terminal / kubectl

| # | Screenshot | Ruta Sugerida | Descripción |
|---|-----------|---------------|-------------|
| 13 | `kubectl get pods` | `kubectl-pods-running.png` | 6/6 pods Running |
| 14 | `kubectl get svc,ingress` | `kubectl-services-ingress.png` | Servicios + IP de Ingress |
| 15 | `kubectl top pods` | `kubectl-resource-usage.png` | Uso de CPU/memoria por pod |
| 16 | `terraform output` | `terraform-outputs.png` | Outputs de infraestructura |
| 17 | Health check responses | `health-checks-passing.png` | JSON responses de /health para cada servicio |
| 18 | `gcloud artifacts docker images list` | `artifact-registry-cli.png` | Lista de imágenes desde CLI |

### 1.3 Application UIs

| # | Screenshot | Ruta Sugerida | Descripción |
|---|-----------|---------------|-------------|
| 19 | Grafana Dashboard | `grafana-dashboard.png` | Dashboard principal con métricas ML |
| 20 | Grafana Data Sources | `grafana-datasources.png` | Prometheus configurado como data source |
| 21 | Prometheus Targets | `prometheus-targets-up.png` | Todos los targets UP |
| 22 | MLflow UI | `mlflow-ui.png` | Experiments y runs registrados |
| 23 | FastAPI Swagger (BankChurn) | `fastapi-swagger-bankchurn.png` | Documentación automática de la API |
| 24 | FastAPI Swagger (CarVision) | `fastapi-swagger-carvision.png` | Documentación automática de la API |
| 25 | FastAPI Swagger (Telecom) | `fastapi-swagger-telecom.png` | Documentación automática de la API |
| 26 | Prediction Response | `prediction-response.png` | JSON response con predicción real |

### 1.4 CI/CD

| # | Screenshot | Ruta Sugerida | Descripción |
|---|-----------|---------------|-------------|
| 27 | GitHub Actions Workflows | `github-actions-workflows.png` | Lista de workflows disponibles |
| 28 | GitHub Secrets | `github-secrets-configured.png` | Secrets configurados (sin valores) |
| 29 | Deploy Workflow Run | `github-actions-deploy-run.png` | Ejecución exitosa del workflow |
| 30 | Workflow Job Details | `github-actions-job-details.png` | Detalle de build + push + deploy |

---

## 2. Videos / GIFs Recomendados

Crear screencasts cortos (30-90 seg) y convertir a GIF para el README.

| # | Video/GIF | Duración | Contenido |
|---|-----------|----------|-----------|
| 1 | `demo-prediction-flow.gif` | 30s | Request → FastAPI → Prediction → Response |
| 2 | `gke-deployment-walkthrough.gif` | 60s | GCP Console: cluster → workloads → pods → logs |
| 3 | `grafana-monitoring.gif` | 45s | Dashboards de métricas en tiempo real |
| 4 | `cicd-pipeline-trigger.gif` | 60s | Git push → GitHub Actions → GKE deploy |
| 5 | `terraform-apply.gif` | 45s | Terminal: `terraform plan` → `apply` → outputs |

### Herramientas Recomendadas
- **Screenshots**: Flameshot, ShareX, o simplemente Print Screen
- **Screen recording**: OBS Studio (gratis), Loom, o asciinema (para terminal)
- **GIF conversion**: `ffmpeg -i video.mp4 -vf "fps=10,scale=800:-1" output.gif`
- **Terminal recording**: `asciinema rec demo.cast` → embed en README

---

## 3. Estructura de Archivos de Evidencia

```
docs/
├── evidence/
│   ├── screenshots/
│   │   ├── gcp-console/
│   │   │   ├── gcp-project-dashboard.png
│   │   │   ├── gke-cluster-overview.png
│   │   │   ├── gke-workloads-running.png
│   │   │   ├── gke-services-ingress.png
│   │   │   ├── artifact-registry-images.png
│   │   │   ├── cloud-build-history.png
│   │   │   ├── cloud-sql-instance.png
│   │   │   └── billing-dashboard.png
│   │   ├── terminal/
│   │   │   ├── kubectl-pods-running.png
│   │   │   ├── kubectl-services-ingress.png
│   │   │   ├── terraform-outputs.png
│   │   │   └── health-checks-passing.png
│   │   ├── application/
│   │   │   ├── grafana-dashboard.png
│   │   │   ├── prometheus-targets-up.png
│   │   │   ├── mlflow-ui.png
│   │   │   ├── fastapi-swagger-bankchurn.png
│   │   │   └── prediction-response.png
│   │   └── cicd/
│   │       ├── github-actions-workflows.png
│   │       ├── github-secrets-configured.png
│   │       └── github-actions-deploy-run.png
│   └── gifs/
│       ├── demo-prediction-flow.gif
│       ├── gke-deployment-walkthrough.gif
│       └── grafana-monitoring.gif
├── GCP_PRODUCTION_GUIDE.md
├── GCP_DEPLOYMENT_EVIDENCE.md
└── ARCHITECTURE_PORTFOLIO.md
```

---

## 4. Checklist de Captura (Orden Recomendado)

Ejecutar en este orden para capturar toda la evidencia de forma eficiente.

### Sesión 1: Infraestructura (15 min)

```bash
# 1. Abrir GCP Console en el navegador
# Screenshot: Project Dashboard, APIs habilitadas

# 2. GKE → Clusters
# Screenshot: Cluster overview con nodos y zona

# 3. Artifact Registry → Repositories
# Screenshot: 3 imágenes con tags

# 4. Cloud Storage → Buckets
# Screenshot: Bucket de modelos con archivos

# 5. Cloud Build → History
# Screenshot: Build exitoso de CarVision

# 6. Terminal
kubectl get pods -n ml-portfolio
kubectl get svc,ingress -n ml-portfolio
terraform -chdir=infra/terraform/gcp output
# Screenshot cada comando
```

### Sesión 2: Aplicaciones (15 min)

```bash
# 1. Port-forward a BankChurn
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio &
# Abrir http://localhost:8001/docs → Screenshot Swagger UI

# 2. Health check
curl http://localhost:8001/health | python3 -m json.tool
# Screenshot

# 3. Prediction request
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":35,"Tenure":5,"Balance":50000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":75000}' | python3 -m json.tool
# Screenshot

# 4. Repetir para CarVision y Telecom
kubectl port-forward svc/carvision-service 8002:80 -n ml-portfolio &
kubectl port-forward svc/telecom-service 8003:80 -n ml-portfolio &
```

### Sesión 3: Monitoring (10 min)

```bash
# 1. Grafana
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio &
# Login: admin/admin → Dashboard → Screenshot

# 2. Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio &
# Status → Targets → Screenshot

# 3. MLflow
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio &
# Experiments → Screenshot
```

### Sesión 4: CI/CD (10 min)

```bash
# 1. GitHub → Settings → Secrets and variables → Actions
# Screenshot: 4 secrets configurados

# 2. GitHub → Actions → Workflows
# Screenshot: deploy-gcp.yml workflow

# 3. Trigger manual run o push a main
# Screenshot: Workflow en ejecución y completado
```

---

## 5. Integración en README.md

Agregar una sección de "Live Deployment" al README principal:

```markdown
## Live GCP Deployment

This project has been **deployed to Google Cloud Platform** with full production infrastructure:

### Infrastructure
- **GKE Cluster**: 3-zone regional cluster with autoscaling (1-5 nodes)
- **Artifact Registry**: 3 Docker images (BankChurn, CarVision, TelecomAI)
- **GCS Buckets**: ML models and MLflow artifacts
- **GCE Load Balancer**: HTTP ingress with path-based routing
- **Monitoring**: Prometheus + Grafana dashboards

### Deployment Evidence

| Component | Screenshot |
|-----------|-----------|
| GKE Workloads | ![GKE Workloads](docs/evidence/screenshots/gcp-console/gke-workloads-running.png) |
| All Pods Running | ![Pods](docs/evidence/screenshots/terminal/kubectl-pods-running.png) |
| Grafana Dashboard | ![Grafana](docs/evidence/screenshots/application/grafana-dashboard.png) |
| CI/CD Pipeline | ![CI/CD](docs/evidence/screenshots/cicd/github-actions-deploy-run.png) |

### Quick Demo
![Prediction Demo](docs/evidence/gifs/demo-prediction-flow.gif)

> See [GCP Production Guide](docs/GCP_PRODUCTION_GUIDE.md) for the complete deployment walkthrough.
```

---

## 6. Consejos para Máximo Impacto en Portfolio

1. **Consistencia visual**: Usa el mismo tema (dark/light) en todas las capturas
2. **Anotaciones**: Agrega flechas o rectángulos rojos para señalar puntos clave
3. **Resolución**: Captura a 1920x1080 mínimo para claridad
4. **Contexto**: Cada screenshot debe tener suficiente contexto (URL visible, timestamps)
5. **Orden narrativo**: Los screenshots deben contar una historia de deployment end-to-end
6. **Limpieza**: Oculta datos sensibles (project IDs, tokens) en las capturas
7. **README badges**: Agrega badges de deployment status al README principal

### Badges Sugeridos para README

```markdown
![GCP](https://img.shields.io/badge/GCP-Deployed-4285F4?logo=google-cloud&logoColor=white)
![GKE](https://img.shields.io/badge/GKE-Running-34A853?logo=kubernetes&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?logo=mlflow&logoColor=white)
![Monitoring](https://img.shields.io/badge/Monitoring-Prometheus%2BGrafana-E6522C?logo=prometheus&logoColor=white)
```

---

## 7. Comando Rápido para Capturar Toda la Evidencia de Terminal

```bash
#!/bin/bash
# Ejecutar este script y guardar el output como evidencia

echo "========================================="
echo "ML-MLOps Portfolio - GCP Deployment Evidence"
echo "Date: $(date)"
echo "========================================="

echo ""
echo "=== 1. Cluster Nodes ==="
kubectl get nodes -o wide

echo ""
echo "=== 2. All Pods ==="
kubectl get pods -n ml-portfolio -o wide

echo ""
echo "=== 3. Services & Ingress ==="
kubectl get svc,ingress -n ml-portfolio

echo ""
echo "=== 4. Resource Usage ==="
kubectl top pods -n ml-portfolio 2>/dev/null || echo "Metrics server not available"

echo ""
echo "=== 5. Health Checks ==="
for DEPLOY in bankchurn-predictor carvision-intelligence telecom-intelligence; do
  echo "--- ${DEPLOY} ---"
  kubectl exec -n ml-portfolio deployment/${DEPLOY} -- curl -s http://localhost:8000/health 2>/dev/null
  echo ""
done

echo ""
echo "=== 6. Artifact Registry Images ==="
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/${PROJECT_ID}/ml-portfolio-images \
  --format="table(package,tags,createTime)" 2>/dev/null

echo ""
echo "=== 7. GCS Models ==="
gsutil ls -r gs://${MODELS_BUCKET}/ 2>/dev/null

echo ""
echo "=== 8. Terraform State ==="
terraform -chdir=infra/terraform/gcp output 2>/dev/null

echo ""
echo "========================================="
echo "Evidence collection complete"
echo "========================================="
```

Guardar como: `scripts/collect_evidence.sh`
