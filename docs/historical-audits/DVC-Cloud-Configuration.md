# Configuración de DVC con Almacenamiento Cloud — Portafolio ML-MLOps

**Fecha**: 2025-11-25  
**Estado**: 📋 DOCUMENTACIÓN / PENDIENTE DE IMPLEMENTAR  
**Alcance**: Configuración de DVC para replicabilidad de datos y modelos

---

## 1) Estado Actual

### Configuración Actual de DVC

```ini
# .dvc/config
[core]
    remote = storage
['remote "storage"']
    url = /home/duque_om/projects/Projects Tripe Ten/.dvc-storage
```

**Problema**: El remote actual es local (`/home/.../Projects Tripe Ten/.dvc-storage`), lo que significa:
- ❌ Los datos no son accesibles desde otros equipos
- ❌ `dvc push` solo funciona en la máquina local
- ❌ Colaboradores no pueden ejecutar `dvc pull`
- ❌ CI/CD no puede acceder a los artefactos

---

## 2) Configuración Recomendada

### Opción A: Amazon S3

```bash
# Configurar remote S3
dvc remote add -d storage s3://my-ml-portfolio-bucket/dvc-storage

# Configurar credenciales (opciones)
# 1. Variables de entorno
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# 2. O configurar en DVC
dvc remote modify storage access_key_id "your-key"
dvc remote modify storage secret_access_key "your-secret"

# 3. O usar perfil de AWS CLI
dvc remote modify storage profile my-profile
```

### Opción B: Google Cloud Storage

```bash
# Configurar remote GCS
dvc remote add -d storage gs://my-ml-portfolio-bucket/dvc-storage

# Autenticación (usar service account)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### Opción C: Azure Blob Storage

```bash
# Configurar remote Azure
dvc remote add -d storage azure://my-container/dvc-storage
dvc remote modify storage account_name my-account
dvc remote modify storage account_key "your-key"
```

### Opción D: MinIO (Self-hosted S3-compatible)

```bash
# Configurar MinIO
dvc remote add -d storage s3://dvc-bucket
dvc remote modify storage endpointurl http://localhost:9000
dvc remote modify storage access_key_id minioadmin
dvc remote modify storage secret_access_key minioadmin
```

---

## 3) Pasos de Migración

### Paso 1: Crear Bucket en Cloud

```bash
# AWS S3
aws s3 mb s3://ml-mlops-portfolio-dvc --region us-east-1

# GCS
gsutil mb gs://ml-mlops-portfolio-dvc

# Azure
az storage container create --name dvc-storage --account-name myaccount
```

### Paso 2: Actualizar Configuración DVC

```bash
cd /path/to/ML-MLOps-Portfolio

# Remover remote local
dvc remote remove storage

# Añadir remote cloud (ejemplo S3)
dvc remote add -d storage s3://ml-mlops-portfolio-dvc/data
dvc remote modify storage region us-east-1
```

### Paso 3: Subir Datos Existentes

```bash
# Verificar archivos tracked por DVC
dvc status

# Subir al nuevo remote
dvc push -r storage
```

### Paso 4: Verificar Acceso

```bash
# Desde otra máquina o en CI
dvc pull -r storage
```

---

## 4) Configuración para CI/CD

### GitHub Actions Secrets

Añadir los siguientes secrets en GitHub:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (opcional)

### Ejemplo de Job en CI

```yaml
- name: Configure DVC
  run: |
    pip install dvc[s3]  # o dvc[gs], dvc[azure]
    dvc remote modify storage access_key_id ${{ secrets.AWS_ACCESS_KEY_ID }}
    dvc remote modify storage secret_access_key ${{ secrets.AWS_SECRET_ACCESS_KEY }}

- name: Pull DVC data
  run: dvc pull

- name: Run training
  run: dvc repro
```

---

## 5) Estructura de Archivos DVC por Proyecto

### BankChurn-Predictor

```
BankChurn-Predictor/
├── dvc.yaml           # Pipeline definition
├── dvc.lock           # Pipeline state
├── data/
│   └── raw/
│       └── Churn.csv.dvc  # Tracked data file
└── models/
    └── model.pkl.dvc      # Tracked model artifact
