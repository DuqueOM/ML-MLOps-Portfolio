# ════════════════════════════════════════════════════════════════════════════════
# MÓDULO 21: GLOSARIO COMPLETO MLOps
# Diccionario Exhaustivo de A-Z con Explicaciones Profundas, Analogías y Ejemplos
# Guía MLOps v5.0: Senior Edition | DuqueOM | Diciembre 2025
# ════════════════════════════════════════════════════════════════════════════════

<div align="center">

# 📖 MÓDULO 21: Glosario Completo MLOps

**Diccionario Exhaustivo con Explicaciones Profundas, Analogías y Ejemplos del Portafolio**

*"Dominar el vocabulario técnico es el primer paso para comunicarte como Senior."*

| Nivel        | Duración   |
|:------------:|:----------:|
| 📚 Referencia | Consulta continua |

</div>

---

## 📚 Introducción

Este glosario define **todos** los términos técnicos utilizados en la Guía MLOps v5.0 y en los proyectos del portafolio (BankChurn, CarVision, TelecomAI). Cada término incluye:

- **Definición técnica** precisa y completa
- **Explicación conceptual** para entender el "por qué"
- **Analogía desarrollada** para facilitar comprensión intuitiva
- **Ejemplo del portafolio** cuando aplica
- **Términos relacionados** para profundizar

### Cómo usar este glosario

1. **Primera lectura**: Lee las analogías para captar la intuición
2. **Profundización**: Lee la explicación conceptual completa
3. **Aplicación**: Revisa los ejemplos del portafolio
4. **Conexión**: Explora los términos relacionados

---

## A

### Accuracy (Exactitud)

**Definición técnica:** Métrica de clasificación que mide el porcentaje de predicciones correctas sobre el total. Se calcula como `(TP + TN) / (TP + TN + FP + FN)` donde TP=True Positives, TN=True Negatives, FP=False Positives, FN=False Negatives.

**Explicación conceptual:** Accuracy responde a la pregunta "¿qué porcentaje de mis predicciones fueron correctas?". Es intuitiva pero **peligrosamente engañosa** con clases desbalanceadas. Si el 95% de tus clientes NO abandonan (no-churn), un modelo que siempre predice "no-churn" tiene 95% accuracy pero es completamente inútil para detectar churners.

**Analogía desarrollada:** Imagina un arquero que dispara 100 flechas a un blanco. Si 85 dan en el blanco, su accuracy es 85%. Pero si el blanco ocupa el 95% del muro, incluso disparando con los ojos cerrados acertarías 95%. Por eso en ML usamos métricas adicionales (Precision, Recall) que nos dicen *qué tan bien* acertamos a cada zona específica.

**En el portafolio:** BankChurn tiene ~20% de churners. Un modelo "dummy" que siempre predice "no-churn" tendría 80% accuracy. Por eso usamos ROC-AUC (86%) y Recall como métricas principales.

**Relacionados:** Precision, Recall, F1 Score, ROC-AUC, Class Imbalance

---

### ADR (Architecture Decision Record)

**Definición técnica:** Documento estructurado que registra una decisión de arquitectura significativa junto con su contexto, las alternativas consideradas, la decisión tomada y sus consecuencias (positivas y negativas).

**Explicación conceptual:** En proyectos de software, tomamos cientos de decisiones técnicas. Meses después, nadie recuerda *por qué* se eligió PostgreSQL en vez de MongoDB, o por qué el modelo usa RandomForest y no XGBoost. Los ADRs resuelven esto: son la "memoria institucional" del proyecto. Siguen un formato estándar (Estado, Contexto, Decisión, Consecuencias) que facilita la lectura y búsqueda.

**Analogía desarrollada:** Piensa en un ADR como el acta de una reunión de arquitectos. Años después de construir un edificio, si alguien pregunta "¿por qué las vigas son de acero y no de madera?", el acta explica: "En 2020, consideramos madera (más barata) y acero (más resistente). Elegimos acero porque el edificio está en zona sísmica. Consecuencia: costo 20% mayor pero certificación antisísmica garantizada."

**Ejemplo del portafolio:**
```markdown
# ADR-001: Uso de RandomForest sobre XGBoost

## Estado: Aceptado

## Contexto
Necesitamos un modelo de clasificación para churn que sea interpretable 
para el equipo de negocio y robusto sin tuning extensivo.

## Decisión
Usamos RandomForestClassifier con class_weight='balanced'.

## Consecuencias
+ Feature importances nativas (explicabilidad)
+ Robusto sin hiperparámetro tuning complejo
- Puede perder 1-2% AUC vs XGBoost optimizado
```

**Relacionados:** ML Canvas, C4 Model, Documentación, DECISIONES_TECH.md

---

### API (Application Programming Interface)

**Definición técnica:** Contrato que define cómo dos sistemas de software se comunican. Especifica los endpoints disponibles, los formatos de entrada/salida, los métodos HTTP soportados y los códigos de respuesta. En MLOps, las APIs REST son el mecanismo principal para exponer modelos ML como servicios consumibles.

**Explicación conceptual:** Un modelo ML entrenado es solo un archivo (.pkl, .joblib). Para que sea útil, otros sistemas deben poder enviarle datos y recibir predicciones. Una API actúa como la "ventana al mundo" del modelo: recibe requests HTTP con datos del cliente, los valida, los pasa al modelo, y devuelve la predicción en formato estructurado (JSON). Esto desacopla el modelo de los consumidores: la app móvil, el dashboard, el sistema de CRM pueden todos usar la misma API sin conocer los detalles internos del modelo.

**Analogía desarrollada:** Una API es como el mesero de un restaurante. Tú (el cliente) no entras a la cocina a preparar tu comida (no cargas el modelo en tu código). En su lugar, le dices al mesero qué quieres (envías un request), él lleva el pedido a la cocina (la API invoca al modelo), y te trae el plato preparado (la API devuelve la predicción). El menú es la documentación de la API: te dice qué puedes pedir y cómo.

**Ejemplo del portafolio (BankChurn FastAPI):**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    CreditScore: int = Field(..., ge=300, le=850)
    Age: int = Field(..., ge=18, le=100)
    Balance: float = Field(..., ge=0)
    # ... más features

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    risk_level: str

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    df = pd.DataFrame([request.model_dump()])
    proba = model.predict_proba(df)[0, 1]
    return PredictionResponse(
        prediction=int(proba > 0.5),
        probability=proba,
        risk_level="high" if proba > 0.7 else "medium" if proba > 0.3 else "low"
    )
