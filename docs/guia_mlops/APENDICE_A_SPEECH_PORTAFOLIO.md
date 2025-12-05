# Speech de entrevista – Portafolio ML/MLOps (5–7 minutos)

## 0. Objetivo del speech

Este guion está pensado para una respuesta de **“Cuéntame de tu portafolio / experiencia en ML/MLOps”** en **5–7 minutos**.  
Te posiciona explícitamente como **Senior / Staff ML(MLOps) Engineer** que diseña y opera **sistemas ML multi‑proyecto**.

---

## 1. Apertura (0:00 – 1:00)

**Mensaje clave:** Quién eres, qué rol buscas, y una frase muy clara sobre el portafolio.

- Preséntate con rol y foco:
  - "Soy *Daniel Duque*, ML/MLOps Engineer, y mi foco es llevar modelos de ML a producción con buenas prácticas de ingeniería de software, observabilidad y automatización."
- En una frase, resume el portfolio:
  - "Para demostrarlo construí un portafolio compuesto por **3 proyectos ML de negocio reales** (churn bancario, pricing de vehículos y recomendación de planes de telecom), todos integrados en un **ecosistema MLOps unificado**."
- Aclara el nivel que quieres transmitir:
  - "Más que tres demos aisladas, es **un sistema multi‑servicio**, con CI/CD compartido, MLflow centralizado, Docker/Kubernetes, monitoreo con Prometheus/Grafana y workflows de drift + retraining."

---

## 2. Vista global del portfolio (1:00 – 2:30)

**Mensaje clave:** No son proyectos sueltos; hay una plataforma y decisiones de arquitectura.

- Estructura:
  - "El repo tiene tres servicios: **BankChurn‑Predictor**, **CarVision‑Market‑Intelligence** y **TelecomAI‑Customer‑Intelligence**."
  - "Comparten librerías comunes, una **pipeline de CI unificada** en GitHub Actions y un **stack de observabilidad e infraestructura** coherente."
- CI/CD:
  - "La CI se define en un único workflow con **matrices de Python** y **umbrales de cobertura por proyecto** (≈79–97%), integración con **GHCR** para las imágenes Docker y **tests de integración** con Docker Compose."
- Plataforma MLOps:
  - "Uso **MLflow** como capa de experiment tracking y model registry común."
  - "Para producción describo despliegue con **Docker + Kubernetes**, IaC con **Terraform**, y monitoreo con **Prometheus + Grafana**."
- Temas avanzados:
  - "Incluí **explainability con SHAP**, **data drift monitoring con Evidently** y un workflow de **retrain orquestado por GitHub Actions** en el caso de churn."
  - "También documento **FinOps** y el diseño de un **Feature Store** compartido como extensiones futuras."

Frase puente:

> "Sobre esa plataforma, cada proyecto resuelve un problema de negocio distinto. Te resumo cada uno muy rápido."

---

## 3. Proyecto 1 – BankChurn‑Predictor (2:30 – 3:45)

**Mensaje clave:** Proyecto “estrella” de churn con MLOps profundo.

- Problema y valor:
  - "BankChurn‑Predictor es un sistema para **predecir churn de clientes bancarios**, priorizando recall para reducir fuga de clientes."
- Modelado:
  - "Uso un **ensemble** con modelos clásicos y técnicas de balanceo de clases, con métricas sólidas documentadas en la *Model Card*."
  - "Todo está encapsulado en pipelines de sklearn para evitar discrepancias entre entrenamiento y serving."
- MLOps:
  - "Tiene **alta cobertura de tests**, incluyendo rutas complejas como `explainability.py` con SHAP y fallbacks cuando la librería no está disponible."
  - "Está integrado con **MLflow** para registrar experimentos, métricas y versiones de modelo."
- Explainability:
  - "Implementé una clase `ModelExplainer` basada en **SHAP** con mecanismos de fallback (coeficientes / feature_importances) y pruebas unitarias que cubren esos caminos."
- Drift + Retrain:
  - "Para este proyecto añadí un flujo de **data drift monitoring** con **Evidently** que genera reportes y, de forma manual controlada, puede disparar el workflow de **retrain** en GitHub Actions."
- Documentación:
  - "El proyecto tiene **ARCHITECTURE.md**, README muy detallado y Model Card, lo que permite entender decisiones de diseño, trade‑offs y roadmap (Feature Store, explainability avanzada, etc.)."

