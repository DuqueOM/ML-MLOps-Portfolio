# 📁 Plantillas — Guía MLOps v2

> Plantillas reutilizables para proyectos ML/MLOps profesionales

---

## 📋 Índice de Plantillas

### Documentación ML

| Plantilla | Descripción | Uso |
|:----------|:------------|:----|
| [Model Card](model_card_template.md) | Documentación completa de un modelo ML | Obligatorio para cada modelo en producción |
| [Dataset Card](dataset_card_template.md) | Documentación de datasets | Obligatorio para cada dataset |

### CI/CD

| Plantilla | Descripción | Uso |
|:----------|:------------|:----|
| [GitHub Actions CI](ci_github_actions.yml) | Pipeline CI/CD completo | Base para proyectos nuevos |
| [CI Template (básico)](ci_template.yml) | Versión mínima de CI | Quick start |

### Infraestructura

| Plantilla | Descripción | Uso |
|:----------|:------------|:----|
| [Dockerfile](Dockerfile) | Multi-stage para ML APIs | Base para containerización |
| [Dockerfile Template](Dockerfile_template) | Versión simplificada | Quick start |
| [docker-compose.yml](docker-compose.yml) | Stack completo con servicios | Desarrollo local |

### Proyecto

| Plantilla | Descripción | Uso |
|:----------|:------------|:----|
| [pyproject.toml](pyproject_template.toml) | Configuración de paquete Python | Base para proyectos nuevos |
| [README Template](README_TEMPLATE.md) | README profesional | Todos los proyectos |
| [Makefile](Makefile) | Automatización de tareas | Base para proyectos nuevos |

### Scripts

| Plantilla | Descripción | Uso |
|:----------|:------------|:----|
| [run_demo.sh](run_demo.sh) | Script de demo del proyecto | Presentaciones |

---

## 🎯 Cómo Usar las Plantillas

### 1. Copiar la plantilla

```bash
# Copiar Model Card a tu proyecto
cp templates/model_card_template.md docs/model_card.md

# Copiar CI workflow
cp templates/ci_github_actions.yml .github/workflows/ci.yml
```

### 2. Personalizar

Reemplaza los placeholders `{placeholder}` con los valores de tu proyecto.

### 3. Validar

```bash
# Verificar sintaxis YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# Verificar Markdown
markdownlint docs/model_card.md
```

---

## 📝 Convenciones

### Placeholders

| Formato | Ejemplo | Descripción |
|:--------|:--------|:------------|
| `{nombre}` | `{model_name}` | Campo obligatorio |
| `{ej. valor}` | `{ej. RandomForest}` | Incluye ejemplo |
| `{YYYY-MM-DD}` | `{2024-01-15}` | Formato de fecha |

### Secciones Opcionales

Las secciones marcadas con `<!-- OPCIONAL -->` pueden eliminarse si no aplican.

---

## ✅ Checklist de Uso

- [ ] Copié la plantilla correcta
- [ ] Reemplacé todos los `{placeholders}`
- [ ] Eliminé secciones que no aplican
- [ ] Validé la sintaxis (YAML/Markdown)
- [ ] Revisé que tenga sentido para mi proyecto

---

## 🔗 Referencias

- [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) - Mitchell et al., 2019
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010) - Gebru et al., 2021
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

## 📚 Módulos Relacionados

| Plantilla | Módulo |
|-----------|--------|
| pyproject, README, Makefile | [03_ESTRUCTURA_PROYECTO.md](../03_ESTRUCTURA_PROYECTO.md) |
| CI workflows | [12_CI_CD.md](../12_CI_CD.md) |
| Dockerfile, docker-compose | [13_DOCKER.md](../13_DOCKER.md) |
| Model Card, Dataset Card | [19_DOCUMENTACION.md](../19_DOCUMENTACION.md) |

---

<div align="center">

[← Índice Principal](../00_INDICE.md) | [PLANTILLAS.md](../PLANTILLAS.md)

</div>
