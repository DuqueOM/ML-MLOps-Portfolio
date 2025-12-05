# Talking Points – Portafolio ML/MLOps

Guía rápida para responder preguntas de entrevista sobre el portafolio y cada proyecto.

---

## 1. Mensaje global del portafolio

- **Rol objetivo**
  - Apunta a **Senior / Staff ML(MLOps) Engineer**.
  - Demuestra capacidad de diseñar y operar un **ecosistema multi‑servicio**.

- **Arquitectura global**
  - 3 proyectos: churn bancario, pricing vehículos, recomendación de planes telecom.
  - Librerías comunes y estructura homogénea de proyectos.
  - **MLflow centralizado**, **Docker + Kubernetes**, **Terraform** descrito para IaC.

- **CI/CD y calidad**
  - Un único workflow (`ci-mlops.yml`) con **matrices de Python** y **umbrales de cobertura por proyecto**.
  - Coverage ≈ **79%+** en BankChurn y ≈ **97%** en CarVision y TelecomAI.
  - Jobs de **integration tests**, build y push de imágenes a **GHCR**, escaneos de seguridad.

- **Observabilidad y operaciones**
  - APIs con **/metrics** vía Prometheus.
  - Integración con **Grafana** descrita en docs.
  - **RUNBOOK** y `OPERATIONS_PORTFOLIO.md` para procedimientos operativos.

- **Temas avanzados**
  - **Explainability** (SHAP + fallbacks) en BankChurn.
  - **Data drift monitoring** con Evidently + reporte y recomendaciones de **retrain**.
  - Diseño de **Feature Store** compartido como futura extensión.
  - Sección específica de **FinOps** (costes, right‑sizing, buenas prácticas de infra).

---

## 2. BankChurn‑Predictor – Talking Points

- **Problema de negocio**
  - Reducir **churn de clientes bancarios** identificando quién probablemente se marchará.
  - Prioriza recall y estabilidad del modelo; impacto directo en retención.

- **Modeling & ML**
  - Pipelines de sklearn con **preprocesamiento + modelo**.
  - **Ensemble** y técnicas de desbalanceo (SMOTE / resampling).
  - Métricas sólidas (AUC, F1) documentadas en Model Card.

- **MLOps / Plataforma**
  - **Alta cobertura de tests** (incluyendo rutas complejas como explainability).
  - Seguimiento de experimentos en **MLflow**.
  - Makefile con comandos estándar (`train`, `evaluate`, `check-drift`, `serve`, etc.).

- **Explainability**
  - Clase `ModelExplainer` con:
    - SHAP (Tree/KernelExplainer).
    - Fallbacks (coeficientes o `feature_importances_`).
    - Pruebas unitarias para cubrir escenarios sin SHAP o sin explainer.

- **Drift & Retrain**
  - Script de drift basado en **Evidently**.
  - Workflow `drift-bankchurn.yml`: genera reportes y recomendaciones.
  - Workflow `retrain-bankchurn.yml`: reentrena y registra modelos en MLflow, con opción de promoción.

- **Diferenciadores para entrevista**
  - Caso donde puedes hablar de:
    - trade‑offs de **automatizar o no** el retraining,
    - relación entre drift y **métricas de negocio**,
    - cómo integrar esto con un equipo real (alertas, SLOs).

---

## 3. CarVision‑Market‑Intelligence – Talking Points

- **Problema de negocio**
  - Predicción del **precio de vehículos** para soporte a decisiones de compra/venta.

- **Modeling & ML**
  - Modelos de regresión (ej. RandomForest) comparados con alternativas.
  - Métricas como **R²** y **RMSE** (documentadas en la Model Card).
  - Diseño de **FeatureEngineer** reutilizable como transformer sklearn.

- **Producto y UX**
  - **API de inferencia** para integrarse con otros sistemas.
  - **Dashboard Streamlit** con:
    - overview del dataset,
    - análisis de mercado,
    - métricas de modelo,
    - predictor interactivo.

- **MLOps / Calidad**
  - Coverage ≈ **97%**.
  - Integración con CI unificada, MLflow, Docker, GHCR.
  - Buen manejo de configuración, logging y estructura de paquetes.

- **Diferenciadores para entrevista**
  - Ejemplo claro de pasar de un **modelo en notebook** a un **producto utilizable**.
  - Permite hablar de experiencia colaborando con negocio (dashboard, explicaciones visuales).

---

## 4. TelecomAI‑Customer‑Intelligence – Talking Points

- **Problema de negocio**
  - **Recomendar el plan de telecom óptimo** (Standard vs Ultra) según uso.
  - Minimiza tanto la fuga por sobre‑coste como la pérdida de ingresos por infra‑venta.

- **Modeling & ML**
  - Modelos tipo GradientBoosting / RandomForest.
  - Métricas (documentadas y fáciles de citar):
    - **AUC‑ROC ≈ 0.84**
    - **Accuracy ≈ 82%**
    - **F1 ≈ 0.63**
    - **Cobertura de tests ≈ 97%**

- **Servicio y operaciones**
  - API **FastAPI** con:
    - `/predict` (plan recomendado + probabilidad),
    - `/health` (incluye estado **degraded** para escenarios sin modelo).
  - Exposición de métricas en `/metrics` para Prometheus.
  - Arquitectura y operaciones documentadas en `ARCHITECTURE.md` y ONE‑PAGER.

- **MLOps / Plataforma**
  - Comparte CI, MLflow, Docker, GHCR del resto.
  - Casos de test e2e para validar comportamiento end‑to‑end.

- **Diferenciadores para entrevista**
  - Excelente ejemplo de **microservicio ML** con:
    - health checks realistas,
    - alta cobertura,
    - integración en un ecosistema mayor.

---

## 5. Preguntas frecuentes y ángulos de respuesta

- **“¿En qué se diferencia esto de un proyecto típico de Kaggle?”**
  - Enfatizar:
    - sistemas multi‑servicio,
    - CI/CD, cobertura, observabilidad,
    - documentación de arquitectura y operaciones.
- **“¿Qué harías si tuvieras más tiempo?”**
  - Implementar el **Feature Store real**, extender drift monitoring a los 3 proyectos,
    añadir **auth, RBAC y multi‑tenant** en las APIs, y pipelines de datos en streaming.
- **“¿Cómo aplicarías esto en nuestra empresa?”**
  - Responder con:
    - estandarizar pipelines y CI/CD,
    - mejorar visibilidad de modelos en producción (logs, métricas, alertas),
    - diseñar **runbooks** y **playbooks de incidentes**,
    - definir una estrategia de **FinOps** básica para workloads de ML.

---

## 6. Uso recomendado de esta guía

- Imprimir o tener abierta esta hoja durante simulacros de entrevista.
- Practicar el **speech de 5–7 minutos** del archivo [APENDICE_A_SPEECH_PORTAFOLIO.md](APENDICE_A_SPEECH_PORTAFOLIO.md).
- Usar estas bullets para responder preguntas de seguimiento sin perder el mensaje principal:
  - soluciones de negocio,
  - calidad técnica,
  - visión de plataforma.

---

<div align="center">

**Apéndice B — Material de Preparación para Entrevistas**

[← Apéndice A: Speech](APENDICE_A_SPEECH_PORTAFOLIO.md) | [Volver al Índice](00_INDICE.md)

</div>
