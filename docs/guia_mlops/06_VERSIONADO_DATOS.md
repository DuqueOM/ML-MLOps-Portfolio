# ════════════════════════════════════════════════════════════════════════════════
# MÓDULO 05: INGENIERÍA DE DATOS Y DVC
# Versionado de Datos, DAGs y Reproducibilidad
# Guía MLOps v5.0: Senior Edition | DuqueOM | Noviembre 2025
# ════════════════════════════════════════════════════════════════════════════════

<div align="center">

# 📊 MÓDULO 05: Ingeniería de Datos y DVC

### El Arte de Versionar lo que Git No Puede

*"Si no puedo recrear tus datos, no puedo reproducir tu modelo."*

| Duración             | Teoría               | Práctica             |
| :------------------: | :------------------: | :------------------: |
| **5-6 horas**        | 30%                  | 70%                  |

</div>

---

## 🎯 ADR de Inicio: ¿Cuándo (NO) Usar DVC?

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ADR-006: Criterios para Usar DVC                                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  ✅ USA DVC SI:                                                               ║
║  • Datos > 100MB que no caben cómodamente en Git                              ║
║  • Necesitas reproducibilidad exacta de datasets                              ║
║  • Equipo colabora en el mismo pipeline de datos                              ║
║  • Quieres DAGs declarativos para pipelines                                   ║
║  • Datos son batch (no streaming)                                             ║
║                                                                               ║
║  ❌ NO USES DVC SI:                                                           ║
║  • Datos < 50MB y no cambian frecuentemente → Git LFS o Git directo           ║
║  • Datos son streaming (Kafka, Kinesis) → No aplica versionado batch          ║
║  • Ya tienes Data Lake con Delta Lake/Iceberg → Usar versionado nativo        ║
║  • Solo 1 persona trabaja en el proyecto → Puede ser overkill                 ║
║  • Pipeline ya está en Airflow/Prefect → Evitar duplicación                   ║
║                                                                               ║
║  DECISIÓN PARA BANKCHURN:                                                     ║
║  Usar DVC porque: datos ~50MB con potencial de crecer, equipo colabora,       ║
║  queremos reproducibilidad completa, y el pipeline es batch.                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Lo Que Lograrás en Este Módulo

1. **Entender** el problema del versionado de datos en ML
2. **Configurar** DVC con remote storage
3. **Crear** pipelines reproducibles con `dvc.yaml`
4. **Diseñar** DAGs para proyectos complejos

### 🧩 Cómo se aplica en este portafolio

- En `BankChurn-Predictor/` ya tienes configurado DVC con:
  - `dvc.yaml` y `params.yaml` en la raíz del proyecto.
  - Carpeta `data/` con datasets y `.dvc/` con metadatos de versionado.
- Desde esa carpeta puedes practicar el flujo completo de este módulo ejecutando:
  ```bash
  cd BankChurn-Predictor
  dvc status
  dvc repro
  dvc pull
  ```
- Aplica los mismos principios a futuros proyectos del portafolio para mantener datos y
  pipelines de forma reproducible, especialmente cuando crees el proyecto integrador.

---

## 5.1 El Problema: Git No Escala para Datos

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    😱 EL INFIERNO DEL VERSIONADO DE DATOS                     ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   SIN VERSIONADO:                                                             ║
║                                                                               ║
║   data/                                                                       ║
║   ├── churn.csv                   # ¿Original o procesado?                    ║
║   ├── churn_v2.csv                # ¿Qué cambió?                              ║
║   ├── churn_final.csv             # ¿Es realmente el final?                   ║
║   ├── churn_final_v2.csv          # 😱                                        ║
║   ├── churn_final_FINAL.csv       # 💀                                        ║
║   └── churn_20231115_backup.csv   # ???                                       ║
║                                                                               ║
║   PROBLEMAS:                                                                  ║
║   • No sé qué datos usó el modelo v1.2.3                                      ║
║   • No puedo reproducir resultados de hace 2 meses                            ║
║   • Git se rompe con archivos grandes                                         ║
║   • Colaboración es imposible ("¿tienes el CSV actualizado?")                 ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   CON DVC:                                                                    ║
║                                                                               ║
║   data/                                                                       ║
║   └── raw/                                                                    ║
║       └── churn.csv.dvc     # Metadatos en Git, datos en storage              ║
║                                                                               ║
║   git checkout v1.2.3 && dvc checkout                                         ║
║   → Tengo EXACTAMENTE los datos de esa versión                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### Comparativa de Soluciones