```

### Ejemplo de `dvc.yaml`

```yaml
stages:
  prepare:
    cmd: python src/bankchurn/data.py
    deps:
      - data/raw/Churn.csv
    outs:
      - data/processed/train.csv
      - data/processed/test.csv

  train:
    cmd: python main.py --mode train
    deps:
      - data/processed/train.csv
      - src/bankchurn/training.py
    outs:
      - models/model.pkl
    metrics:
      - metrics.json:
          cache: false

  evaluate:
    cmd: python main.py --mode evaluate
    deps:
      - models/model.pkl
      - data/processed/test.csv
    metrics:
      - evaluation_metrics.json:
          cache: false
```

---

## 6) Comandos Útiles de DVC

### Operaciones Básicas

```bash
# Ver estado de datos y pipelines
dvc status

# Reproducir pipeline
dvc repro

# Subir datos al remote
dvc push

# Descargar datos del remote
dvc pull

# Ver diferencias
dvc diff
```

### Tracking de Archivos

```bash
# Añadir archivo a DVC
dvc add data/raw/large_dataset.csv

# Añadir directorio completo
dvc add data/raw/

# Remover de DVC
dvc remove data/raw/large_dataset.csv.dvc
```

### Gestión de Remotes

```bash
# Listar remotes
dvc remote list

# Ver configuración de remote
dvc remote modify storage --list

# Cambiar remote por defecto
dvc remote default storage
```

---

## 7) Costos Estimados (Cloud Storage)

| Proveedor | Almacenamiento | Transferencia | Costo Mensual Estimado* |
|-----------|---------------|---------------|------------------------|
| AWS S3 Standard | $0.023/GB | $0.09/GB out | ~$5-20 |
| GCS Standard | $0.020/GB | $0.12/GB out | ~$5-20 |
| Azure Blob Hot | $0.018/GB | $0.087/GB out | ~$5-20 |
| MinIO (self-hosted) | - | - | Costo de servidor |

*Para ~50GB de datos y uso moderado

---

## 8) Checklist de Implementación

### Preparación
- [ ] Crear cuenta/proyecto en cloud provider
- [ ] Crear bucket con nombre único
- [ ] Configurar permisos IAM/Service Account
- [ ] Generar credenciales (access keys)

### Configuración
- [ ] Actualizar `.dvc/config` con nuevo remote
- [ ] Configurar credenciales localmente
- [ ] Subir datos existentes (`dvc push`)
- [ ] Verificar descarga (`dvc pull` desde otra ubicación)

### CI/CD
- [ ] Añadir secrets a GitHub
- [ ] Actualizar workflows con `dvc pull`
- [ ] Probar pipeline completo en CI

### Documentación
- [ ] Actualizar README de cada proyecto
- [ ] Documentar proceso de onboarding para colaboradores

---

## 9) Ejemplo de README Actualizado

```markdown
## Data Setup

This project uses DVC for data versioning.

### First-time Setup

1. Install DVC with S3 support:
   ```bash
   pip install dvc[s3]
   ```

2. Configure AWS credentials:
   ```bash
   aws configure
   # Or set environment variables
   export AWS_ACCESS_KEY_ID="your-key"
   export AWS_SECRET_ACCESS_KEY="your-secret"
   ```

3. Pull the data:
   ```bash
   dvc pull
   ```

### Reproducing Experiments

```bash
# Run full pipeline
dvc repro

# Run specific stage
dvc repro train
```
```

---

## 10) Próximos Pasos Recomendados

1. **Inmediato**: Decidir proveedor cloud (S3 recomendado por compatibilidad)
2. **Esta semana**: Crear bucket y configurar credenciales
3. **Próxima sprint**: Migrar datos y actualizar CI/CD
4. **Continuo**: Documentar en README de cada proyecto

---

*Documentación generada como parte del proceso de auditoría del portafolio ML-MLOps.*
