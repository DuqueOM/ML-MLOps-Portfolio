<div align="center">

# 🚀 Portafolio de ML/MLOps — sistemas de ML en producción

**3 servicios de ML · desplegados en GKE + EKS en marzo de 2026 y luego apagados para ahorrar costos · 19 ADRs · más de 395 pruebas**

[English](README.md) · Español

[![Portafolio](https://img.shields.io/badge/Portafolio-Sitio_web-blue?style=for-the-badge)](https://duqueom.github.io/ML-MLOps-Portfolio/)
[![YouTube](https://img.shields.io/badge/Video_demo-YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/7dFFqq2ROPw)

</div>

> **Esta página es un resumen en español para reclutadores.** El detalle técnico (arquitectura, métricas, ADRs,
> evidencia del despliegue y guía de inicio rápido) está en inglés, en el [README principal](README.md).

## Qué es

Tres servicios de machine learning en un mismo repositorio: predicción de abandono de clientes (BankChurn), análisis
de sentimiento financiero (NLPInsight) y pronóstico de demanda de taxis (ChicagoTaxi). Cada servicio se sirve con
FastAPI, Docker y Kubernetes, con Terraform, CI/CD en GitHub Actions, MLflow y monitoreo con Prometheus y Grafana.

Es un proyecto de MLOps: llevar modelos de machine learning a producción y operarlos, con pruebas automatizadas,
despliegue, monitoreo y decisiones documentadas.

## Estado

- Desplegados en GKE (Google Cloud) y EKS (AWS) en marzo de 2026 y luego apagados para ahorrar costos: con las dos
  nubes encendidas cuestan cerca de 180-220 USD al mes.
- El código, las más de 395 pruebas automatizadas, la infraestructura como código (Terraform) y la evidencia de ese
  periodo (pruebas de carga, capturas de pantalla y reportes de incidentes) siguen públicos.
- Se puede volver a desplegar en cerca de 1 hora. Detalle: [PORTFOLIO_STATUS.md](PORTFOLIO_STATUS.md) (en inglés).

## Tres problemas que encontré y resolví en pruebas de carga en mis propios clústeres

| Problema | Causa | Solución | Resultado |
|----------|-------|----------|-----------|
| 81% de errores bajo carga | Varios workers de uvicorn compitiendo por la misma CPU dentro de Kubernetes | Inferencia con asyncio y un pool de hilos | De 81% a 0% de errores con la mitad de CPU (2000m → 1000m) |
| SHAP (la explicación de cada predicción) devolvía solo ceros | TreeExplainer no funciona con StackingClassifier | KernelExplainer, con valores en las 10 variables originales | Explicaciones reales en producción |
| El autoescalador (HPA) nunca reducía réplicas | HPA por memoria con un modelo que ocupa memoria fija | Escalar solo por CPU | De 3 a 1 pods en 8 minutos |

Cada incidente tiene su reporte con la causa, la solución y los números (en inglés):
[reportes de incidentes](https://duqueom.github.io/ML-MLOps-Portfolio/technical-evidence/).

## Enlaces

- [Sitio del portafolio](https://duqueom.github.io/ML-MLOps-Portfolio/) (en inglés)
- [Video demo de 3 minutos](https://youtu.be/7dFFqq2ROPw)
- [Decisiones de arquitectura: 19 ADRs](docs/decisions/) (en inglés)
- [Historial de cambios](CHANGELOG.md) (en inglés)
- [Mis otros proyectos](https://github.com/DuqueOM): un agente de atención al cliente para WhatsApp con tool calling
  (en desarrollo) y `read_aloud`, una app de texto a voz con una voz que ajusté con LoRA

## Autor

**Duque Ortega Mutis** · Junior AI Engineer · apps con LLM y agentes · ML en producción

Antes de la tecnología dirigí mis propios negocios durante 14 años. Eso me enseñó a medir antes de suponer, a escribir
las decisiones y a mantener visibles los costos; este repositorio es donde lo apliqué a sistemas de ML. Diseñé la
arquitectura y tomé las decisiones (19 ADRs); los agentes de programación con IA (Windsurf Cascade en ese momento) me ayudaron a construirlo
más rápido. El diseño del sistema, las decisiones y las soluciones de los incidentes son míos.

Busco puestos junior de AI Engineer, ML Engineer o MLOps · Remoto o Ciudad de México · Español (nativo), inglés (B1).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/duqueom)
[![GitHub](https://img.shields.io/badge/GitHub-Seguir-181717?style=flat&logo=github)](https://github.com/DuqueOM)
[![Correo](https://img.shields.io/badge/Correo-Contacto-EA4335?style=flat&logo=gmail)](mailto:DuqueOrtegaMutis@gmail.com)
