# 🎯 Simulacro de Entrevista Junior ML Engineer
## Portafolio MLOps — 50 Preguntas Fundamentales

**Autor del Portafolio**: Daniel Duque (DuqueOM)  
**Versión**: 1.0  
**Fecha**: Diciembre 2025  
**Nivel**: Junior (0-2 años de experiencia)

---

## 📋 Índice

1. [Python Básico](#1-python-básico-preguntas-1-10)
2. [Machine Learning Fundamentos](#2-machine-learning-fundamentos-preguntas-11-20)
3. [Datos y Preprocesamiento](#3-datos-y-preprocesamiento-preguntas-21-30)
4. [Git y Herramientas](#4-git-y-herramientas-preguntas-31-40)
5. [Práctica con el Portafolio](#5-práctica-con-el-portafolio-preguntas-41-50)

---

## 🎯 Antes de Empezar

### ¿Qué se espera de un Junior?

| Lo que SÍ se espera | Lo que NO se espera |
|---------------------|---------------------|
| Fundamentos sólidos de Python | Diseño de arquitecturas complejas |
| Entender train/test split | Optimización de hiperparámetros avanzada |
| Saber qué es overfitting | Implementar MLOps completo |
| Usar Git básico | CI/CD avanzado |
| Leer y modificar código existente | Escribir código de producción desde cero |
| Hacer preguntas inteligentes | Tener todas las respuestas |

### Consejos para la Entrevista

1. **Sé honesto**: "No lo sé, pero lo investigaría así..." es mejor que inventar
2. **Muestra curiosidad**: Haz preguntas sobre el código que ves
3. **Relaciona con el portafolio**: "En BankChurn aprendí que..."
4. **Piensa en voz alta**: El proceso importa más que la respuesta perfecta

---

# 1. Python Básico (Preguntas 1-10)

## Pregunta 1: Tipos de Datos
**¿Cuál es la diferencia entre lista, tupla y diccionario?**

### Respuesta:
```python
# Lista: mutable, ordenada
features = ["age", "salary", "tenure"]
features.append("score")  # OK

# Tupla: inmutable, ordenada
coordinates = (40.7, -74.0)
# coordinates[0] = 41.0  # ERROR

# Diccionario: mutable, key-value
customer = {"id": 123, "name": "John", "churn": False}
customer["score"] = 0.85  # OK
```

**Cuándo usar cada uno**:
- **Lista**: Colección que cambiará (features a seleccionar)
- **Tupla**: Datos que no deben cambiar (coordenadas, constantes)
- **Diccionario**: Acceso por clave (configuración, datos de cliente)

---

## Pregunta 2: List Comprehension
**Reescribe este código con list comprehension:**
```python
result = []
for x in range(10):
    if x % 2 == 0:
        result.append(x**2)
```

### Respuesta:
```python
result = [x**2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]
```

**Ventajas**:
- Más conciso
- Más rápido (optimizado internamente)
- Más "pythónico"

---

## Pregunta 3: Funciones y Argumentos
**¿Qué hace `*args` y `**kwargs`?**

### Respuesta:
```python
def log_experiment(*args, **kwargs):
    # args: tupla de argumentos posicionales
    # kwargs: diccionario de argumentos con nombre
    print(f"Metrics: {args}")
    print(f"Config: {kwargs}")

log_experiment(0.85, 0.82, model="rf", n_estimators=100)
# Metrics: (0.85, 0.82)
# Config: {'model': 'rf', 'n_estimators': 100}
```

**En el portafolio** (`BankChurn/trainer.py`):
```python
def __init__(self, config: BankChurnConfig, **kwargs):
    self.config = config
    self.extra_params = kwargs  # Flexibilidad para params adicionales
```

---

## Pregunta 4: Manejo de Errores
**¿Por qué usamos try/except?**

### Respuesta:
```python
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df
    except FileNotFoundError:
        print(f"Error: {path} no existe")
        raise
    except pd.errors.EmptyDataError:
        print("Error: archivo vacío")
        raise
```

**Buenas prácticas**:
- Capturar excepciones específicas, no genéricas
- Hacer logging del error
- Re-lanzar si no puedes manejarlo

---

## Pregunta 5: Import y Módulos
**¿Cuál es la diferencia entre estas formas de import?**

### Respuesta:
```python
# Importar módulo completo
import pandas as pd
df = pd.read_csv("data.csv")

# Importar función específica
from sklearn.model_selection import train_test_split
X_train, X_test = train_test_split(X)

# Importar todo (⚠️ evitar en producción)
from math import *  # Contamina el namespace
```

**Best practice**: Importar lo que necesitas, usar alias estándar (`pd`, `np`, `plt`).

---

## Pregunta 6: Type Hints
**¿Qué significan los type hints y por qué usarlos?**

### Respuesta:
```python
def predict_churn(
    credit_score: int,
    age: int,
    is_active: bool
) -> float:
    """Retorna probabilidad de churn."""
    ...
```

**Beneficios**:
1. **Documentación**: Claro qué espera y retorna
2. **IDE support**: Autocompletado, detección de errores
3. **Tooling**: `mypy` puede verificar tipos

**En el portafolio**: Todos los archivos usan type hints (`config.py`, `training.py`).

---

## Pregunta 7: Clases Básicas
**¿Qué es `__init__` y `self`?**

### Respuesta:
```python
class BankChurnTrainer:
    def __init__(self, config):
        # Constructor: se ejecuta al crear instancia
        self.config = config  # self = esta instancia
        self.model_ = None
    
    def train(self, X, y):
        # self permite acceder a atributos de la instancia
        if self.config.model_type == "rf":
            self.model_ = RandomForestClassifier()
        self.model_.fit(X, y)

# Uso
trainer = BankChurnTrainer(config)  # __init__ se llama aquí
trainer.train(X, y)
```

---

## Pregunta 8: Lectura de Archivos
**¿Cómo lees un archivo CSV con pandas?**

### Respuesta:
```python
import pandas as pd

# Básico
df = pd.read_csv("data/raw/Churn.csv")

# Con opciones
df = pd.read_csv(
    "data/raw/Churn.csv",
    sep=",",
    encoding="utf-8",
    na_values=["", "NA", "null"],
    dtype={"customer_id": str}
)

# Verificar
print(df.shape)       # (10000, 14)
print(df.info())      # Tipos y nulls
print(df.head())      # Primeras filas
```

---

## Pregunta 9: Entornos Virtuales
**¿Por qué usamos entornos virtuales?**

### Respuesta:
```bash
# Crear entorno
python -m venv .venv

# Activar
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

**Razones**:
1. **Aislamiento**: Cada proyecto tiene sus propias versiones
2. **Reproducibilidad**: Mismo entorno en cualquier máquina
3. **Evita conflictos**: sklearn 1.3 en proyecto A, sklearn 1.2 en proyecto B

---

## Pregunta 10: Debugging Básico
**¿Cómo depuras código en Python?**

### Respuesta:
```python
# 1. Print statements (básico pero útil)
print(f"X shape: {X.shape}, y shape: {y.shape}")

# 2. Usar assert
assert X.shape[0] == y.shape[0], "Mismatch en filas"

# 3. Breakpoints en IDE (recomendado)
# Poner breakpoint y usar F5 para debugear

# 4. pdb (en terminal)
import pdb; pdb.set_trace()

# 5. Logging (producción)
import logging
logging.debug(f"Loaded {len(df)} rows")
```

---

# 2. Machine Learning Fundamentos (Preguntas 11-20)

## Pregunta 11: Train/Test Split
**¿Por qué separamos datos en train y test?**

### Respuesta:
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,      # 80/20 split
    random_state=42,    # Reproducibilidad
    stratify=y          # Mantener proporción de clases
)
```

**Razón**: Evaluar cómo el modelo generaliza a datos **nunca vistos**.
- **Train**: Aprende patrones
- **Test**: Simula producción, mide rendimiento real

**Error común**: Usar test para ajustar modelo → overfitting al test.

---

## Pregunta 12: Overfitting vs Underfitting
**Explica overfitting y underfitting.**

### Respuesta:

| Concepto | Síntomas | Causa | Solución |
|----------|----------|-------|----------|
| **Overfitting** | Train acc: 99%, Test acc: 70% | Modelo muy complejo | Regularización, más datos, simplificar |
| **Underfitting** | Train acc: 60%, Test acc: 58% | Modelo muy simple | Más features, modelo más complejo |

```python
# Detectar en el portafolio
print(f"Train accuracy: {model.score(X_train, y_train):.2%}")
print(f"Test accuracy: {model.score(X_test, y_test):.2%}")

# Si diferencia > 10%, posible overfitting
```

---

## Pregunta 13: Clasificación vs Regresión
**¿Cuándo usar clasificación y cuándo regresión?**

### Respuesta:

| Problema | Tipo | Target | Métrica |
|----------|------|--------|---------|
| ¿Cliente hará churn? | Clasificación | Sí/No (0/1) | Accuracy, F1, AUC |
| ¿Cuánto cuesta el auto? | Regresión | Precio ($) | RMSE, MAE, R² |
| ¿Qué plan elegirá? | Clasificación multiclase | A/B/C | Accuracy, F1 macro |

**En el portafolio**:
- **BankChurn**: Clasificación binaria (churn: 0/1)
- **CarVision**: Regresión (precio continuo)
- **TelecomAI**: Clasificación multiclase (tipo de plan)

---

## Pregunta 14: Cross-Validation
**¿Qué es cross-validation y por qué usarla?**

### Respuesta:
```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=5)
print(f"Accuracy: {scores.mean():.3f} (+/- {scores.std()*2:.3f})")
```

**Proceso K-Fold (K=5)**:
1. Divide datos en 5 partes iguales
2. Entrena en 4, valida en 1
3. Repite 5 veces (cada parte es validación una vez)
4. Promedia resultados

**Ventajas**:
- Usa todos los datos para entrenar y validar
- Estimación más robusta del rendimiento
- Detecta variabilidad del modelo

---

## Pregunta 15: Feature Scaling
**¿Por qué normalizamos features?**

### Respuesta:
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# Antes: age=[18-92], salary=[20000-200000]
# Después: ambas con media=0, std=1
```

**Razones**:
1. **Algoritmos sensibles a escala**: SVM, KNN, redes neuronales
2. **Gradiente descent**: Converge más rápido
3. **Interpretación**: Coeficientes comparables

**Algoritmos que NO necesitan scaling**: Random Forest, Decision Tree, XGBoost.

---

## Pregunta 16: One-Hot Encoding
**¿Cómo manejas variables categóricas?**

### Respuesta:
```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = encoder.fit_transform(df[['Geography', 'Gender']])

# Geography: France, Germany, Spain
# → Geography_France, Geography_Germany, Geography_Spain
```

**Alternativas**:
- **Label Encoding**: Para ordinales (Bajo < Medio < Alto)
- **Target Encoding**: Codifica con la media del target (⚠️ riesgo de leakage)

---

## Pregunta 17: Missing Values
**¿Cómo manejas valores faltantes?**

### Respuesta:
```python
from sklearn.impute import SimpleImputer

# Numéricos: media o mediana
imputer_num = SimpleImputer(strategy='median')

# Categóricos: moda o valor constante
imputer_cat = SimpleImputer(strategy='constant', fill_value='Unknown')
```

**Estrategias**:
| Caso | Estrategia |
|------|------------|
| Pocos missing (<5%) | Imputar con media/moda |
| Muchos missing | Considerar eliminar columna |
| Missing tiene significado | Crear feature `is_missing` |

---

## Pregunta 18: Random Forest
**Explica cómo funciona Random Forest.**

### Respuesta:
```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=100,  # 100 árboles
    max_depth=10,      # Profundidad máxima
    random_state=42
)
```

**Concepto simple**:
1. Crea N árboles de decisión
2. Cada árbol usa subset aleatorio de datos y features
3. Predicción final = voto mayoritario (clasificación) o promedio (regresión)

**Ventajas**: Robusto, pocas configuraciones, maneja bien missing values.

---

## Pregunta 19: Métricas de Clasificación
**¿Qué es accuracy, precision, recall y F1?**

### Respuesta:
```python
from sklearn.metrics import classification_report

print(classification_report(y_test, y_pred))
```

| Métrica | Fórmula | Cuándo priorizar |
|---------|---------|------------------|
| **Accuracy** | Correctos / Total | Clases balanceadas |
| **Precision** | TP / (TP + FP) | Costo alto de falsos positivos |
| **Recall** | TP / (TP + FN) | Costo alto de falsos negativos |
| **F1** | 2 × (P × R) / (P + R) | Balance entre P y R |

**En BankChurn**: Priorizo **Recall** (no queremos perder clientes que harán churn).

---

## Pregunta 20: Curva ROC y AUC
**¿Qué es AUC-ROC?**

### Respuesta:
```python
from sklearn.metrics import roc_auc_score, roc_curve

# AUC: Área bajo la curva ROC
auc = roc_auc_score(y_test, y_pred_proba[:, 1])
print(f"AUC: {auc:.3f}")
```

**Interpretación**:
- **AUC = 1.0**: Clasificador perfecto
- **AUC = 0.5**: Clasificador aleatorio
- **AUC > 0.8**: Generalmente bueno

**Ventaja**: Funciona bien con clases desbalanceadas.

---

# 3. Datos y Preprocesamiento (Preguntas 21-30)

## Pregunta 21: Exploración de Datos
**¿Qué haces primero cuando recibes un dataset?**

### Respuesta:
```python
import pandas as pd

df = pd.read_csv("data.csv")

# 1. Dimensiones
print(f"Shape: {df.shape}")  # (filas, columnas)

# 2. Tipos de datos
print(df.dtypes)

# 3. Missing values
print(df.isnull().sum())

# 4. Estadísticas básicas
print(df.describe())

# 5. Primeras filas
print(df.head())

# 6. Target distribution
print(df['target'].value_counts(normalize=True))
```

---

## Pregunta 22: Detección de Outliers
**¿Cómo detectas outliers?**

### Respuesta:
```python
import numpy as np

# Método IQR
Q1 = df['Balance'].quantile(0.25)
Q3 = df['Balance'].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

outliers = df[(df['Balance'] < lower) | (df['Balance'] > upper)]
print(f"Outliers: {len(outliers)}")
```

**Qué hacer con outliers**:
1. Verificar si son errores de datos → corregir
2. Si son legítimos → considerar winsorization o mantener
3. Para modelos sensibles → eliminar o transformar

---

## Pregunta 23: Correlación
**¿Cómo identificas features correlacionadas?**

### Respuesta:
```python
import seaborn as sns
import matplotlib.pyplot as plt

# Matriz de correlación
corr = df.corr()

# Heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.show()

# Features altamente correlacionadas (>0.9)
high_corr = (corr.abs() > 0.9) & (corr != 1.0)
```

**¿Por qué importa?** Features muy correlacionadas son redundantes → considerar eliminar una.

---

## Pregunta 24: Desbalance de Clases
**¿Qué haces cuando tienes 95% clase A y 5% clase B?**

### Respuesta:
```python
# 1. Cambiar métrica (no usar accuracy)
from sklearn.metrics import f1_score, recall_score

# 2. Class weights
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(class_weight='balanced')

# 3. Oversampling (SMOTE)
from imblearn.over_sampling import SMOTE
X_res, y_res = SMOTE().fit_resample(X, y)

# 4. Undersampling
from imblearn.under_sampling import RandomUnderSampler
```

**En BankChurn**: 80/20 balance → usamos `class_weight='balanced'` y F1.

---

## Pregunta 25: Feature Selection
**¿Cómo seleccionas features importantes?**

### Respuesta:
```python
from sklearn.ensemble import RandomForestClassifier

# 1. Feature importance de RF
rf = RandomForestClassifier().fit(X, y)
importances = pd.DataFrame({
    'feature': X.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

# 2. Correlación con target
correlations = df.corr()['target'].abs().sort_values(ascending=False)

# 3. SelectKBest
from sklearn.feature_selection import SelectKBest, f_classif
selector = SelectKBest(f_classif, k=10)
X_selected = selector.fit_transform(X, y)
```

---

## Pregunta 26: Data Leakage
**¿Qué es data leakage y cómo evitarlo?**

### Respuesta:
Data leakage = cuando información del futuro o del target filtra al entrenamiento.

```python
# ❌ MAL: fit scaler en TODO antes de split
scaler.fit(X)  # Ve datos de test
X_train, X_test = train_test_split(X)

# ✅ BIEN: fit solo en train
X_train, X_test = train_test_split(X)
scaler.fit(X_train)  # Solo ve train
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)
```

**En el portafolio**: Usamos Pipeline de sklearn que maneja esto automáticamente.

---

## Pregunta 27: Pipelines de sklearn
**¿Por qué usar Pipeline?**

### Respuesta:
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier())
])

# Un solo fit/predict
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
```

**Beneficios**:
1. **Evita leakage**: fit solo en train automáticamente
2. **Código limpio**: Todo en un objeto
3. **Fácil deploy**: `joblib.dump(pipe, 'model.joblib')`
4. **Reproducibilidad**: Mismo proceso siempre

---

## Pregunta 28: Guardado de Modelos
**¿Cómo guardas y cargas un modelo entrenado?**

### Respuesta:
```python
import joblib

# Guardar
joblib.dump(model, 'artifacts/model.joblib')

# Cargar
model = joblib.load('artifacts/model.joblib')

# Usar
prediction = model.predict(new_data)
```

**En producción** (FastAPI):
```python
@lru_cache()
def load_model():
    return joblib.load("artifacts/pipeline.joblib")
```

---

## Pregunta 29: Validación de Datos
**¿Cómo validas que los datos de entrada son correctos?**

### Respuesta:
```python
from pydantic import BaseModel, Field, validator

class CustomerInput(BaseModel):
    credit_score: int = Field(ge=300, le=850)
    age: int = Field(ge=18, le=100)
    geography: str
    
    @validator('geography')
    def geography_valid(cls, v):
        valid = ['France', 'Germany', 'Spain']
        if v not in valid:
            raise ValueError(f'Must be one of {valid}')
        return v
```

**Beneficios**: Errores claros antes de llegar al modelo.

---

## Pregunta 30: Reproducibilidad
**¿Cómo garantizas que tu experimento sea reproducible?**

### Respuesta:
```python
import random
import numpy as np

# 1. Fijar seeds
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# 2. En modelos
model = RandomForestClassifier(random_state=SEED)

# 3. En split
train_test_split(X, y, random_state=SEED)

# 4. Documentar versiones
# requirements.txt o pyproject.toml con versiones fijas
```

---

# 4. Git y Herramientas (Preguntas 31-40)

## Pregunta 31: Git Básico
**¿Cuál es el flujo básico de Git?**

### Respuesta:
```bash
# 1. Ver estado
git status

# 2. Añadir cambios
git add .                     # Todo
git add archivo.py            # Específico

# 3. Commit
git commit -m "feat: add preprocessing step"

# 4. Push
git push origin main

# 5. Pull (obtener cambios)
git pull origin main
```

---

## Pregunta 32: Branches
**¿Por qué usar branches?**

### Respuesta:
```bash
# Crear branch
git checkout -b feature/add-validation

# Trabajar...
git add .
git commit -m "feat: add pydantic validation"

# Push branch
git push origin feature/add-validation

# Crear Pull Request en GitHub
# Después de aprobar, merge a main
```

**Razones**:
- Aislar cambios
- Revisar código antes de merge
- Mantener main siempre funcional

---

## Pregunta 33: .gitignore
**¿Qué debe ir en .gitignore?**

### Respuesta:
```gitignore
# Datos (grandes, sensibles)
data/
*.csv
*.parquet

# Artefactos
artifacts/
*.joblib
*.pkl

# Entornos
.venv/
__pycache__/

# IDEs
.vscode/
.idea/

# Logs
*.log
mlruns/
```

**Regla**: No subir datos grandes, artefactos binarios, ni secretos.

---

## Pregunta 34: Requirements
**¿Cómo manejas dependencias?**

### Respuesta:
```bash
# Crear requirements.txt
pip freeze > requirements.txt

# Mejor: usar pip-tools
pip-compile requirements.in > requirements.txt

# Instalar
pip install -r requirements.txt

# Moderno: pyproject.toml
pip install -e ".[dev]"
```

---

## Pregunta 35: Makefile
**¿Para qué sirve un Makefile?**

### Respuesta:
```makefile
.PHONY: install test train

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src

train:
	python main.py --config configs/config.yaml

lint:
	ruff check src/
```

**Uso**:
```bash
make install
make test
make train
```

**Beneficio**: Comandos estándar, documentados, fáciles de recordar.

---

## Pregunta 36: pytest Básico
**¿Cómo escribes un test básico?**

### Respuesta:
```python
# tests/test_data.py
import pytest
import pandas as pd

def test_load_data():
    df = pd.read_csv("data/raw/sample.csv")
    assert len(df) > 0
    assert "target" in df.columns

def test_no_nulls_in_target():
    df = pd.read_csv("data/raw/sample.csv")
    assert df["target"].isnull().sum() == 0

# Ejecutar
# pytest tests/test_data.py -v
```

---

## Pregunta 37: Estructura de Proyecto
**¿Cómo organizas un proyecto ML?**

### Respuesta:
```
mi-proyecto/
├── src/miproyecto/     # Código fuente
│   ├── __init__.py
│   ├── config.py       # Configuración
│   ├── data.py         # Carga de datos
│   ├── features.py     # Feature engineering
│   └── training.py     # Entrenamiento
├── app/                # APIs
├── tests/              # Tests
├── configs/            # YAML configs
├── data/raw/           # Datos
├── artifacts/          # Modelos guardados
├── pyproject.toml      # Dependencias
├── Makefile           
└── README.md
```

---

## Pregunta 38: README
**¿Qué debe tener un buen README?**

### Respuesta:
```markdown
# Nombre del Proyecto

## Descripción
Qué hace el proyecto, problema que resuelve.

## Instalación
```bash
pip install -e .
```

## Uso Rápido
```python
from miproyecto import predict
result = predict(data)
```

## Estructura
Árbol de directorios.

## Tests
```bash
make test
```

## Autor
Nombre, contacto.
```

---

## Pregunta 39: Docker Básico
**¿Qué es Docker y por qué usarlo?**

### Respuesta:
Docker empaqueta tu aplicación con todas sus dependencias.

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

```bash
# Construir
docker build -t mi-app .

# Ejecutar
docker run mi-app
```

**Beneficio**: "Funciona en mi máquina" → Funciona en cualquier máquina.

---

## Pregunta 40: APIs Básicas
**¿Qué es una API REST?**

### Respuesta:
API = Interfaz para que otros programas usen tu código.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: dict):
    # Usar modelo
    return {"prediction": result}
```

```bash
# Ejecutar
uvicorn app:app --reload

# Probar
curl http://localhost:8000/health
```

---

# 5. Práctica con el Portafolio (Preguntas 41-50)

## Pregunta 41: Describir el Portafolio
**Cuéntame sobre el portafolio.**

### Respuesta:
"Es un portafolio de MLOps con 3 proyectos production-ready:

1. **BankChurn-Predictor**: Clasificación binaria para predecir churn de clientes bancarios. Pipeline sklearn unificado, FastAPI, 79% coverage.

2. **CarVision-Market-Intelligence**: Regresión para predecir precios de autos usados. FeatureEngineer centralizado, Streamlit dashboard.

3. **TelecomAI**: Clasificación multiclase para segmentación de clientes de telecom.

Todos siguen las mismas prácticas: estructura src/, Pydantic para configs, pytest, GitHub Actions CI."

---

## Pregunta 42: Ejecutar el Proyecto
**¿Cómo ejecuto BankChurn?**

### Respuesta:
```bash
# 1. Clonar
git clone https://github.com/duqueom/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio/BankChurn-Predictor

# 2. Crear entorno
python -m venv .venv
source .venv/bin/activate

# 3. Instalar
pip install -e ".[dev]"

# 4. Entrenar
python main.py --config configs/config.yaml

# 5. API
uvicorn app.fastapi_app:app --reload

# 6. Tests
pytest tests/ -v
```

---

## Pregunta 43: Entender el Pipeline
**¿Cómo funciona el pipeline de BankChurn?**

### Respuesta:
```python
# 1. Cargar config
config = BankChurnConfig.from_yaml("configs/config.yaml")

# 2. Cargar datos
df = pd.read_csv(config.data.raw_path)

# 3. Crear trainer
trainer = Trainer(config)

# 4. Entrenar (dentro crea Pipeline sklearn)
trainer.fit(X, y)
# Pipeline = [preprocessor, model]
# preprocessor = ColumnTransformer(numeric_pipe, categorical_pipe)

# 5. Evaluar
metrics = trainer.evaluate(X_test, y_test)

# 6. Guardar
trainer.save("artifacts/")
```

---

## Pregunta 44: Modificar el Código
**¿Cómo añadirías una nueva feature?**

### Respuesta:
```python
# 1. En config.yaml, añadir columna
features:
  numerical:
    - CreditScore
    - Age
    - NewFeature  # Nueva

# 2. Si requiere transformación, editar FeatureEngineer
class FeatureEngineer:
    def transform(self, X):
        X['NewFeature'] = X['Col1'] / X['Col2']
        return X

# 3. Agregar test
def test_new_feature():
    fe = FeatureEngineer()
    result = fe.transform(sample_df)
    assert 'NewFeature' in result.columns

# 4. Ejecutar tests
pytest tests/test_features.py -v
```

---

## Pregunta 45: Leer un Error
**Este código falla. ¿Por qué?**
```python
X_train = scaler.fit_transform(X_train)
X_test = scaler.fit_transform(X_test)
```

### Respuesta:
**Problema**: `fit_transform` en test causa data leakage.

```python
# ✅ Correcto
X_train = scaler.fit_transform(X_train)  # fit + transform
X_test = scaler.transform(X_test)        # solo transform
```

El scaler debe aprender (fit) solo de training data.

---

## Pregunta 46: Interpretar Métricas
**El modelo tiene accuracy 95% pero el negocio no está contento. ¿Por qué?**

### Respuesta:
Posibles razones:

1. **Clases desbalanceadas**: Si 95% son clase 0, predecir siempre 0 da 95% accuracy pero es inútil.

2. **Métrica incorrecta**: El negocio necesita recall (no perder churners) pero optimizaste accuracy.

3. **Falsos negativos costosos**: Cada cliente que hace churn y no detectamos cuesta $X.

**Solución**: Usar F1, recall, o una métrica de negocio (costo).

---

## Pregunta 47: Configuración YAML
**¿Por qué usar archivos YAML para configuración?**

### Respuesta:
```yaml
# configs/config.yaml
model:
  type: "random_forest"
  n_estimators: 100
  max_depth: 10

data:
  raw_path: "data/raw/Churn.csv"
  test_size: 0.2

training:
  random_state: 42
```

**Ventajas**:
1. **Separación**: Cambiar parámetros sin tocar código
2. **Versionable**: Git puede trackear cambios
3. **Legible**: Fácil de entender
4. **Reproducibilidad**: Guardar config de cada experimento

---

## Pregunta 48: CI/CD Básico
**¿Qué hace el workflow de GitHub Actions?**

### Respuesta:
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v
```

**Flujo**:
1. Push código → GitHub Actions se activa
2. Crea máquina virtual limpia
3. Instala dependencias
4. Ejecuta tests
5. Reporta pass/fail

---

## Pregunta 49: Debugging en Producción
**El API retorna error 500. ¿Cómo lo depuras?**

### Respuesta:
```python
# 1. Ver logs
uvicorn app:app --log-level debug

# 2. Añadir logging
import logging
logging.basicConfig(level=logging.DEBUG)

@app.post("/predict")
def predict(data: Input):
    logging.debug(f"Input: {data}")
    try:
        result = model.predict(...)
        logging.debug(f"Result: {result}")
        return result
    except Exception as e:
        logging.error(f"Error: {e}")
        raise

# 3. Probar localmente
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"credit_score": 650, ...}'
```

---

## Pregunta 50: Próximos Pasos
**¿Qué aprenderías después de este portafolio?**

### Respuesta:
"Con las bases del portafolio, me gustaría profundizar en:

1. **MLflow/Experiment Tracking**: Ya está configurado, pero quiero usarlo más para comparar experimentos sistemáticamente.

2. **Docker avanzado**: Optimizar imágenes, multi-stage builds.

3. **Testing más robusto**: Añadir tests de integración, property-based testing.

4. **Kubernetes básico**: Entender cómo escalar los servicios.

5. **Monitoreo en producción**: Detectar drift, alertas.

El portafolio me dio la base; ahora quiero profundizar en cada área."

---

# 📚 Recursos para Preparación

## Módulos de la Guía Relacionados

| Pregunta | Módulo |
|----------|--------|
| Python básico | [01_PYTHON_MODERNO.md](01_PYTHON_MODERNO.md) |
| ML fundamentos | [07_SKLEARN_PIPELINES.md](07_SKLEARN_PIPELINES.md), [08_INGENIERIA_FEATURES.md](08_INGENIERIA_FEATURES.md) |
| Git | [05_GIT_PROFESIONAL.md](05_GIT_PROFESIONAL.md) |
| Testing | [11_TESTING_ML.md](11_TESTING_ML.md) |
| APIs | [14_FASTAPI.md](14_FASTAPI.md) |

## Checklist Pre-Entrevista

- [ ] Puedo ejecutar `make install && make test` en BankChurn
- [ ] Entiendo qué hace cada archivo en `src/bankchurn/`
- [ ] Sé explicar train/test split y por qué importa
- [ ] Puedo leer y modificar el `config.yaml`
- [ ] Entiendo el flujo Git básico

---

<div align="center">

**¡Éxito en tu entrevista! 🚀**

*Recuerda: ser Junior significa estar aprendiendo. Muestra curiosidad y ganas de aprender.*

[← Índice](00_INDICE.md) | [Simulacro Mid →](SIMULACRO_ENTREVISTA_MID.md) | [Simulacro Senior →](SIMULACRO_ENTREVISTA_SENIOR_PARTE1.md)

</div>