| Solución | Tamaño Máx | Versionado | Pipelines | Costo | Complejidad |
| :------- | :--------: | :--------: | :-------: | :---: | :---------: |
| Git directo | ~10MB | ✅ | ❌ | Gratis | Baja |
| Git LFS | ~2GB | ✅ | ❌ | $$$ | Baja |
| **DVC** | Ilimitado | ✅ | ✅ | Storage | Media |
| Delta Lake | Ilimitado | ✅ | ❌ | Spark | Alta |
| LakeFS | Ilimitado | ✅ | ❌ | Server | Alta |

---

## 5.2 Configuración Inicial de DVC

### Instalación

```bash
# Con pip
pip install dvc

# Con extras para storage
pip install "dvc[s3]"      # Amazon S3
pip install "dvc[gs]"      # Google Cloud Storage
pip install "dvc[azure]"   # Azure Blob Storage
pip install "dvc[gdrive]"  # Google Drive (para proyectos personales)
```

### Inicialización

```bash
# En un repo Git existente
cd bankchurn-predictor
dvc init

# Esto crea:
# .dvc/           - Directorio de configuración
# .dvc/.gitignore
# .dvc/config
# .dvcignore      - Qué ignorar (como .gitignore)
```

### Configurar Remote Storage

```bash
# ════════════════════════════════════════════════════════════════════
# OPCIÓN 1: Local (para desarrollo)
# ════════════════════════════════════════════════════════════════════
dvc remote add -d localremote /path/to/dvc-storage
# -d = default remote

# ════════════════════════════════════════════════════════════════════
# OPCIÓN 2: Amazon S3
# ════════════════════════════════════════════════════════════════════
dvc remote add -d s3remote s3://my-bucket/dvc-storage
dvc remote modify s3remote region us-east-1
# Credenciales: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY en env

# ════════════════════════════════════════════════════════════════════
# OPCIÓN 3: Google Cloud Storage
# ════════════════════════════════════════════════════════════════════
dvc remote add -d gcsremote gs://my-bucket/dvc-storage
# Credenciales: GOOGLE_APPLICATION_CREDENTIALS en env

# ════════════════════════════════════════════════════════════════════
# OPCIÓN 4: Google Drive (Gratis, bueno para proyectos personales)
# ════════════════════════════════════════════════════════════════════
dvc remote add -d gdriveremote gdrive://folder-id
# La primera vez pedirá autenticación OAuth

# ════════════════════════════════════════════════════════════════════
# Ver configuración
# ════════════════════════════════════════════════════════════════════
cat .dvc/config
```

### Estructura de Directorios Recomendada

```
bankchurn-predictor/
├── data/
│   ├── raw/                    # Datos originales (DVC tracked)
│   │   ├── .gitkeep
│   │   └── churn.csv          # → churn.csv.dvc en Git
│   ├── processed/             # Datos procesados (output de pipeline)
│   │   └── .gitkeep
│   └── external/              # Datos de terceros
│       └── .gitkeep
├── models/                    # Modelos entrenados (DVC tracked)
│   └── .gitkeep
├── .dvc/
│   └── config
├── .dvcignore
└── dvc.yaml                   # Pipeline definition
```

---

## 5.3 Versionado Básico de Archivos

### Añadir Datos a DVC

```bash
# Añadir archivo
dvc add data/raw/churn.csv

# Esto crea:
# data/raw/churn.csv.dvc   - Metadatos (hash, size)
# data/raw/.gitignore      - Ignora el CSV en Git

# Ver contenido del .dvc
cat data/raw/churn.csv.dvc
```

```yaml
# data/raw/churn.csv.dvc
outs:
- md5: abc123def456...
  size: 52428800
  hash: md5
  path: churn.csv
```

### Flujo de Trabajo

