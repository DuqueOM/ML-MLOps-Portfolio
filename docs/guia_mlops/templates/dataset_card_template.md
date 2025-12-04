# Dataset Card — {dataset_name}

> Plantilla basada en [Datasheets for Datasets (Gebru et al., 2021)](https://arxiv.org/abs/1803.09010)

---

## 1. Información General

| Campo | Valor |
|:------|:------|
| **Nombre del dataset** | {dataset_name} |
| **Versión** | {version} |
| **Fecha de creación** | {YYYY-MM-DD} |
| **Autor(es)/Fuente** | {nombre(s) o fuente} |
| **Licencia** | {CC BY 4.0/MIT/Propietaria/etc.} |
| **URL** | {URL del dataset si es público} |

---

## 2. Motivación

### 2.1 ¿Por qué se creó este dataset?
{Explicar el propósito original del dataset en 2-3 oraciones}

### 2.2 ¿Quién lo creó y con qué financiamiento?
- **Creadores**: {Organización/Investigadores}
- **Financiamiento**: {Si aplica}

### 2.3 ¿Qué tareas soporta?
- {Tarea 1: ej. Clasificación binaria de churn}
- {Tarea 2: ej. Análisis exploratorio de clientes}

---

## 3. Composición

### 3.1 Estadísticas Generales
| Métrica | Valor |
|:--------|:------|
| **Registros totales** | {n} |
| **Features** | {n} |
| **Tamaño en disco** | {n} MB/GB |
| **Formato** | {CSV/Parquet/JSON} |

### 3.2 Descripción de Features

| Feature | Tipo | Descripción | Ejemplo |
|:--------|:-----|:------------|:--------|
| {feature_1} | {int/float/str/bool} | {descripción} | {valor ejemplo} |
| {feature_2} | {int/float/str/bool} | {descripción} | {valor ejemplo} |
| {feature_3} | {int/float/str/bool} | {descripción} | {valor ejemplo} |
| ... | ... | ... | ... |

### 3.3 Variable Target
| Campo | Valor |
|:------|:------|
| **Nombre** | {target_column} |
| **Tipo** | {Binaria/Multiclase/Continua} |
| **Distribución** | {ej. 80% clase 0, 20% clase 1} |

### 3.4 Valores Faltantes

| Feature | % Missing | Estrategia de imputación |
|:--------|:---------:|:-------------------------|
| {feature_1} | {n}% | {Media/Mediana/Moda/Eliminar} |
| {feature_2} | {n}% | {Media/Mediana/Moda/Eliminar} |

### 3.5 ¿Contiene datos sensibles?
- **PII (Información Personal Identificable)**: {Sí/No}
- **Datos financieros**: {Sí/No}
- **Datos de salud**: {Sí/No}
- **Otros datos sensibles**: {Describir si aplica}

---

## 4. Proceso de Recolección

### 4.1 ¿Cómo se recolectaron los datos?
{Describir el proceso de recolección: encuestas, logs, scraping, APIs, etc.}

### 4.2 Período de Recolección
| Campo | Valor |
|:------|:------|
| **Fecha inicio** | {YYYY-MM-DD} |
| **Fecha fin** | {YYYY-MM-DD} |
| **Frecuencia** | {Única/Diaria/Mensual/etc.} |

### 4.3 ¿Quién recolectó los datos?
{Organización, equipo, sistema automatizado}

### 4.4 Mecanismos de Validación
- {Validación 1: ej. Checks de integridad}
- {Validación 2: ej. Revisión manual de muestras}

---

## 5. Preprocesamiento y Limpieza

### 5.1 Transformaciones Aplicadas
1. {Paso 1: ej. Eliminación de duplicados}
2. {Paso 2: ej. Normalización de fechas}
3. {Paso 3: ej. Corrección de outliers}

### 5.2 ¿Se guardaron los datos crudos?
- **Ubicación**: {ruta o "No aplica"}
- **Acceso**: {Restringido/Público}

### 5.3 Software Usado
- {Herramienta 1: ej. pandas 2.0}
- {Herramienta 2: ej. Great Expectations}

---

## 6. Splits de Datos

### 6.1 División para ML
| Split | Registros | % | Estrategia |
|:------|:---------:|:-:|:-----------|
| Train | {n} | {%} | {Random/Temporal/Stratified} |
| Validation | {n} | {%} | {Random/Temporal/Stratified} |
| Test | {n} | {%} | {Random/Temporal/Stratified} |

### 6.2 Consideraciones Temporales
{Si los datos son temporales, describir cómo se manejó para evitar data leakage}

---

## 7. Usos del Dataset

### 7.1 Usos Recomendados
- {Uso 1: ej. Entrenamiento de modelos de clasificación}
- {Uso 2: ej. Análisis exploratorio}
- {Uso 3: ej. Benchmarking de algoritmos}

### 7.2 Usos NO Recomendados
- {Uso 1: ej. No usar para decisiones automatizadas sin supervisión humana}
- {Uso 2: ej. No usar para inferir características de poblaciones no representadas}

### 7.3 ¿Ha sido usado en otros trabajos?
| Trabajo | Tipo | Resultado |
|:--------|:-----|:----------|
| {Paper/Proyecto 1} | {Clasificación} | {AUC=0.85} |
| {Paper/Proyecto 2} | {Regresión} | {RMSE=1.2} |

---

## 8. Sesgos y Limitaciones

### 8.1 Sesgos Conocidos
| Sesgo | Descripción | Impacto |
|:------|:------------|:--------|
| {Sesgo 1} | {descripción} | {Alto/Medio/Bajo} |
| {Sesgo 2} | {descripción} | {Alto/Medio/Bajo} |

### 8.2 Limitaciones
- {Limitación 1: ej. Solo representa clientes de una región geográfica}
- {Limitación 2: ej. Datos de un período específico que puede no generalizar}

### 8.3 Grupos Subrepresentados
| Grupo | % en Dataset | % en Población Real |
|:------|:------------:|:-------------------:|
| {Grupo 1} | {n}% | {n}% |
| {Grupo 2} | {n}% | {n}% |

---

## 9. Consideraciones Éticas

### 9.1 ¿Contiene información que pueda identificar individuos?
{Sí/No - si sí, describir qué información y cómo se anonimizó}

### 9.2 ¿Hay consentimiento de los sujetos?
{Describir el proceso de consentimiento o por qué no aplica}

### 9.3 ¿Puede el uso del dataset causar daño?
{Describir potenciales daños y mitigaciones}

---

## 10. Mantenimiento

### 10.1 ¿Quién mantiene el dataset?
| Rol | Nombre | Contacto |
|:----|:-------|:---------|
| **Responsable** | {nombre} | {email} |
| **Soporte** | {equipo} | {email/slack} |

### 10.2 ¿Con qué frecuencia se actualiza?
- **Frecuencia**: {No se actualiza/Mensual/Trimestral/etc.}
- **Política de versiones**: {Semver/Fecha/etc.}

### 10.3 ¿Cómo reportar errores?
{Describir proceso: issue en GitHub, email, formulario}

---

## 11. Distribución

### 11.1 ¿Cómo se distribuye?
- **Formato**: {CSV/Parquet/API}
- **Ubicación**: {URL/S3/GCS}
- **Acceso**: {Público/Restringido/Con registro}

### 11.2 Licencia
- **Tipo**: {CC BY 4.0/MIT/etc.}
- **Restricciones**: {Uso comercial permitido/Solo investigación/etc.}

### 11.3 Cita Recomendada
```bibtex
@dataset{dataset_name,
  author = {{autor}},
  title = {{título}},
  year = {{año}},
  url = {{url}}
}
```

---

## 12. Changelog

| Versión | Fecha | Cambios |
|:--------|:------|:--------|
| {v1.0.0} | {YYYY-MM-DD} | Versión inicial |
| {v1.1.0} | {YYYY-MM-DD} | {Descripción del cambio} |

---

## Referencias

- [{Título de referencia 1}]({URL})
- [{Título de referencia 2}]({URL})

---

*Última actualización: {YYYY-MM-DD}*
