# 00 — Introducción a la Guía MLOps v2

> **Tiempo estimado**: 0.5 días (4 horas)
> 
> **Prerrequisitos**: Python básico, Git elemental, comodidad con terminal

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Entender el **objetivo final** del curso (portafolio ML reproducido)
2. ✅ Configurar tu **entorno de desarrollo** correctamente
3. ✅ Navegar el **mapa guía → repo** sin confusión
4. ✅ Ejecutar el **setup inicial** con éxito

---

## 📖 ¿Qué es esta Guía?

Esta guía es un **curso end-to-end** diseñado para enseñarte, paso a paso, cómo construir un portafolio ML/MLOps profesional desde cero. Al finalizar, habrás reproducido localmente los 3 proyectos del repositorio `ML-MLOps-Portfolio`:

| Proyecto | Tipo | Descripción |
|:---------|:-----|:------------|
| **BankChurn-Predictor** | Clasificación binaria | Predicción de abandono de clientes |
| **CarVision-Market-Intelligence** | Regresión | Predicción de precios de autos |
| **TelecomAI-Customer-Intelligence** | Clasificación multiclase | Segmentación de clientes |

### ¿Para quién es?

- **Perfil de entrada**: Conocimientos básicos de Python (funciones, clases, módulos)
- **Perfil de salida**: Capacidad de construir y desplegar sistemas ML production-ready

### ¿Qué NO es?

- ❌ No es un curso de Machine Learning teórico
- ❌ No es solo teoría sin práctica
- ❌ No requiere conocimientos previos de MLOps

---

## 🗺️ Mapa Guía → Repositorio

Esta tabla muestra la correspondencia entre cada módulo de la guía y los archivos/directorios del repositorio objetivo:

| Módulo | Concepto | Archivos del Repo |
|:-------|:---------|:------------------|
| 00 | Introducción | `README.md`, estructura general |
| 01 | Python Moderno | `src/*/config.py`, type hints en todo el código |
| 02 | Ingeniería de Datos | `src/*/data.py`, `data/` |
| 03 | Feature Engineering | `src/*/features.py`, `FeatureEngineer` |
| 04 | Modelado | `src/*/train.py`, `src/*/model.py` |
| 05 | MLflow & DVC | `mlruns/`, `dvc.yaml`, `.dvc/` |
| 06 | Despliegue API | `app/fastapi_app.py`, `Dockerfile` |
| 07 | Dashboard | `app/streamlit_app.py` |
| 08 | CI/CD & Testing | `.github/workflows/`, `tests/` |
| 09 | Model & Dataset Cards | `docs/model_card.md`, `docs/dataset_card.md` |
| 10 | Observabilidad | `src/*/logging.py`, métricas |
| 11 | Mantenimiento | `MAINTENANCE.md`, runbooks |

---

## 💻 Requerimientos del Sistema

### Hardware Mínimo

| Recurso | Mínimo | Recomendado |
|:--------|:-------|:------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 8 GB | 16 GB |
| **Disco** | 10 GB libres | 20 GB libres |
| **GPU** | No requerida | No requerida |

### Software Requerido

| Software | Versión | Verificar con |
|:---------|:--------|:--------------|
| **Python** | 3.10+ | `python --version` |
| **Git** | 2.30+ | `git --version` |
| **pip** | 21.0+ | `pip --version` |
| **Make** (opcional) | 4.0+ | `make --version` |
| **Docker** (opcional) | 20.10+ | `docker --version` |

### Editor/IDE Recomendado

- **VS Code** con extensiones:
  - Python
  - Pylance
  - GitLens
  - Docker
  - YAML

---

## 🚀 Setup Inicial

### Paso 1: Clonar el repositorio

```bash
# Clonar el repositorio completo
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Navegar a la guía
cd docs/guia_mlops
```

### Paso 2: Crear entorno virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Linux/Mac)
source .venv/bin/activate

# Activar (Windows)
.venv\Scripts\activate
```

### Paso 3: Instalar dependencias

```bash
# Instalar dependencias de la guía
pip install -r requirements.txt
```

### Paso 4: Verificar instalación

```bash
# Verificar que todo funciona
python -c "import pandas; import sklearn; import mlflow; print('OK!')"

# Verificar MkDocs
mkdocs --version
```

### Paso 5: (Opcional) Servir documentación

```bash
# Iniciar servidor de documentación local
mkdocs serve