```bash
# 1. Modificar datos
# ... (actualizar churn.csv con nuevos registros)

# 2. Actualizar tracking
dvc add data/raw/churn.csv

# 3. Commit ambos cambios
git add data/raw/churn.csv.dvc data/raw/.gitignore
git commit -m "data(raw): update churn dataset with Q4 2024 data"

# 4. Push datos a remote
dvc push

# 5. Push código a Git
git push
```

### Recuperar Datos de Versión Anterior

```bash
# Ver versiones del archivo
git log data/raw/churn.csv.dvc

# Checkout versión específica
git checkout v1.0.0 -- data/raw/churn.csv.dvc
dvc checkout data/raw/churn.csv

# O más simple: checkout todo
git checkout v1.0.0
dvc checkout
# → Ahora tienes código Y datos de v1.0.0
```

---

## 5.4 Pipelines con dvc.yaml (El Poder Real)

### ¿Por Qué Pipelines?

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                         PIPELINES DVC: REPRODUCIBILIDAD                       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   SIN PIPELINE:                                                               ║
║   "Para reproducir, ejecuta preprocess.py, luego train.py, luego..."          ║
║   "Ah, pero primero asegúrate de tener los datos correctos..."                ║
║   "Y usa los mismos hiperparámetros que están en... algún lugar..."           ║
║                                                                               ║
║   CON PIPELINE DVC:                                                           ║
║   $ dvc repro                                                                 ║
║   → Ejecuta TODO automáticamente, en orden correcto,                          ║
║     saltando stages que no cambiaron.                                         ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### dvc.yaml Completo para BankChurn

```yaml
# dvc.yaml
stages:
  # ════════════════════════════════════════════════════════════════════
  # STAGE 1: Preparación de Datos
  # ════════════════════════════════════════════════════════════════════
  prepare:
    cmd: python src/bankchurn/data/prepare.py
    deps:
      - src/bankchurn/data/prepare.py
      - data/raw/churn.csv
      - configs/config.yaml
    params:
      - prepare.test_size
      - prepare.random_state
    outs:
      - data/processed/train.csv
      - data/processed/test.csv

  # ════════════════════════════════════════════════════════════════════
  # STAGE 2: Feature Engineering
  # ════════════════════════════════════════════════════════════════════
  featurize:
    cmd: python src/bankchurn/features/build.py
    deps:
      - src/bankchurn/features/build.py
      - data/processed/train.csv
      - data/processed/test.csv
      - configs/config.yaml
    params:
      - features.numerical
      - features.categorical
    outs:
      - data/processed/train_features.pkl
      - data/processed/test_features.pkl

  # ════════════════════════════════════════════════════════════════════
  # STAGE 3: Entrenamiento
  # ════════════════════════════════════════════════════════════════════
  train:
    cmd: python src/bankchurn/training.py
    deps:
      - src/bankchurn/training.py
      - data/processed/train_features.pkl
      - configs/config.yaml
    params:
      - train.n_estimators
      - train.max_depth
      - train.random_state
    outs:
      - models/pipeline.pkl
    metrics:
      - metrics/train_metrics.json:
          cache: false

  # ════════════════════════════════════════════════════════════════════
  # STAGE 4: Evaluación
  # ════════════════════════════════════════════════════════════════════
  evaluate:
    cmd: python src/bankchurn/evaluate.py
    deps:
      - src/bankchurn/evaluate.py
      - models/pipeline.pkl
      - data/processed/test_features.pkl
    metrics:
      - metrics/eval_metrics.json:
          cache: false
    plots:
      - metrics/roc_curve.json:
          x: fpr
          y: tpr
      - metrics/confusion_matrix.json:
          template: confusion
          x: predicted
          y: actual
```

### params.yaml (Configuración del Pipeline)

```yaml
# params.yaml
prepare:
  test_size: 0.2
  random_state: 42

features:
  numerical:
    - CreditScore
    - Age
    - Tenure
    - Balance
    - NumOfProducts
    - EstimatedSalary
  categorical:
    - Geography
    - Gender

train:
  n_estimators: 100
  max_depth: 10
  random_state: 42
```

### Comandos de Pipeline