Frase de cierre:

> "BankChurn muestra mi capacidad de diseñar un sistema ML **end‑to‑end** con explainability, drift y retraining, no sólo un modelo."

---

## 4. Proyecto 2 – CarVision‑Market‑Intelligence (3:45 – 5:00)

**Mensaje clave:** Pricing de vehículos con API + dashboard y foco fuerte en experiencia de usuario y calidad de código.

- Problema:
  - "CarVision es un proyecto de **pricing de vehículos**: predice el precio de mercado a partir de características del coche, ayudando a tomar decisiones de compra/venta."
- Modelado:
  - "Uso modelos de regresión (por ejemplo, RandomForest Regressor) comparados con alternativas lineales, con métricas como **R²** y **RMSE** documentadas."
  - "La parte interesante es el diseño de un **FeatureEngineer** como transformer de sklearn para mantener alineados entrenamiento y serving."
- Producto / UX:
  - "Además de la **API de inferencia**, hay un **dashboard en Streamlit** con 4 secciones (overview, análisis de mercado, métricas del modelo y predictor interactivo), pensado para stakeholders no técnicos."
- MLOps:
  - "La cobertura de tests es muy alta (alrededor del 97%), y se integra en la misma CI compartida usando MLflow, Docker, GHCR, etc."
- Valor:
  - "Este proyecto demuestra que puedo llevar un caso de uso tabular a un producto usable con API, UI, tracking de experimentos y buenas prácticas de ingeniería."

Frase de cierre:

> "CarVision refuerza mi perfil **producto + plataforma**, mostrando cómo empaqueto modelos en APIs y dashboards operables."

---

## 5. Proyecto 3 – TelecomAI‑Customer‑Intelligence (5:00 – 6:00)

**Mensaje clave:** Recomendador de planes con métricas claras y buen diseño operando como microservicio robusto.

- Problema:
  - "TelecomAI es un sistema de **recomendación de planes de telecom** (Standard vs Ultra) basado en el comportamiento de uso."
- Métricas:
  - "El modelo consigue aproximadamente **0.84 de AUC‑ROC**, **82% de accuracy** y **0.63 de F1**, con una **cobertura de tests ~97%**."
- Servicio:
  - "Está implementado como una **API FastAPI** con endpoints `/predict` y `/health`, y con **métricas de Prometheus** expuestas en `/metrics` para observabilidad."
  - "El health check maneja estados *degraded* (por ejemplo cuando el modelo no está disponible en CI), lo que es muy realista a nivel de producción."
- Plataforma:
  - "Comparte el mismo pipeline de CI/CD, prácticas de Docker y experiment tracking del resto del portfolio."
- Documentación:
  - "Tiene un **ONE‑PAGER de negocio**, README completo, Model Card y un **ARCHITECTURE.md** alineado con los otros dos proyectos."

Frase de cierre:

> "TelecomAI es un microservicio ML muy limpio y con excelente coverage, que demuestra consistencia en mis patrones de diseño."

---

## 6. Cierre (6:00 – 7:00)

**Mensaje clave:** Reforzar nivel, madurez y cómo esto se traduce en valor para el equipo.

- Nivel:
  - "En conjunto, el portafolio está diseñado para demostrar un nivel **Senior / Staff**: no sólo modelos, sino **sistemas completos**, con CI/CD multi‑proyecto, observabilidad, workflows de retraining y documentación estilo empresa."
- Aprendizajes:
  - "En el proceso he trabajado temas como explainability, drift, diseño de Feature Store, y **FinOps** para estimar y optimizar costes en cloud."
- Cómo encaja en la empresa:
  - "Mi objetivo es traer este enfoque al equipo: **estandarizar pipelines**, mejorar **confiabilidad y observabilidad** de los modelos en producción y reducir el tiempo desde prototipo hasta valor en negocio."

Cierre corto:

> "Si queréis, puedo profundizar en cualquiera de los tres proyectos, en la parte de CI/CD, en explainability o en cómo diseñaría el Feature Store y el coste en vuestra infraestructura actual."

---

<div align="center">

**Apéndice A — Material de Preparación para Entrevistas**

[← Volver al Índice](00_INDICE.md) | [Apéndice B: Talking Points →](APENDICE_B_TALKING_POINTS.md)

</div>
