# Model Card — {model_name}

> Plantilla basada en [Model Cards for Model Reporting (Mitchell et al., 2019)](https://arxiv.org/abs/1810.03993)

---

## 1. Información General

| Campo | Valor |
|:------|:------|
| **Nombre del modelo** | {model_name} |
| **Versión** | {version} |
| **Fecha de creación** | {YYYY-MM-DD} |
| **Autor(es)** | {nombre(s)} |
| **Licencia** | {MIT/Apache 2.0/Propietaria} |
| **Repositorio** | {URL del repo} |

---

## 2. Propósito del Modelo

### 2.1 Objetivo Principal
{Describir el objetivo principal del modelo en 2-3 oraciones}

### 2.2 Uso Previsto
- **Contexto de uso**: {Producción/Estimación/POC/Investigación}
- **Usuarios objetivo**: {Data Scientists/Analistas/Usuarios finales}
- **Decisiones que informa**: {Qué decisiones de negocio apoya}

### 2.3 Usos NO Recomendados
- {Caso de uso 1 donde NO usar el modelo}
- {Caso de uso 2 donde NO usar el modelo}

---

## 3. Datos de Entrenamiento

### 3.1 Fuente de Datos
| Campo | Valor |
|:------|:------|
| **Origen** | {Kaggle/Interno/API externa} |
| **Fecha de extracción** | {YYYY-MM-DD} |
| **Período cubierto** | {Desde-Hasta} |

### 3.2 Estadísticas del Dataset
| Métrica | Valor |
|:--------|:------|
| **Registros totales** | {n} |
| **Features** | {n} |
| **Target** | {nombre de la columna target} |
| **Split Train/Val/Test** | {70/15/15 o el que aplique} |

### 3.3 Preprocesamiento
1. {Paso 1: ej. Eliminación de duplicados}
2. {Paso 2: ej. Imputación de valores nulos}
3. {Paso 3: ej. Encoding de categorías}
4. {Paso 4: ej. Normalización/Estandarización}

---

## 4. Arquitectura del Modelo

### 4.1 Tipo de Modelo
- **Algoritmo base**: {RandomForest/XGBoost/LogisticRegression/etc.}
- **Framework**: {scikit-learn/TensorFlow/PyTorch}
- **Pipeline**: {Sí/No - si sí, describir componentes}

### 4.2 Hiperparámetros Principales
```yaml
# Hiperparámetros del modelo final
{hyperparameter_1}: {value}
{hyperparameter_2}: {value}
{hyperparameter_3}: {value}
```

### 4.3 Técnicas de Optimización
- **Búsqueda de hiperparámetros**: {GridSearch/RandomSearch/Bayesian/etc.}
- **Validación cruzada**: {k-fold, k={n}}
- **Criterio de selección**: {F1/AUC/RMSE/etc.}

---

## 5. Métricas de Rendimiento

### 5.1 Métrica Principal
| Métrica | Train | Validation | Test |
|:--------|:-----:|:----------:|:----:|
| **{Métrica principal}** | {value} | {value} | {value} |

### 5.2 Métricas Secundarias
| Métrica | Train | Validation | Test |
|:--------|:-----:|:----------:|:----:|
| Accuracy | {value} | {value} | {value} |
| Precision | {value} | {value} | {value} |
| Recall | {value} | {value} | {value} |
| F1-Score | {value} | {value} | {value} |
| AUC-ROC | {value} | {value} | {value} |

### 5.3 Matriz de Confusión (Test Set)
```
              Predicted
              Neg    Pos
Actual Neg    TN     FP
       Pos    FN     TP
```

---

## 6. Análisis de Sesgos y Fairness

### 6.1 Grupos Demográficos Analizados
| Grupo | Métrica | Valor |
|:------|:--------|:------|
| {Grupo 1} | {Métrica} | {value} |
| {Grupo 2} | {Métrica} | {value} |

### 6.2 Sesgos Conocidos
- **Sesgo identificado 1**: {Descripción y magnitud}
- **Sesgo identificado 2**: {Descripción y magnitud}

### 6.3 Mitigaciones Aplicadas
- {Mitigación 1: ej. Class weighting}
- {Mitigación 2: ej. SMOTE para oversampling}

---

## 7. Limitaciones

### 7.1 Limitaciones Técnicas
- {Limitación 1: ej. No funciona bien con datos fuera del rango de entrenamiento}
- {Limitación 2: ej. Requiere features específicos que pueden no estar disponibles}

### 7.2 Limitaciones Éticas
- {Limitación 1: ej. Puede perpetuar sesgos históricos en los datos}
- {Limitación 2: ej. No debe usarse para decisiones que afecten derechos fundamentales}

### 7.3 Casos donde NO Usar
- {Caso 1}
- {Caso 2}

---

## 8. Consideraciones de Despliegue

### 8.1 Requisitos de Infraestructura
| Recurso | Mínimo | Recomendado |
|:--------|:-------|:------------|
| CPU | {n} cores | {n} cores |
| RAM | {n} GB | {n} GB |
| Disco | {n} GB | {n} GB |
| GPU | {Sí/No} | {Sí/No} |

### 8.2 Latencia Esperada
- **Inferencia unitaria**: {n} ms
- **Batch (100 registros)**: {n} ms

### 8.3 Dependencias Críticas
```
{package_1}=={version}
{package_2}=={version}
{package_3}=={version}
```

---

## 9. Monitoreo y Mantenimiento

### 9.1 Métricas a Monitorear
- {Métrica 1: ej. Prediction drift}
- {Métrica 2: ej. Feature drift}
- {Métrica 3: ej. Latencia de inferencia}

### 9.2 Umbrales de Alerta
| Métrica | Umbral Warning | Umbral Crítico |
|:--------|:--------------:|:--------------:|
| {Métrica 1} | {value} | {value} |
| {Métrica 2} | {value} | {value} |

### 9.3 Plan de Reentrenamiento
- **Frecuencia**: {Mensual/Trimestral/Por evento}
- **Trigger**: {Degradación de métricas/Nuevo dataset/Cambio en distribución}
- **Responsable**: {Nombre/Equipo}

---

## 10. Versionamiento y Artefactos

### 10.1 Control de Versiones
| Item | Referencia |
|:-----|:-----------|
| **Código** | {commit hash o tag} |
| **Modelo serializado** | {ruta/modelo.pkl} |
| **MLflow Run ID** | {run_id} |
| **DVC Hash** | {hash} |

### 10.2 Artefactos Generados
- `{ruta}/model.pkl` — Modelo serializado
- `{ruta}/preprocessor.pkl` — Preprocesador
- `{ruta}/metrics.json` — Métricas de evaluación
- `{ruta}/feature_importance.csv` — Importancia de features

---

## 11. Changelog

| Versión | Fecha | Cambios |
|:--------|:------|:--------|
| {v1.0.0} | {YYYY-MM-DD} | Versión inicial |
| {v1.1.0} | {YYYY-MM-DD} | {Descripción del cambio} |

---

## 12. Contacto y Soporte

| Rol | Nombre | Contacto |
|:----|:-------|:---------|
| **Responsable técnico** | {nombre} | {email} |
| **Responsable de negocio** | {nombre} | {email} |
| **Soporte** | {equipo} | {email/slack} |

---

## Referencias

- [{Título de referencia 1}]({URL})
- [{Título de referencia 2}]({URL})

---

*Última actualización: {YYYY-MM-DD}*
