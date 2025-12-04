# 07 — Dashboard

> **Tiempo estimado**: 2 días (16 horas)
> 
> **Prerrequisitos**: Módulo 06 completado

---

## 🎯 Objetivos del Módulo

Al completar este módulo serás capaz de:

1. ✅ Crear un **dashboard Streamlit** funcional
2. ✅ **Consumir la API** desde el dashboard
3. ✅ Implementar **caching** para performance
4. ✅ Desplegar el dashboard localmente

---

## 📖 Contenido Teórico

### 1. Streamlit Básico

```python
"""app/streamlit_app.py — Dashboard principal."""
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from typing import Optional

# ===== Configuración =====
st.set_page_config(
    page_title="Churn Predictor",
    page_icon="📊",
    layout="wide",
)

API_URL = "http://localhost:8000"


# ===== Funciones de API =====
@st.cache_data(ttl=60)
def check_api_health() -> dict:
    """Verifica el estado de la API."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.json()
    except requests.exceptions.RequestException:
        return {"status": "unhealthy", "error": "API no disponible"}


def predict_churn(customer_data: dict) -> Optional[dict]:
    """Realiza predicción via API."""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=customer_data,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return None


# ===== UI Principal =====
def main():
    st.title("📊 Churn Prediction Dashboard")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Estado de la API
        health = check_api_health()
        if health.get("status") == "healthy":
            st.success("✅ API conectada")
        else:
            st.error("❌ API no disponible")
        
        st.divider()
        st.info("Este dashboard permite predecir la probabilidad de churn de clientes.")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["🎯 Predicción", "📈 Análisis", "ℹ️ Información"])
    
    with tab1:
        prediction_tab()
    
    with tab2:
        analysis_tab()
    
    with tab3:
        info_tab()


def prediction_tab():
    """Tab de predicción individual."""
    st.header("Predicción de Churn")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Datos del Cliente")
        
        age = st.slider("Edad", min_value=18, max_value=100, value=35)
        balance = st.number_input("Balance ($)", min_value=0.0, value=50000.0)
        tenure = st.slider("Meses como cliente", min_value=0, max_value=120, value=24)
        num_products = st.selectbox("Número de productos", options=[1, 2, 3, 4], index=1)
        is_active = st.checkbox("Cliente activo", value=True)
    
    with col2:
        st.subheader("Resultado")
        
        if st.button("🔮 Predecir", type="primary", use_container_width=True):
            customer_data = {
                "age": age,
                "balance": balance,
                "tenure": tenure,
                "num_products": num_products,
                "is_active": is_active,
            }
            
            with st.spinner("Calculando..."):
                result = predict_churn(customer_data)
            
            if result:
                prob = result["churn_probability"]
                pred = result["churn_prediction"]
                conf = result["confidence"]
                
                # Mostrar resultado
                if pred:
                    st.error(f"⚠️ Alto riesgo de churn: {prob:.1%}")
                else:
                    st.success(f"✅ Bajo riesgo de churn: {prob:.1%}")
                
                # Métricas
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Probabilidad", f"{prob:.1%}")
                col_b.metric("Predicción", "Churn" if pred else "No Churn")
                col_c.metric("Confianza", conf.capitalize())
                
                # Gauge chart
                fig = px.pie(
                    values=[prob, 1 - prob],
                    names=["Churn", "No Churn"],
                    color_discrete_sequence=["#ff6b6b", "#51cf66"],
                    hole=0.6,
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)


def analysis_tab():
    """Tab de análisis de datos."""
    st.header("Análisis Exploratorio")
    
    # Datos de ejemplo
    sample_data = pd.DataFrame({
        "age": [25, 35, 45, 55, 30, 40, 50, 28],
        "balance": [1000, 5000, 10000, 20000, 3000, 8000, 15000, 2000],
        "tenure": [12, 24, 36, 48, 6, 30, 42, 18],
        "churn": [0, 0, 1, 0, 1, 0, 0, 1],
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.histogram(
            sample_data, x="age", color="churn",
            title="Distribución de Edad por Churn",
            barmode="overlay",
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(
            sample_data, x="tenure", y="balance", color="churn",
            title="Balance vs Tenure",
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.dataframe(sample_data, use_container_width=True)


def info_tab():
    """Tab de información."""
    st.header("Información del Modelo")
    
    st.markdown("""
    ### Sobre el Modelo
    
    Este modelo de predicción de churn utiliza:
    - **Algoritmo**: Random Forest Classifier
    - **Features**: edad, balance, tenure, productos, actividad
    - **Métricas**: AUC-ROC > 0.85, F1 > 0.75
    
    ### Uso Recomendado
    
    1. Ingrese los datos del cliente
    2. Haga clic en "Predecir"
    3. Revise la probabilidad y confianza
    4. Tome acciones preventivas si el riesgo es alto
    
    ### Limitaciones
    
    - El modelo fue entrenado con datos históricos
    - Las predicciones son probabilísticas
    - Factores externos pueden afectar el churn real
    """)


if __name__ == "__main__":
    main()
```

---

### 2. Caching en Streamlit

```python
"""Ejemplos de caching."""
import streamlit as st
import pandas as pd


# Cache para datos (TTL de 1 hora)
@st.cache_data(ttl=3600)
def load_data(path: str) -> pd.DataFrame:
    """Carga datos con cache."""
    return pd.read_parquet(path)


# Cache para recursos (modelos, conexiones)
@st.cache_resource
def load_model():
    """Carga modelo con cache."""
    import joblib
    return joblib.load("models/pipeline.pkl")


# Cache con hash personalizado
@st.cache_data(hash_funcs={pd.DataFrame: lambda df: df.to_json()})
def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Procesa datos con cache."""
    return df.groupby("category").mean()
```

---

### 3. Ejecutar Dashboard

```bash
# Desarrollo
streamlit run app/streamlit_app.py

# Con configuración personalizada
streamlit run app/streamlit_app.py --server.port 8501 --server.headless true
```

---

## 🔧 Mini-Proyecto: Dashboard de Predicción

### Objetivo

1. Crear dashboard Streamlit
2. Consumir API de predicción
3. Mostrar visualizaciones
4. Implementar caching

### Criterios de Éxito

- [ ] Dashboard carga en http://localhost:8501
- [ ] Predicción funciona con API
- [ ] Visualizaciones interactivas
- [ ] Cache implementado

---

## ✅ Validación

```bash
make check-07
```

---

## ➡️ Siguiente Módulo

**[08 — CI/CD & Testing](../08_ci_cd_testing/index.md)**

---

*Última actualización: 2024-12*