```

**Relacionados:** REST, FastAPI, Endpoint, HTTP, Pydantic, OpenAPI/Swagger

---

### Artefacto (Artifact)

**Definición técnica:** Cualquier archivo generado durante el ciclo de vida de ML que necesita ser versionado, almacenado y potencialmente reproducido. Incluye: modelos serializados (.pkl, .joblib, .onnx), datasets procesados, gráficos de evaluación, reportes de métricas, logs de entrenamiento, y configuraciones.

**Explicación conceptual:** Un proyecto ML no es solo código—genera "productos intermedios" en cada etapa. El dataset limpio es un artefacto. El modelo entrenado es un artefacto. El reporte de métricas es un artefacto. La gestión profesional de artefactos permite: (1) reproducibilidad—volver a cualquier versión anterior, (2) trazabilidad—saber qué datos y código produjeron qué modelo, (3) colaboración—compartir resultados entre equipos.

**Analogía desarrollada:** Piensa en una fábrica de autos. Los planos son artefactos (código). Las piezas moldeadas son artefactos (datasets procesados). El motor ensamblado es un artefacto (modelo entrenado). El auto terminado es un artefacto (pipeline completo). Cada pieza tiene un número de serie y registro de qué máquina la produjo, cuándo, con qué materiales. Si un auto tiene un defecto, puedes rastrear hacia atrás hasta encontrar la pieza defectuosa y qué lote de materiales causó el problema.

**Ejemplo del portafolio:**
```
artifacts/
├── model.joblib          # Modelo serializado (pipeline completo)
├── metrics.json          # {"roc_auc": 0.86, "recall": 0.75}
├── feature_importance.png # Gráfico de importancia
└── training_config.yaml  # Configuración usada
```

**Relacionados:** MLflow, Model Registry, DVC, Reproducibilidad

---

### ASGI (Asynchronous Server Gateway Interface)
**Definición:** Especificación para servidores web async en Python. Maneja múltiples requests concurrentemente.

**Analogía:** Mesero que anota pedido mesa 1, mientras espera va a mesa 2, etc. Maneja conversaciones "en paralelo".

**Relacionados:** Uvicorn, FastAPI, Async/Await

---

### AUC-ROC
**Definición:** Área bajo curva ROC. Mide capacidad de distinguir clases. 1.0 = perfecto, 0.5 = aleatorio.

**Analogía:** Separando manzanas buenas de malas. AUC 0.9 = 90% de las veces asigna mayor score a la manzana buena.

**Relacionados:** ROC Curve, Precision, Recall, Threshold

---

### Auto-scaling
**Definición:** Sistema que aumenta/disminuye recursos automáticamente según demanda.

**Analogía:** Restaurante contratando meseros temporales cuando hay mucha gente.

**Relacionados:** HPA, Kubernetes, Load Balancer

---

## B

### Backpropagation
**Definición:** Algoritmo de entrenamiento de redes neuronales que propaga el error hacia atrás calculando gradientes.

**Analogía:** Equipo de relevos donde analizas hacia atrás quién contribuyó al fallo.

**Relacionados:** Gradient Descent, Learning Rate, Neural Network

---

### Baseline
**Definición:** Modelo simple como referencia. Si tu modelo complejo no lo supera, algo está mal.

**Analogía:** Antes de comprar auto deportivo, verifica que sea más rápido que tu bicicleta.

**Relacionados:** Benchmark, Model Evaluation

---

### BaseEstimator
**Definición:** Clase base sklearn con `get_params()` y `set_params()`. Todos los estimadores heredan de ella.

**Analogía:** Contrato estándar que todos los constructores deben seguir para que el sistema funcione.

**Relacionados:** TransformerMixin, Custom Transformer, Pipeline

---

### Batch Prediction
**Definición:** Procesar múltiples muestras a la vez, programadamente. Contrasta con online/real-time.

**Analogía:** Catering (cocinas todo de antemano) vs restaurante a la carta (cocinas cada plato al pedirlo).

**Relacionados:** Online Prediction, Latencia

---

### Black
**Definición:** Formateador Python opinionado. Aplica estilo consistente automáticamente.

**Analogía:** Corrector que arregla gramática y estilo sin preguntarte.

```bash
black src/
```

**Relacionados:** Linting, Flake8, isort

---

### Branch (Rama)
**Definición:** Línea de desarrollo paralela en Git.

**Analogía:** Fotocopia del manuscrito para probar final alternativo sin afectar original.

```bash
git checkout -b feature/add-mlflow
```

**Relacionados:** Git, Merge, Pull Request

---

## C

### C4 Model
**Definición:** Visualización de arquitectura en 4 niveles: Context, Container, Component, Code.

**Analogía:** Google Maps con zoom. Mundo → País → Ciudad → Calle.

**Relacionados:** ADR, Arquitectura

---

### CI/CD
**Definición:** Continuous Integration (tests automáticos) + Continuous Deployment (deploy automático).

**Analogía:** Fábrica con control de calidad automatizado que envía autos aprobados al concesionario.

**Relacionados:** GitHub Actions, Pipeline, DevOps

---

### Classification
**Definición:** Problema ML supervisado para predecir categorías discretas.

**Analogía:** Doctor diagnosticando enfermedades (multiclase) o decidiendo operar/no operar (binaria).

**Relacionados:** Regression, Supervised Learning

---

### Class Imbalance (Desbalance de Clases)

**Definición técnica:** Situación donde una o más clases están significativamente subrepresentadas en el dataset de entrenamiento. Ratios como 95:5, 99:1 o peores son comunes en problemas reales (fraude, churn, enfermedades raras).

**Explicación conceptual:** Los algoritmos de ML optimizan métricas globales. Si el 95% de tus datos son "no-fraude", el modelo aprende que la estrategia más "segura" es predecir siempre "no-fraude"—obtiene 95% accuracy haciendo nada útil. El desbalance es quizás el problema más común y subestimado en ML aplicado. Afecta tanto al entrenamiento (el modelo no ve suficientes ejemplos de la clase minoritaria) como a la evaluación (accuracy es engañosa).

**Analogía desarrollada:** Imagina entrenar un perro buscador de trufas dándole 1000 piedras y solo 10 trufas. El perro aprende rápidamente que decir "piedra" le da premio el 99% de las veces. Nunca aprende realmente a oler trufas. Para entrenarlo bien, necesitas: (1) darle más trufas (oversampling), (2) penalizarlo más cuando falla una trufa (class weights), o (3) medir su éxito por trufas encontradas, no por piedras correctamente ignoradas (métricas apropiadas).

**Soluciones técnicas:**
```python
# 1. Class weights (penaliza más errores en clase minoritaria)
RandomForestClassifier(class_weight='balanced')

# 2. SMOTE (genera ejemplos sintéticos de clase minoritaria)
from imblearn.over_sampling import SMOTE
X_resampled, y_resampled = SMOTE().fit_resample(X, y)

# 3. Threshold adjustment (bajar umbral de decisión)
proba = model.predict_proba(X)[:, 1]
predictions = (proba > 0.3).astype(int)  # En vez de 0.5

# 4. Métricas apropiadas
from sklearn.metrics import recall_score, roc_auc_score
# NO usar accuracy como métrica principal
```

**En el portafolio:** BankChurn tiene ~20% churners. Usamos `class_weight='balanced'` y priorizamos Recall sobre Accuracy.

**Relacionados:** class_weight, SMOTE, Recall, Precision, ROC-AUC, Threshold

---

### class_weight

**Definición técnica:** Parámetro de sklearn que asigna pesos diferentes a las clases durante el entrenamiento. Con `class_weight='balanced'`, los pesos se calculan automáticamente como inversamente proporcionales a la frecuencia de cada clase.

**Explicación conceptual:** Es la forma más simple de manejar desbalance. En lugar de modificar los datos (oversampling/undersampling), modificamos cómo el modelo "valora" los errores. Un error en la clase minoritaria "cuenta más" que un error en la clase mayoritaria. Matemáticamente, es como si tuviéramos más ejemplos de la clase minoritaria sin realmente duplicarlos.

**Fórmula:** `weight[i] = n_samples / (n_classes * n_samples_i)`

**Ejemplo del portafolio:**
```python
# BankChurn: 80% no-churn, 20% churn
# Sin class_weight: modelo ignora churners
# Con class_weight='balanced': churners valen 4x más

from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    class_weight='balanced',  # Crítico para churn
    random_state=42
)
```

**Relacionados:** Class Imbalance, SMOTE, RandomForest

---

### Cold Start
**Definición:** Tiempo para que servicio esté listo tras iniciarse. Incluye cargar modelo en memoria.

**Analogía:** Encender auto en invierno. Debes esperar que el motor se caliente.

**Relacionados:** Serverless, Lambda, Latencia

---

### ColumnTransformer
**Definición:** Sklearn: aplica diferentes transformaciones a diferentes columnas.

**Analogía:** Lavandería con máquinas diferentes: color→encoder, blanca→scaler, delicados→passthrough.

```python
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), num_cols),
    ('cat', OneHotEncoder(), cat_cols),
])
```

**Relacionados:** Pipeline, Transformer

---

### Commit
**Definición:** Snapshot de cambios en Git con hash único y mensaje.

**Analogía:** Foto de tu escritorio. Puedes volver a cualquier foto anterior.

```bash
git commit -m "feat: add probability calibration"
```

**Relacionados:** Git, Branch, Push, Conventional Commits

---

### conftest.py

**Definición técnica:** Archivo especial de pytest que contiene fixtures (funciones que proveen datos/recursos) compartidas entre todos los tests del directorio y subdirectorios. pytest lo descubre automáticamente sin necesidad de imports.

**Explicación conceptual:** Los tests necesitan datos de prueba, conexiones a bases de datos mock, modelos pre-entrenados, etc. Sin conftest.py, cada archivo de tests tendría que definir o importar estos recursos. conftest.py centraliza esta lógica: defines las fixtures una vez, y están disponibles automáticamente en todos los tests. Es el "almacén central de recursos de testing".

**Analogía desarrollada:** Imagina un set de filmación. Antes de cada escena, alguien prepara el escenario: pone las luces, coloca los props, prepara el vestuario. conftest.py es ese equipo de preparación. Los actores (tests) llegan y todo está listo. No tienen que traer sus propios props—solo los piden por nombre y aparecen.

**Ejemplo del portafolio (CarVision):**
```python
# tests/conftest.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_data():
    """Datos sintéticos para tests."""
    np.random.seed(42)
    return pd.DataFrame({
        'year': np.random.randint(2010, 2023, 100),
        'mileage': np.random.randint(10000, 150000, 100),
        'price': np.random.uniform(5000, 50000, 100),
    })