```bash
# ════════════════════════════════════════════════════════════════════
# REPRODUCIR PIPELINE
# ════════════════════════════════════════════════════════════════════

# Ejecutar todo el pipeline
dvc repro

# Ejecutar stage específico (y sus dependencias)
dvc repro train

# Forzar re-ejecución (aunque no haya cambios)
dvc repro --force

# Ver qué se ejecutaría sin ejecutar
dvc repro --dry

# ════════════════════════════════════════════════════════════════════
# VISUALIZAR PIPELINE
# ════════════════════════════════════════════════════════════════════

# Ver DAG en terminal
dvc dag

# Generar imagen del DAG
dvc dag --dot | dot -Tpng -o pipeline.png

# Ver dependencias de un stage
dvc dag --outs train
```

### Visualización del DAG

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                              DVC DAG: BANKCHURN                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║                        ┌─────────────────┐                                    ║
║                        │  data/raw/*.csv │                                    ║
║                        │  configs/*.yaml │                                    ║
║                        └────────┬────────┘                                    ║
║                                 │                                             ║
║                                 ▼                                             ║
║                        ┌─────────────────┐                                    ║
║                        │    prepare      │                                    ║
║                        └────────┬────────┘                                    ║
║                                 │                                             ║
║                                 ▼                                             ║
║                        ┌─────────────────┐                                    ║
║                        │   featurize     │                                    ║
║                        └────────┬────────┘                                    ║
║                                 │                                             ║
║                     ┌───────────┴───────────┐                                 ║
║                     ▼                       ▼                                 ║
║            ┌─────────────────┐    ┌─────────────────┐                         ║
║            │     train       │    │    (test data)  │                         ║
║            └────────┬────────┘    └────────┬────────┘                         ║
║                     │                      │                                  ║
║                     └──────────┬───────────┘                                  ║
║                                ▼                                              ║
║                       ┌─────────────────┐                                     ║
║                       │    evaluate     │                                     ║
║                       └────────┬────────┘                                     ║
║                                │                                              ║
║                                ▼                                              ║
║                       ┌─────────────────┐                                     ║
║                       │    metrics/     │                                     ║
║                       └─────────────────┘                                     ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 5.5 Métricas y Experimentos

### Tracking de Métricas

```bash
# Ver métricas actuales
dvc metrics show

# Comparar con otra rama/commit
dvc metrics diff HEAD~1

# Output ejemplo:
# Path                     Metric    HEAD     HEAD~1   Change
# metrics/eval_metrics.json  auc_roc   0.8721   0.8534   0.0187
# metrics/eval_metrics.json  f1        0.7234   0.7012   0.0222
```

### Experimentos con DVC

```bash
# ════════════════════════════════════════════════════════════════════
# EJECUTAR EXPERIMENTOS
# ════════════════════════════════════════════════════════════════════

# Experimento con cambio de parámetro
dvc exp run --set-param train.n_estimators=200

# Múltiples experimentos en paralelo
dvc exp run --queue --set-param train.n_estimators=100
dvc exp run --queue --set-param train.n_estimators=200
dvc exp run --queue --set-param train.n_estimators=300
dvc exp run --run-all --parallel 3

# ════════════════════════════════════════════════════════════════════
# COMPARAR EXPERIMENTOS
# ════════════════════════════════════════════════════════════════════

# Ver todos los experimentos
dvc exp show

# Output:
# ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
# ┃ Experiment    ┃ auc_roc     ┃ f1          ┃ n_estimators   ┃
# ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
# │ main          │ 0.8721      │ 0.7234      │ 100            │
# │ exp-abc123    │ 0.8856      │ 0.7421      │ 200            │
# │ exp-def456    │ 0.8812      │ 0.7356      │ 300            │
# └───────────────┴─────────────┴─────────────┴────────────────┘

# ════════════════════════════════════════════════════════════════════
# APLICAR MEJOR EXPERIMENTO
# ════════════════════════════════════════════════════════════════════

# Aplicar a workspace
dvc exp apply exp-abc123

# O crear branch
dvc exp branch exp-abc123 feature/best-model
```

---

## 5.6 Patrones Avanzados

### Multi-Output Stages

```yaml
# dvc.yaml
stages:
  split:
    cmd: python src/split.py
    deps:
      - data/raw/full_dataset.csv
    outs:
      - data/processed/train.csv
      - data/processed/val.csv
      - data/processed/test.csv
```

### Stages Condicionales (foreach)

```yaml
# dvc.yaml - Entrenar múltiples modelos
stages:
  train:
    foreach:
      - random_forest
      - xgboost
      - lightgbm
    do:
      cmd: python src/train.py --model ${item}
      deps:
        - src/train.py
        - data/processed/train.csv
      params:
        - train.${item}
      outs:
        - models/${item}.pkl
      metrics:
        - metrics/${item}_metrics.json:
            cache: false
```

### Integración con MLflow

```python
# src/bankchurn/training.py
import mlflow
import dvc.api
import yaml

def train():
    # Obtener parámetros de DVC
    params = dvc.api.params_show()
    
    with mlflow.start_run():
        # Log parámetros
        mlflow.log_params(params["train"])
        
        # Entrenar...
        model = train_model(params["train"])
        
        # Log métricas
        metrics = evaluate(model)
        mlflow.log_metrics(metrics)
        
        # Guardar métricas para DVC también
        with open("metrics/train_metrics.json", "w") as f:
            json.dump(metrics, f)
        
        # Log modelo
        mlflow.sklearn.log_model(model, "model")
---

## 🧨 Errores habituales y cómo depurarlos en DVC

Aunque DVC parece “solo añadir un comando más”, en la práctica los errores suelen venir de **desalineación entre Git, datos y configuración**.

### 1) Datos no aparecen al clonar el repo (`dvc pull`/`dvc checkout` olvidados)

**Síntomas típicos**

- Clonas el repositorio, ejecutas el código y obtienes errores como:
  ```text
  FileNotFoundError: data/raw/churn.csv not found
  ```
- La carpeta `data/` está vacía o solo tiene `.gitkeep`.

**Cómo identificarlo**

- Ejecuta:
  ```bash
  dvc list .
  dvc status
  ```
  para ver qué outs están trackeados.
- Mira si existen archivos `.dvc` (`data/raw/churn.csv.dvc`) pero no los datos reales.

**Cómo corregirlo**

- Después de clonar o cambiar de rama/tag, **siempre** ejecuta:
  ```bash
  dvc pull      # trae los datos desde el remote
  dvc checkout  # sincroniza versiones de datos con los .dvc actuales
  ```
- Documenta esto en el README del proyecto y en este módulo como parte del flujo estándar.

---

### 2) `.dvc` committeados pero remote sin configurar (`dvc push` fallando)

**Síntomas típicos**

- Haces `dvc push` y ves errores tipo:
  ```text
  ERROR: failed to push data to the cloud - config file error
  ```
  o credenciales faltantes.
- Compañeros de equipo tienen los `.dvc`, pero `dvc pull` no trae nada.

**Cómo identificarlo**

- Revisa `.dvc/config` para ver qué remote está configurado (`localremote`, `s3remote`, etc.).
- Ejecuta `dvc remote list` y valida que el remote por defecto (`-d`) exista y sea accesible.

**Cómo corregirlo**

- Asegúrate de que todos usen **el mismo nombre de remote** y que esté configurado en el repo (no solo en local).
- Para remotes cloud (S3, GCS): documenta las variables de entorno necesarias (`AWS_ACCESS_KEY_ID`, etc.).
- Haz un `dvc push` de prueba y luego un `dvc pull` desde otra máquina para validar.

---

### 3) `dvc repro` no ejecuta stages que esperas (cambios no detectados)

**Síntomas típicos**

- Modificas código o parámetros, ejecutas `dvc repro` y ves:
  ```text
  Stage 'train' didn't change, skipping
  ```
  aunque esperabas que volviera a entrenar.

**Cómo identificarlo**

- Mira el `dvc.yaml` y verifica que:
  - El script que cambiaste esté en `deps:` del stage.
  - Los parámetros que tocaste estén en `params:`.

**Cómo corregirlo**

- Asegúrate de listar **todas las dependencias reales** en `deps:` (scripts, configs, datos intermedios).
- Si cambiaste parámetros en `params.yaml`, agrégalos a la lista `params:` del stage correspondiente.
- Si quieres forzar una re-ejecución puntual, usa `dvc repro --force train`.

---

### 4) Conflictos entre `.gitignore` y `.dvc` (datos en Git por accidente)

**Síntomas típicos**

- Ves archivos grandes (`data/raw/*.csv`, `models/*.pkl`) en `git status`.
- Existen `.dvc` pero los datos también se han añadido a Git.

**Cómo identificarlo**

- Revisa `data/raw/.gitignore` generado por `dvc add` y el `.gitignore` del proyecto principal; puede que se estén pisando.

**Cómo corregirlo**

- Respeta el patrón DVC:
  - Los datos **no** se añaden a Git, solo los `.dvc`.
  - Asegúrate de que `.gitignore` incluya las carpetas de datos/artefactos y que no contradiga los `.gitignore` generados por DVC.
- Si ya has commiteado datos grandes, elimínalos del historial (o al menos del último commit) y deja solo los `.dvc`.

---

### 5) DVC + CI/CD: pipelines que fallan en GitHub Actions

**Síntomas típicos**

- En CI, `dvc repro` falla porque no encuentra datos o no tiene acceso al remote.

**Cómo identificarlo**

- Revisa el workflow de CI y verifica si:
  - Has instalado DVC con los extras correctos (`dvc[s3]`, etc.).
  - Has configurado variables de entorno con credenciales.
  - Estás ejecutando `dvc pull` **antes** de correr el pipeline.

**Cómo corregirlo**

- Añade pasos en tu workflow:
  ```yaml
  - name: Install DVC
    run: pip install "dvc[s3]"

  - name: Pull data with DVC
    run: dvc pull

  - name: Run pipeline
    run: dvc repro
  ```
- Usa `dvc repro --dry` localmente para ver qué debería ejecutarse antes de llevarlo a CI.

---

### Patrón general de debugging en DVC

1. **Inspecciona el estado** con `dvc status` y `dvc dag`.
2. **Verifica remotes y credenciales** (`dvc remote list`, `.dvc/config`).
3. **Comprueba deps/outs/params** en `dvc.yaml` para el stage problemático.
4. **Sincroniza Git + DVC**: `git checkout <tag/branch>` seguido de `dvc checkout` y `dvc pull` si hace falta.

Con este checklist, DVC pasa de ser “caja negra que falla” a una herramienta controlable para reproducir datos y pipelines.

---

## 5.7 Ejercicio Integrador

### Setup Completo de DVC

```bash
# 1. Inicializar DVC
cd bankchurn-predictor
dvc init

# 2. Configurar remote (local para empezar)
mkdir -p ~/dvc-storage
dvc remote add -d localremote ~/dvc-storage

# 3. Crear estructura de datos
mkdir -p data/{raw,processed} models metrics

# 4. Añadir datos raw
# (asumiendo que tienes churn.csv)
cp /path/to/churn.csv data/raw/
dvc add data/raw/churn.csv

# 5. Crear dvc.yaml (copiar del ejemplo anterior)

# 6. Crear params.yaml

# 7. Commit todo
git add .
git commit -m "data(dvc): setup DVC pipeline"

# 8. Ejecutar pipeline
dvc repro

# 9. Push a remote
dvc push
git push
```

### Checklist de Verificación

```
CONFIGURACIÓN:
[ ] DVC inicializado
[ ] Remote configurado y funcionando
[ ] Datos raw tracked con DVC

PIPELINE:
[ ] dvc.yaml con stages definidos
[ ] params.yaml con parámetros
[ ] dvc repro ejecuta sin errores

VERSIONADO:
[ ] Puedo hacer git checkout + dvc checkout a versiones anteriores
[ ] dvc push/pull funcionan correctamente
[ ] Métricas se trackean con dvc metrics show
```

---

## 5.8 Autoevaluación

### Preguntas de Reflexión

1. ¿Por qué DVC usa hashes MD5 en lugar de guardar los archivos?
2. ¿Qué pasa si cambio `params.yaml` pero no el código?
3. ¿Cuándo DVC salta un stage sin ejecutarlo?
4. ¿Cómo integrarías DVC con GitHub Actions para CI?

---

## 📦 Cómo se Usó en el Portafolio

El portafolio tiene DVC configurado a nivel global:

### Estructura DVC del Portafolio

```
ML-MLOps-Portfolio/
├── .dvc/                  # Configuración DVC
│   └── config             # Remote storage config
├── .dvc-storage/          # Remote local (para demo)
├── .dvcignore            # Archivos a ignorar
└── */data/raw/*.dvc       # Archivos .dvc en cada proyecto
```

### Archivos .dvc Reales

```bash
# BankChurn-Predictor/data/raw/bank_churn.csv.dvc
md5: abc123def456...
size: 1234567
path: bank_churn.csv

# CarVision-Market-Intelligence/data/raw/car_prices.csv.dvc
md5: xyz789ghi012...
size: 2345678
path: car_prices.csv
```

### Flujo de Datos en el Portafolio

```
┌──────────────────────────────────────────────────────────────┐
│                    FLUJO DE DATOS DVC                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  data/raw/*.csv    →    .dvc files    →    .dvc-storage/     │
│  (gitignored)           (tracked)          (remote local)    │
│                                                              │
│  Para CI/CD:                                                 │
│  git clone → dvc pull → datos disponibles                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Comandos DVC del Portafolio

```bash
# Ver qué datos están trackeados
dvc status

# Obtener datos después de clonar
dvc pull

# Agregar nuevos datos
dvc add data/raw/nuevos_datos.csv
git add data/raw/nuevos_datos.csv.dvc data/raw/.gitignore
git commit -m "data(dvc): add nuevos_datos"
dvc push
```

### 🔧 Ejercicio: Trabaja con DVC Real

```bash
# 1. Ve a la raíz del portafolio
cd ML-MLOps-Portfolio

# 2. Verifica estado de DVC
dvc status

# 3. Obtén los datos (si no los tienes)
dvc pull

# 4. Verifica que los datos existen
ls -la BankChurn-Predictor/data/raw/
ls -la CarVision-Market-Intelligence/data/raw/

# 5. Experimenta: modifica params y reproduce
cd BankChurn-Predictor
dvc repro  # Si tienes dvc.yaml configurado
```

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **DVC vs Git LFS**: Explica que DVC es específico para ML (pipelines, métricas), LFS es genérico para archivos grandes.

2. **Reproducibilidad**: Menciona que puedes recrear cualquier experimento con `dvc checkout` + `git checkout`.

3. **Data Lineage**: Explica cómo DVC trackea la procedencia de datos transformados.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Datos sensibles | Usa DVC con storage encriptado (S3 + KMS) |
| Datasets grandes | Usa `dvc push/pull` selectivo por carpeta |
| CI/CD | Cachea datos en CI para evitar descargas repetidas |
| Colaboración | Documenta dónde está el remote storage |

### Flujo Profesional de Datos

1. Raw data → nunca modificar, solo agregar
2. Processed data → versionado con DVC
3. Features → cacheados para reutilización
4. Modelos → versionados con métricas


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [DVC Tutorial - DataTalks](https://www.youtube.com/watch?v=kLKBcPonMYw) | Video |
| 🟡 | [DVC Documentation](https://dvc.org/doc) | Docs |

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **DVC**: Data Version Control
- **Remote Storage**: Almacenamiento externo para datos
- **dvc.yaml**: Definición de pipelines reproducibles

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 06:
- **6.1**: Configurar DVC en proyecto
- **6.2**: Push/pull de datos

---

## 🎤 Checkpoint: Simulacro Junior

> 🎯 **¡Has completado los fundamentos!** (Módulos 01-06)
> 
> Si buscas posiciones **Junior ML Engineer**, ahora es buen momento para practicar:
> 
> **[→ SIMULACRO_ENTREVISTA_JUNIOR.md](SIMULACRO_ENTREVISTA_JUNIOR.md)**
> - 50 preguntas de Python, ML básico, Git y estructura
> - Enfoque en fundamentos y capacidad de aprendizaje

---

## 🔜 Siguiente Paso

Con datos versionados, es hora de construir **pipelines de sklearn avanzados**.

**[Ir a Módulo 07: sklearn Pipelines →](07_SKLEARN_PIPELINES.md)**

---

<div align="center">

[← Git Profesional](05_GIT_PROFESIONAL.md) | [Siguiente: sklearn Pipelines →](07_SKLEARN_PIPELINES.md)

</div>
