# Guía Completa de Documentación Visual — GCP Deployment

> **Para quién es esta guía**: Para alguien que nunca ha usado GCP y necesita documentar visualmente un proyecto ya desplegado. Se explica **qué es cada cosa**, **dónde encontrarla exactamente**, **qué hacer paso a paso** y **por qué importa** para el portafolio profesional.
>
> **Tiempo estimado total**: ~2 horas divididas en 5 sesiones independientes
>
> **Resultado final**: 30+ screenshots + 5 GIFs/videos que demuestran un deployment real de ML en producción

---

## Índice

1. [Conceptos Fundamentales](#1-conceptos-fundamentales)
2. [Herramientas Necesarias](#2-herramientas-necesarias)
3. [Preparación: Estructura de Carpetas](#3-preparación-estructura-de-carpetas)
4. [Sesión 1: GCP Console en el Navegador](#4-sesión-1-gcp-console-en-el-navegador)
5. [Sesión 2: Terminal — Estado del Sistema](#5-sesión-2-terminal--estado-del-sistema)
6. [Sesión 3: APIs en Vivo — FastAPI y Predicciones](#6-sesión-3-apis-en-vivo--fastapi-y-predicciones)
7. [Sesión 4: Monitoring — Grafana, Prometheus, MLflow](#7-sesión-4-monitoring--grafana-prometheus-mlflow)
8. [Sesión 5: CI/CD — GitHub Actions](#8-sesión-5-cicd--github-actions)
9. [Videos y GIFs para el README](#9-videos-y-gifs-para-el-readme)
10. [Integración en README.md](#10-integración-en-readmemd)
11. [Consejos de Calidad Profesional](#11-consejos-de-calidad-profesional)

---

## 1. Conceptos Fundamentales

Antes de tomar cualquier captura, necesitas entender qué estás viendo para poder explicarlo con confianza en entrevistas y en tu portafolio.

### ¿Qué es Google Cloud Platform (GCP)?

GCP es la plataforma de computación en la nube de Google. En lugar de tener servidores físicos propios, alquilas capacidad de cómputo, almacenamiento y servicios de Google. Tu proyecto usa GCP para ejecutar tus APIs de ML en servidores de Google (GKE), almacenar los modelos entrenados en la nube (Cloud Storage), guardar las imágenes Docker de tus aplicaciones (Artifact Registry), y monitorear el rendimiento en tiempo real.

### ¿Qué es Kubernetes y GKE?

**Kubernetes** es un sistema que gestiona automáticamente múltiples aplicaciones en contenedores Docker. Decide en qué servidor correr cada aplicación, las reinicia si fallan, y las escala si hay mucho tráfico. **GKE** (Google Kubernetes Engine) es Kubernetes gestionado por Google — Google se encarga del mantenimiento del sistema, tú solo defines qué aplicaciones quieres correr.

**Analogía**: Kubernetes es como un "director de orquesta" que coordina todos tus servicios. GKE es ese director contratado y pagado por Google.

### ¿Qué es un Pod?

Un **Pod** es la unidad mínima de Kubernetes. Contiene uno o más contenedores Docker corriendo juntos. En tu proyecto, cada API (BankChurn, CarVision, TelecomAI) corre en su propio Pod. Cuando ves `kubectl get pods` y todos dicen `Running`, significa que todas tus aplicaciones están vivas y respondiendo.

### ¿Qué es el Ingress?

El **Ingress** es el "portero" de tu cluster. Es un balanceador de carga que recibe tráfico de internet y lo dirige al servicio correcto según la URL. Tu Ingress tiene la IP pública `34.120.120.57` y dirige `/bankchurn/*` a la API de BankChurn, `/carvision/*` a la API de CarVision, y `/telecom/*` a la API de TelecomAI.

### ¿Qué es Artifact Registry?

Es el repositorio privado de imágenes Docker de GCP. Cuando construiste las imágenes Docker de tus aplicaciones, las subiste aquí. Cuando Kubernetes necesita iniciar un Pod, descarga la imagen desde aquí. **Analogía**: Es como un "almacén privado de aplicaciones empaquetadas" al que solo tu proyecto tiene acceso.

### ¿Qué es Cloud Storage (GCS)?

Es el sistema de almacenamiento de archivos de GCP. Guardaste aquí los modelos de ML entrenados (archivos `.pkl` y `.joblib`). Cuando una API arranca, descarga su modelo desde aquí. **Analogía**: Es como Google Drive pero para aplicaciones — almacenamiento masivo, barato y accesible desde cualquier servidor de GCP.

### ¿Qué es Terraform?

Terraform es una herramienta que permite definir infraestructura como código. En lugar de hacer clic en la consola de GCP para crear recursos, escribiste archivos de configuración (`.tf`) que describen exactamente qué crear. Terraform los leyó y creó todo automáticamente. **Por qué importa para el portafolio**: Demuestra que sabes hacer "Infrastructure as Code" (IaC), una habilidad muy valorada en DevOps y MLOps.

### ¿Qué es Prometheus y Grafana?

**Prometheus** recolecta métricas de tus aplicaciones cada pocos segundos (CPU, memoria, número de requests, latencia, etc.). **Grafana** toma esos datos y los muestra en dashboards con gráficas. En producción real, siempre necesitas monitoreo. Tener Prometheus + Grafana demuestra que tu deployment es production-ready.

### ¿Qué es MLflow?

MLflow es una plataforma para gestionar el ciclo de vida de modelos ML. Registra experimentos, métricas de entrenamiento, versiones de modelos y permite comparar diferentes runs de entrenamiento.

### ¿Qué es GitHub Actions?

Es el sistema de CI/CD (Integración Continua / Despliegue Continuo) de GitHub. Cuando haces `git push`, automáticamente ejecuta un workflow que construye las imágenes Docker y las despliega en GKE. Esto elimina el proceso manual de deployment.

---

## 2. Herramientas Necesarias

### Para Screenshots

**Flameshot (recomendada — permite anotar directamente)**

```bash
# Instalar en WSL/Ubuntu
sudo apt update && sudo apt install flameshot -y

# Usar: abre interfaz gráfica para seleccionar área y agregar anotaciones
flameshot gui

# Tomar captura de pantalla completa y guardar directamente
flameshot full -p /home/duque_om/projects/ML-MLOps-Portfolio/docs/evidence/screenshots/
```

**Alternativa simple — Print Screen**
- Presiona `Print Screen` en tu teclado (guarda en el portapapeles)
- En Windows con WSL: usa `Win + Shift + S` para recorte de pantalla
- En Chrome: `F12` → menú (⋮) → "Capture screenshot" captura la página completa

### Para Videos y GIFs

**asciinema — para grabar sesiones de terminal (muy profesional)**

```bash
# Instalar
sudo apt install asciinema -y

# Grabar una sesión
asciinema rec nombre-del-demo.cast

# Todo lo que escribas queda grabado. Para terminar:
exit

# Reproducir la grabación
asciinema play nombre-del-demo.cast
```

**OBS Studio — para grabar pantalla completa (navegador + terminal)**
- Descarga desde: https://obsproject.com (gratuito)
- Graba pantalla completa o ventanas específicas
- Exporta a MP4

**Convertir video MP4 a GIF**

```bash
# Instalar ffmpeg
sudo apt install ffmpeg -y

# Convertir (800px de ancho, 10fps, loop infinito)
ffmpeg -i video.mp4 -vf "fps=10,scale=800:-1:flags=lanczos" -loop 0 output.gif
```

### Configuración de Pantalla Antes de Empezar

1. Pon el navegador en pantalla completa (`F11`) para capturas de GCP Console
2. Elige un tema (claro u oscuro) y mantenlo consistente en todas las capturas
3. Cierra pestañas innecesarias para que la barra de pestañas esté limpia
4. Asegúrate de que la URL sea siempre visible en las capturas de navegador
5. Para capturas de terminal: aumenta el tamaño de fuente (`Ctrl + +`) para mejor legibilidad

---

## 3. Preparación: Estructura de Carpetas

Crea la estructura de carpetas donde guardarás toda la evidencia. Ejecuta esto en tu terminal WSL:

```bash
cd /home/duque_om/projects/ML-MLOps-Portfolio

mkdir -p docs/evidence/screenshots/gcp-console
mkdir -p docs/evidence/screenshots/terminal
mkdir -p docs/evidence/screenshots/aplicaciones
mkdir -p docs/evidence/screenshots/monitoring
mkdir -p docs/evidence/screenshots/cicd
mkdir -p docs/evidence/gifs

echo "Estructura creada:"
ls docs/evidence/screenshots/
```

**¿Por qué esta estructura?** Cuando referencíes las imágenes en el README de GitHub, necesitas rutas organizadas. Un portafolio con imágenes ordenadas en carpetas lógicas demuestra disciplina y organización.

---

## 4. Sesión 1: GCP Console en el Navegador

> **Dónde**: En tu navegador web (Chrome recomendado)
> **Qué necesitas**: Estar logueado en https://console.cloud.google.com
> **Tiempo**: ~30 minutos | **Capturas en esta sesión**: 16 screenshots

---

### 4.1 — Abrir la Consola y Seleccionar tu Proyecto

**¿Qué es la GCP Console?** Es el panel de control visual de toda tu infraestructura. Es un sitio web donde puedes ver, gestionar y monitorear todos los recursos que creaste con Terraform y los comandos de terminal.

**Pasos exactos:**

1. Abre Chrome y ve a: **https://console.cloud.google.com**
2. Inicia sesión con la cuenta de Google que usaste para crear el proyecto GCP
3. En la parte superior izquierda verás un selector de proyectos (puede decir "My First Project" u otro nombre). Haz clic ahí
4. En el popup que aparece, busca y selecciona: **`ml-portfolio-duque-om-202602`**
5. La página se recargará mostrando el dashboard de tu proyecto
6. **Verifica**: la URL debe contener `?project=ml-portfolio-duque-om-202602`

---

> **📸 CAPTURA #01 — Dashboard del Proyecto GCP**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/01-project-dashboard.png`
> - **URL**: `console.cloud.google.com/home/dashboard?project=ml-portfolio-duque-om-202602`
> - **Qué debe verse**: El dashboard principal con el nombre del proyecto en la barra superior, tarjetas de recursos activos, y la URL con el project ID visible
> - **Por qué importa**: Es la "portada" de tu infraestructura GCP — demuestra que tienes un proyecto real activo en producción
> - **Cómo tomarla**: Asegúrate de que la URL sea visible → `flameshot gui` → selecciona toda la ventana del navegador

---

### 4.2 — APIs Habilitadas

**¿Qué son las APIs?** Las APIs son los "servicios" de GCP que activaste. Cada servicio que usas (Kubernetes, Docker Registry, Cloud Build, etc.) requiere habilitar su API primero. Ver las APIs habilitadas demuestra que configuraste correctamente el proyecto desde cero.

**Pasos exactos:**

1. En el menú izquierdo (barra lateral), busca **"APIs & Services"**
   - Si no ves el menú, haz clic en el ícono de tres líneas (☰) en la esquina superior izquierda para expandirlo
2. Haz clic en **"APIs & Services"** → **"Enabled APIs & services"**
3. Verás una lista de APIs. Las más importantes para tu proyecto:
   - `Kubernetes Engine API` — para GKE
   - `Artifact Registry API` — para las imágenes Docker
   - `Cloud Build API` — para construir imágenes en la nube
   - `Cloud Storage API` — para los modelos ML
   - `Cloud SQL Admin API` — para la base de datos PostgreSQL

---

> **📸 CAPTURA #02 — APIs Habilitadas**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/02-apis-habilitadas.png`
> - **URL**: `console.cloud.google.com/apis/dashboard?project=ml-portfolio-duque-om-202602`
> - **Qué debe verse**: Lista de APIs con Kubernetes Engine API, Artifact Registry API y Cloud Build API visibles
> - **Por qué importa**: Muestra la configuración correcta de servicios GCP — un paso que muchos principiantes omiten y que diferencia un deployment profesional

---

### 4.3 — Cluster de Kubernetes (GKE)

**¿Qué es el cluster?** Tu cluster GKE es el conjunto de servidores (nodos) donde corren todas tus aplicaciones. Lo creaste con Terraform y contiene 1-5 nodos `e2-medium` en la región `us-central1`. Piénsalo como el "datacenter virtual" de tu proyecto.

**Pasos exactos:**

1. En el menú izquierdo, busca **"Kubernetes Engine"** (puede estar en la sección "Compute")
   - Alternativa: usa la barra de búsqueda superior y escribe "Kubernetes Engine"
2. Haz clic en **"Kubernetes Engine"** → **"Clusters"**
3. Verás tu cluster: **`ml-portfolio-gke-production`**
   - Estado: debe tener un ✓ verde o decir "Running"
   - Zona: `us-central1`

---

> **📸 CAPTURA #03 — Lista de Clusters GKE**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/03-gke-clusters-lista.png`
> - **URL**: `console.cloud.google.com/kubernetes/list?project=ml-portfolio-duque-om-202602`
> - **Qué debe verse**: El cluster `ml-portfolio-gke-production` con estado verde/Running, zona us-central1
> - **Por qué importa**: Evidencia del cluster Kubernetes en producción — el corazón de tu deployment

4. Haz clic en el nombre **`ml-portfolio-gke-production`** para ver el detalle
5. En la vista de detalle verás: número de nodos, versión de Kubernetes, zona geográfica, node pools

---

> **📸 CAPTURA #04 — Detalle del Cluster GKE**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/04-gke-cluster-detalle.png`
> - **Qué debe verse**: Detalles del cluster: nodos activos, versión K8s, zona, configuración de node pools
> - **Por qué importa**: Muestra la configuración técnica del cluster — demuestra conocimiento de infraestructura cloud

---

### 4.4 — Workloads (Las 6 Aplicaciones Corriendo)

**¿Qué son los Workloads?** Son tus aplicaciones desplegadas dentro del cluster. Cada Deployment de Kubernetes aparece aquí. Debes ver 6 workloads corriendo: tus 3 APIs de ML + MLflow + Prometheus + Grafana.

**Pasos exactos:**

1. En el menú izquierdo de Kubernetes Engine, haz clic en **"Workloads"**
2. Verás la lista de todos los Deployments. Deben aparecer:
   - `bankchurn-predictor` — API de predicción de churn bancario
   - `carvision-intelligence` — API de valoración de vehículos
   - `telecom-intelligence` — API de predicción de churn de telecomunicaciones
   - `mlflow-server` — Servidor de tracking de experimentos ML
   - `prometheus` — Sistema de recolección de métricas
   - `grafana` — Dashboard de visualización de métricas
3. Todos deben tener un ícono verde (✓) o estado "OK"
4. Si alguno tiene ícono amarillo o rojo, hay un problema con ese servicio

---

> **📸 CAPTURA #05 — Todos los Workloads Running ⭐ (LA MÁS IMPORTANTE)**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/05-gke-workloads-running.png`
> - **URL**: `console.cloud.google.com/kubernetes/workload?project=ml-portfolio-duque-om-202602`
> - **Qué debe verse**: Los 6 workloads listados con todos en estado verde/OK
> - **Por qué importa**: **Esta es la captura más importante del portafolio** — demuestra que 6 servicios ML están corriendo simultáneamente en producción en GCP
> - **Tip**: Si no caben todos en pantalla, usa `Ctrl + -` para hacer zoom out en el navegador hasta que quepan todos

5. Haz clic en **`bankchurn-predictor`** para ver su detalle interno
6. Verás: imagen Docker usada, número de réplicas, recursos asignados, estado de los pods

---

> **📸 CAPTURA #06 — Detalle de Workload BankChurn**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/06-workload-bankchurn-detalle.png`
> - **Qué debe verse**: Detalle del deployment: imagen Docker de Artifact Registry, pods running, recursos CPU/memoria
> - **Por qué importa**: Muestra la configuración técnica de un servicio ML en producción con todos sus componentes

---

### 4.5 — Services e Ingress (Punto de Acceso Público)

**¿Qué son los Services?** Son los puntos de acceso internos a cada aplicación dentro del cluster. **¿Qué es el Ingress?** Es el balanceador de carga público — la IP `34.120.120.57` que el mundo exterior usa para acceder a tus APIs. Sin el Ingress, tus APIs solo serían accesibles desde dentro del cluster.

**Pasos exactos:**

1. En el menú izquierdo de Kubernetes Engine, haz clic en **"Services & Ingress"**
2. Verás dos pestañas: **"Services"** e **"Ingress"**
3. En la pestaña **"Services"** verás los servicios internos

---

> **📸 CAPTURA #07 — Services del Cluster**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/07-gke-services.png`
> - **Qué debe verse**: Lista de servicios: bankchurn-service, carvision-service, telecom-service, grafana-service, etc.
> - **Por qué importa**: Muestra la arquitectura de red interna del cluster y cómo se comunican los servicios

4. Haz clic en la pestaña **"Ingress"**
5. Verás el Ingress `ml-portfolio-ingress` con la IP: **`34.120.120.57`**

---

> **📸 CAPTURA #08 — Ingress con IP Pública**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/08-gke-ingress-ip.png`
> - **Qué debe verse**: El Ingress `ml-portfolio-ingress` con la IP pública `34.120.120.57` visible
> - **Por qué importa**: Demuestra que el sistema es accesible públicamente desde internet con una IP real asignada por GCP

---

### 4.6 — Artifact Registry (Imágenes Docker)

**¿Qué es Artifact Registry?** Es el repositorio privado donde almacenaste las imágenes Docker de tus 3 APIs. Es como "Docker Hub pero privado y dentro de GCP". Cuando Kubernetes necesita iniciar un Pod, descarga la imagen desde aquí.

**Pasos exactos:**

1. En la barra de búsqueda superior de GCP Console, escribe: **"Artifact Registry"**
2. Haz clic en el resultado "Artifact Registry"
3. Verás el repositorio: **`ml-portfolio-images`** en la región `us-central1`
4. Haz clic en **`ml-portfolio-images`**
5. Verás las 3 imágenes: `bankchurn-predictor`, `carvision-market-intelligence`, `telecomai-customer-intelligence`

---

> **📸 CAPTURA #09 — Artifact Registry con 3 Imágenes**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/09-artifact-registry-imagenes.png`
> - **Qué debe verse**: Las 3 imágenes Docker listadas con sus nombres y fechas de creación
> - **Por qué importa**: Demuestra que construiste y publicaste imágenes Docker reales en un registry privado de GCP

6. Haz clic en **`bankchurn-predictor`** para ver sus versiones (tags)
7. Verás los tags: **`latest`** y **`v1.0.0`**

---

> **📸 CAPTURA #10 — Tags de Imagen Docker (Versionado)**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/10-artifact-registry-tags.png`
> - **Qué debe verse**: Los tags `latest` y `v1.0.0` con sus fechas y tamaños
> - **Por qué importa**: Muestra versionado semántico profesional de imágenes Docker — práctica estándar en producción

---

### 4.7 — Cloud Storage (Modelos ML en la Nube)

**¿Qué es Cloud Storage?** Es donde guardaste los modelos de Machine Learning entrenados. Cuando una API arranca en Kubernetes, lo primero que hace es descargar su modelo desde aquí. Esto permite actualizar modelos sin reconstruir la imagen Docker — una práctica MLOps fundamental.

**Pasos exactos:**

1. En la barra de búsqueda, escribe: **"Cloud Storage"**
2. Haz clic en "Cloud Storage" → "Buckets"
3. Verás el bucket: **`ml-portfolio-duque-om-202602-ml-models-production`**
4. Haz clic en ese bucket
5. Verás las carpetas: `bankchurn/`, `carvision/`, `telecom/`

---

> **📸 CAPTURA #11 — Cloud Storage Bucket con Carpetas de Modelos**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/11-gcs-bucket-modelos.png`
> - **Qué debe verse**: Las carpetas bankchurn/, carvision/, telecom/ dentro del bucket
> - **Por qué importa**: Demuestra arquitectura de separación entre código y modelos — práctica profesional de MLOps que permite actualizar modelos sin redeploy

6. Haz clic en la carpeta **`bankchurn/`** y verás el archivo `best_model.pkl`

---

> **📸 CAPTURA #12 — Archivo de Modelo en GCS**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/12-gcs-modelo-bankchurn.png`
> - **Qué debe verse**: El archivo best_model.pkl con su tamaño y fecha de subida
> - **Por qué importa**: Evidencia concreta de que los modelos ML están almacenados en producción y son accesibles por las APIs

---

### 4.8 — Cloud Build (Historial de Builds)

**¿Qué es Cloud Build?** Es el servicio que construyó la imagen Docker de CarVision directamente en GCP. Se usó porque el build local en WSL se colgaba al subir capas grandes. Este historial demuestra capacidad de resolución de problemas — cuando algo no funciona localmente, sabes usar alternativas en la nube.

**Pasos exactos:**

1. En la barra de búsqueda, escribe: **"Cloud Build"**
2. Haz clic en "Cloud Build"
3. En el menú izquierdo, haz clic en **"History"**
4. Verás el historial de builds. Busca el build de CarVision con estado **SUCCESS** y duración ~4m37s

---

> **📸 CAPTURA #13 — Cloud Build History**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/13-cloud-build-history.png`
> - **Qué debe verse**: El build exitoso de carvision-market-intelligence con estado SUCCESS y duración visible
> - **Por qué importa**: Demuestra uso de Cloud Build como solución profesional cuando el build local falló — resolución de problemas reales en producción

5. Haz clic en el build de CarVision para ver los logs detallados

---

> **📸 CAPTURA #14 — Cloud Build Logs Detallados**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/14-cloud-build-logs.png`
> - **Qué debe verse**: Los logs del build mostrando los pasos completados (fetch, build, push) y el tiempo total
> - **Por qué importa**: Muestra el proceso técnico de construcción de imagen Docker en la nube con todos sus pasos

---

### 4.9 — IAM y Service Account

**¿Qué es IAM?** IAM (Identity and Access Management) gestiona quién puede hacer qué en tu proyecto GCP. El "service account" `ml-portfolio-deployer` es una cuenta especial (no humana) que usaron tus scripts y GitHub Actions para autenticarse con GCP y hacer deployments automáticos sin necesidad de un usuario humano.

**Pasos exactos:**

1. En la barra de búsqueda, escribe: **"IAM"**
2. Haz clic en "IAM & Admin" → "IAM"
3. Verás la lista de miembros con sus roles
4. Busca: `ml-portfolio-deployer@ml-portfolio-duque-om-202602.iam.gserviceaccount.com`

---

> **📸 CAPTURA #15 — IAM Service Account con Roles**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/15-iam-service-account.png`
> - **Qué debe verse**: El service account ml-portfolio-deployer con sus roles asignados (Artifact Registry Admin, Kubernetes Engine Developer, Storage Admin)
> - **Por qué importa**: Demuestra configuración correcta de seguridad y principio de mínimo privilegio — práctica de seguridad empresarial

---

### 4.10 — Billing Dashboard (Costos Reales)

**¿Qué es el Billing Dashboard?** Muestra cuánto está costando tu infraestructura. Incluir esto en el portafolio demuestra consciencia de costos — una habilidad crítica en entornos empresariales donde el presupuesto importa tanto como la funcionalidad.

**Pasos exactos:**

1. En la barra de búsqueda, escribe: **"Billing"**
2. Haz clic en "Billing"
3. Si tienes múltiples cuentas de facturación, selecciona la asociada a tu proyecto
4. Verás el costo del mes actual y el desglose por servicio (GKE, Cloud Storage, Artifact Registry, etc.)

---

> **📸 CAPTURA #16 — Billing Dashboard**
>
> - **Archivo**: `docs/evidence/screenshots/gcp-console/16-billing-dashboard.png`
> - **Qué debe verse**: Costo total del mes y desglose por servicio
> - **Por qué importa**: Demuestra consciencia de costos cloud — habilidad muy valorada en empresas. Un ML Engineer que no considera costos no es production-ready

---

## 5. Sesión 2: Terminal — Estado del Sistema

> **Dónde**: En tu terminal WSL (la ventana de texto donde escribiste los comandos durante el deployment)
> **Qué necesitas**: Tener el cluster GKE configurado en kubectl (ya lo tienes del deployment)
> **Tiempo**: ~20 minutos | **Capturas en esta sesión**: 8 screenshots

### Antes de empezar: Verificar que kubectl está conectado al cluster

**¿Qué es kubectl?** Es la herramienta de línea de comandos para controlar Kubernetes. Con ella puedes ver el estado de todos los pods, servicios, logs, etc. Es el equivalente de terminal al GCP Console que viste en el navegador.

Abre tu terminal WSL y ejecuta:

```bash
# Verificar que kubectl está conectado al cluster correcto
kubectl config current-context
```

Debe responder algo como: `gke_ml-portfolio-duque-om-202602_us-central1_ml-portfolio-gke-production`

Si no responde eso, reconecta con:
```bash
gcloud container clusters get-credentials ml-portfolio-gke-production \
  --region us-central1 \
  --project ml-portfolio-duque-om-202602
```

**¿Por qué es necesario esto?** kubectl puede estar configurado para apuntar a diferentes clusters. Este comando asegura que estás hablando con el cluster correcto en GCP.

---

### 5.1 — Estado de Todos los Pods

**¿Qué vas a ver?** La lista completa de todos los contenedores (pods) corriendo en tu cluster, con su estado, tiempo de vida y nodo donde están corriendo.

**Ejecuta en terminal:**

```bash
# Comando principal — ver todos los pods del namespace ml-portfolio
kubectl get pods -n ml-portfolio -o wide
```

**¿Qué significa cada columna?**
- `NAME`: nombre único del pod (ej: `bankchurn-predictor-7d9f8b-xyz`)
- `READY`: cuántos contenedores del pod están listos (ej: `1/1` = 1 de 1 listo)
- `STATUS`: estado actual — `Running` es lo que quieres ver
- `RESTARTS`: cuántas veces se reinició (0 es ideal)
- `AGE`: hace cuánto tiempo está corriendo
- `IP`: dirección IP interna del pod
- `NODE`: en qué servidor del cluster está corriendo

**Lo que debes ver:**
```
NAME                                    READY   STATUS    RESTARTS   AGE
bankchurn-predictor-xxxx-xxxx           1/1     Running   0          Xh
carvision-intelligence-xxxx-xxxx        1/1     Running   0          Xh
telecom-intelligence-xxxx-xxxx          1/1     Running   0          Xh
mlflow-server-xxxx-xxxx                 1/1     Running   0          Xh
prometheus-xxxx-xxxx                    1/1     Running   0          Xh
grafana-xxxx-xxxx                       1/1     Running   0          Xh
```

---

> **📸 CAPTURA #17 — kubectl get pods (6/6 Running)**
>
> - **Archivo**: `docs/evidence/screenshots/terminal/17-kubectl-pods-running.png`
> - **Comando**: `kubectl get pods -n ml-portfolio -o wide`
> - **Qué debe verse**: Los 6 pods en estado `Running` con `READY 1/1` y `RESTARTS 0`
> - **Por qué importa**: Esta es la evidencia técnica más directa de que el sistema está funcionando — complementa la captura del GCP Console
> - **Tip**: Aumenta el tamaño de fuente de la terminal (`Ctrl + +`) antes de capturar para mejor legibilidad

---

### 5.2 — Estado de Services e Ingress

**¿Qué vas a ver?** Los servicios de red que exponen cada aplicación y el Ingress con la IP pública.

```bash
# Ver servicios e ingress
kubectl get svc,ingress -n ml-portfolio
```

**¿Qué significa cada columna en Services?**
- `TYPE`: `NodePort` significa que el servicio es accesible desde fuera del pod (necesario para el Ingress)
- `CLUSTER-IP`: IP interna del servicio dentro del cluster
- `PORT(S)`: puertos expuestos (ej: `80:30xxx/TCP`)

**¿Qué significa en Ingress?**
- `ADDRESS`: la IP pública `34.120.120.57` — esta es la IP que el mundo exterior usa

---

> **📸 CAPTURA #18 — kubectl get svc,ingress**
>
> - **Archivo**: `docs/evidence/screenshots/terminal/18-kubectl-services-ingress.png`
> - **Comando**: `kubectl get svc,ingress -n ml-portfolio`
> - **Qué debe verse**: Lista de servicios NodePort y el Ingress con IP `34.120.120.57`
> - **Por qué importa**: Muestra la arquitectura de red del cluster desde la perspectiva técnica de terminal

---

### 5.3 — Uso de Recursos (CPU y Memoria)

**¿Qué vas a ver?** El consumo real de CPU y memoria de cada pod en tiempo real. Esto demuestra que el sistema está bajo carga real y que los recursos están bien dimensionados.

```bash
# Ver uso de recursos de los pods
kubectl top pods -n ml-portfolio
```

**¿Qué significa cada columna?**
- `CPU(cores)`: uso de CPU en millicores (1000m = 1 CPU completa). Ej: `50m` = 5% de un CPU
- `MEMORY(bytes)`: uso de memoria RAM. Ej: `256Mi` = 256 megabytes

**Nota**: Si el comando da error `error: Metrics API not available`, es porque el metrics-server no está instalado. En ese caso, omite esta captura y continúa.

---

> **📸 CAPTURA #19 — kubectl top pods (Uso de Recursos)**
>
> - **Archivo**: `docs/evidence/screenshots/terminal/19-kubectl-top-pods.png`
> - **Comando**: `kubectl top pods -n ml-portfolio`
> - **Qué debe verse**: CPU y memoria usada por cada pod
> - **Por qué importa**: Demuestra que el sistema está bajo carga real y que sabes monitorear recursos en Kubernetes

---

### 5.4 — Imágenes en Artifact Registry desde CLI

**¿Por qué desde CLI y no solo desde el navegador?** Porque demuestra que sabes operar GCP tanto visualmente como desde la línea de comandos — una habilidad diferenciadora. Los ingenieros senior trabajan principalmente desde CLI.

```bash
# Listar imágenes en Artifact Registry
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images \
  --format="table(package,tags,createTime)" \
  --project=ml-portfolio-duque-om-202602
```

**¿Qué verás?** Una tabla con las 3 imágenes Docker, sus tags (latest, v1.0.0) y la fecha en que fueron creadas.

---

> **📸 CAPTURA #20 — Artifact Registry desde CLI**
>
> - **Archivo**: `docs/evidence/screenshots/terminal/20-artifact-registry-cli.png`
> - **Qué debe verse**: Tabla con las 3 imágenes Docker, sus tags y fechas de creación
> - **Por qué importa**: Demuestra dominio de la CLI de GCP — habilidad diferenciadora respecto a quienes solo usan la consola web

---

### 5.5 — Modelos en Cloud Storage desde CLI

```bash
# Listar modelos en el bucket de GCS
gsutil ls -r gs://ml-portfolio-duque-om-202602-ml-models-production/
```

**¿Qué verás?** La estructura de carpetas y archivos del bucket:
```
gs://ml-portfolio-duque-om-202602-ml-models-production/bankchurn/best_model.pkl
gs://ml-portfolio-duque-om-202602-ml-models-production/carvision/model.joblib
gs://ml-portfolio-duque-om-202602-ml-models-production/telecom/model.joblib
```

---

> **📸 CAPTURA #21 — Modelos en GCS desde CLI**
>
> - **Archivo**: `docs/evidence/screenshots/terminal/21-gcs-modelos-cli.png`
> - **Qué debe verse**: Los 3 archivos de modelos ML en el bucket de GCS
> - **Por qué importa**: Evidencia técnica de que los modelos están almacenados en la nube y son accesibles

---

### 5.6 — Terraform Outputs (Infraestructura como Código)

**¿Qué son los Terraform outputs?** Son los valores que Terraform exporta después de crear la infraestructura — como la IP del cluster, el nombre del bucket, la URL del registry, etc. Mostrar esto demuestra que la infraestructura fue creada con código, no manualmente.

```bash
# Navegar al directorio de Terraform
cd /home/duque_om/projects/ML-MLOps-Portfolio

# Ver los outputs de Terraform
terraform -chdir=infra/terraform/gcp output
```

---

> **📸 CAPTURA #22 — Terraform Outputs**
>
> - **Archivo**: `docs/evidence/screenshots/terminal/22-terraform-outputs.png`
> - **Qué debe verse**: Los outputs de Terraform: cluster name, registry URL, bucket names, etc.
> - **Por qué importa**: Demuestra Infrastructure as Code (IaC) — la infraestructura fue creada con código reproducible, no con clics manuales

---

### 5.7 — Health Checks de las APIs

**¿Qué es un health check?** Es una petición HTTP al endpoint `/health` de cada API para verificar que está respondiendo correctamente. Es la forma más directa de probar que las APIs están vivas y funcionando.

**¿Qué es `kubectl exec`?** Es un comando que te permite ejecutar comandos dentro de un contenedor que está corriendo en Kubernetes. Es como "entrar" al contenedor y ejecutar algo desde adentro.

```bash
# Health check de BankChurn
echo "=== BankChurn Health ==="
kubectl exec -n ml-portfolio deployment/bankchurn-predictor -- \
  curl -s http://localhost:8000/health | python3 -m json.tool

# Health check de CarVision
echo "=== CarVision Health ==="
kubectl exec -n ml-portfolio deployment/carvision-intelligence -- \
  curl -s http://localhost:8000/health | python3 -m json.tool

# Health check de TelecomAI
echo "=== TelecomAI Health ==="
kubectl exec -n ml-portfolio deployment/telecom-intelligence -- \
  curl -s http://localhost:8000/health | python3 -m json.tool
```

**¿Qué verás?** Una respuesta JSON de cada API confirmando que está activa:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

> **📸 CAPTURA #23 — Health Checks de las 3 APIs**
>
> - **Archivo**: `docs/evidence/screenshots/terminal/23-health-checks-apis.png`
> - **Qué debe verses**: Las 3 respuestas JSON de health check con `"status": "healthy"` y `"model_loaded": true`
> - **Por qué importa**: Prueba definitiva de que las APIs están respondiendo y los modelos ML están cargados en memoria
> - **Tip**: Ejecuta los 3 comandos seguidos para que quepan en una sola captura

---

### 5.8 — Logs de un Pod en Tiempo Real

**¿Qué son los logs?** Son los mensajes que genera una aplicación mientras corre — errores, peticiones recibidas, información de inicio, etc. Ver los logs demuestra que sabes diagnosticar problemas en producción.

```bash
# Ver los últimos 50 logs de BankChurn
kubectl logs -n ml-portfolio deployment/bankchurn-predictor --tail=50

# Ver logs en tiempo real (presiona Ctrl+C para detener)
kubectl logs -n ml-portfolio deployment/bankchurn-predictor -f --tail=20
```

---

> **📸 CAPTURA #24 — Logs de Pod en Tiempo Real**
>
> - **Archivo**: `docs/evidence/screenshots/terminal/24-kubectl-logs.png`
> - **Qué debe verse**: Los logs de inicio de la API de BankChurn mostrando que cargó el modelo y está escuchando en el puerto 8000
> - **Por qué importa**: Demuestra capacidad de debugging y monitoreo de aplicaciones en producción Kubernetes

---

## 6. Sesión 3: APIs en Vivo — FastAPI y Predicciones Reales

> **Dónde**: Terminal WSL + Navegador web (ambos al mismo tiempo)
> **Qué necesitas**: kubectl conectado al cluster (verificado en la sesión anterior)
> **Tiempo**: ~20 minutos | **Capturas en esta sesión**: 9 screenshots
>
> **Concepto clave — Port-forward**: Tus APIs corren dentro del cluster GKE y no son directamente accesibles desde tu computadora local. El comando `kubectl port-forward` crea un "túnel" temporal entre tu computadora y el servicio dentro del cluster. Es como abrir una puerta temporal para que puedas acceder desde tu navegador local.

### Antes de empezar: Abrir 4 ventanas de terminal

Para esta sesión necesitas varias ventanas de terminal abiertas simultáneamente porque cada port-forward ocupa una terminal mientras está activo.

**Opción A — Varias pestañas de terminal:**
Abre 4 pestañas en tu terminal WSL (generalmente `Ctrl + Shift + T` o clic derecho → "New Tab")

**Opción B — tmux (más profesional):**
```bash
# Instalar tmux si no lo tienes
sudo apt install tmux -y

# Iniciar una sesión tmux
tmux new-session -s portfolio

# Crear paneles: Ctrl+B luego % (divide verticalmente) o " (divide horizontalmente)
# Navegar entre paneles: Ctrl+B luego flecha direccional
```

---

### 6.1 — Port-Forward a BankChurn API

**¿Qué hace este comando?** Crea un túnel entre el puerto 8001 de tu computadora local y el puerto 80 del servicio bankchurn-service dentro del cluster. Mientras el comando esté corriendo, puedes acceder a la API desde tu navegador en `http://localhost:8001`.

**En la Terminal 1, ejecuta:**
```bash
# Este comando se queda corriendo — NO lo cierres
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio
```

Verás algo como:
```
Forwarding from 127.0.0.1:8001 -> 8000
Forwarding from [::1]:8001 -> 8000
```

Eso significa que el túnel está activo. **Deja esta terminal abierta.**

---

### 6.2 — FastAPI Swagger UI de BankChurn

**¿Qué es Swagger UI?** FastAPI genera automáticamente una interfaz web interactiva para documentar y probar tu API. Está disponible en `/docs`. Es una de las características más valoradas de FastAPI — la documentación se genera sola a partir del código.

**En el navegador:**
1. Abre una nueva pestaña
2. Ve a: **http://localhost:8001/docs**
3. Verás la interfaz Swagger con todos los endpoints documentados:
   - `GET /health` — verificar que la API está viva
   - `POST /predict` — hacer una predicción de churn
   - `GET /metrics` — métricas de Prometheus
4. La interfaz muestra los parámetros de entrada, los tipos de datos, y ejemplos

---

> **📸 CAPTURA #25 — FastAPI Swagger UI de BankChurn**
>
> - **Archivo**: `docs/evidence/screenshots/aplicaciones/25-fastapi-swagger-bankchurn.png`
> - **URL**: `http://localhost:8001/docs`
> - **Qué debe verse**: La interfaz Swagger completa con todos los endpoints listados, descripción de la API, y los modelos de datos
> - **Por qué importa**: Demuestra que las APIs tienen documentación automática profesional — una característica de FastAPI que diferencia APIs bien construidas

---

### 6.3 — Hacer una Predicción Real de BankChurn

**¿Qué vas a hacer?** Enviar datos reales de un cliente bancario a la API y obtener una predicción de si ese cliente va a abandonar el banco (churn) o no. Esto es el corazón del proyecto — el modelo ML funcionando en producción.

**Opción A — Desde Swagger UI (más visual):**
1. En la página de Swagger (`http://localhost:8001/docs`), haz clic en `POST /predict`
2. Haz clic en **"Try it out"** (botón en la esquina derecha)
3. En el campo "Request body", pega este JSON con datos de un cliente:
```json
{
  "CreditScore": 650,
  "Geography": "France",
  "Gender": "Male",
  "Age": 35,
  "Tenure": 5,
  "Balance": 50000.0,
  "NumOfProducts": 2,
  "HasCrCard": 1,
  "IsActiveMember": 1,
  "EstimatedSalary": 75000.0
}
```
4. Haz clic en **"Execute"**
5. Verás la respuesta del modelo en la sección "Response body"

**Opción B — Desde terminal (más técnico):**
```bash
# Abrir una nueva terminal (Terminal 2) y ejecutar:
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 650,
    "Geography": "France",
    "Gender": "Male",
    "Age": 35,
    "Tenure": 5,
    "Balance": 50000.0,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 75000.0
  }' | python3 -m json.tool
```

**¿Qué verás en la respuesta?** Algo similar a:
```json
{
  "churn_probability": 0.23,
  "churn_prediction": false,
  "risk_category": "Low Risk",
  "feature_contributions": {
    "Age": 0.05,
    "Balance": -0.03,
    "NumOfProducts": -0.08
  }
}
```

---

> **📸 CAPTURA #26 — Predicción Real de BankChurn**
>
> - **Archivo**: `docs/evidence/screenshots/aplicaciones/26-bankchurn-prediccion-real.png`
> - **Qué debe verse**: La respuesta JSON completa con la probabilidad de churn, la predicción y las contribuciones de features (SHAP)
> - **Por qué importa**: **Esta es la demostración más impactante** — un modelo ML real haciendo predicciones en producción en GCP. Es el "producto final" de todo el trabajo de MLOps
> - **Tip**: Captura tanto el request (datos de entrada) como la respuesta para mostrar el flujo completo

---

### 6.4 — Port-Forward y Swagger de CarVision

**En la Terminal 2, ejecuta:**
```bash
kubectl port-forward svc/carvision-service 8002:80 -n ml-portfolio
```

**En el navegador:**
1. Ve a: **http://localhost:8002/docs**
2. Verás la API de valoración de vehículos con sus endpoints

---

> **📸 CAPTURA #27 — FastAPI Swagger UI de CarVision**
>
> - **Archivo**: `docs/evidence/screenshots/aplicaciones/27-fastapi-swagger-carvision.png`
> - **URL**: `http://localhost:8002/docs`
> - **Qué debe verse**: La interfaz Swagger de CarVision con los endpoints de predicción de precio de vehículos
> - **Por qué importa**: Muestra que tienes múltiples APIs ML independientes corriendo simultáneamente en el mismo cluster

**Hacer una predicción de CarVision:**
```bash
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2019,
    "make": "Toyota",
    "model": "Camry",
    "condition": "Good",
    "odometer": 45000,
    "color": "White",
    "state": "CA"
  }' | python3 -m json.tool
```

---

> **📸 CAPTURA #28 — Predicción Real de CarVision**
>
> - **Archivo**: `docs/evidence/screenshots/aplicaciones/28-carvision-prediccion-real.png`
> - **Qué debe verse**: La respuesta JSON con el precio estimado del vehículo y los factores que influyen en el precio
> - **Por qué importa**: Demuestra un caso de uso real de ML — valoración automática de vehículos usados

---

### 6.5 — Port-Forward y Swagger de TelecomAI

**En la Terminal 3, ejecuta:**
```bash
kubectl port-forward svc/telecom-service 8003:80 -n ml-portfolio
```

**En el navegador:**
1. Ve a: **http://localhost:8003/docs**

---

> **📸 CAPTURA #29 — FastAPI Swagger UI de TelecomAI**
>
> - **Archivo**: `docs/evidence/screenshots/aplicaciones/29-fastapi-swagger-telecom.png`
> - **URL**: `http://localhost:8003/docs`
> - **Qué debe verse**: La interfaz Swagger de TelecomAI con los endpoints de predicción de churn de telecomunicaciones
> - **Por qué importa**: Completa la evidencia de los 3 servicios ML independientes

**Hacer una predicción de TelecomAI:**
```bash
curl -X POST http://localhost:8003/predict \
  -H "Content-Type: application/json" \
  -d '{
    "tenure": 12,
    "MonthlyCharges": 65.5,
    "TotalCharges": 786.0,
    "Contract": "Month-to-month",
    "PaymentMethod": "Electronic check",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "TechSupport": "No"
  }' | python3 -m json.tool
```

---

> **📸 CAPTURA #30 — Predicción Real de TelecomAI**
>
> - **Archivo**: `docs/evidence/screenshots/aplicaciones/30-telecom-prediccion-real.png`
> - **Qué debe verse**: La respuesta JSON con la probabilidad de churn del cliente de telecomunicaciones
> - **Por qué importa**: Demuestra el tercer caso de uso ML — predicción de abandono en telecomunicaciones

---

### 6.6 — Las 3 Swagger UIs Abiertas Simultáneamente

Esta captura especial muestra las 3 APIs corriendo al mismo tiempo — es una imagen muy impactante para el portafolio.

**Cómo hacerlo:**
1. Abre 3 pestañas en el navegador:
   - Pestaña 1: `http://localhost:8001/docs` (BankChurn)
   - Pestaña 2: `http://localhost:8002/docs` (CarVision)
   - Pestaña 3: `http://localhost:8003/docs` (TelecomAI)
2. Usa la función de "dividir pantalla" del navegador o toma una captura de cada pestaña mostrando la barra de pestañas

---

> **📸 CAPTURA #31 — Barra de Pestañas con las 3 APIs**
>
> - **Archivo**: `docs/evidence/screenshots/aplicaciones/31-tres-apis-pestanas.png`
> - **Qué debe verse**: Las 3 pestañas del navegador abiertas (localhost:8001, :8002, :8003) con los títulos de cada API visibles
> - **Por qué importa**: Imagen de alto impacto visual que demuestra 3 servicios ML corriendo simultáneamente

---

### 6.7 — Endpoint de Métricas (Prometheus Format)

**¿Qué es esto?** Cada API expone un endpoint `/metrics` que Prometheus usa para recolectar métricas. Ver este endpoint demuestra que las APIs están instrumentadas para monitoreo — una práctica de producción avanzada.

```bash
# Ver las métricas de BankChurn en formato Prometheus
curl http://localhost:8001/metrics | head -50
```

**¿Qué verás?** Texto con métricas en formato Prometheus:
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/predict",status="200"} 5.0
# HELP prediction_latency_seconds Time for prediction
prediction_latency_seconds_bucket{le="0.1"} 3.0
```

---

> **📸 CAPTURA #32 — Endpoint de Métricas Prometheus**
>
> - **Archivo**: `docs/evidence/screenshots/aplicaciones/32-metrics-endpoint.png`
> - **Qué debe verse**: Las métricas en formato Prometheus con contadores de requests y latencias
> - **Por qué importa**: Demuestra instrumentación avanzada de las APIs para monitoreo — diferencia un deployment amateur de uno production-ready

---

## 7. Sesión 4: Monitoring — Grafana, Prometheus y MLflow

> **Dónde**: Terminal WSL + Navegador web
> **Qué necesitas**: kubectl conectado al cluster
> **Tiempo**: ~20 minutos | **Capturas en esta sesión**: 8 screenshots
>
> **Por qué el monitoring es tan importante para el portafolio**: En producción real, un sistema sin monitoreo es como volar a ciegas. Tener Prometheus + Grafana demuestra que tu deployment no es solo un "hello world" en la nube — es un sistema production-ready con observabilidad completa. Esto es lo que separa a un ML Engineer junior de uno senior.

---

### 7.1 — Grafana: Dashboard de Métricas

**¿Qué es Grafana?** Es una herramienta de visualización de datos que se conecta a Prometheus (y otras fuentes) para mostrar métricas en tiempo real con gráficas, alertas y dashboards personalizables. Es el estándar de la industria para monitoreo de sistemas.

**Paso 1 — Crear el port-forward a Grafana:**

Abre una nueva terminal (o una pestaña nueva en tu terminal) y ejecuta:

```bash
# Este comando crea el túnel a Grafana — déjalo corriendo
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio
```

Verás:
```
Forwarding from 127.0.0.1:3000 -> 3000
```

**Paso 2 — Abrir Grafana en el navegador:**

1. Ve a: **http://localhost:3000**
2. Verás la pantalla de login de Grafana
3. Ingresa las credenciales:
   - **Usuario**: `admin`
   - **Contraseña**: `admin`
4. Si te pide cambiar la contraseña, puedes saltarlo haciendo clic en "Skip"

---

> **📸 CAPTURA #33 — Grafana Login Screen**
>
> - **Archivo**: `docs/evidence/screenshots/monitoring/33-grafana-login.png`
> - **URL**: `http://localhost:3000`
> - **Qué debe verse**: La pantalla de login de Grafana con el logo y los campos de usuario/contraseña
> - **Por qué importa**: Demuestra que Grafana está corriendo y accesible — primer paso del monitoreo

**Paso 3 — Navegar al Dashboard principal:**

Una vez dentro de Grafana:
1. En el menú izquierdo, busca el ícono de cuadrícula (⊞) o "Dashboards"
2. Haz clic en **"Dashboards"**
3. Verás los dashboards disponibles. Si hay uno llamado "ML Portfolio Metrics" o similar, haz clic en él
4. Si no hay dashboards preconfigurados, ve a **"Explore"** para ver los datos crudos

---

> **📸 CAPTURA #34 — Grafana Dashboard Principal**
>
> - **Archivo**: `docs/evidence/screenshots/monitoring/34-grafana-dashboard.png`
> - **URL**: `http://localhost:3000/dashboards`
> - **Qué debe verse**: El dashboard de Grafana con gráficas de métricas (CPU, memoria, requests por segundo, latencia)
> - **Por qué importa**: **Captura de alto impacto** — un dashboard de monitoreo en tiempo real es evidencia visual poderosa de un sistema production-ready
> - **Tip**: Si las gráficas están vacías, primero genera algo de tráfico haciendo varias predicciones con curl, luego espera 30 segundos y recarga

**Paso 4 — Ver la configuración de Data Sources:**

1. En el menú izquierdo, haz clic en el ícono de engranaje (⚙) → **"Data sources"**
2. Verás que Prometheus está configurado como fuente de datos
3. Haz clic en "Prometheus" para ver la configuración

---

> **📸 CAPTURA #35 — Grafana Data Sources (Prometheus Configurado)**
>
> - **Archivo**: `docs/evidence/screenshots/monitoring/35-grafana-datasources.png`
> - **URL**: `http://localhost:3000/datasources`
> - **Qué debe verse**: Prometheus listado como data source con estado "Data source is working" (punto verde)
> - **Por qué importa**: Demuestra la integración correcta entre Grafana y Prometheus — la arquitectura de monitoreo completa

---

### 7.2 — Prometheus: Targets y Métricas

**¿Qué es Prometheus?** Es el sistema que recolecta métricas. Cada 15 segundos, Prometheus hace una petición HTTP a cada servicio en el endpoint `/metrics` y guarda los datos. Los "targets" son los servicios que Prometheus está monitoreando.

**Paso 1 — Crear el port-forward a Prometheus:**

En una nueva terminal:
```bash
# Túnel a Prometheus — déjalo corriendo
kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio
```

**Paso 2 — Abrir Prometheus en el navegador:**

1. Ve a: **http://localhost:9090**
2. Verás la interfaz de Prometheus con un campo de búsqueda de métricas

---

> **📸 CAPTURA #36 — Prometheus UI Principal**
>
> - **Archivo**: `docs/evidence/screenshots/monitoring/36-prometheus-ui.png`
> - **URL**: `http://localhost:9090`
> - **Qué debe verse**: La interfaz de Prometheus con el campo de expresiones y el logo
> - **Por qué importa**: Demuestra que Prometheus está corriendo y accesible

**Paso 3 — Ver los Targets (servicios monitoreados):**

1. En el menú superior de Prometheus, haz clic en **"Status"** → **"Targets"**
2. Verás la lista de todos los servicios que Prometheus está monitoreando
3. Cada target debe tener estado **"UP"** (en verde)
4. Los targets incluyen: bankchurn, carvision, telecom, y el propio prometheus

---

> **📸 CAPTURA #37 — Prometheus Targets UP ⭐**
>
> - **Archivo**: `docs/evidence/screenshots/monitoring/37-prometheus-targets-up.png`
> - **URL**: `http://localhost:9090/targets`
> - **Qué debe verse**: Todos los targets en estado UP (verde) con el timestamp de la última scrape exitosa
> - **Por qué importa**: Demuestra que el monitoreo está activo y recolectando datos de todos los servicios ML en tiempo real

**Paso 4 — Ejecutar una consulta de métricas:**

En el campo de expresión de la página principal de Prometheus, escribe:
```
http_requests_total
```
Luego haz clic en **"Execute"** y luego en la pestaña **"Graph"** para ver la gráfica.

---

> **📸 CAPTURA #38 — Prometheus Query con Gráfica**
>
> - **Archivo**: `docs/evidence/screenshots/monitoring/38-prometheus-query-graph.png`
> - **URL**: `http://localhost:9090/graph`
> - **Qué debe verse**: La gráfica de `http_requests_total` mostrando el número de requests a las APIs a lo largo del tiempo
> - **Por qué importa**: Demuestra capacidad de consultar métricas con PromQL — el lenguaje de consulta de Prometheus

---

### 7.3 — MLflow: Tracking de Experimentos ML

**¿Qué es MLflow?** Es la plataforma de gestión del ciclo de vida de modelos ML. Registra cada experimento de entrenamiento con sus parámetros, métricas y artefactos. Permite comparar diferentes versiones de modelos y reproducir experimentos.

**¿Por qué importa para el portafolio?** MLflow demuestra que no solo entrenas modelos — los gestionas profesionalmente. Esto es lo que diferencia un proyecto de ML académico de uno empresarial.

**Paso 1 — Crear el port-forward a MLflow:**

En una nueva terminal:
```bash
# Túnel a MLflow — déjalo corriendo
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio
```

**Paso 2 — Abrir MLflow en el navegador:**

1. Ve a: **http://localhost:5000**
2. Verás la interfaz de MLflow con la lista de experimentos

---

> **📸 CAPTURA #39 — MLflow UI — Lista de Experimentos**
>
> - **Archivo**: `docs/evidence/screenshots/monitoring/39-mlflow-experiments.png`
> - **URL**: `http://localhost:5000`
> - **Qué debe verse**: La interfaz de MLflow con los experimentos de entrenamiento (BankChurn, CarVision, TelecomAI)
> - **Por qué importa**: Demuestra gestión profesional del ciclo de vida de modelos ML — una práctica MLOps avanzada

**Paso 3 — Explorar un experimento:**

1. Haz clic en el experimento de BankChurn
2. Verás la lista de "runs" (ejecuciones de entrenamiento)
3. Haz clic en un run para ver sus detalles: parámetros, métricas, artefactos

---

> **📸 CAPTURA #40 — MLflow Run con Métricas de Entrenamiento**
>
> - **Archivo**: `docs/evidence/screenshots/monitoring/40-mlflow-run-detalle.png`
> - **Qué debe verse**: El detalle de un run de MLflow mostrando parámetros del modelo (ej: n_estimators, max_depth) y métricas (accuracy, AUC, F1-score)
> - **Por qué importa**: Muestra el proceso completo de experimentación ML — desde el entrenamiento hasta el deployment en producción

---

## 8. Sesión 5: CI/CD — GitHub Actions

> **Dónde**: Navegador web en GitHub.com
> **Tiempo**: ~15 minutos | **Capturas en esta sesión**: 7 screenshots
>
> **¿Por qué CI/CD es crucial?** Demuestra que el proyecto no requiere intervención manual para desplegarse. Cualquier cambio en el código se despliega automáticamente en GKE. Esto es un requisito en cualquier empresa de tecnología seria.

---

### 8.1 — Repositorio en GitHub

1. Ve a: **https://github.com/DuqueOM/ML-MLOps-Portfolio**
2. Observa la estructura: `k8s/`, `infra/`, `docs/`, `.github/workflows/`

---

> **📸 CAPTURA #41 — Repositorio GitHub Principal**
>
> - **Archivo**: `docs/evidence/screenshots/cicd/41-github-repositorio.png`
> - **URL**: `https://github.com/DuqueOM/ML-MLOps-Portfolio`
> - **Qué debe verse**: Página principal del repositorio con estructura de carpetas, README y estadísticas (commits, branches)
> - **Por qué importa**: Muestra que el proyecto está versionado en Git y es público — accesible para cualquier reclutador

---

### 8.2 — GitHub Actions Workflows

**¿Qué son los Workflows?** Son los archivos YAML en `.github/workflows/` que definen qué pasos ejecutar automáticamente cuando haces `git push`. Tu workflow `deploy-gcp.yml` construye imágenes Docker y las despliega en GKE.

1. En el repositorio, haz clic en la pestaña **"Actions"**
2. Verás el workflow **"Deploy to GCP"** en el panel izquierdo

---

> **📸 CAPTURA #42 — GitHub Actions — Lista de Workflows**
>
> - **Archivo**: `docs/evidence/screenshots/cicd/42-github-actions-workflows.png`
> - **URL**: `https://github.com/DuqueOM/ML-MLOps-Portfolio/actions`
> - **Qué debe verse**: La pestaña Actions con el workflow "Deploy to GCP" listado
> - **Por qué importa**: Demuestra que tienes un pipeline de CI/CD configurado y listo

---

### 8.3 — GitHub Secrets Configurados

**¿Qué son los Secrets?** Son variables de entorno secretas que GitHub almacena de forma segura. Contienen las credenciales para conectarse a GCP. Los valores nunca son visibles — solo sus nombres.

1. En el repositorio, haz clic en **"Settings"**
2. En el menú izquierdo: **"Secrets and variables"** → **"Actions"**
3. Verás los 4 secrets: `GCP_PROJECT_ID`, `GCP_SA_KEY`, `GCP_REGION`, `GKE_CLUSTER_NAME`

---

> **📸 CAPTURA #43 — GitHub Secrets Configurados**
>
> - **Archivo**: `docs/evidence/screenshots/cicd/43-github-secrets.png`
> - **URL**: `https://github.com/DuqueOM/ML-MLOps-Portfolio/settings/secrets/actions`
> - **Qué debe verse**: Los 4 secrets listados con sus nombres pero sin sus valores (siempre ocultos por seguridad)
> - **Por qué importa**: Demuestra configuración correcta de seguridad — las credenciales nunca están en el código fuente

---

### 8.4 — Código del Workflow

1. En el repositorio, navega a `.github/workflows/deploy-gcp.yml`
2. Verás el código YAML del pipeline

---

> **📸 CAPTURA #44 — Código del Workflow deploy-gcp.yml**
>
> - **Archivo**: `docs/evidence/screenshots/cicd/44-workflow-codigo.png`
> - **URL**: `https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/.github/workflows/deploy-gcp.yml`
> - **Qué debe verse**: El código YAML mostrando los jobs: detect-changes, build-and-push, deploy-to-gke, smoke-tests
> - **Por qué importa**: Muestra el pipeline de CI/CD como código — Infrastructure as Code aplicado al proceso de deployment

---

### 8.5 — Ejecutar el Workflow y Capturar su Ejecución

**Opción A — Trigger manual desde GitHub:**
1. En la pestaña **"Actions"**, haz clic en el workflow "Deploy to GCP"
2. Haz clic en **"Run workflow"** → **"Run workflow"** (confirmar)

**Opción B — Disparar con un commit:**
```bash
cd /home/duque_om/projects/ML-MLOps-Portfolio
echo "" >> docs/evidence/README.md
git add docs/evidence/README.md
git commit -m "docs: trigger CI/CD pipeline for portfolio evidence"
git push origin main
```

Luego ve a GitHub → Actions y observa el workflow ejecutándose.

---

> **📸 CAPTURA #45 — Workflow en Ejecución (En Progreso)**
>
> - **Archivo**: `docs/evidence/screenshots/cicd/45-workflow-en-progreso.png`
> - **Qué debe verse**: El workflow con los jobs en progreso (punto amarillo/naranja) — detect-changes, build-and-push, deploy-to-gke
> - **Por qué importa**: Captura el momento exacto en que el pipeline está trabajando — evidencia del CI/CD en acción

---

> **📸 CAPTURA #46 — Workflow Completado Exitosamente ⭐**
>
> - **Archivo**: `docs/evidence/screenshots/cicd/46-workflow-completado.png`
> - **Qué debe verse**: Todos los jobs en verde (✓) con el tiempo total de ejecución
> - **Por qué importa**: **Evidencia definitiva del CI/CD funcionando** — desde un `git push` hasta el deployment automático en GKE

---

> **📸 CAPTURA #47 — Detalle del Job build-and-push**
>
> - **Archivo**: `docs/evidence/screenshots/cicd/47-workflow-job-detalle.png`
> - **Cómo llegar**: Haz clic en la ejecución completada → haz clic en el job "build-and-push"
> - **Qué debe verse**: Los pasos del job con sus tiempos: checkout, auth GCP, build Docker, push a Artifact Registry — todos en verde
> - **Por qué importa**: Muestra el nivel de detalle del pipeline — cada paso está documentado y verificado automáticamente

---

## 9. Videos y GIFs para el README

Los GIFs son el elemento más impactante de un portafolio técnico. Un GIF de 30 segundos que muestra el sistema funcionando vale más que 10 screenshots estáticos. Aquí están los 5 GIFs más importantes para crear, con instrucciones exactas.

### Herramientas necesarias para esta sección

```bash
# Instalar todo lo necesario
sudo apt install asciinema ffmpeg -y

# Para grabar pantalla completa (instalar OBS Studio desde el sitio oficial)
# https://obsproject.com — descarga el instalador para Linux/Ubuntu
```

---

### GIF #1 — Demo de Predicción en Vivo (el más importante)

**¿Qué muestra?** El flujo completo: pods corriendo → port-forward → predicción ML → respuesta JSON con probabilidad de churn. Este GIF resume todo el proyecto en 45 segundos.

**Paso a paso:**

```bash
# 1. Iniciar la grabación de terminal con asciinema
asciinema rec /tmp/demo-prediccion.cast --title "ML Portfolio - Live Prediction Demo"

# 2. Dentro de la grabación, ejecuta estos comandos DESPACIO (pausa 2-3 segundos entre cada uno):

# Mostrar que los pods están corriendo
kubectl get pods -n ml-portfolio

# Crear el túnel a BankChurn
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio &
sleep 2

# Hacer una predicción real
curl -s -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 650,
    "Geography": "France",
    "Gender": "Male",
    "Age": 35,
    "Tenure": 5,
    "Balance": 50000.0,
    "NumOfProducts": 2,
    "HasCrCard": 1,
    "IsActiveMember": 1,
    "EstimatedSalary": 75000.0
  }' | python3 -m json.tool

# 3. Terminar la grabación
exit
```

**Convertir a GIF:**
```bash
# Subir a asciinema.org (opción más fácil — genera un link embebible)
asciinema upload /tmp/demo-prediccion.cast
# Copia el link que te da y úsalo en el README con: [![asciicast](link)](link)

# O convertir localmente a SVG animado (requiere npm)
npm install -g svg-term-cli
svg-term --in /tmp/demo-prediccion.cast \
  --out docs/evidence/gifs/01-demo-prediccion.svg \
  --window --width 120 --height 30
```

**Guardar como**: `docs/evidence/gifs/01-demo-prediccion.gif` (o `.svg` si usas svg-term)

---

### GIF #2 — GKE Workloads en GCP Console

**¿Qué muestra?** Navegar por GCP Console: proyecto → Kubernetes Engine → Workloads → ver los 6 pods running → hacer clic en uno para ver su detalle.

**Cómo grabarlo con OBS Studio:**

1. Abre OBS Studio
2. Crea una nueva "Scene":
   - Haz clic en el `+` en la sección "Scenes"
   - Nómbrala "GKE Demo"
3. Agrega una fuente de captura:
   - Haz clic en `+` en "Sources"
   - Selecciona "Window Capture" o "Display Capture"
   - Selecciona la ventana de Chrome
4. Haz clic en **"Start Recording"** (botón rojo en la esquina inferior derecha)
5. Navega por GCP Console mostrando los workloads — hazlo despacio y deliberadamente, pausa 2 segundos en cada pantalla importante
6. Haz clic en **"Stop Recording"**
7. El video se guarda en `~/Videos/` por defecto

**Convertir a GIF:**
```bash
# Reemplaza 'obs-recording.mkv' con el nombre real del archivo grabado
ffmpeg -i ~/Videos/obs-recording.mkv \
  -vf "fps=8,scale=900:-1:flags=lanczos" \
  -loop 0 \
  docs/evidence/gifs/02-gke-workloads.gif
```

**Guardar como**: `docs/evidence/gifs/02-gke-workloads.gif`

---

### GIF #3 — Grafana Dashboard en Tiempo Real

**¿Qué muestra?** Abrir Grafana, navegar al dashboard, ver las métricas actualizándose mientras se hacen requests a las APIs.

**Para que las gráficas se vean activas, primero genera tráfico:**

```bash
# En una terminal separada, enviar requests continuamente durante la grabación
for i in $(seq 1 30); do
  curl -s -X POST http://localhost:8001/predict \
    -H "Content-Type: application/json" \
    -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":35,"Tenure":5,"Balance":50000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":75000}' \
    > /dev/null
  sleep 2
done &
```

Luego graba con OBS Studio mientras navegas por Grafana mostrando las gráficas con datos.

```bash
ffmpeg -i ~/Videos/grafana-recording.mkv \
  -vf "fps=8,scale=900:-1:flags=lanczos" \
  -loop 0 \
  docs/evidence/gifs/03-grafana-monitoring.gif
```

**Guardar como**: `docs/evidence/gifs/03-grafana-monitoring.gif`

---

### GIF #4 — Pipeline CI/CD en GitHub Actions

**¿Qué muestra?** Hacer un `git push` en la terminal, cambiar al navegador y ver el workflow de GitHub Actions ejecutándose automáticamente job por job.

**El pipeline tarda varios minutos, así que acelera el video al grabar:**

```bash
# 1. Graba con OBS Studio mientras:
#    - Haces el git push en terminal
#    - Cambias al navegador y muestras GitHub Actions ejecutándose
#    - Esperas a que termine (puedes acelerar esta parte en edición)

# 2. Convertir acelerando 4x (para que el GIF no sea muy largo)
ffmpeg -i ~/Videos/cicd-recording.mkv \
  -vf "setpts=0.25*PTS,fps=10,scale=900:-1:flags=lanczos" \
  -loop 0 \
  docs/evidence/gifs/04-cicd-pipeline.gif
```

**Guardar como**: `docs/evidence/gifs/04-cicd-pipeline.gif`

---

### GIF #5 — Las 3 APIs Respondiendo Simultáneamente

**¿Qué muestra?** Una terminal dividida en 3 paneles (con tmux) donde cada panel hace requests a una API diferente y muestra las respuestas en tiempo real.

**Configurar tmux con 3 paneles:**

```bash
# Iniciar sesión tmux
tmux new-session -s portfolio-demo

# Dividir la pantalla en 3 paneles verticales:
# Ctrl+B luego % (divide en 2 verticalmente)
# Ctrl+B luego flecha derecha (ir al panel derecho)
# Ctrl+B luego % (divide en 3 verticalmente)

# En el panel izquierdo (Ctrl+B + flecha izquierda para navegar):
watch -n 3 'curl -s -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d "{\"CreditScore\":650,\"Geography\":\"France\",\"Gender\":\"Male\",\"Age\":35,\"Tenure\":5,\"Balance\":50000,\"NumOfProducts\":2,\"HasCrCard\":1,\"IsActiveMember\":1,\"EstimatedSalary\":75000}" \
  | python3 -m json.tool | head -5'

# En el panel central:
watch -n 3 'curl -s http://localhost:8002/health | python3 -m json.tool'

# En el panel derecho:
watch -n 3 'curl -s http://localhost:8003/health | python3 -m json.tool'
```

Graba con OBS Studio o asciinema mientras los 3 paneles muestran respuestas.

**Guardar como**: `docs/evidence/gifs/05-tres-apis-simultaneas.gif`

---

## 10. Integración en README.md

Una vez que tengas las capturas y GIFs, agrégalos al README principal. Esta sección te da el código exacto para hacerlo.

### Dónde agregar la sección en el README

Abre el archivo `/home/duque_om/projects/ML-MLOps-Portfolio/README.md` y agrega esta sección después de la descripción principal del proyecto (después del primer párrafo o después de la sección de "Features"):

### Código a agregar en README.md

```markdown
---

## 🚀 Live GCP Deployment

Este proyecto está **desplegado en Google Cloud Platform** con infraestructura completa de producción:

| Componente | Tecnología | Estado |
|-----------|-----------|--------|
| Orquestación de contenedores | Google Kubernetes Engine (GKE) | ✅ Running |
| Registry de imágenes | Artifact Registry | ✅ 3 imágenes |
| Almacenamiento de modelos | Cloud Storage (GCS) | ✅ 3 modelos |
| Monitoreo | Prometheus + Grafana | ✅ Running |
| Tracking de experimentos ML | MLflow | ✅ Running |
| CI/CD | GitHub Actions | ✅ Configurado |
| Infrastructure as Code | Terraform | ✅ Aplicado |

### 📊 Evidencia del Deployment

#### Infraestructura en GCP — 6 Servicios Running
![GKE Workloads Running](docs/evidence/screenshots/gcp-console/05-gke-workloads-running.png)

#### Estado del Cluster desde Terminal
![kubectl pods running](docs/evidence/screenshots/terminal/17-kubectl-pods-running.png)

#### APIs de ML con Documentación Automática (FastAPI + Swagger)
![FastAPI Swagger BankChurn](docs/evidence/screenshots/aplicaciones/25-fastapi-swagger-bankchurn.png)

#### Predicción Real de ML en Producción
![Predicción BankChurn](docs/evidence/screenshots/aplicaciones/26-bankchurn-prediccion-real.png)

#### Monitoreo en Tiempo Real — Grafana + Prometheus
![Grafana Dashboard](docs/evidence/screenshots/monitoring/34-grafana-dashboard.png)

#### Pipeline CI/CD Completado — GitHub Actions
![GitHub Actions](docs/evidence/screenshots/cicd/46-workflow-completado.png)

### 🎬 Demo en Vivo
![Demo Predicción](docs/evidence/gifs/01-demo-prediccion.gif)

> 📖 Ver la [Guía Completa de Deployment en GCP](docs/GCP_PRODUCTION_GUIDE.md) para el proceso detallado, problemas encontrados y soluciones aplicadas.
> 📋 Ver el [Plan de Documentación Visual](docs/GCP_DEPLOYMENT_EVIDENCE.md) para reproducir todas las capturas.
```

### Badges para agregar al inicio del README

Agrega estos badges justo debajo del título del README (antes de la descripción):

```markdown
![GCP](https://img.shields.io/badge/GCP-Deployed-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)
![GKE](https://img.shields.io/badge/GKE-6_Pods_Running-34A853?style=for-the-badge&logo=kubernetes&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-3_Images-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-3_APIs-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
```

---

## 11. Consejos de Calidad Profesional

### Consistencia Visual — Reglas de Oro

Antes de empezar cualquier sesión de capturas, configura tu entorno:

1. **Elige un tema y mantenlo**: Si usas tema oscuro en el navegador, úsalo en TODAS las capturas. Si usas tema claro, ídem. La inconsistencia visual hace que el portafolio se vea descuidado.

2. **Resolución mínima 1920×1080**: Capturas de baja resolución se ven pixeladas en pantallas modernas. Asegúrate de que tu monitor esté en resolución Full HD o superior.

3. **Sin notificaciones del sistema**: Antes de grabar, activa el modo "No molestar":
   - En Ubuntu: `gsettings set org.gnome.desktop.notifications show-banners false`
   - En Windows: `Win + A` → activar "No molestar"

4. **URL siempre visible en capturas de navegador**: La barra de URL demuestra que estás en el sitio real de GCP, no en una imagen editada. Nunca ocultes la URL.

5. **Tamaño de fuente legible en terminal**: Antes de capturar la terminal, aumenta el tamaño de fuente con `Ctrl + +` hasta que el texto sea claramente legible incluso en una imagen reducida.

### Cómo Agregar Anotaciones con Flameshot

Las anotaciones guían la atención del espectador hacia lo importante:

```bash
# Abrir Flameshot en modo GUI (selección de área + anotaciones)
flameshot gui
```

**Herramientas de Flameshot y cuándo usarlas:**

| Herramienta | Ícono | Cuándo usarla |
|-------------|-------|---------------|
| Rectángulo | ▭ | Para resaltar el estado "Running" de los pods |
| Flecha | → | Para señalar la IP pública del Ingress |
| Texto | T | Para agregar etiquetas como "6/6 Running" |
| Blur/Pixelate | ⬛ | Para ocultar project IDs, tokens, o datos sensibles |
| Número | ① | Para numerar pasos en una secuencia |

**Ejemplo de flujo de anotación:**
1. Toma la captura con `flameshot gui`
2. Selecciona el área de la pantalla que quieres capturar
3. Dibuja un rectángulo rojo alrededor de los pods en estado "Running"
4. Agrega texto "6/6 Running ✓" cerca del rectángulo
5. Guarda la imagen

### Información Sensible a Ocultar

Antes de publicar cualquier captura, verifica que NO contenga:
- Tokens de API o claves privadas (usa blur de Flameshot)
- Contraseñas (aunque sean de demo como `admin/admin`)
- Números de tarjeta de crédito en el billing dashboard
- Direcciones de email personales
- Números de teléfono

**Regla práctica**: Si no lo publicarías en Twitter, no lo publiques en el portafolio sin ocultar.

### Orden Narrativo — Cuenta una Historia

Las capturas deben contar una historia coherente de principio a fin. Este es el orden narrativo ideal:

```
1. Proyecto GCP activo (el escenario donde todo ocurre)
       ↓
2. Infraestructura creada con Terraform (cómo se construyó)
       ↓
3. Imágenes Docker en Artifact Registry (el código empaquetado)
       ↓
4. Modelos ML en Cloud Storage (los cerebros del sistema)
       ↓
5. 6 Pods Running en GKE (el sistema vivo y funcionando)
       ↓
6. APIs respondiendo con Swagger UI (el producto accesible)
       ↓
7. Predicciones reales del modelo ML (el valor de negocio)
       ↓
8. Monitoreo activo con Grafana (el sistema en producción real)
       ↓
9. CI/CD pipeline completado (la automatización del futuro)
```

### Nomenclatura de Archivos

Usa siempre el formato: `##-descripcion-corta.png`

- El número de dos dígitos (`01`, `02`, ...) garantiza que los archivos se ordenen correctamente
- Guiones en lugar de espacios o underscores
- Descripción en minúsculas y sin caracteres especiales

**Correcto**: `05-gke-workloads-running.png`
**Incorrecto**: `GKE Workloads Running.png`, `screenshot_5.png`, `captura.png`

---

## Resumen: Lista Completa de Capturas por Prioridad

### Capturas Críticas (hazlas sí o sí)

| # | Archivo | Por qué es crítica |
|---|---------|-------------------|
| 05 | `gcp-console/05-gke-workloads-running.png` | 6 pods running — el corazón del deployment |
| 17 | `terminal/17-kubectl-pods-running.png` | Evidencia técnica desde CLI |
| 23 | `terminal/23-health-checks-apis.png` | APIs respondiendo con modelo cargado |
| 26 | `aplicaciones/26-bankchurn-prediccion-real.png` | Predicción ML real en producción |
| 34 | `monitoring/34-grafana-dashboard.png` | Monitoreo en tiempo real |
| 37 | `monitoring/37-prometheus-targets-up.png` | Todos los targets monitoreados |
| 46 | `cicd/46-workflow-completado.png` | CI/CD pipeline funcionando |

### Capturas de Alto Impacto (muy recomendadas)

| # | Archivo | Valor para el portafolio |
|---|---------|--------------------------|
| 01 | `gcp-console/01-project-dashboard.png` | Muestra el proyecto GCP real |
| 08 | `gcp-console/08-gke-ingress-ip.png` | IP pública real asignada por GCP |
| 09 | `gcp-console/09-artifact-registry-imagenes.png` | 3 imágenes Docker en registry privado |
| 13 | `gcp-console/13-cloud-build-history.png` | Cloud Build como solución profesional |
| 22 | `terminal/22-terraform-outputs.png` | Infrastructure as Code demostrado |
| 25 | `aplicaciones/25-fastapi-swagger-bankchurn.png` | Documentación automática de API |
| 39 | `monitoring/39-mlflow-experiments.png` | Gestión profesional de experimentos ML |
| 43 | `cicd/43-github-secrets.png` | Seguridad en CI/CD |

### GIFs por Prioridad

| # | Archivo | Prioridad |
|---|---------|-----------|
| 01 | `gifs/01-demo-prediccion.gif` | **Crítica** — el demo más impactante |
| 02 | `gifs/02-gke-workloads.gif` | Alta — infraestructura visual |
| 03 | `gifs/03-grafana-monitoring.gif` | Alta — monitoreo en acción |
| 04 | `gifs/04-cicd-pipeline.gif` | Alta — automatización demostrada |
| 05 | `gifs/05-tres-apis-simultaneas.gif` | Media — impacto visual adicional |

---

## Script Automatizado de Recopilación de Evidencia de Terminal

Ejecuta este script para capturar toda la evidencia de terminal en un solo comando y guardarla como texto:

```bash
# Desde la raíz del proyecto
bash scripts/collect_evidence.sh | tee docs/evidence/terminal-evidence-$(date +%Y%m%d).txt
```

El archivo resultante (`terminal-evidence-YYYYMMDD.txt`) es evidencia adicional que puedes adjuntar al portafolio o referenciar en el README.