@pytest.fixture
def trained_pipeline(sample_data):
    """Pipeline entrenado para tests de inferencia."""
    from carvision.pipeline import build_pipeline
    pipe = build_pipeline()
    X = sample_data.drop('price', axis=1)
    y = sample_data['price']
    return pipe.fit(X, y)

@pytest.fixture
def config():
    """Configuración de test."""
    return {'model': {'n_estimators': 10}, 'random_state': 42}
```

**Relacionados:** pytest, Fixture, Unit Test, Integration Test

---

### Conventional Commits

**Definición técnica:** Especificación para escribir mensajes de commit estandarizados. Formato: `<type>(<scope>): <description>`. Types incluyen: feat, fix, docs, style, refactor, test, chore.

**Explicación conceptual:** Los mensajes de commit son la historia del proyecto. "fixed bug" o "updates" no dicen nada útil. Conventional Commits impone estructura: el tipo indica qué cambió (feature nueva, bug fix, documentación), el scope indica dónde (api, pipeline, tests), la descripción explica qué. Esto permite: (1) generar CHANGELOGs automáticamente, (2) determinar versiones semánticas, (3) entender la historia del proyecto rápidamente.

**Analogía desarrollada:** Imagina un libro de bitácora de un barco. "Navegamos" no ayuda. "2024-01-15 14:00 - Cambio de rumbo: de Norte a Noroeste para evitar tormenta detectada a 50km" es útil. Conventional Commits son esa bitácora estructurada para código.

**Ejemplos del portafolio:**
```bash
# Formato: <type>(<scope>): <description>

feat(api): add batch prediction endpoint
fix(pipeline): handle NaN values in categorical columns
docs(readme): add quick start guide and badges
test(training): add integration tests for cross-validation
refactor(features): extract FeatureEngineer to separate module
chore(deps): update scikit-learn to 1.3.0
```

**Relacionados:** Git, pre-commit, Semantic Versioning

---

### Concept Drift
**Definición:** Cambio en relación features-target. Patrones aprendidos ya no son válidos.

**Analogía:** Modelo entrenado pre-pandemia predice gustos de películas post-pandemia incorrectamente.

**vs Data Drift:** Data Drift = cambia X. Concept Drift = cambia P(Y|X).

---

### ConfigMap
**Definición:** Kubernetes: almacena configuración no sensible como pares clave-valor.

**Analogía:** Tablón de anuncios de oficina. Información pública que todos necesitan.

---

### Container (Contenedor)
**Definición:** Software empaquetado con código y dependencias. Ejecuta igual en cualquier ambiente.

**Analogía:** Contenedor de barco. Funciona igual en cualquier puerto.

**Relacionados:** Docker, Image, Kubernetes

---

### Coverage
**Definición:** Porcentaje de código ejecutado por tests. No garantiza corrección.

**Analogía:** Inspector que revisó 80% de habitaciones. No significa que encontró todos los problemas.

```bash
pytest --cov=src
```

**Target:** >80% para código crítico

---

### Cross-Validation
**Definición:** Evaluar modelo dividiendo datos en K folds. Entrena K veces con diferentes splits.

**Analogía:** 5 estudiantes, 5 rondas. En cada ronda, diferente estudiante es evaluado.

```python
scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
```

**Relacionados:** K-Fold, Overfitting

---

### Custom Transformer
**Definición:** Clase sklearn personalizada que hereda BaseEstimator + TransformerMixin.

**Analogía:** Pieza LEGO personalizada con conexiones estándar (fit/transform).

```python
class RatioFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        X['ratio'] = X['Balance'] / (X['Products'] + 1)
        return X
```

---

## D

### DAG (Directed Acyclic Graph)
**Definición:** Grafo dirigido sin ciclos. Representa dependencias entre tareas.

**Analogía:** Instrucciones de receta. No puedes hornear antes de mezclar.

**Relacionados:** DVC, Pipeline, Airflow

---

### Data Drift

**Definición técnica:** Cambio en la distribución estadística de las features (P(X)) entre el momento del entrenamiento y la inferencia en producción. No implica necesariamente que la relación feature-target haya cambiado, solo que los datos de entrada son diferentes.

**Explicación conceptual:** Tu modelo fue entrenado con datos de 2023. Llega 2025 y los patrones de los clientes han cambiado: son más jóvenes, usan más canales digitales, tienen balances diferentes. Aunque la "lógica" de qué causa churn no haya cambiado, tu modelo recibe inputs que nunca vio y puede fallar. Data drift es como un médico entrenado solo con pacientes adultos intentando diagnosticar niños—la anatomía es diferente aunque las enfermedades sean las mismas.

**Analogía desarrollada:** Imagina un modelo que predice si lloverá basándose en la presión atmosférica. Fue entrenado en Madrid. Lo despliegas en Ciudad de México (altitud muy diferente). La presión "normal" en CDMX es mucho menor que en Madrid. El modelo ve presiones que interpreta como "muy baja" y siempre predice lluvia. No es que el modelo esté roto—es que los datos de entrada son muy diferentes a los de entrenamiento.

**Tipos de drift:**
- **Covariate shift**: Cambia P(X), pero P(Y|X) permanece igual
- **Prior probability shift**: Cambia P(Y), la proporción de clases
- **Concept drift**: Cambia P(Y|X), la relación misma

**Detección técnica:**
```python
# Kolmogorov-Smirnov test para cada feature
from scipy.stats import ks_2samp

for col in features:
    stat, pvalue = ks_2samp(train_data[col], prod_data[col])
    if pvalue < 0.05:
        print(f"Drift detectado en {col}: KS={stat:.3f}, p={pvalue:.4f}")

# Population Stability Index (PSI)
# PSI < 0.1: No drift
# PSI 0.1-0.2: Drift moderado
# PSI > 0.2: Drift significativo
```

**Herramientas:** Evidently, NannyML, Great Expectations

**Relacionados:** Concept Drift, Model Monitoring, Evidently, Retraining

---

### Data Leakage
**Definición:** Información del futuro o test filtra al entrenamiento. Métricas infladas.

**Analogía:** Estudiar con las respuestas del mismo examen. 100% en práctica, 0% en real.

**Ejemplos:** `price_per_mile = price / miles`, normalizar antes de split.

---

### Dependency Injection
**Definición:** Dependencias se pasan desde afuera en lugar de crearse internamente.

**Analogía:** Cafetería recibe leche de proveedor en vez de tener vacas propias.

```python
# Con DI: fácil de testear
class Predictor:
    def __init__(self, model: BaseEstimator):
        self.model = model  # Inyectado
```

**Relacionados:** SOLID, Testing

---

### Deployment
**Definición:** Poner modelo/aplicación en ambiente donde usuarios reales lo usan.

**Analogía:** Abrir restaurante al público después de cocinar en casa y probar con amigos.

**Tipos:** Batch, REST API, Edge, Streaming

---

### Docker
**Definición:** Plataforma para aplicaciones en contenedores. Código + dependencias portables.

**Analogía:** Máquina del tiempo para código. Congelas ambiente exacto.

```dockerfile
FROM python:3.11-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "app:app"]
```

---

### Docstring
**Definición:** String de documentación al inicio de funciones/clases.

**Analogía:** Instrucciones en la caja de un producto.

```python
def predict(data: pd.DataFrame) -> np.ndarray:
    """
    Genera predicciones de churn.
    
    Args:
        data: DataFrame con features.
    Returns:
        Array de probabilidades 0-1.
    """
