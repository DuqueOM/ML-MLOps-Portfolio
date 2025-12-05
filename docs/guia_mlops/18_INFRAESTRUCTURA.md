# 18. Infraestructura como Código

## 🎯 Objetivo

Conceptos de IaC (Terraform) y orquestación (Kubernetes) para despliegue ML.

> **Nota**: Este módulo es AVANZADO. Para el portafolio actual, Docker + GitHub Actions es suficiente.

---

## Terraform Básico

### Concepto

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  TERRAFORM = Definir infraestructura en código                            ║
║                                                                           ║
║  En lugar de:                                                             ║
║  "Crear una instancia EC2 manualmente en la consola AWS"                  ║
║                                                                           ║
║  Escribes:                                                                ║
║  resource "aws_instance" "ml_server" {                                    ║
║    ami           = "ami-12345"                                            ║
║    instance_type = "t3.medium"                                            ║
║  }                                                                        ║
║                                                                           ║
║  Beneficios:                                                              ║
║  • Reproducible                                                           ║
║  • Versionado en Git                                                      ║
║  • Auditado                                                               ║
║  • Destruir y recrear fácilmente                                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Estructura Típica

```hcl
# main.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# ECS para ML API
resource "aws_ecs_cluster" "ml_cluster" {
  name = "ml-portfolio-cluster"
}

resource "aws_ecs_service" "bankchurn_api" {
  name            = "bankchurn-api"
  cluster         = aws_ecs_cluster.ml_cluster.id
  task_definition = aws_ecs_task_definition.bankchurn.arn
  desired_count   = 2
  
  load_balancer {
    target_group_arn = aws_lb_target_group.bankchurn.arn
    container_name   = "bankchurn"
    container_port   = 8000
  }
}
```

---

## Kubernetes Básico

### Concepto

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  KUBERNETES = Orquestar contenedores a escala                             ║
║                                                                           ║
║  Pod: Un contenedor corriendo                                             ║
║  Deployment: N réplicas de un Pod                                         ║
║  Service: Exponer Pods a la red                                           ║
║  Ingress: Routing HTTP externo                                            ║
║                                                                           ║
║  Para ML:                                                                 ║
║  • Deployment para API de inferencia                                      ║
║  • HPA (Horizontal Pod Autoscaler) para escalar con carga                 ║
║  • Secrets para API keys y credenciales                                   ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Deployment YAML

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: bankchurn-api
  labels:
    app: bankchurn
spec:
  replicas: 2
  selector:
    matchLabels:
      app: bankchurn
  template:
    metadata:
      labels:
        app: bankchurn
    spec:
      containers:
      - name: bankchurn
        image: ghcr.io/user/bankchurn:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        env:
        - name: MLFLOW_TRACKING_URI
          valueFrom:
            secretKeyRef:
              name: ml-secrets
              key: mlflow-uri
---
apiVersion: v1
kind: Service
metadata:
  name: bankchurn-service
spec:
  selector:
    app: bankchurn
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## ¿Cuándo Usar Qué?

| Escenario | Solución Recomendada |
|-----------|---------------------|
| Proyecto personal/demo | Docker + docker-compose |
| Startup pequeña | ECS Fargate o Cloud Run |
| Empresa mediana | EKS/GKE con Terraform |
| Enterprise | Full K8s + GitOps (ArgoCD) |

### Para Este Portafolio

**Docker + GitHub Actions es suficiente.**

Terraform y K8s son skills valiosos, pero no necesarios para demostrar competencia MLOps en proyectos de portafolio.

---

## 🧨 Errores habituales y cómo depurarlos en Infraestructura como Código

Aunque este módulo es avanzado, es común cometer errores que dejan tu IaC frágil o inconsistente.

### 1) Terraform aplicado “a mano” sin estado controlado

**Síntomas típicos**

- Se ejecuta `terraform apply` desde distintas máquinas sin control del `terraform.tfstate`.
- Recursos que aparecen duplicados o que se destruyen sin querer.

**Cómo identificarlo**

- Verifica dónde se guarda el estado: local vs backend remoto (S3, GCS, etc.).

**Cómo corregirlo**

- Para proyectos serios, usa un **backend remoto** para el estado y controla quién puede aplicar cambios.

---

### 2) Manifiestos de K8s que funcionan en minikube pero no en cloud

**Síntomas típicos**

- Deployment correcto en local, pero en EKS/GKE los Pods quedan `CrashLoopBackOff` o `ImagePullBackOff`.

**Cómo identificarlo**

- Revisa la imagen referenciada (`image:`) y las credenciales de registry.

**Cómo corregirlo**

- Asegura que la imagen esté en un registry accesible desde el cluster (ECR/GCR/GHCR) y que el cluster tenga permisos para leerla.

---

### 3) Resources/limits mal configurados en K8s

**Síntomas típicos**

- Pods que se matan por OOMKilled o throttling excesivo de CPU.

**Cómo identificarlo**

- Observa eventos del Pod y métricas de consumo real.

**Cómo corregirlo**

- Ajusta `requests` y `limits` según el perfil real de uso de tu API ML, empezando conservador y ajustando con métricas.

---

### 4) ¿Cuándo escalar más allá de Docker?

**Síntomas típicos**

- Intentar introducir Terraform/K8s en un proyecto de portafolio cuando aún no dominas Docker + CI/CD.

**Cómo identificarlo**

- Si todavía no tienes un flujo sólido con Docker + GitHub Actions, probablemente es pronto para meter K8s.

**Cómo corregirlo**

