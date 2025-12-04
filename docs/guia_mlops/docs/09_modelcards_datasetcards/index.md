# 09 — Model Cards & Dataset Cards

> **Tiempo estimado**: 1.5 días (12 horas)
> 
> **Prerrequisitos**: Módulos 01-08 completados

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Crear **Model Cards** completos y profesionales
2. ✅ Documentar **Dataset Cards** siguiendo estándares
3. ✅ Aplicar **buenas prácticas** de documentación ML
4. ✅ Usar **plantillas** reutilizables

---

## 📖 Contenido Teórico

### 1. ¿Qué es un Model Card?

Un **Model Card** es un documento estandarizado que describe:
- Propósito y uso previsto del modelo
- Datos de entrenamiento y métricas
- Limitaciones y sesgos conocidos
- Consideraciones éticas

> **Referencia**: [Model Cards for Model Reporting (Mitchell et al., 2019)](https://arxiv.org/abs/1810.03993)

### 2. ¿Qué es un Dataset Card?

Un **Dataset Card** documenta:
- Origen y composición de los datos
- Proceso de recolección
- Sesgos y limitaciones
- Consideraciones de privacidad

> **Referencia**: [Datasheets for Datasets (Gebru et al., 2021)](https://arxiv.org/abs/1803.09010)

---

### 3. Ejemplo: Model Card Completo

```markdown
# Model Card — Churn Predictor v1.0

## 1. Información General
- **Nombre**: churn_predictor
- **Versión**: 1.0.0
- **Fecha**: 2024-01-15
- **Autor**: Data Science Team

## 2. Propósito
Predecir la probabilidad de que un cliente abandone el servicio
en los próximos 30 días.

**Uso previsto**: Identificación proactiva de clientes en riesgo
para campañas de retención.

**Usos NO recomendados**:
- Decisiones automatizadas sin supervisión humana
- Segmentación para marketing sin consentimiento

## 3. Datos de Entrenamiento
- **Origen**: Base de datos interna de clientes
- **Período**: Enero 2022 - Diciembre 2023
- **Registros**: 100,000 (80% train, 10% val, 10% test)
- **Balance de clases**: 80% no-churn, 20% churn

## 4. Arquitectura
- **Algoritmo**: Random Forest Classifier
- **Pipeline**: StandardScaler → RandomForest
- **Hiperparámetros**:
  - n_estimators: 200
  - max_depth: 15
  - min_samples_leaf: 5

## 5. Métricas
| Métrica | Train | Val | Test |
|---------|-------|-----|------|
| Accuracy | 0.87 | 0.85 | 0.84 |
| AUC-ROC | 0.92 | 0.89 | 0.88 |
| F1 | 0.78 | 0.75 | 0.74 |
| Precision | 0.82 | 0.79 | 0.78 |
| Recall | 0.74 | 0.71 | 0.70 |

## 6. Sesgos y Limitaciones
### Sesgos identificados
- Menor recall en clientes menores de 25 años
- Performance reducida en clientes de regiones rurales

### Limitaciones
- Entrenado solo con datos de 2022-2023
- No considera factores macroeconómicos
- Requiere mínimo 3 meses de historial

## 7. Consideraciones Éticas
- No usar para decisiones que afecten términos de servicio
- Revisar predicciones antes de acciones de retención agresivas
- Monitorear sesgo demográfico regularmente

## 8. Monitoreo
- **Métricas**: accuracy, AUC, latencia, drift
- **Umbrales**: AUC < 0.80 → reentrenar
- **Frecuencia de revisión**: Mensual

## 9. Mantenimiento
- **Responsable**: data-science@company.com
- **Reentrenamiento**: Trimestral o por degradación
- **Última actualización**: 2024-01-15
```

---

### 4. Ejemplo: Dataset Card

```markdown
# Dataset Card — Customer Churn Dataset v1.0

## 1. Información General
- **Nombre**: customer_churn_dataset
- **Versión**: 1.0.0
- **Registros**: 100,000
- **Features**: 15
- **Formato**: Parquet

## 2. Composición
| Feature | Tipo | Descripción | Rango |
|---------|------|-------------|-------|
| customer_id | string | ID único | - |
| age | int | Edad del cliente | 18-100 |
| gender | string | Género | Male/Female |
| balance | float | Saldo de cuenta | 0-500000 |
| tenure | int | Meses como cliente | 0-120 |
| num_products | int | Productos contratados | 1-4 |
| is_active | bool | Cliente activo | True/False |
| churn | int | Variable target | 0/1 |

## 3. Recolección
- **Método**: Extracción de base de datos transaccional
- **Período**: 01/2022 - 12/2023
- **Frecuencia**: Snapshot mensual

## 4. Preprocesamiento
1. Eliminación de duplicados (0.5% del total)
2. Imputación de balance faltante (2%) con mediana
3. Normalización de formatos de fecha

## 5. Limitaciones y Sesgos
- **Sesgo geográfico**: 80% de clientes urbanos
- **Sesgo temporal**: No incluye período COVID-19 inicial
- **Datos faltantes**: 2% en balance, 0.5% en tenure

## 6. Consideraciones Éticas
- Datos anonimizados (sin PII)
- Consentimiento obtenido via términos de servicio
- No usar para identificación de individuos

## 7. Distribución
- **Licencia**: Propietaria - Solo uso interno
- **Acceso**: Restringido a equipo de Data Science
```

---

## 🔧 Mini-Proyecto: Documentar tu Modelo

### Objetivo

1. Crear Model Card para tu pipeline
2. Crear Dataset Card para tus datos
3. Usar las plantillas de `templates/`

### Estructura

```
work/09_modelcards_datasetcards/
├── docs/
│   ├── model_card.md
│   └── dataset_card.md
└── tests/
    └── test_docs.py  # Verificar que existen
```

### Criterios de Éxito

- [ ] Model Card con todas las secciones
- [ ] Dataset Card con descripción de features
- [ ] Sesgos y limitaciones documentados
- [ ] Información de contacto incluida

---

## ✅ Validación

```bash
make check-09
```

---

## ➡️ Siguiente Módulo

**[10 — Observabilidad & Monitoring](../10_observabilidad_monitoring/index.md)**

---

*Última actualización: 2024-12*