```

---

### DVC (Data Version Control)
**Definición:** Versiona datasets y pipelines ML. Datos grandes en storage remoto, metadatos en Git.

**Analogía:** Git = álbum con miniaturas. DVC = almacén con fotos originales grandes.

```bash
dvc add data/dataset.csv
dvc push
git add data/dataset.csv.dvc
```

---

## E

### E2E Test
**Definición:** Test del sistema completo, desde entrada hasta salida final.

**Analogía:** Test drive de auto completo, no motor aislado.

---

### Early Stopping
**Definición:** Detiene entrenamiento cuando validación deja de mejorar. Evita overfitting.

**Analogía:** Sacar galletas del horno cuando están doradas, antes de que se quemen.

```python
EarlyStopping(monitor='val_loss', patience=5)
```

---

### Embedding
**Definición:** Representación vectorial densa de datos de alta dimensionalidad.

**Analogía:** Mapear ciudades del mundo en papel 2D. Similares quedan cerca.

**Uso:** Word2Vec, Entity embeddings

---

### Endpoint
**Definición:** URL específica de API que realiza operación particular.

**Analogía:** Ventanillas de banco. Cada una hace algo diferente.

```python
@app.get("/health")
@app.post("/predict")
```

---

### Ensemble
**Definición:** Combina múltiples modelos para mejores predicciones.

**Analogía:** 100 doctores opinando en vez de 1. Opinión agregada suele ser mejor.

**Tipos:** Bagging (Random Forest), Boosting (XGBoost), Stacking

---

### Environment
**Definición:** Conjunto aislado de dependencias donde ejecuta código.

**Analogía:** Diferentes cocinas para diferentes tipos de comida.

**Tipos:** Desarrollo, Staging, Producción

---

### Evidently

**Definición técnica:** Librería open-source de Python para monitoreo de modelos ML en producción. Genera reportes interactivos de data drift, target drift, data quality, y performance del modelo comparando datasets de referencia con datasets actuales.

**Explicación conceptual:** Cuando despliegas un modelo, necesitas saber si sigue funcionando bien. Evidently automatiza esta vigilancia: compara los datos que ve el modelo en producción con los datos de entrenamiento, detecta cambios estadísticos (drift), genera alertas, y produce reportes visuales. Es como tener un "chequeo médico" continuo para tu modelo.

**Analogía desarrollada:** Imagina que tienes un carro. Evidently es el tablero de instrumentos que te dice si la presión de las llantas bajó, si el aceite necesita cambio, si el motor está sobrecalentando. No esperas a que el carro se descomponga—el tablero te avisa antes de que el problema sea grave.

**Ejemplo práctico:**
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset

# Comparar datos de training vs producción
report = Report(metrics=[
    DataDriftPreset(),
    DataQualityPreset(),
])

report.run(
    reference_data=train_df,
    current_data=production_df
)

# Generar reporte HTML interactivo
report.save_html("drift_report.html")

# O extraer métricas programáticamente
drift_results = report.as_dict()
if drift_results['metrics'][0]['result']['dataset_drift']:
    print("⚠️ Drift significativo detectado!")
```

**Capacidades:**
- Data Drift: Detecta cambios en distribuciones de features
- Target Drift: Detecta cambios en distribución del target
- Data Quality: Valores faltantes, outliers, correlaciones
- Model Performance: Accuracy, precision, recall en producción
- Regression Performance: MAE, RMSE, error distribution

**Relacionados:** Data Drift, Model Monitoring, Observabilidad, NannyML

---

### Experiment Tracking
**Definición:** Registrar parámetros, métricas, artefactos de cada experimento ML.

**Analogía:** Cuaderno de laboratorio de científico.

**Herramientas:** MLflow, W&B, Neptune

---

## F

### F1 Score
**Definición:** Media armónica de Precision y Recall. Balance entre ambas.

**Fórmula:** `F1 = 2 × (Precision × Recall) / (Precision + Recall)`

**Analogía:** Buscador de trufas. No sirve encontrar pocas muy precisamente ni todas con muchas falsas.

---

### FastAPI
**Definición:** Framework Python para APIs de alto rendimiento con validación automática.

**Analogía:** Mesero eficiente que valida pedidos, da menú descriptivo, atiende muchas mesas.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.post("/predict")
async def predict(data: PredictionInput):
    return {"probability": model.predict_proba([data])[0, 1]}
```

**Relacionados:** Pydantic, Uvicorn, REST

---

### Feature
**Definición:** Variable de entrada para predicciones.

**Analogía:** Ingredientes de receta. Para predecir si pastel sale bien: harina, azúcar, temperatura.

**Tipos:** Numéricas, Categóricas, Binarias, Derivadas

---

### Feature Engineering
**Definición:** Crear/transformar/seleccionar features para mejorar modelo.

**Analogía:** Chef preparando ingredientes. Ingredientes crudos se transforman en algo digerible.

```python
df['balance_per_product'] = df['Balance'] / (df['NumOfProducts'] + 1)
```

---

### Feature Store
**Definición:** Sistema centralizado para almacenar y servir features consistentemente.

**Analogía:** Almacén central de ingredientes preparados para cadena de restaurantes.

**Herramientas:** Feast, Tecton

---

### Fixture (pytest)
**Definición:** Función que provee datos/recursos reutilizables para tests.

**Analogía:** Setup de set de filmación antes de cada escena.

```python
@pytest.fixture
def sample_customer():
    return {"Age": 35, "Balance": 50000}
```

---

### Flake8
**Definición:** Linting para Python: errores lógicos, estilo PEP8, complejidad.

**Analogía:** Corrector de estilo de periódico.

```bash
flake8 src/
```

---

## G

### Git
**Definición:** Control de versiones distribuido.

**Analogía:** "Deshacer" infinito. Volver a cualquier momento, ver qué cambió y por qué.

```bash
git add . && git commit -m "mensaje" && git push
```

---

### GitHub Actions
**Definición:** CI/CD integrado en GitHub.

**Analogía:** Mayordomo robot que ejecuta instrucciones automáticamente.

```yaml
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/
```

---

### Gitleaks
**Definición:** Detecta secrets accidentalmente commiteados.

**Analogía:** Detector de metales en aeropuerto para código.

---

### Gradient Descent
**Definición:** Algoritmo que encuentra parámetros que minimizan pérdida.

**Analogía:** En montaña con niebla, das pasos pequeños siempre cuesta abajo.

**Relacionados:** Learning Rate, Loss Function

---

### Grafana
**Definición:** Visualización y dashboards para métricas.

**Analogía:** Tablero de instrumentos de avión.

**Relacionados:** Prometheus, Observabilidad

---

## H

### Health Check
**Definición:** Endpoint que verifica si servicio funciona.

**Analogía:** Médico preguntando "¿cómo te sientes?".

```python
@app.get("/health")
def health():
    return {"status": "healthy"}
