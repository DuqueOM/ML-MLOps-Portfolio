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
║  "Crear una instancia EC2 manualmente en la consola AWS"                 ║
║                                                                           ║
║  Escribes:                                                                ║
║  resource "aws_instance" "ml_server" {                                   ║
║    ami           = "ami-12345"                                           ║
║    instance_type = "t3.medium"                                           ║
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
║  • HPA (Horizontal Pod Autoscaler) para escalar con carga                ║
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

## ✅ Checkpoint

Para este nivel:
- [ ] Entiendes el concepto de IaC
- [ ] Puedes leer un deployment.yaml de K8s
- [ ] Sabes cuándo escalar más allá de Docker

---

<div align="center">

[← Despliegue](17_DESPLIEGUE.md) | [Siguiente: Documentación →](19_DOCUMENTACION.md)

</div>