- Sigue la recomendación del módulo: primero domina Docker + CI/CD. Usa IaC/K8s solo si tu contexto profesional lo exige.

---

### 5) Patrón general de debugging en IaC

1. Aplica primero en entornos de prueba pequeños (playgrounds, sandbox).
2. Revisa siempre el **plan** (`terraform plan`, `kubectl diff`) antes de aplicar.
3. Usa métricas y eventos del cluster para ajustar configuración en lugar de adivinar.

Con este enfoque, IaC y K8s se vuelven herramientas que suman, no otra fuente de problemas.

---

## Horizontal Pod Autoscaler (HPA)

El HPA escala automáticamente los pods basándose en métricas como CPU o memoria.

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bankchurn-hpa
  namespace: mlops
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bankchurn-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Esperar 5 min antes de escalar abajo
    scaleUp:
      stabilizationWindowSeconds: 0    # Escalar arriba inmediatamente
```

**¿Por qué 70% CPU?** Es un balance entre eficiencia (no desperdiciar recursos) y capacidad de respuesta (tener margen para picos).

---

## ConfigMaps y Secrets

### ConfigMap (configuración no sensible)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: bankchurn-config
  namespace: mlops
data:
  LOG_LEVEL: "INFO"
  MODEL_PATH: "/app/artifacts/model.joblib"
  MLFLOW_TRACKING_URI: "http://mlflow-service:5000"
```

### Secret (ejemplo didáctico, **no usar en producción**)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ml-secrets
  namespace: mlops
type: Opaque
data:
  # Valores de ejemplo. En un entorno real se inyectan desde el sistema de secretos.
  database-password: REEMPLAZAR_EN_ENTORNO_REAL
  api-key: REEMPLAZAR_EN_ENTORNO_REAL
```

### Uso en Deployment

```yaml
spec:
  containers:
  - name: bankchurn
    envFrom:
    - configMapRef:
        name: bankchurn-config
    - secretRef:
        name: ml-secrets
```

---

## Ingress para Routing HTTP

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mlops-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: api.mlops.example.com
    http:
      paths:
      - path: /bankchurn
        pathType: Prefix
        backend:
          service:
            name: bankchurn-service
            port:
              number: 80
      - path: /carvision
        pathType: Prefix
        backend:
          service:
            name: carvision-service
            port:
              number: 80
```

---

## 📦 Cómo se usó en el Portafolio

El directorio `k8s/` del portafolio contiene 8 manifests production-ready:

| Archivo | Propósito |
|---------|-----------|
| `namespace.yaml` | Namespace `mlops` aislado |
| `bankchurn-deployment.yaml` | Deployment + Service + HPA |
| `carvision-deployment.yaml` | Deployment + Service |
| `telecom-deployment.yaml` | Deployment + Service |
| `prometheus-deployment.yaml` | Monitoreo |
| `grafana-deployment.yaml` | Dashboards |
| `ingress.yaml` | Routing HTTP |
| `storage.yaml` | PersistentVolumeClaims |

**Comandos útiles:**

```bash
# Aplicar todos los manifests
kubectl apply -f k8s/

# Ver estado de pods
kubectl get pods -n mlops

# Ver logs de un pod
kubectl logs -f deployment/bankchurn-api -n mlops

# Escalar manualmente (si no usas HPA)
kubectl scale deployment bankchurn-api --replicas=3 -n mlops

# Port-forward para testing local
kubectl port-forward svc/bankchurn-service 8001:80 -n mlops
```

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **IaC (Infrastructure as Code)**: Por qué Terraform/Pulumi sobre click-ops.

2. **Kubernetes basics**: Pods, Deployments, Services, ConfigMaps.

3. **Cloud agnostic**: Diseña para portabilidad cuando sea posible.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Multi-environment | Usa Terraform workspaces o directorios |
| Secrets | External Secrets Operator o cloud-native solutions |
| Costos | Tagging obligatorio para cost allocation |
| DR (Disaster Recovery) | Documenta y prueba regularmente |

### Stack Recomendado

```
IaC:        Terraform + Terragrunt
Containers: Docker + Kubernetes
CI/CD:      GitHub Actions + ArgoCD
Secrets:    Vault o AWS Secrets Manager
Monitoring: Prometheus + Grafana
```


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo | Duración |
|:--:|:--------|:-----|:--------:|
| 🔴 | [Kubernetes Tutorial - TechWorld Nana](https://www.youtube.com/watch?v=X48VuDVv0do) | Video | 4h |
| 🟡 | [Terraform Tutorial - freeCodeCamp](https://www.youtube.com/watch?v=7xngnjfIlK4) | Video | 2.5h |
| 🟢 | [Kubernetes Fundamentals - LF](https://training.linuxfoundation.org/) | Curso | 35h |

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones detalladas de:
- **Kubernetes**: Orquestación de contenedores
- **HPA**: Horizontal Pod Autoscaler
- **ConfigMap/Secret**: Configuración en K8s
- **Terraform**: Infrastructure as Code

---

## ✅ Checkpoint

Para este nivel:
- [ ] Entiendes el concepto de IaC (infraestructura como código)
- [ ] Puedes leer un deployment.yaml de K8s
- [ ] Sabes qué hace un HPA y cuándo usarlo
- [ ] Entiendes la diferencia entre ConfigMap y Secret
- [ ] Sabes cuándo escalar más allá de Docker

**Ejercicios**: Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulos 17-18

---

<div align="center">

[← Despliegue](17_DESPLIEGUE.md) | [Siguiente: Documentación →](19_DOCUMENTACION.md)

</div>