```

---

### HPA (Horizontal Pod Autoscaler)
**Definición:** Kubernetes: escala pods automáticamente según métricas.

**Analogía:** Gerente de restaurante que llama más meseros si hay muchas mesas ocupadas.

---

### Hyperparameter
**Definición:** Parámetro configurado ANTES del entrenamiento.

**Analogía:** Decisiones antes de hornear: temperatura, tiempo, tamaño de molde.

**Ejemplos:** n_estimators, learning_rate, max_depth

---

### Hyperparameter Tuning
**Definición:** Encontrar combinación óptima de hiperparámetros.

**Analogía:** Afinar guitarra. Probar perillas hasta mejor sonido.

**Técnicas:** Grid Search, Random Search, Bayesian Optimization

---

## I

### Image (Docker)
**Definición:** Template inmutable para crear contenedores.

**Analogía:** Receta + ingredientes pre-empaquetados. Imagen es el kit, contenedor es el pastel horneado.

---

### Imputer
**Definición:** Rellena valores faltantes (NaN).

**Analogía:** Restaurador de pinturas rellenando huecos.

```python
SimpleImputer(strategy='median')
```

---

### Inference
**Definición:** Usar modelo entrenado para predicciones sobre datos nuevos.

**Analogía:** Entrenamiento = estudiar. Inferencia = tomar el examen.

---

### Ingress
**Definición:** Kubernetes: gestiona acceso HTTP externo al cluster.

**Analogía:** Recepción de edificio que dirige tráfico.

---

### Integration Test
**Definición:** Verifica que múltiples componentes funcionan juntos.

**Analogía:** Probar que motor, transmisión y ruedas funcionan juntos.

---

### isort
**Definición:** Ordena imports de Python automáticamente.

**Analogía:** Organizador de armario que siempre pone ropa en mismo orden.

---

## J

### Job (GitHub Actions)
**Definición:** Conjunto de steps en mismo runner.

**Relacionados:** Workflow, Step, Runner

---

### Joblib
**Definición:** Serializa objetos Python, especialmente modelos sklearn.

```python
joblib.dump(model, "model.pkl")
model = joblib.load("model.pkl")
```

---

## K

### Kubernetes (K8s)
**Definición:** Orquestador de contenedores para automatizar despliegue y escalado.

**Analogía:** Director de orquesta coordinando muchos músicos (contenedores).

**Recursos:** Pod, Deployment, Service, Ingress

---

### K-Fold
**Definición:** Dividir datos en K partes para cross-validation.

**Relacionados:** Cross-Validation, Stratified

---

## L

### Latency (Latencia)
**Definición:** Tiempo de respuesta del sistema. En APIs ML: milisegundos.

**Analogía:** Tiempo entre pedir comida y que llegue.

**P95:** El 95% de requests responden en menos de X ms.

---

### Learning Rate
**Definición:** Tamaño de paso en gradient descent.

**Analogía:** Paso grande = llegas rápido pero puedes pasar el mínimo. Paso pequeño = lento pero preciso.

---

### Linting
**Definición:** Análisis estático para detectar errores y violaciones de estilo.

**Herramientas:** Flake8, pylint, mypy

---

### Load Balancer
**Definición:** Distribuye tráfico entre múltiples servidores.

**Analogía:** Hostess de restaurante que asigna mesas equitativamente.

---

### Loss Function (Función de Pérdida)
**Definición:** Mide qué tan mal son las predicciones. El entrenamiento la minimiza.

**Ejemplos:** MSE (regresión), Cross-Entropy (clasificación)

---

## M

### Makefile
**Definición:** Archivo con comandos abreviados para tareas comunes.

```makefile
test:
    pytest tests/ -v
lint:
    black src/ && flake8 src/
```

---

### Matrix (GitHub Actions)
**Definición:** Ejecutar job con múltiples combinaciones de parámetros.

```yaml
strategy:
  matrix:
    python-version: [3.10, 3.11]
```

---

### Metric (Métrica)
**Definición:** Valor numérico que mide rendimiento del modelo.

**Clasificación:** Accuracy, Precision, Recall, F1, AUC
**Regresión:** MSE, RMSE, MAE, R²

---

### Middleware
**Definición:** Código que intercepta requests/responses entre cliente y aplicación.

**Analogía:** Portero que revisa credenciales antes de dejarte pasar.

---

### MLflow
**Definición:** Plataforma open-source para gestionar ciclo de vida ML.

**Componentes:** Tracking, Projects, Models, Registry

```python
with mlflow.start_run():
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.sklearn.log_model(model, "model")
```

---

### MLOps

**Definición técnica:** Conjunto de prácticas que unifican Machine Learning, DevOps y Data Engineering para automatizar y estandarizar el ciclo de vida completo de modelos ML: desde experimentación hasta producción, incluyendo monitoreo, reentrenamiento y gobernanza.

**Explicación conceptual:** Data Scientists saben entrenar modelos. DevOps sabe desplegar aplicaciones. Data Engineers saben mover datos. MLOps es el puente que conecta estos tres mundos. Sin MLOps, tienes "modelos en notebooks" que nunca llegan a producción, o modelos desplegados que nadie monitorea y se degradan silenciosamente. MLOps trae madurez industrial al ML.

**Analogía desarrollada:** Imagina que los Data Scientists son chefs que crean recetas increíbles en su cocina experimental. DevOps es el equipo que opera restaurantes a escala. MLOps es el proceso que convierte esa receta experimental en un menú estandarizado, con control de calidad, ingredientes versionados, y alertas si la calidad baja. Sin MLOps, tienes un chef genial cuyas recetas nadie puede reproducir consistentemente.

**Pilares de MLOps:**
1. **Versionado**: Código (Git), Datos (DVC), Modelos (MLflow)
2. **Automatización**: CI/CD, pipelines de entrenamiento
3. **Testing**: Datos, modelos, APIs, integración
4. **Monitoreo**: Drift, performance, latencia
5. **Reproducibilidad**: Ambientes, seeds, configuraciones

**Relacionados:** DevOps, CI/CD, MLflow, DVC, Model Monitoring

---

### Multi-stage Build (Docker)

**Definición técnica:** Técnica de construcción de imágenes Docker que usa múltiples `FROM` statements, permitiendo separar el ambiente de compilación/build del ambiente de ejecución. El resultado es una imagen final más pequeña y segura que solo contiene lo necesario para ejecutar la aplicación.

**Explicación conceptual:** Cuando construyes una aplicación, necesitas herramientas de compilación, tests, dependencias de desarrollo. Pero en producción, solo necesitas el binario final y las dependencias runtime. Multi-stage te permite "cocinar" en una cocina completa y luego servir solo el plato terminado, sin llevar todos los utensilios al comedor.

**Analogía desarrollada:** Imagina construir un mueble IKEA. Necesitas martillo, destornillador, nivel, instrucciones, embalaje. Pero una vez terminado, solo quieres el mueble en tu sala—no el taller completo. Multi-stage es exactamente eso: usas un container "taller" con todas las herramientas, construyes, y luego copias solo el resultado final a un container "sala" limpio y minimalista.

**Ejemplo del portafolio:**
```dockerfile
# ═══════════════════════════════════════════════════════
# STAGE 1: Builder - Tiene todas las herramientas
# ═══════════════════════════════════════════════════════
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias de compilación (solo en builder)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python en directorio aislado
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# ═══════════════════════════════════════════════════════
# STAGE 2: Runtime - Solo lo necesario para ejecutar
# ═══════════════════════════════════════════════════════
FROM python:3.11-slim

# Usuario no-root (seguridad)
RUN useradd --create-home appuser

WORKDIR /app

# Copiar SOLO las dependencias instaladas (no el toolchain)
COPY --from=builder /app/deps /usr/local/lib/python3.11/site-packages/

# Copiar código de aplicación
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser artifacts/ ./artifacts/

USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Beneficios:**
- **Imagen más pequeña**: De ~1.5GB a ~500MB
- **Más segura**: Sin compiladores ni herramientas de ataque
- **Más rápida de desplegar**: Menos bytes que transferir

**Relacionados:** Docker, Container, Dockerfile, Non-root User

---

### Model Card
**Definición:** Documento describiendo modelo: propósito, datos, métricas, limitaciones, ética.

**Analogía:** Prospecto de medicamento. Información completa sobre qué hace y sus efectos.

---

### Model Registry
**Definición:** Sistema para versionar y gestionar modelos ML.

**Estados:** Staging → Production → Archived

---

### mypy
**Definición:** Type checking estático para Python.

```bash
mypy src/
```

**Relacionados:** Type Hints, Pydantic

---

## N

### NaN (Not a Number)
**Definición:** Valor especial para datos faltantes o indefinidos.

```python
import numpy as np
np.nan
```

---

### Namespace
**Definición:** Kubernetes: división lógica del cluster para aislamiento.

**Analogía:** Departamentos en una empresa. Cada uno tiene sus recursos.

---

## O

### Observability (Observabilidad)
**Definición:** Capacidad de entender estado interno de sistema desde outputs externos.

**3 Pilares:** Logs, Metrics, Traces

**Analogía:** Instrumentos de avión. Si no puedes ver, no puedes arreglar.

---

### One-Hot Encoding
**Definición:** Convierte variables categóricas en vectores binarios.

