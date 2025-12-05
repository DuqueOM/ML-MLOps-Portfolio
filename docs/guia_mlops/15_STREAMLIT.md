# 16. Streamlit Dashboards para ML

## 🎯 Objetivo del Módulo

Construir dashboards interactivos profesionales como el de CarVision.

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  Streamlit = La forma más rápida de crear UIs para ML                        ║
║                                                                              ║
║  ✅ Python puro (sin HTML/CSS/JS)                                            ║
║  ✅ Reactivo (cambios automáticos)                                           ║
║  ✅ Widgets interactivos                                                     ║
║  ✅ Integración con pandas/plotly                                            ║
║  ✅ Deploy fácil                                                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📋 Contenido

1. [Estructura de un Dashboard ML](#161-estructura-de-un-dashboard-ml)
2. [Caching para Performance](#162-caching-para-performance)
3. [Tabs y Secciones](#163-tabs-y-secciones)
4. [Visualizaciones con Plotly](#164-visualizaciones-con-plotly)
5. [Predictor Interactivo](#165-predictor-interactivo)

---

## 16.1 Estructura de un Dashboard ML

### Arquitectura del Dashboard CarVision

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CarVision Dashboard                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │  Overview   │ │   Market    │ │   Model     │ │    Price    │            │
│  │   (KPIs)    │ │  Analysis   │ │  Metrics    │ │  Predictor  │            │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘            │
│                                                                             │
│  TAB 1: Overview                TAB 2: Market Analysis                      │
│  • Total vehicles               • Investment recommendations                │
│  • Average price                • Risk assessment                           │
│  • Price distribution           • Market trends                             │
│                                                                             │
│  TAB 3: Model Metrics           TAB 4: Price Predictor                      │
│  • RMSE, MAE, R², MAPE         • Input form                                 │
│  • Bootstrap confidence         • Single prediction                         │
│  • Temporal backtest            • Gauge visualization                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Código Base

```python
# app/streamlit_app.py - Estructura básica

import streamlit as st
import pandas as pd
import joblib
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIG (debe ser la primera llamada Streamlit)
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="CarVision Market Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ═══════════════════════════════════════════════════════════════════════════
# CACHING: Cargar datos y modelo UNA vez
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_data  # Cache para datos (inmutables)
def load_data():
    """Carga dataset - cached para performance."""
    path = Path("data/raw/vehicles_us.csv")
    if path.exists():
        return pd.read_csv(path)
    return None


@st.cache_resource  # Cache para recursos (modelo, conexiones)
def load_model():
    """Carga modelo - cached para no recargar en cada interacción."""
    path = Path("artifacts/model.joblib")
    if path.exists():
        return joblib.load(path)
    return None


# ═══════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════

def main():
    st.title("�� CarVision Market Intelligence")
    st.markdown("*Análisis de mercado y predicción de precios de vehículos*")
    
    # Cargar datos
    df = load_data()
    model = load_model()
    
    if df is None:
        st.error("❌ No se encontró el dataset")
        return
    
    # Tabs para organizar contenido
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "📈 Market Analysis", 
        "🎯 Model Metrics",
        "💰 Price Predictor"
    ])
    
    with tab1:
        render_overview(df)
    
    with tab2:
        render_market_analysis(df)
    
    with tab3:
        render_model_metrics()
    
    with tab4:
        render_price_predictor(model, df)


if __name__ == "__main__":
    main()
```

---

## 16.2 Caching para Performance

### @st.cache_data vs @st.cache_resource

```python
# @st.cache_data: Para DATOS (DataFrames, listas, dicts)
# Se serializa y almacena. Inmutable.

@st.cache_data(ttl=3600)  # TTL: 1 hora
def load_data():
    df = pd.read_csv("data.csv")
    return df

@st.cache_data
def compute_statistics(df):
    """Cálculos pesados - cached."""
    return {
        "mean": df["price"].mean(),
        "median": df["price"].median(),
        "std": df["price"].std(),
    }


# @st.cache_resource: Para RECURSOS (modelos, conexiones DB)
# No se serializa. Se mantiene la referencia.

@st.cache_resource
def load_model():
    return joblib.load("model.joblib")

@st.cache_resource
def get_db_connection():
    return create_engine("postgresql://...")
```

### Patrón: Separar Carga de Visualización

```python
# ❌ MALO: Carga datos cada vez que cambia un widget
def main():
    filter_year = st.slider("Año", 2010, 2024)
    df = pd.read_csv("data.csv")  # Se ejecuta en cada interacción!
    filtered = df[df["year"] >= filter_year]
    st.dataframe(filtered)


# ✅ BUENO: Datos cargados una vez, filtrado es rápido
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

def main():
    df = load_data()  # Cached - instantáneo después de la primera carga
    
    filter_year = st.slider("Año", 2010, 2024)
    filtered = df[df["year"] >= filter_year]  # Operación rápida en memoria
    st.dataframe(filtered)
```

---

## 16.3 Tabs y Secciones

### Tab 1: Overview

```python
def render_overview(df: pd.DataFrame):
    """Tab de resumen con KPIs principales."""
    
    st.header("📊 Portfolio Overview")
    
    # KPIs en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Vehicles",
            value=f"{len(df):,}",
            delta=None
        )
    
    with col2:
        avg_price = df["price"].mean()
        st.metric(
            label="Average Price",
            value=f"${avg_price:,.0f}",
            delta=None
        )
    
    with col3:
        median_price = df["price"].median()
        st.metric(
            label="Median Price",
            value=f"${median_price:,.0f}",
            delta=f"{((avg_price - median_price) / median_price * 100):+.1f}% vs avg"
        )
    
    with col4:
        avg_age = 2024 - df["model_year"].mean()
        st.metric(
            label="Avg Vehicle Age",
            value=f"{avg_age:.1f} years",
            delta=None
        )
    
    st.divider()
    
    # Distribución de precios
    st.subheader("Price Distribution")
    
    import plotly.express as px
    fig = px.histogram(
        df, 
        x="price", 
        nbins=50,
        title="Vehicle Price Distribution"
    )
    fig.update_layout(
        xaxis_title="Price ($)",
        yaxis_title="Count"
    )
    st.plotly_chart(fig, use_container_width=True)
```

### Tab 3: Model Metrics

```python
def render_model_metrics():
    """Tab de métricas del modelo."""
    
    st.header("🎯 Model Performance")
    
    # Cargar métricas
    metrics_path = Path("artifacts/metrics.json")
    if not metrics_path.exists():
        st.warning("⚠️ Métricas no disponibles. Entrene el modelo primero.")
        return
    
    import json
    metrics = json.loads(metrics_path.read_text())
    
    # Mostrar métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("RMSE", f"${metrics['rmse']:,.0f}")
    with col2:
        st.metric("MAE", f"${metrics['mae']:,.0f}")
    with col3:
        st.metric("R²", f"{metrics['r2']:.3f}")
    with col4:
        st.metric("MAPE", f"{metrics['mape']:.1f}%")
    
    # Explicación de métricas
    with st.expander("ℹ️ ¿Qué significan estas métricas?"):
        st.markdown("""
        - **RMSE** (Root Mean Square Error): Error promedio en dólares. Menor es mejor.
        - **MAE** (Mean Absolute Error): Error absoluto promedio. Más interpretable que RMSE.
        - **R²** (Coefficient of Determination): % de varianza explicada. 1.0 es perfecto.
        - **MAPE** (Mean Absolute Percentage Error): Error porcentual promedio.
        """)
```

---

## 16.4 Visualizaciones con Plotly

### Gráficos Interactivos

```python
import plotly.express as px
import plotly.graph_objects as go

def create_price_by_brand(df: pd.DataFrame):
    """Box plot de precios por marca."""
    
    # Top 10 marcas por volumen
    top_brands = df["brand"].value_counts().head(10).index
    df_top = df[df["brand"].isin(top_brands)]
    
    fig = px.box(
        df_top,
        x="brand",
        y="price",
        title="Price Distribution by Brand (Top 10)",
        color="brand"
    )
    
    fig.update_layout(
        xaxis_title="Brand",
        yaxis_title="Price ($)",
        showlegend=False
    )
    
    return fig


def create_price_gauge(predicted_price: float, min_price: float, max_price: float):
    """Gauge para mostrar predicción de precio."""
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=predicted_price,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Predicted Price", "font": {"size": 24}},
        number={"prefix": "$", "font": {"size": 40}},
        gauge={
            "axis": {"range": [min_price, max_price], "tickprefix": "$"},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [min_price, min_price + (max_price-min_price)*0.33], "color": "lightgreen"},
                {"range": [min_price + (max_price-min_price)*0.33, min_price + (max_price-min_price)*0.66], "color": "yellow"},
                {"range": [min_price + (max_price-min_price)*0.66, max_price], "color": "salmon"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": predicted_price
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig
```

---

## 16.5 Predictor Interactivo

### Tab 4: Price Predictor

```python
def render_price_predictor(model, df: pd.DataFrame):
    """Tab de predicción interactiva de precios."""
    
    st.header("💰 Price Predictor")
    
    if model is None:
        st.error("❌ Modelo no cargado. Entrene el modelo primero.")
        return
    
    st.markdown("Ingrese las características del vehículo para obtener una estimación de precio.")
    
    # Form para inputs
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            model_year = st.number_input(
                "Model Year",
                min_value=1990,
                max_value=2024,
                value=2018,
                help="Año del modelo del vehículo"
            )
            
            odometer = st.number_input(
                "Odometer (miles)",
                min_value=0,
                max_value=500000,
                value=50000,
                step=1000,
                help="Millaje del vehículo"
            )
            
            # Obtener opciones únicas del dataset
            models = sorted(df["model"].dropna().unique())
            selected_model = st.selectbox(
                "Model",
                options=models[:100],  # Limitar para performance
                index=0
            )
        
        with col2:
            fuel_options = df["fuel"].dropna().unique().tolist()
            fuel = st.selectbox("Fuel Type", options=fuel_options)
            
            trans_options = df["transmission"].dropna().unique().tolist()
            transmission = st.selectbox("Transmission", options=trans_options)
            
            condition_options = ["new", "like new", "excellent", "good", "fair", "salvage"]
            condition = st.selectbox("Condition", options=condition_options, index=3)
        
        submitted = st.form_submit_button("🔮 Predict Price", use_container_width=True)
    
    # Hacer predicción cuando se envía el form
    if submitted:
        # Preparar datos para predicción
        input_data = pd.DataFrame([{
            "model_year": model_year,
            "odometer": odometer,
            "model": selected_model,
            "fuel": fuel,
            "transmission": transmission,
            "condition": condition,
        }])
        
        try:
            # Predecir
            prediction = model.predict(input_data)[0]
            
            # Mostrar resultado
            st.success(f"### 💵 Estimated Price: **${prediction:,.0f}**")
            
            # Gauge de visualización
            min_price = df["price"].quantile(0.05)
            max_price = df["price"].quantile(0.95)
            
            fig = create_price_gauge(prediction, min_price, max_price)
            st.plotly_chart(fig, use_container_width=True)
            
            # Contexto de mercado
            percentile = (df["price"] < prediction).mean() * 100
            st.info(f"📊 Este precio está en el percentil {percentile:.0f} del mercado.")
            
        except Exception as e:
            st.error(f"Error en predicción: {str(e)}")
---

## 🧨 Errores habituales y cómo depurarlos en Streamlit para ML

En dashboards de ML es fácil mezclar lógica pesada con UI y terminar con apps lentas o que se rompen al mínimo cambio.

### 1) App muy lenta o que recalcula todo en cada interacción

**Síntomas típicos**

- Cada vez que mueves un slider, tarda varios segundos.
- Ves en logs que se vuelve a leer el CSV o cargar el modelo a cada cambio.

**Cómo identificarlo**

- Busca lecturas de disco o cargas de modelo dentro de la función `main` o dentro de callbacks de widgets.

**Cómo corregirlo**

- Usa `@st.cache_data` para datos y `@st.cache_resource` para el modelo, como en los ejemplos del módulo.
- Separa **carga** (funciones cacheadas) de **visualización** (funciones ligeras que usan los datos ya cargados).

---

### 2) Errores al filtrar o mapear columnas (DataFrame desalineado)

**Síntomas típicos**

- Errores tipo `KeyError: 'price'` o columnas que no existen en ciertos entornos.

**Cómo identificarlo**

- Verifica que el dataset que usas en Streamlit tenga la misma estructura que el usado en entrenamiento.

**Cómo corregirlo**

- Centraliza la carga y preprocesado básico en una función (ej. `load_data`) y reutilízala en todas las tabs.
- Añade checks defensivos (`if 'price' not in df.columns: ...`).

---

### 3) Modelo o artefactos que no se encuentran desde Streamlit

**Síntomas típicos**

- El predictor muestra `Modelo no cargado. Entrene el modelo primero.` aunque sabes que existe un modelo.

**Cómo identificarlo**

- Inspecciona la ruta usada en `load_model` y compárala con la estructura real del proyecto / contenedor.

**Cómo corregirlo**

- Alinea las rutas (`artifacts/`, `models/`) entre training, Docker y Streamlit.
- Si corres en Docker, monta los artefactos en la misma ruta que espera la app.

---

### 4) Comportamiento raro por estado oculto o re-runs

**Síntomas típicos**

- Formularios que se envían varias veces.
- Widgets que vuelven a su valor inicial sin razón aparente.

**Cómo identificarlo**

- Revisa el uso de `st.session_state` y de formularios (`st.form`).

**Cómo corregirlo**

- Usa `st.form` para agrupar inputs y ejecutar lógica solo cuando el usuario pulsa el botón de submit.
- Cuando necesites estado, usa `st.session_state` de forma explícita y documenta qué claves manejas.

---

### 5) Patrón general de debugging en Streamlit

1. Reproduce el problema con un **mínimo ejemplo** (quita tabs/funciones hasta aislar el fallo).
2. Añade logs (`st.write`, `print`) temporales para ver en qué orden se ejecuta el código.
3. Verifica qué funciones deberían estar cacheadas y cuáles no.
4. Asegúrate de que las dependencias clave (datos, modelo) están disponibles antes de renderizar la UI.

Con este enfoque, tus dashboards serán rápidos, robustos y mantenibles.

---

## 16.6 Dashboard Avanzado: Visualizaciones Profesionales

### Gauge Chart para Predicciones

```python
import plotly.graph_objects as go

def create_price_gauge(predicted_price: float, min_price: float = 0, max_price: float = 100000):
    """Crea un gauge chart para visualizar predicción de precio."""
    
    # Determinar color según rango
    if predicted_price < max_price * 0.3:
        color = "green"
    elif predicted_price < max_price * 0.7:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=predicted_price,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Predicted Price", 'font': {'size': 24}},
        number={'prefix': "$", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [min_price, max_price], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'steps': [
                {'range': [0, max_price * 0.3], 'color': 'lightgreen'},
                {'range': [max_price * 0.3, max_price * 0.7], 'color': 'lightyellow'},
                {'range': [max_price * 0.7, max_price], 'color': 'lightcoral'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': predicted_price
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

# Uso en Streamlit
if prediction is not None:
    gauge = create_price_gauge(prediction, min_price=0, max_price=80000)
    st.plotly_chart(gauge, use_container_width=True)
```

### Métricas con Confianza (Bootstrap)

```python
def display_model_metrics(metrics: dict):
    """Muestra métricas del modelo con intervalos de confianza."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="RMSE",
            value=f"${metrics['rmse']:,.0f}",
            delta=f"±{metrics.get('rmse_ci', 500):,.0f}",
            delta_color="inverse"  # Menor es mejor
        )
    
    with col2:
        st.metric(
            label="MAE",
            value=f"${metrics['mae']:,.0f}",
            delta=f"±{metrics.get('mae_ci', 300):,.0f}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="R²",
            value=f"{metrics['r2']:.3f}",
            delta=f"{metrics.get('r2_improvement', 0):.1%} vs baseline",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            label="MAPE",
            value=f"{metrics['mape']:.1%}",
            delta=f"±{metrics.get('mape_ci', 0.02):.1%}",
            delta_color="inverse"
        )
```

### Feature Importance Interactivo

```python
import plotly.express as px

def plot_feature_importance(model, feature_names: list, top_n: int = 15):
    """Gráfico interactivo de importancia de features."""
    
    # Extraer importancias (asume RandomForest o similar)
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'named_steps'):
        # Pipeline sklearn
        clf = model.named_steps.get('classifier') or model.named_steps.get('model')
        importances = clf.feature_importances_
    else:
        st.warning("Modelo no soporta feature_importances_")
        return None
    
    # Crear DataFrame y ordenar
    df_imp = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=True).tail(top_n)
    
    # Gráfico horizontal
    fig = px.bar(
        df_imp, 
        x='importance', 
        y='feature',
        orientation='h',
        title=f'Top {top_n} Feature Importances',
        labels={'importance': 'Importance', 'feature': 'Feature'},
        color='importance',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=400, showlegend=False)
    return fig

# Uso
with st.expander("🔍 Feature Importance", expanded=True):
    fig = plot_feature_importance(model, feature_names)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
```

### Multi-page App con Navigation

```python
# pages/1_📊_Overview.py
import streamlit as st

st.set_page_config(page_title="Overview", page_icon="📊")
st.title("📊 Dashboard Overview")

# ... contenido de overview

# pages/2_🔮_Predictor.py
import streamlit as st

st.set_page_config(page_title="Predictor", page_icon="🔮")
st.title("🔮 Price Predictor")

# ... contenido de predictor

# Estructura de archivos:
# app/
# ├── streamlit_app.py       # Main entry point
# └── pages/
#     ├── 1_📊_Overview.py
#     ├── 2_📈_Analysis.py
#     └── 3_🔮_Predictor.py
```

---

## 📦 Cómo se usó en el Portafolio

El dashboard de CarVision (`CarVision-Market-Intelligence/app/streamlit_app.py`) implementa:

| Componente | Líneas | Técnica |
|------------|:------:|---------|
| 4 Tabs navegables | 150-600 | `st.tabs()` |
| KPIs ejecutivos | 200-250 | `st.metric()` con delta |
| Gauge de predicción | 450-500 | Plotly `go.Indicator` |
| Feature importance | 350-400 | Plotly `px.bar` horizontal |
| Bootstrap validation | 400-430 | Métricas con intervalos |
| Caching de modelo | 50-80 | `@st.cache_resource` |

---

## 💼 Consejos Profesionales

> **Recomendaciones para destacar en entrevistas y proyectos reales**

### Para Entrevistas

1. **Streamlit vs Gradio vs Dash**: Trade-offs (Streamlit simple, Gradio para ML demos, Dash para dashboards complejos).

2. **Session State**: Explica cómo mantener estado entre reruns.

3. **Caching**: `@st.cache_data` vs `@st.cache_resource`.

### Para Proyectos Reales

| Situación | Consejo |
|-----------|---------|
| Modelo pesado | Usa `@st.cache_resource` para cargarlo una vez |
| Datos grandes | Pagina o muestra samples |
| Deployment | Streamlit Cloud para demos, Docker para producción |
| UX | Añade spinners y progress bars |

### Estructura de App Profesional

```
app/
├── streamlit_app.py   # Entry point limpio
├── pages/             # Multi-page app
├── components/        # Widgets reutilizables
└── utils/             # Lógica de negocio
```


---

## 📺 Recursos Externos Recomendados

> Ver [RECURSOS_POR_MODULO.md](RECURSOS_POR_MODULO.md) para la lista completa.

| 🏷️ | Recurso | Tipo | Duración |
|:--:|:--------|:-----|:--------:|
| 🔴 | [Streamlit Crash Course - Patrick Loeber](https://www.youtube.com/watch?v=JwSS70SZdyM) | Video | 45 min |
| 🟡 | [30 Days of Streamlit](https://30days.streamlit.app/) | Curso | 30 días |
| 🟡 | [Streamlit Multi-page Apps](https://www.youtube.com/watch?v=nSw96qUbK9o) | Video | 20 min |
| 🟢 | [Streamlit Gallery](https://streamlit.io/gallery) | Ejemplos | - |

---

## 🔗 Referencias del Glosario

Ver [21_GLOSARIO.md](21_GLOSARIO.md) para definiciones de:
- **Streamlit**: Framework para dashboards en Python
- **@st.cache_resource**: Decorator para cachear modelos
- **Plotly**: Librería de visualizaciones interactivas

---

## ✅ Ejercicios

Ver [EJERCICIOS.md](EJERCICIOS.md) - Módulo 15:
- **15.1**: Dashboard de predicción

**Ejercicio completo:**
Crea un dashboard Streamlit para BankChurn con:
1. Tab Overview: Distribución de churn, KPIs
2. Tab Analysis: Factores de riesgo por segmento
3. Tab Predictor: Formulario para predecir churn de un cliente

**Bonus**:
- Añade gauge chart para probabilidad de churn
- Implementa SHAP waterfall plot para explicar predicciones
- Usa multi-page structure

---

## 🎤 Checkpoint: Simulacro Mid

> 🎯 **¡Has completado ML Core + Deploy!** (Módulos 07-15)
> 
> Si buscas posiciones **Mid-Level ML Engineer**, ahora es buen momento para practicar:
> 
> **[→ SIMULACRO_ENTREVISTA_MID.md](SIMULACRO_ENTREVISTA_MID.md)**
> - 60 preguntas de pipelines, testing, CI/CD, Docker, APIs
> - Enfoque en implementación end-to-end y debugging

---

<div align="center">

[← FastAPI Producción](14_FASTAPI.md) | [Siguiente: Observabilidad →](16_OBSERVABILIDAD.md)

</div>
