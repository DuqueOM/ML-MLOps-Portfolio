# 08. Ingeniería de Features para ML

## 🎯 Objetivo del Módulo

Dominar la creación de features sin introducir **data leakage**, el error más peligroso y difícil de detectar en ML.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🚨 DATA LEAKAGE: El Asesino Silencioso de Modelos                           ║
║                                                                              ║
║  Tu modelo tiene 99% accuracy en validación...                               ║
║  ...pero 50% en producción.                                                  ║
║                                                                              ║
║  ¿Por qué? Porque durante el entrenamiento, el modelo "vio" información      ║
║  que NO tendrá disponible cuando haga predicciones reales.                   ║
║                                                                              ║
║  Es como estudiar para un examen con las respuestas en la mano.              ║
║  Sacas 100 en el examen de práctica, pero 0 en el real.                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Contenido

1. [¿Qué es Data Leakage?](#81-qué-es-data-leakage)
2. [Tipos de Leakage en ML](#82-tipos-de-leakage)
3. [Caso Real: CarVision](#83-caso-real-carvision)
4. [Prevención con Pipelines](#84-prevención-con-pipelines)
5. [Feature Engineering Seguro](#85-feature-engineering-seguro)

---

## 8.1 ¿Qué es Data Leakage?

### La Analogía del Detective

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  🔍 IMAGINA UN DETECTIVE RESOLVIENDO UN CASO:                             ║
║                                                                           ║
║  SIN LEAKAGE (correcto):                                                  ║
║  • El detective solo tiene las pistas disponibles AL MOMENTO del crimen   ║
║  • Debe deducir quién es el culpable con información limitada             ║
║  • Es difícil, pero es la realidad                                        ║
║                                                                           ║
║  CON LEAKAGE (trampa):                                                    ║
║  • El detective tiene acceso al informe FINAL del caso                    ║
║  • Ya sabe quién es el culpable antes de investigar                       ║
║  • "Resuelve" el caso fácilmente, pero no aprendió nada                   ║
║                                                                           ║
║  EN ML:                                                                   ║
║  • El modelo debe predecir usando SOLO información disponible             ║
║    en el momento de la predicción                                         ║
║  • Si usas información del futuro o del target, es TRAMPA                 ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Ejemplo Clásico: Predecir Precio con precio_per_mile

```python
# ❌ LEAKAGE: Usando feature derivada del target

# Datos originales
df = pd.DataFrame({
    'price': [15000, 25000, 35000],      # Target a predecir
    'odometer': [80000, 50000, 20000],
})

# Feature engineering INCORRECTO
df['price_per_mile'] = df['price'] / df['odometer']  # ← LEAKAGE!

# ¿Por qué es leakage?
# price_per_mile = price / odometer
# Por lo tanto: price = price_per_mile * odometer
# El modelo "aprende" a multiplicar, no a predecir precios reales

# En producción:
# - No tienes el price (es lo que quieres predecir)
# - No puedes calcular price_per_mile
# - El modelo no sabe qué hacer
```

---

## 8.2 Tipos de Leakage

### 1. Target Leakage (Feature contiene información del target)

```python
# ❌ MALO: Feature calculada con el target
df['price_category'] = pd.cut(df['price'], bins=[0, 10000, 50000, inf])

# El modelo aprende: "si price_category es 'alto', predice price alto"
# Pero en producción NO tienes price_category porque no tienes price
```

### 2. Train-Test Contamination (Datos de test "filtrados" a train)

```python
# ❌ MALO: Normalizar ANTES de split
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # ← Usa estadísticas de TODO X
X_train, X_test = train_test_split(X_scaled)
# El scaler "vio" datos de test durante fit

# ✅ CORRECTO: Normalizar DESPUÉS de split
X_train, X_test = train_test_split(X)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Solo train
X_test_scaled = scaler.transform(X_test)        # Usa params de train
```

### 3. Temporal Leakage (Usar información del futuro)

```python
# ❌ MALO: Predecir churn de enero usando datos de febrero
df['avg_purchases_next_month'] = ...  # Información del futuro

# ✅ CORRECTO: Solo usar información disponible al momento de predicción
df['avg_purchases_last_3_months'] = ...  # Información del pasado
```

---

## 8.3 Caso Real: CarVision

### El Problema Original

En CarVision, teníamos features que causaban leakage:

```python
# src/carvision/features.py - ANTES (con leakage potencial)

class FeatureEngineer:
    def transform(self, X):
        X = X.copy()
        
        # ✅ OK: vehicle_age no depende del target
        X['vehicle_age'] = 2024 - X['model_year']
        
        # ✅ OK: brand no depende del target
        X['brand'] = X['model'].str.split().str[0]
        
        # ⚠️ PELIGRO: price_per_mile DEPENDE de price (target)
        X['price_per_mile'] = X['price'] / (X['odometer'] + 1)
        
        # ⚠️ PELIGRO: price_category DEPENDE de price (target)
        X['price_category'] = pd.cut(X['price'], ...)
        
        return X
```

### La Solución: drop_columns en Config

```yaml
# configs/config.yaml

preprocessing:
  numeric_features:
    - odometer
    - vehicle_age
  categorical_features:
    - fuel
    - transmission
    - brand
  drop_columns:           # ← Features que causan leakage
    - price_per_mile      # Depende de price
    - price_category      # Depende de price
```

```python
# src/carvision/data.py

def infer_feature_types(df, target, drop_columns=None, ...):
    """Infiere tipos de features, excluyendo las que causan leakage."""
    
    # Columnas a excluir
    exclude = {target}  # Siempre excluir el target
    if drop_columns:
        exclude.update(drop_columns)  # Excluir features con leakage
    
    # Inferir tipos solo de columnas seguras
    for col in df.columns:
        if col in exclude:
            continue  # Saltar columnas peligrosas
        # ... resto de la lógica
```

### ¿Por qué NO eliminamos price_per_mile del FeatureEngineer?

```python
# La feature EXISTE en el transformer, pero se ELIMINA antes del modelo

# Motivo: price_per_mile es útil para ANÁLISIS (no para predicción)
# En el dashboard de Streamlit, usamos price_per_mile para visualizaciones
# Pero en el modelo de predicción, la eliminamos

# Flujo:
# 1. FeatureEngineer crea price_per_mile (para análisis)
# 2. Config especifica drop_columns = [price_per_mile]
# 3. ColumnTransformer NO incluye price_per_mile en sus transformers
# 4. Modelo entrena sin price_per_mile
```

---

## 8.4 Prevención con Pipelines

### El Pipeline como Barrera Anti-Leakage

```python
# ✅ CORRECTO: Pipeline garantiza orden correcto

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Definir QUÉ columnas usar (excluyendo las peligrosas)
num_cols = ['odometer', 'vehicle_age']  # SIN price_per_mile
cat_cols = ['fuel', 'transmission', 'brand']

# Pipeline aplica transformaciones EN ORDEN
pipeline = Pipeline([
    ('features', FeatureEngineer()),      # Crea features
    ('pre', ColumnTransformer([           # Solo usa features SEGURAS
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(), cat_cols)
    ])),
    ('model', RandomForestRegressor())
])

# fit() entrena todo con datos de TRAIN solamente
pipeline.fit(X_train, y_train)

# predict() aplica las MISMAS transformaciones
# usando parámetros aprendidos de TRAIN
predictions = pipeline.predict(X_test)
```

### Diagrama del Flujo Seguro

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FLUJO ANTI-LEAKAGE CON PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ENTRENAMIENTO:                                                             │
│  ┌──────────┐    ┌────────────────┐    ┌────────────┐    ┌──────────┐       │
│  │ X_train  │───►│FeatureEng      │───►│DropDanger  │───►│ Scaler   │       │
│  │          │    │ (crea features)│    │ (elimina   │    │ fit()    │       │
│  └──────────┘    └────────────────┘    │  leakage)  │    └────┬─────┘       │
│                                        └────────────┘         │             │
│                                                               ▼             │
│                                                        ┌──────────┐         │
│                                                        │  Model   │         │
│                                                        │  fit()   │         │
│                                                        └──────────┘         │
│                                                                             │
│  PREDICCIÓN:                                                                │
│  ┌──────────┐    ┌──────────────┐    ┌────────────┐    ┌──────────┐         │
│  │ X_new    │───►│FeatureEng    │───►│DropDanger  │───►│ Scaler   │         │
│  │          │    │ (mismas feat)│    │ (mismas    │    │transform │         │
│  └──────────┘    └──────────────┘    │  columnas) │    │ (NO fit) │         │
│                                      └────────────┘    └────┬─────┘         │
│                                                             │               │
│                                                             ▼               │
│                                                      ┌──────────┐           │
│                                                      │  Model   │           │
│                                                      │ predict()│           │
│                                                      └──────────┘           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8.5 Feature Engineering Seguro

### Checklist Anti-Leakage

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  ✅ CHECKLIST ANTES DE CREAR UNA FEATURE                                  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  1. ¿Esta feature estará disponible en producción?                        ║
║     □ SÍ → OK                                                             ║
║     □ NO → ❌ NO USAR para predicción                                     ║
║                                                                           ║
║  2. ¿Esta feature usa información del target (directa o indirectamente)?  ║
║     □ NO → OK                                                             ║
║     □ SÍ → ❌ LEAKAGE - eliminar o recalcular sin target                  ║
║                                                                           ║
║  3. ¿Esta feature usa información del futuro?                             ║
║     □ NO → OK                                                             ║
║     □ SÍ → ❌ TEMPORAL LEAKAGE - usar solo datos pasados                  ║
║                                                                           ║
║  4. ¿Las estadísticas de esta feature se calcularon con datos de test?    ║
║     □ NO → OK                                                             ║
║     □ SÍ → ❌ TRAIN-TEST CONTAMINATION - recalcular solo con train        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Features Seguras vs Peligrosas

| Feature | Segura | Motivo |
|---------|:------:|--------|
| `vehicle_age = 2024 - model_year` | ✅ | No depende del target |
| `brand = model.split()[0]` | ✅ | No depende del target |
| `is_luxury = brand in ['bmw', 'mercedes']` | ✅ | No depende del target |
| `price_per_mile = price / odometer` | ❌ | Usa el target (price) |
| `price_category = cut(price)` | ❌ | Usa el target (price) |
| `avg_price_by_brand` (calculado con todo el dataset) | ❌ | Contamina train/test |

### Código: Feature Engineering Seguro

```python
# src/carvision/features.py - Versión SEGURA

class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Feature engineering sin leakage."""
    
    def __init__(self, current_year: int = None):
        self.current_year = current_year
    
    def fit(self, X, y=None):
        # Stateless: no aprende nada que pueda causar leakage
        return self
    
    def transform(self, X):
        X = X.copy()
        year = self.current_year or pd.Timestamp.now().year
        
        # ✅ SEGURO: Solo usa columnas de entrada (no target)
        if 'model_year' in X.columns:
            X['vehicle_age'] = year - X['model_year']
        
        if 'model' in X.columns:
            X['brand'] = X['model'].astype(str).str.split().str[0]
        
        # ⚠️ CONDICIONAL: Solo crear si price existe (para análisis)
        # El modelo NO usará estas features (drop_columns en config)
        if 'price' in X.columns and 'odometer' in X.columns:
            X['price_per_mile'] = X['price'] / (X['odometer'] + 1)
        
        return X
```

---

## ✅ Ejercicio: Detectar Leakage

```python
# Analiza este código y encuentra todos los casos de leakage

def prepare_data(df):
    # 1. Normalizar todas las features
    scaler = StandardScaler()
    df[['age', 'income']] = scaler.fit_transform(df[['age', 'income']])
    
    # 2. Crear features
    df['income_category'] = pd.cut(df['target_income'], bins=3)
    df['age_bucket'] = pd.cut(df['age'], bins=[0, 30, 50, 100])
    
    # 3. Split
    X_train, X_test = train_test_split(df.drop('target_income', axis=1))
    y_train, y_test = train_test_split(df['target_income'])
    
    return X_train, X_test, y_train, y_test
```

<details>
<summary>📝 Ver Solución</summary>

```python
# PROBLEMAS DETECTADOS:

# 1. ❌ TRAIN-TEST CONTAMINATION (línea 3-4)
# scaler.fit_transform se aplica a TODO el dataset antes del split
# El scaler "ve" estadísticas de test durante entrenamiento

# 2. ❌ TARGET LEAKAGE (línea 7)
# income_category se calcula usando target_income
# El modelo aprenderá a "leer" el target desde esta feature

# 3. ❌ SPLIT INCONSISTENTE (líneas 11-12)
# train_test_split se llama dos veces con diferentes random states
# X_train no corresponde con y_train

# VERSIÓN CORREGIDA:
def prepare_data_correct(df):
    # 1. Split PRIMERO
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # 2. Features SIN leakage
    for data in [train_df, test_df]:
        data['age_bucket'] = pd.cut(data['age'], bins=[0, 30, 50, 100])
        # NO crear income_category - usa el target
    
    # 3. Separar X e y
    X_train = train_df.drop('target_income', axis=1)
    y_train = train_df['target_income']
    X_test = test_df.drop('target_income', axis=1)
    y_test = test_df['target_income']
    
    # 4. Escalar SOLO con datos de train
    scaler = StandardScaler()
    X_train[['age', 'income']] = scaler.fit_transform(X_train[['age', 'income']])
    X_test[['age', 'income']] = scaler.transform(X_test[['age', 'income']])
    
    return X_train, X_test, y_train, y_test
```

</details>

---

## ✅ Checkpoint

- [ ] Entiendes qué es data leakage y por qué es peligroso
- [ ] Puedes identificar los 3 tipos de leakage
- [ ] Sabes cómo usar `drop_columns` para eliminar features peligrosas
- [ ] Entiendes por qué el Pipeline previene leakage
- [ ] Puedes aplicar el checklist anti-leakage a nuevas features

---

## 📦 Cómo se Usó en el Portafolio

El proyecto **CarVision** es el ejemplo principal de feature engineering seguro:

### FeatureEngineer Centralizado

```python
# CarVision-Market-Intelligence/src/carvision/features.py
class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Centraliza TODO el feature engineering.
    
    Usado en: training, FastAPI, Streamlit - siempre igual.
    """
    
    def __init__(self, current_year: int = None):
        self.current_year = current_year
    
    def transform(self, X):
        X = X.copy()
        year = self.current_year or pd.Timestamp.now().year
        
        # ✅ Features SEGURAS (no usan target)
        X['vehicle_age'] = year - X['model_year']
        X['brand'] = X['model'].str.split().str[0]
        X['mileage_category'] = pd.cut(X['odometer'], bins=[0, 50000, 100000, float('inf')])
        
        return X
```

### Prevención de Leakage en Config

```yaml
# CarVision-Market-Intelligence/configs/config.yaml
data:
  target_column: price
  drop_columns:
    - price_per_mile    # ❌ Usa target
    - price_category    # ❌ Usa target
    - id                # No predictivo
```

### Caso Real: Bug Corregido

El portafolio tuvo un bug de leakage que fue corregido:

```python
# ❌ ANTES (con leakage)
X['price_per_mile'] = X['price'] / X['odometer']  # Usaba el target!

# ✅ DESPUÉS (sin leakage)
# price_per_mile se elimina en drop_columns
# Solo se calcula para análisis exploratorio, NO para el modelo
```

### Archivos Clave

| Proyecto | Feature Engineering | Anti-Leakage |
|----------|--------------------|--------------| 
| CarVision | `src/carvision/features.py` | `drop_columns` en config |
| BankChurn | En `ColumnTransformer` | Sin features derivadas del target |
| TelecomAI | En pipeline | Sin features peligrosas |

### 🔧 Ejercicio: Audita CarVision

```bash
# 1. Revisa el FeatureEngineer
cat CarVision-Market-Intelligence/src/carvision/features.py

# 2. Verifica drop_columns en config
cat CarVision-Market-Intelligence/configs/config.yaml | grep -A5 "drop_columns"

# 3. Ejecuta tests para verificar que no hay leakage
cd CarVision-Market-Intelligence
pytest tests/test_features.py -v
```

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **Feature Store**: Explica por qué centralizar features mejora consistencia training/serving.

2. **Data Leakage**: Da ejemplos concretos (usar target en features, información del futuro).

3. **Feature Selection**: Conoce métodos (mutual information, RFE, importancia de modelo).

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Features temporales | Cuidado con leakage: no uses info futura |
| Categorías nuevas | Usa `handle_unknown='ignore'` en encoders |
| Features de texto | TF-IDF para baseline, embeddings para avanzado |
| Interacciones | PolynomialFeatures con grado 2 máximo |

### Checklist de Feature Engineering

- [ ] Sin data leakage verificado
- [ ] Transformaciones aplicadas consistentemente train/serve
- [ ] Features documentadas (significado, fuente, transformación)
- [ ] Outliers manejados (clip, winsorize, o flag)
- [ ] Missing values con estrategia clara


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo |
|:--:|:--------|:-----|
| 🔴 | [Feature Engineering for ML - Krish Naik](https://www.youtube.com/watch?v=6WDFfaYtN6s) | Video |
| 🟡 | [Avoiding Data Leakage](https://www.youtube.com/watch?v=NfOYWZnPK3I) | Video |

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **Data Leakage**: Filtración de información del target
- **Feature Engineering**: Creación de variables predictivas
- **ColumnTransformer**: Procesamiento paralelo de columnas

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 08:
- **8.1**: Detectar data leakage
- **8.2**: Pipeline sin leakage

---

<div align="center">

[← sklearn Pipelines](07_SKLEARN_PIPELINES.md) | [Siguiente: Training Profesional →](09_TRAINING_PROFESIONAL.md)

</div>