```
Country: [France, Spain, Germany]
France → [1, 0, 0]
Spain  → [0, 1, 0]
```

---

### Overfitting (Sobreajuste)
**Definición:** Modelo memoriza datos de entrenamiento, no generaliza.

**Analogía:** Estudiante que memoriza respuestas exactas pero no entiende conceptos.

**Señales:** Train accuracy muy alta, validation accuracy baja.

**Soluciones:** Más datos, regularización, early stopping, dropout

---

## P

### Pipeline (sklearn)
**Definición:** Secuencia de transformaciones y estimador final encadenados.

**Analogía:** Línea de ensamblaje. Cada estación hace una transformación.

```python
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier())
])
```

---

### Pod
**Definición:** Kubernetes: unidad de deployment más pequeña. Uno o más contenedores.

**Analogía:** Apartamento en edificio. Contenedores son habitaciones del apartamento.

---

### Precision (Precisión)
**Definición:** De predicciones positivas, ¿cuántas son correctas? TP / (TP + FP)

**Analogía:** De las personas que detuviste como sospechosas, ¿cuántas eran realmente criminales?

---

### Pre-commit Hook
**Definición:** Script que se ejecuta automáticamente antes de cada commit.

**Analogía:** Control de calidad que revisa tu trabajo antes de entregarlo.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks:
      - id: black
```

---

### Prometheus
**Definición:** Sistema de monitoreo y alertas. Recolecta métricas de servicios.

**Relacionados:** Grafana, Metrics, Observabilidad

---

### Pull Request (PR)
**Definición:** Solicitud para integrar cambios con revisión de código.

**Analogía:** Propuesta formal que requiere aprobación antes de aceptarse.

---

### Pydantic
**Definición:** Validación de datos en Python usando type hints.

```python
class Customer(BaseModel):
    age: int = Field(ge=18, le=100)
    name: str
```

**Relacionados:** Type Hints, FastAPI, Validation

---

### pytest
**Definición:** Framework de testing para Python.

```python
def test_prediction():
    result = model.predict([[35, 50000]])
    assert result[0] in [0, 1]
```

---

## R

### Random Forest

**Definición técnica:** Algoritmo de ensemble learning que construye múltiples árboles de decisión durante el entrenamiento y combina sus predicciones (votación mayoritaria para clasificación, promedio para regresión). Cada árbol se entrena con un subconjunto aleatorio de datos (bagging) y features (random subspace).

**Explicación conceptual:** Un solo árbol de decisión puede sobreajustarse fácilmente y es muy sensible a pequeños cambios en los datos. Random Forest resuelve esto con la "sabiduría de las multitudes": entrena cientos de árboles "diversos" (cada uno ve datos diferentes) y promedia sus opiniones. Los errores individuales se cancelan, produciendo un modelo robusto y estable.

**Analogía desarrollada:** Imagina 100 doctores, cada uno especializado en diferentes aspectos (algunos ven más casos de ciertas enfermedades, otros atienden diferentes demografías). Si cada doctor da su diagnóstico individualmente, algunos acertarán y otros fallarán. Pero si los 100 votan y tomas la opinión mayoritaria, casi siempre aciertas. Eso es Random Forest: democracia de árboles donde los errores individuales se cancelan.

**Por qué es popular en MLOps:**
- **Interpretabilidad**: Feature importances nativas
- **Robustez**: Funciona bien "out of the box" sin tuning extensivo
- **Versatilidad**: Clasificación y regresión
- **Sin normalización**: No requiere escalar features

**Ejemplo del portafolio (BankChurn):**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# Parámetros clave:
# - n_estimators: Número de árboles (más = más estable, más lento)
# - max_depth: Profundidad máxima (controla overfitting)
# - class_weight: Manejo de desbalance

pipeline = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', SimpleImputer(strategy='median'), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
    ])),
    ('classifier', RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight='balanced',  # Crítico para churn
        random_state=42,
        n_jobs=-1  # Paralelizar
    ))
])

# Feature importance después de entrenar
importances = pipeline.named_steps['classifier'].feature_importances_
```

**Hiperparámetros importantes:**
| Parámetro | Default | Efecto |
|-----------|---------|--------|
| n_estimators | 100 | Más árboles = más estable pero más lento |
| max_depth | None | Limitar previene overfitting |
| min_samples_split | 2 | Mayor valor = árboles más pequeños |
| class_weight | None | 'balanced' para clases desbalanceadas |

**Relacionados:** Ensemble, Bagging, Decision Tree, class_weight, Feature Importance

---

### Recall (Sensibilidad)

**Definición técnica:** Métrica que mide qué proporción de los casos positivos reales fueron correctamente identificados. Fórmula: `TP / (TP + FN)`. También llamada Sensibilidad o True Positive Rate.

**Explicación conceptual:** Recall responde: "De todos los casos positivos reales, ¿cuántos logré detectar?". Es crítica cuando el costo de **no detectar** un positivo es alto: diagnóstico de cáncer (no detectar = paciente sin tratamiento), detección de fraude (no detectar = pérdida financiera), predicción de churn (no detectar = cliente perdido).

**Analogía desarrollada:** Imagina un detector de metales en un aeropuerto. Recall es: "De todas las armas reales que pasaron, ¿cuántas detectó?". Un Recall del 100% significa que detectó todas las armas (aunque haya generado muchas falsas alarmas con llaves y monedas). En seguridad, preferimos alta sensibilidad aunque suene más veces innecesariamente.

**En el portafolio:** BankChurn prioriza Recall porque el costo de no detectar un churner (perderlo) es mayor que el costo de ofrecerle retención a alguien que no iba a irse.

**Trade-off Precision vs Recall:**
```
                    Predicción
                    Positivo    Negativo
Realidad Positivo   TP          FN (Recall falla aquí)
         Negativo   FP          TN

Recall = TP / (TP + FN) → Maximizar TP, minimizar FN
```

**Relacionados:** Precision, F1 Score, Threshold, ROC-AUC

---

### Regression (Regresión)
**Definición:** Problema ML para predecir valor numérico continuo.

**Ejemplos:** Precio de casa, temperatura, ventas

---

### Regularization (Regularización)
**Definición:** Técnicas para prevenir overfitting penalizando complejidad.

**Tipos:** L1 (Lasso), L2 (Ridge), Dropout, Early Stopping

---

### Replica
**Definición:** Copia de un pod/servicio para alta disponibilidad.

**Relacionados:** Deployment, ReplicaSet

---

### Reproducibility (Reproducibilidad)
**Definición:** Obtener mismos resultados con mismo código y datos.

**Clave:** Seeds, versionado de datos/código/ambiente

---

### REST API
**Definición:** Estilo arquitectónico con HTTP methods: GET, POST, PUT, DELETE.

**Relacionados:** API, HTTP, Endpoint

---

### Runbook

**Definición técnica:** Documento operacional que contiene procedimientos paso a paso para manejar incidentes, alertas o tareas de mantenimiento de un sistema en producción. Incluye información del servicio, alertas comunes, y procedimientos de emergencia.

**Contenido típico:**
- Información del servicio (owner, criticidad, endpoints)
- Procedimientos para alertas comunes
- Comandos de diagnóstico y recuperación
- Escalamiento y contactos