# Abrir en navegador: http://localhost:8000
```

---

## 📁 Estructura de la Guía

```
guia_mlops/
├── docs/                          # Módulos del curso
│   ├── 00_introduccion/           # ← Estás aquí
│   ├── 01_python_moderno/
│   ├── 02_ingenieria_datos/
│   ├── 03_feature_engineering/
│   ├── 04_modelado/
│   ├── 05_mlflow_dvc/
│   ├── 06_despliegue_api/
│   ├── 07_dashboard/
│   ├── 08_ci_cd_testing/
│   ├── 09_modelcards_datasetcards/
│   ├── 10_observabilidad_monitoring/
│   ├── 11_mantenimiento_auditoria/
│   ├── assets/                    # Imágenes y recursos
│   └── notebooks/                 # Notebooks de práctica
├── templates/                     # Plantillas reutilizables
├── work/                          # Tu espacio de trabajo
├── scripts/                       # Scripts de utilidad
├── mkdocs.yml                     # Configuración de docs
├── Makefile_v2                    # Automatización
├── requirements.txt               # Dependencias
└── SYLLABUS.md                    # Programa del curso
```

---

## 🎓 Cómo Usar Esta Guía

### Flujo de Trabajo Recomendado

```
┌─────────────────────────────────────────────────────────────────┐
│  1. LEER el módulo (docs/XX_modulo/index.md)                    │
│     ↓                                                            │
│  2. PRACTICAR el mini-proyecto en work/                          │
│     ↓                                                            │
│  3. VALIDAR con make check-XX                                    │
│     ↓                                                            │
│  4. COMPARAR con solutions/ si te atascas                        │
│     ↓                                                            │
│  5. CONTINUAR al siguiente módulo                                │
└─────────────────────────────────────────────────────────────────┘
```

### Convenciones de la Guía

| Símbolo | Significado |
|:--------|:------------|
| 💡 | Tip o consejo práctico |
| ⚠️ | Advertencia importante |
| ❌ | Anti-patrón o error común |
| ✅ | Buena práctica |
| 🔧 | Ejercicio práctico |
| 📝 | Nota o aclaración |
| 🎯 | Objetivo de aprendizaje |

### Comandos Make Principales

```bash
# Setup inicial
make setup

# Validar módulo específico
make check-01  # Valida módulo 01
make check-02  # Valida módulo 02
# ... etc

# Validar todos los módulos
make check-all

# Servir documentación
make serve-docs

# Limpiar archivos generados
make clean
```

---

## 📊 Rúbrica de Evaluación

Cada mini-proyecto se evalúa con la siguiente rúbrica (100 puntos):

| Criterio | Puntos | Descripción |
|:---------|:------:|:------------|
| **Funcionalidad** | 40 | Pasa tests, produce outputs esperados |
| **Calidad del código** | 20 | Linters, type hints, modularidad |
| **Documentación** | 15 | README, docstrings |
| **Reproducibilidad** | 15 | make, lockfile, ejecutable |
| **Tests** | 10 | Cobertura mínima |

**Nota mínima aprobatoria**: 70/100 por módulo

---

## 🎯 Ejercicio Práctico: Setup Completo

### Objetivo

Configurar completamente tu entorno de desarrollo y verificar que todo funciona.

### Instrucciones

1. **Clona** el repositorio siguiendo los pasos de arriba
2. **Crea** el entorno virtual
3. **Instala** las dependencias
4. **Ejecuta** las verificaciones:

```bash
# Verificar Python
python --version  # Debe ser 3.10+

# Verificar dependencias instaladas
python -c "
import pandas as pd
import numpy as np
import sklearn
import mlflow
import fastapi
import streamlit
print('Todas las dependencias instaladas correctamente!')
print(f'pandas: {pd.__version__}')
print(f'numpy: {np.__version__}')
print(f'sklearn: {sklearn.__version__}')
print(f'mlflow: {mlflow.__version__}')
"

# Verificar estructura
ls -la docs/
```

### Criterios de Éxito

- [ ] Python 3.10+ instalado y funcionando
- [ ] Entorno virtual creado y activado
- [ ] Todas las dependencias instaladas sin errores
- [ ] Documentación sirviéndose en localhost:8000

---

## ❓ Preguntas Frecuentes

### ¿Necesito Docker desde el inicio?

No. Docker es opcional y se introduce en el módulo 06. Para los primeros módulos, solo necesitas Python y Git.

### ¿Puedo usar Conda en lugar de venv?

Sí, pero los ejemplos usan venv. Si usas Conda, ajusta los comandos según corresponda.

### ¿Qué hago si un test falla?

1. Lee el mensaje de error completo
2. Revisa que seguiste todos los pasos
3. Consulta la carpeta `solutions/` del módulo
4. Si persiste, revisa los módulos anteriores

### ¿Puedo saltar módulos?

No recomendado. Cada módulo construye sobre el anterior. Si tienes experiencia previa, puedes ir más rápido pero revisa cada módulo.

---

## ➡️ Siguiente Paso

Una vez completado el setup, continúa con:

**[Módulo 01 — Python Moderno](../01_python_moderno/index.md)**

---

## 📚 Recursos Adicionales

- [Documentación oficial de Python](https://docs.python.org/3/)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [VS Code Python Tutorial](https://code.visualstudio.com/docs/python/python-tutorial)

---

*Última actualización: 2024-12*