**En el portafolio:** Ver [17_DESPLIEGUE.md → Operaciones y Runbooks](17_DESPLIEGUE.md#-operaciones-y-runbooks).

**Relacionados:** SLO, SLA, Incident Response, On-call

---

### Ruff

**Definición técnica:** Linter y formateador de código Python extremadamente rápido, escrito en Rust. Reemplaza múltiples herramientas (Flake8, Black, isort, pyupgrade, etc.) con una sola herramienta 10-100x más rápida.

**Explicación conceptual:** Tradicionalmente, un proyecto Python necesitaba múltiples herramientas para mantener la calidad del código: Black para formatear, Flake8 para detectar errores, isort para ordenar imports, pyupgrade para sintaxis moderna. Cada herramienta tenía su configuración, versión, y tiempo de ejecución. Ruff unifica todo esto: un solo binario que hace todo, instantáneamente. Es la herramienta moderna que está reemplazando al stack tradicional.

**Analogía desarrollada:** Imagina tener una navaja suiza en vez de cargar tijeras, destornillador, cuchillo y abridor por separado. Ruff es esa navaja suiza: todas las herramientas de calidad de código en una, y además es más ligera y rápida que cualquiera de las individuales.

**Por qué importa:**
- **Velocidad**: 10-100x más rápido que Flake8+Black+isort
- **Unificación**: Una herramienta, una configuración
- **Compatibilidad**: Entiende las reglas de Flake8, Black, isort
- **Moderno**: Soporta Python 3.12+, type hints, f-strings

**Ejemplo de configuración (pyproject.toml):**
```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # Pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.lint.isort]
known-first-party = ["bankchurn", "carvision", "telecomai"]
```

**Uso:**
```bash
# Lint (detectar errores)
ruff check src/

# Lint con auto-fix
ruff check --fix src/

# Format (como Black)
ruff format src/

# Pre-commit hook
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

**Relacionados:** Linting, Black, Flake8, isort, pre-commit, Code Quality

---

## S

### Scaling (Escalado de Features)
**Definición:** Normalizar features a rango similar.

**Técnicas:** StandardScaler (z-score), MinMaxScaler (0-1)

---

### Scikit-learn (sklearn)
**Definición:** Librería Python para ML clásico.

**Módulos:** preprocessing, model_selection, ensemble, metrics

---

### Secret
**Definición:** Valor sensible (contraseña, API key) que no debe estar en código.

**Kubernetes:** Objeto Secret para almacenar datos sensibles encriptados.

---

### Seed (Random State)
**Definición:** Valor para inicializar generadores aleatorios. Garantiza reproducibilidad.

```python
np.random.seed(42)
RandomForestClassifier(random_state=42)
```

---

### Service (Kubernetes)
**Definición:** Abstracción que expone pods como servicio de red.

**Tipos:** ClusterIP, NodePort, LoadBalancer

---

### SHAP

**Definición técnica:** SHapley Additive exPlanations. Framework de interpretabilidad basado en teoría de juegos que asigna a cada feature su contribución marginal a una predicción específica. Funciona con cualquier modelo (model-agnostic).

**Explicación conceptual:** Cuando un modelo predice que un cliente va a abandonar, quieres saber *por qué*. SHAP descompone la predicción en contribuciones de cada feature: "El balance alto contribuyó +0.15 a la probabilidad de churn, la edad joven contribuyó -0.08, el número de productos contribuyó +0.12...". Esto permite explicar cada predicción individual, no solo el modelo en general.

**Analogía desarrollada:** Imagina un jurado de 10 personas que decide un veredicto. SHAP es como analizar cuánto influyó cada jurado en la decisión final. "María estaba muy convencida (+0.3), Juan estaba indeciso (+0.05), Pedro iba en contra (-0.2)...". Sumando todas las contribuciones, obtienes el veredicto final.

**Relacionados:** Interpretabilidad, Feature Importance, Explainability

---

### SMOTE (Synthetic Minority Over-sampling Technique)

**Definición técnica:** Técnica de oversampling que genera ejemplos sintéticos de la clase minoritaria interpolando entre ejemplos existentes y sus k vecinos más cercanos. No duplica ejemplos—crea nuevos puntos en el espacio de features.

**Explicación conceptual:** Cuando tienes 95% de una clase y 5% de otra, el modelo aprende a ignorar la minoritaria. SMOTE resuelve esto generando ejemplos sintéticos "plausibles" de la clase minoritaria. Toma un ejemplo real, encuentra sus vecinos más cercanos (también de la clase minoritaria), y crea nuevos puntos en la línea que los conecta. Así el modelo ve más variedad de la clase minoritaria sin simplemente copiar los mismos ejemplos.

**Analogía desarrollada:** Imagina que tienes 10 fotos de gatos negros y 1000 de perros. Duplicar la foto del gato 100 veces no ayuda—el modelo memoriza esa única foto. SMOTE es como un artista que mira tus 10 fotos de gatos negros y pinta 90 fotos nuevas de gatos negros "plausibles" interpolando características: "este tiene los ojos del gato 1, las orejas del gato 3, el tamaño del gato 7...".

**Ejemplo:**
```python
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split

# Siempre aplicar DESPUÉS del split (evitar data leakage)
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y)

# SMOTE solo en training
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Ahora las clases están balanceadas en training
print(f"Original: {y_train.value_counts().to_dict()}")
print(f"Resampled: {pd.Series(y_train_resampled).value_counts().to_dict()}")
```

**Cuándo usar SMOTE vs class_weight:**
- **SMOTE**: Cuando quieres más variedad en ejemplos minoritarios
- **class_weight**: Más simple, no modifica datos, funciona bien en la mayoría de casos

**Relacionados:** Class Imbalance, Oversampling, class_weight, imblearn

---

### SOLID

**Definición técnica:** Cinco principios de diseño de software orientado a objetos que promueven código mantenible, extensible y testeable.

**Los 5 principios:**

1. **S - Single Responsibility**: Una clase debe tener una sola razón para cambiar
   ```python
   # ❌ Mal: Clase hace demasiado
   class ChurnPredictor:
       def load_data(self): ...
       def clean_data(self): ...
       def train(self): ...
       def save_to_s3(self): ...
   
   # ✅ Bien: Responsabilidades separadas
   class DataLoader: ...
   class FeatureEngineer: ...
   class ChurnTrainer: ...
   class S3Uploader: ...
   ```

2. **O - Open/Closed**: Abierto para extensión, cerrado para modificación
   ```python
   # Puedes añadir nuevos modelos sin modificar código existente
   class BaseTrainer(ABC):
       @abstractmethod
       def train(self, X, y): ...
   
   class RandomForestTrainer(BaseTrainer): ...
   class XGBoostTrainer(BaseTrainer): ...  # Extensión, no modificación
   ```

3. **L - Liskov Substitution**: Subclases deben ser substituibles por sus padres

4. **I - Interface Segregation**: Interfaces pequeñas y específicas

5. **D - Dependency Inversion**: Depender de abstracciones, no de implementaciones

**En el portafolio:** `FeatureEngineer`, `ChurnTrainer` siguen Single Responsibility. El uso de sklearn Pipeline permite Open/Closed (cambiar modelo sin modificar pipeline).

**Relacionados:** Clean Code, Design Patterns, Testing

---

### src/ Layout

**Definición técnica:** Estructura de proyecto Python donde el código fuente reside en un subdirectorio `src/` en lugar de la raíz. El paquete se instala con `pip install -e .` para desarrollo.

**Explicación conceptual:** La estructura "flat" (código en raíz) causa problemas: Python puede importar archivos locales en vez del paquete instalado, tests pueden pasar localmente pero fallar en CI, y es difícil distinguir código de proyecto de configuración. `src/` layout resuelve esto forzando que el código solo sea accesible como paquete instalado.

**Analogía desarrollada:** Imagina una tienda donde los productos están tanto en el almacén como en el piso de venta. Confusión garantizada: ¿el cliente está comprando del almacén o del piso? src/ layout es como tener una puerta clara entre almacén (desarrollo) y piso de venta (paquete instalado).

**Estructura del portafolio:**
```
BankChurn-Predictor/
├── src/
│   └── bankchurn/           # Paquete principal
│       ├── __init__.py
│       ├── config.py        # Configuración Pydantic
│       ├── pipeline.py      # Pipeline sklearn
│       └── trainer.py       # Clase de entrenamiento
├── tests/                   # Tests (fuera de src/)
├── app/                     # APIs (fuera de src/)
├── configs/                 # Configuraciones YAML
├── artifacts/               # Modelos entrenados
└── pyproject.toml          # Configuración de paquete
```

**Configuración en pyproject.toml:**
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "bankchurn"
version = "0.1.0"

[tool.setuptools.packages.find]
where = ["src"]
```

**Relacionados:** pyproject.toml, Package, Import, Project Structure

---

### Staging
**Definición:** Ambiente que replica producción para testing final.

**Analogía:** Ensayo general antes del estreno.

---

### Stratified Split
**Definición:** División que mantiene proporción de clases en train y test.

```python
train_test_split(X, y, stratify=y)
```

---

### Streamlit

**Definición técnica:** Framework Python para crear aplicaciones web interactivas con código puro Python. Convierte scripts de análisis de datos en dashboards web sin necesidad de conocimientos de HTML, CSS o JavaScript.

**Explicación conceptual:** Data Scientists crean análisis increíbles en notebooks, pero compartirlos requiere que el receptor tenga Python instalado y sepa ejecutar notebooks. Streamlit permite convertir ese análisis en una aplicación web que cualquiera puede usar: añades decoradores como `st.title()`, `st.button()`, `st.dataframe()` y Streamlit genera una UI web automáticamente. Es la forma más rápida de pasar de "script de análisis" a "aplicación interactiva".

**Analogía desarrollada:** Imagina que eres un chef que crea recetas increíbles. Jupyter notebooks es como escribir la receta en un cuaderno técnico—otros chefs pueden seguirla, pero no el público general. Streamlit es como montar un food truck donde la gente puede probar tus platos sin saber cocinar. Tu código Python sigue siendo la "cocina", pero ahora tiene una ventana de servicio bonita.

**Ejemplo del portafolio (CarVision Dashboard):**
```python
import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="CarVision Predictor", page_icon="🚗")
st.title("🚗 CarVision Price Predictor")

# Sidebar para inputs
with st.sidebar:
    st.header("Vehicle Features")
    year = st.slider("Year", 2000, 2024, 2018)
    mileage = st.number_input("Mileage", 0, 300000, 50000)
    brand = st.selectbox("Brand", ["Toyota", "Honda", "Ford"])

# Cargar modelo (con cache para no recargar)
@st.cache_resource
def load_model():
    return joblib.load("artifacts/model.joblib")

model = load_model()

# Botón de predicción
if st.button("🔮 Predict Price"):
    input_df = pd.DataFrame([{"year": year, "mileage": mileage, "brand": brand}])
    prediction = model.predict(input_df)[0]
    
    st.success(f"Estimated Price: ${prediction:,.0f}")
    
    # Métricas visuales
    col1, col2 = st.columns(2)
    col1.metric("Predicted Price", f"${prediction:,.0f}")
    col2.metric("Confidence", "High" if prediction > 10000 else "Medium")
```

**Componentes clave:**
- `st.title()`, `st.header()`: Títulos
- `st.slider()`, `st.number_input()`, `st.selectbox()`: Inputs
- `st.button()`: Acciones
- `st.dataframe()`, `st.plotly_chart()`: Visualización
- `@st.cache_resource`: Cache de modelos/datos pesados

**Relacionados:** Dashboard, FastAPI, Gradio, Panel

---

## T

### Target
**Definición:** Variable que queremos predecir. También llamada "label" o "y".

---

### Terraform
**Definición:** Infrastructure as Code. Provisiona recursos en cloud con código.

```hcl
resource "aws_instance" "ml_server" {
  instance_type = "t3.medium"
}
```

---

### Test Coverage
**Definición:** Porcentaje de código ejecutado durante tests.

**Relacionados:** Coverage, pytest

---

### Threshold (Umbral)
**Definición:** Punto de corte para convertir probabilidades en clases.

**Default:** 0.5, pero ajustable según necesidades de negocio.

---

### Throughput
**Definición:** Cantidad de predicciones/requests por unidad de tiempo.

**Analogía:** Cuántos platos puede servir el restaurante por hora.

---

### Traces
**Definición:** Seguimiento de requests a través de sistema distribuido.

**Herramientas:** Jaeger, OpenTelemetry

**Relacionados:** Observabilidad, Logs, Metrics

---

### TransformerMixin
**Definición:** Mixin sklearn que añade `fit_transform()` automáticamente.

**Relacionados:** BaseEstimator, Custom Transformer

---

### Trivy
**Definición:** Escáner de vulnerabilidades para contenedores.

```bash
trivy image my-app:latest
```

---

### Type Hints
**Definición:** Anotaciones en Python que indican tipos esperados.

```python
def predict(data: pd.DataFrame) -> np.ndarray:
    pass
```

**Relacionados:** mypy, Pydantic

---

## U

### Underfitting (Subajuste)
**Definición:** Modelo demasiado simple. No captura patrones.

**Señales:** Train y validation accuracy bajas.

---

### Unit Test
**Definición:** Test de función/método individual en aislamiento.

```python
def test_feature_ratio():
    result = compute_ratio(100, 2)
    assert result == 50
```

---

### Uvicorn
**Definición:** Servidor ASGI de alto rendimiento para FastAPI.

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## V

### Validation Set
**Definición:** Datos para ajustar hiperparámetros, separado de train y test.

**Split típico:** 60% train, 20% validation, 20% test

---

### Vendor Lock-in
**Definición:** Dependencia de proveedor específico que dificulta migración.

**Analogía:** Comprar auto donde repuestos solo existen en una tienda.

---

### Version Control
**Definición:** Sistema para rastrear cambios en archivos.

**Herramientas:** Git (código), DVC (datos), MLflow (modelos)

---

### Voting Classifier
**Definición:** Ensemble que combina predicciones por votación.

```python
VotingClassifier([
    ('rf', RandomForestClassifier()),
    ('xgb', XGBClassifier())
], voting='soft')
```

---

## W

### Weights & Biases (W&B)
**Definición:** Plataforma SaaS para experiment tracking con visualizaciones avanzadas.

**Relacionados:** MLflow, Experiment Tracking

---

### Workflow (GitHub Actions)
**Definición:** Proceso automatizado definido en archivo YAML.

**Relacionados:** Job, Step, CI/CD

---

## X

### XGBoost
**Definición:** Implementación optimizada de gradient boosting. Muy popular en competencias.

```python
from xgboost import XGBClassifier
model = XGBClassifier(n_estimators=100, learning_rate=0.1)
```

---

## Y

### YAML
**Definición:** Formato de serialización legible para configuración.

```yaml
model:
  type: ensemble
  n_estimators: 100
```

---

## Z

### Zero-Downtime Deployment
**Definición:** Actualizar aplicación sin interrumpir servicio.

**Técnicas:** Rolling update, Blue-green deployment

---

## Símbolos y Abreviaciones

| Símbolo | Significado |
|---------|-------------|
| TP | True Positive |
| TN | True Negative |
| FP | False Positive |
| FN | False Negative |
| P95 | Percentil 95 |
| GHCR | GitHub Container Registry |
| IaC | Infrastructure as Code |
| DAG | Directed Acyclic Graph |
| OOM | Out of Memory |
| CRUD | Create, Read, Update, Delete |
| SLA | Service Level Agreement |
| SLO | Service Level Objective |
| TTL | Time To Live |

---

## 📊 Tablas de Referencia Rápida

### Métricas de Clasificación

| Métrica | Fórmula | Uso |
|---------|---------|-----|
| Accuracy | (TP+TN)/(Total) | Balance general (clases balanceadas) |
| Precision | TP/(TP+FP) | Minimizar falsos positivos |
| Recall | TP/(TP+FN) | Minimizar falsos negativos |
| F1 | 2×P×R/(P+R) | Balance P y R |
| AUC-ROC | Área bajo curva | Capacidad discriminatoria |

### Tipos de Testing

| Tipo | Alcance | Ejemplo |
|------|---------|---------|
| Unit | Función individual | `test_compute_ratio()` |
| Integration | Múltiples componentes | `test_pipeline_fit()` |
| E2E | Sistema completo | `test_api_predict_flow()` |

### Ambientes

| Ambiente | Propósito | Datos |
|----------|-----------|-------|
| Development | Desarrollo | Sintéticos/muestra |
| Staging | Testing final | Réplica producción |
| Production | Usuarios reales | Reales |

---

<div align="center">

### Navegación

| ◀️ Anterior | 📑 Índice | ▶️ Siguiente |
|:-----------|:---------:|:------------|
| [20_PROYECTO_INTEGRADOR.md](20_PROYECTO_INTEGRADOR.md) | [Índice](00_INDICE.md) | [22_CHECKLIST.md](22_CHECKLIST.md) |

---

*© 2025 DuqueOM - Guía MLOps v5.0: Senior Edition*

**Módulo 21 Completado** ✅

</div>
