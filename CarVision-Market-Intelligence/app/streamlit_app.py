import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuración de página - DEBE SER LO PRIMERO
st.set_page_config(
    page_title="CarVision Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Definir ROOT_DIR globalmente
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Importar clases y utilidades del proyecto
try:
    from src.carvision.analysis import MarketAnalyzer
    from src.carvision.data import clean_data, load_data
    from src.carvision.features import FeatureEngineer
    from src.carvision.visualization import VisualizationEngine
except ImportError:
    # Fallback for local dev if package not installed
    from src.carvision.analysis import MarketAnalyzer
    from src.carvision.data import clean_data, load_data
    from src.carvision.features import FeatureEngineer
    from src.carvision.visualization import VisualizationEngine


class VehicleDataLoader:
    """Legacy adapter for streamlit app."""

    def load_data(self, path):
        return load_data(path)

    def clean_data(self, df):
        return clean_data(df)


# Constantes
CONFIG_PATH = ROOT_DIR / "configs" / "config.yaml"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"
METRICS_PATH = ARTIFACTS_DIR / "metrics.json"
DATA_PATH = ROOT_DIR / "data" / "raw" / "vehicles_us.csv"

# Estilos CSS personalizados
st.markdown(
    """
    <style>
    .kpi-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .kpi-title {
        font-size: 14px;
        color: #6c757d;
        text-transform: uppercase;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: bold;
        color: #212529;
    }
    .insight-box {
        border-left: 5px solid #007bff;
        background-color: #e9ecef;
        padding: 15px;
        margin-bottom: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_and_clean_data():
    loader = VehicleDataLoader()
    # Fallback de rutas
    possible_paths = [DATA_PATH, Path("vehicles_us.csv"), Path("../vehicles_us.csv"), Path("data/raw/vehicles_us.csv")]

    data_file = None
    for p in possible_paths:
        if p.exists():
            data_file = p
            break

    if not data_file:
        st.error("Dataset not found in any standard location.")
        return None, None

    df = loader.load_data(str(data_file))
    df_clean = loader.clean_data(df)

    # Feature Engineering
    fe = FeatureEngineer()
    df_clean = fe.transform(df_clean)

    return df, df_clean


@st.cache_data
def get_market_analysis(df):
    analyzer = MarketAnalyzer(df)
    return analyzer.generate_executive_summary()


def display_kpi_card(title, value, delta=None, prefix="", suffix=""):
    delta_html = ""
    if delta is not None:
        color = "green" if delta > 0 else "red"
        delta_html = f'<div style="color: {color}; font-size: 0.9em; margin-top: 5px;">{delta:+.1f}% vs mercado</div>'

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{prefix}{value}{suffix}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# Carga de datos
raw_df, df_clean = load_and_clean_data()
if df_clean is None:
    st.stop()

# Sidebar
with st.sidebar:
    st.title("🚗 CarVision Filters")

    # Price filter (first)
    if "price" in df_clean.columns:
        max_price = int(df_clean["price"].quantile(0.99))
        price_range = st.slider("Price Range ($)", 0, max_price, (0, max_price), key="price_range_slider")
    else:
        price_range = (0, 0)

    # Model year filter (full range by default)
    if "model_year" in df_clean.columns:
        min_year = int(df_clean["model_year"].min())
        max_year = int(df_clean["model_year"].max())
        year_range = st.slider("Model Year", min_year, max_year, (min_year, max_year), key="year_range_slider")
    else:
        year_range = (1990, 2024)

    # Manufacturer filter (all selected by default)
    if "model" in df_clean.columns:
        manufacturers = sorted(df_clean["model"].apply(lambda x: str(x).split()[0]).unique())
        selected_manufacturers = st.multiselect(
            "Manufacturers",
            manufacturers,
            default=manufacturers,  # include all by default
            key="manufacturers_multiselect",
        )
    else:
        selected_manufacturers = []

    # Filtrado dinámico
    mask = df_clean["model_year"].between(year_range[0], year_range[1])
    if selected_manufacturers:
        mask &= df_clean["model"].apply(lambda x: str(x).split()[0]).isin(selected_manufacturers)
    if "price" in df_clean.columns:
        mask &= df_clean["price"].between(price_range[0], price_range[1])

    df_filtered = df_clean[mask]

    st.markdown(f"**Filtered Records:** {len(df_filtered):,}")
    st.markdown("---")
    st.caption("v2.0.0 Pro | Powered by Tripe Ten AI")

# Main title
st.title("🚗 CarVision Market Intelligence Dashboard")
st.markdown("Comprehensive platform for automotive market pricing and trend analysis.")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Overview",
        "📈 Market Analysis",
        "🧠 Model Metrics",
        "🔮 Price Predictor",
    ]
)

# --- TAB 1: OVERVIEW ---
with tab1:
    st.header("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        display_kpi_card("Total Vehicles", f"{len(df_filtered):,}")
    with col2:
        display_kpi_card("Average Price", f"{df_filtered['price'].mean():,.0f}", prefix="$")
    with col3:
        display_kpi_card("Median Price", f"{df_filtered['price'].median():,.0f}", prefix="$")
    with col4:
        display_kpi_card(
            "Average Age", f"{(pd.Timestamp.now().year - df_filtered['model_year']).mean():.1f}", suffix=" years"
        )

    st.subheader("Recent Data Sample")
    st.dataframe(
        df_filtered.sort_values("model_year", ascending=False).head(100),
        width="stretch",
    )

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Data Quality - Missing Values")
        missing = raw_df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False)
        if not missing.empty:
            fig_missing = px.bar(
                x=missing.index,
                y=missing.values,
                title="Rows with null values by column",
                labels={"x": "Column", "y": "Rows with null values"},
                color_discrete_sequence=["#ff6b6b"],
            )
            st.plotly_chart(fig_missing, width="stretch")
        else:
            st.success("Clean dataset! No missing values.")

    with col_r:
        st.subheader("Data Integrity")
        duplicates = raw_df.duplicated().sum()
        if duplicates > 0:
            st.warning(f"⚠️ Detected {duplicates:,} duplicate rows in the original dataset.")
        else:
            st.success("✅ No duplicates found.")

    # Key distributions of the filtered dataset
    if len(df_filtered) > 0:
        st.subheader("Key Distributions of Filtered Dataset")
        dist1, dist2 = st.columns(2)

        with dist1:
            if "price" in df_filtered.columns:
                fig_price = px.histogram(
                    df_filtered,
                    x="price",
                    nbins=40,
                    title="Price Distribution",
                    labels={"price": "Price"},
                )
                st.plotly_chart(fig_price, width="stretch")

        with dist2:
            if "model_year" in df_filtered.columns:
                fig_year = px.histogram(
                    df_filtered,
                    x="model_year",
                    nbins=20,
                    title="Distribution by Model Year",
                    labels={"model_year": "Model Year"},
                )
                st.plotly_chart(fig_year, width="stretch")

# --- TAB 2: MARKET ANALYSIS ---
with tab2:
    st.header("Executive Market Report")
    st.caption("Financial summary and opportunity mapping for decision makers and investors.")

    if len(df_filtered) > 0:
        # Usar MarketAnalyzer y VisualizationEngine
        viz_engine = VisualizationEngine(df_filtered)
        analyzer = MarketAnalyzer(df_filtered)
        summary = analyzer.generate_executive_summary()

        # Executive Summary
        with st.expander("📋 Executive Market Summary (Expand)", expanded=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("#### 💡 Insights")
                st.info(
                    f"**Leading Brand:** {summary['insights'].get('most_popular_brand', 'N/A')}\n\n"
                    f"**Highest Value:** {summary['insights'].get('highest_value_brand', 'N/A')}"
                )
            with c2:
                st.markdown("#### 💰 Opportunities")
                st.success(
                    f"**Undervalued Vehicles:** {summary['kpis'].get('total_opportunities', 0)}\n\n"
                    f"**Arbitrage Potential:** ${summary['kpis'].get('potential_arbitrage_value', 0):,.0f}"
                )
            with c3:
                st.markdown("#### 📉 Depreciation")
                depr = summary["insights"].get("avg_depreciation_rate", 0)
                st.warning(f"**Annual Rate:** {depr:.1%}")

        # Executive financial summary
        st.subheader("Executive Financial Summary")

        # Financial KPIs
        fk1, fk2, fk3 = st.columns(3)
        fk1.metric("Total Market Value", f"${summary['kpis']['total_market_value']:,.0f}")
        fk2.metric("Average Price", f"${summary['kpis']['average_price']:,.0f}")
        fk3.metric("Opportunities Detected", f"{summary['kpis']['total_opportunities']:,}")

        # Narrativa ejecutiva sobre el portafolio
        total_vehicles = summary["kpis"].get("total_vehicles", len(df_filtered))
        total_value = summary["kpis"].get("total_market_value", float(df_filtered["price"].sum()))
        avg_price = summary["kpis"].get("average_price", float(df_filtered["price"].mean()))
        total_opps = summary["kpis"].get("total_opportunities", 0)

        st.markdown(
            f"""
            **Filtered Portfolio Overview**

            - Estimated total market value: **${total_value:,.0f}**
            - Average ticket per vehicle: **${avg_price:,.0f}**
            - Volume of units analyzed: **{total_vehicles:,}**
            - Identified opportunities (undervalued vehicles): **{total_opps:,}**

            These figures summarize the market size and return potential
            for an investor operating in this segment.
            """
        )

        fc1, fc2 = st.columns(2)

        # Market value by price segment
        with fc1:
            st.markdown("**Value Distribution by Price Segment**")
            if "price_category" in df_filtered.columns:
                value_by_cat = df_filtered.groupby("price_category")["price"].sum().reset_index()
                value_by_cat = value_by_cat.sort_values("price", ascending=False)
                fig_value_cat = px.bar(
                    value_by_cat,
                    x="price_category",
                    y="price",
                    labels={"price": "Total Value ($)", "price_category": "Segment"},
                    color="price_category",
                )
                st.plotly_chart(fig_value_cat, width="stretch")

        # Value share by brand (Top 8)
        with fc2:
            st.markdown("**Value Share by Brand (Top 8)**")
            df_brands = df_filtered.copy()
            if "model" in df_brands.columns:
                df_brands["brand"] = df_brands["model"].apply(lambda x: str(x).split()[0])
                brand_value = (
                    df_brands.groupby("brand")["price"].sum().sort_values(ascending=False).head(8).reset_index()
                )
                if not brand_value.empty:
                    fig_brand_share = px.pie(
                        brand_value,
                        values="price",
                        names="brand",
                    )
                    st.plotly_chart(fig_brand_share, width="stretch")

        # Arbitrage opportunities by category (if any)
        opps = analyzer.analysis_results.get("opportunities") or []
        if opps:
            st.markdown("**Arbitrage Opportunity Map by Segment**")
            opp_df = pd.DataFrame(opps)
            fig_opp = px.bar(
                opp_df,
                x="category",
                y="potential_value",
                hover_data=["count", "avg_price"],
                labels={"category": "Category", "potential_value": "Average Potential Value ($)"},
            )
            st.plotly_chart(fig_opp, width="stretch")

        # High-level strategic recommendations
        recs = summary.get("recommendations") or []
        if recs:
            st.subheader("Strategic Recommendations for Investors")
            for rec in recs:
                st.markdown(f"- {rec}")

        # Advanced Plotly Dashboard
        st.subheader("Analytical Appendices (Visual Detail)")
        fig_dashboard = viz_engine.create_market_analysis_dashboard()
        st.plotly_chart(fig_dashboard, width="stretch")
    else:
        st.warning("No data to display with the selected filters.")

# --- TAB 3: MODEL METRICS ---
with tab3:
    st.header("Predictive Model Evaluation")

    # Intentar cargar métricas del modelo
    metrics_model: dict = {}
    possible_metrics = [METRICS_PATH, ARTIFACTS_DIR / "metrics_val.json", Path("metrics.json")]

    for p in possible_metrics:
        if p.exists():
            try:
                with open(p) as f:
                    metrics_model = json.load(f)
                break
            except Exception:
                continue

    # Cargar métricas baseline si existen
    metrics_baseline: dict = {}
    possible_baseline = [
        ARTIFACTS_DIR / "metrics_baseline.json",  # ruta configurada en configs/config.yaml
        ARTIFACTS_DIR / "baseline_metrics.json",
        ARTIFACTS_DIR / "baseline.json",
        Path("metrics_baseline.json"),
        Path("baseline_metrics.json"),
    ]
    for p in possible_baseline:
        if p.exists():
            try:
                with open(p) as f:
                    metrics_baseline = json.load(f)
                break
            except Exception:
                continue

    # Cargar resultados de bootstrap si están disponibles
    bootstrap_path = ARTIFACTS_DIR / "metrics_bootstrap.json"
    metrics_bootstrap: dict | None = None
    if bootstrap_path.exists():
        try:
            with open(bootstrap_path) as f:
                metrics_bootstrap = json.load(f)
        except Exception:
            metrics_bootstrap = None

    # Cargar métricas temporales (backtest)
    temporal_path = ARTIFACTS_DIR / "metrics_temporal.json"
    metrics_temporal: dict | None = None
    if temporal_path.exists():
        try:
            with open(temporal_path) as f:
                metrics_temporal = json.load(f)
        except Exception:
            metrics_temporal = None

    if metrics_model:
        # KPIs del modelo
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("RMSE", f"${metrics_model.get('rmse', 0):,.0f}")
        m2.metric("MAE", f"${metrics_model.get('mae', 0):,.0f}")
        m3.metric("R² Score", f"{metrics_model.get('r2', 0):.3f}")
        m4.metric("MAPE", f"{metrics_model.get('mape', 0):.1f}%")

        # Mostrar métricas baseline si existen
        if metrics_baseline:
            st.markdown("### Baseline (Dummy Median)")
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("RMSE Baseline", f"${metrics_baseline.get('rmse', 0):,.0f}")
            b2.metric("MAE Baseline", f"${metrics_baseline.get('mae', 0):,.0f}")
            b3.metric("R² Baseline", f"{metrics_baseline.get('r2', 0):.3f}")
            b4.metric("MAPE Baseline", f"{metrics_baseline.get('mape', 0):.1f}%")

            st.markdown("### Model vs Baseline Comparison")
            # Tabla de comparación para todas las métricas clave
            comp_df = pd.DataFrame(
                {
                    "Metric": ["RMSE", "MAE", "MAPE", "R²"],
                    "Current Model": [
                        metrics_model.get("rmse", 0),
                        metrics_model.get("mae", 0),
                        metrics_model.get("mape", 0),
                        metrics_model.get("r2", 0),
                    ],
                    "Baseline": [
                        metrics_baseline.get("rmse", 0),
                        metrics_baseline.get("mae", 0),
                        metrics_baseline.get("mape", 0),
                        metrics_baseline.get("r2", 0),
                    ],
                }
            )

            # Improvement (positive = better than baseline)
            def compute_improvement(row: pd.Series) -> float:
                base = row["Baseline"]
                model_val = row["Current Model"]
                if base == 0:
                    return 0.0
                # For R², higher is better; for errors (RMSE, MAE, MAPE), lower is better
                if row["Metric"] == "R²":
                    return (model_val - base) / abs(base) * 100
                return (base - model_val) / abs(base) * 100

            comp_df["Improvement %"] = comp_df.apply(compute_improvement, axis=1)

            st.table(
                comp_df.style.format(
                    {
                        "Current Model": "{:.4g}",
                        "Baseline": "{:.4g}",
                        "Improvement %": "{:+.1f}%",
                    }
                )
            )

            # Comparative visualization model vs baseline
            plot_df = comp_df.melt(
                id_vars="Metric",
                value_vars=["Current Model", "Baseline"],
                var_name="System",
                value_name="Value",
            )
            fig_comp = px.bar(
                plot_df,
                x="Metric",
                y="Value",
                color="System",
                barmode="group",
                labels={"Value": "Metric Value"},
            )
            st.plotly_chart(fig_comp, width="stretch")

            st.caption(
                "Lower values are better for RMSE/MAE/MAPE; higher values are better for R². "
                "The 'Improvement %' column indicates the relative gain of the model vs. median baseline."
            )

        # Bootstrap: statistical significance
        if metrics_bootstrap:
            st.markdown("### Statistical Significance (Bootstrap RMSE)")
            d_mean = metrics_bootstrap.get("delta_rmse_mean")
            ci_low, ci_high = metrics_bootstrap.get("delta_rmse_ci95", [None, None])
            p_val = metrics_bootstrap.get("p_value_two_sided")

            c_boot1, c_boot2, c_boot3 = st.columns(3)
            c_boot1.metric("Δ RMSE (model - baseline)", f"{d_mean:.2f}")
            c_boot2.metric("95% CI", f"[{ci_low:.2f}, {ci_high:.2f}]")
            c_boot3.metric("p-value (two-tailed)", f"{p_val:.3f}")

            if ci_high is not None and ci_high < 0 and p_val is not None and p_val < 0.05:
                st.success("The RMSE reduction is statistically significant (95% CI entirely below 0).")
            else:
                st.info(
                    "The model improvement over baseline is not clearly significant across all resamples, "
                    "but may still be relevant from a business perspective."
                )

        # Temporal metrics (backtest on recent years)
        if metrics_temporal:
            st.markdown("### Performance in Recent Years (Temporal Backtest)")
            t1, t2, t3, t4, t5 = st.columns(5)
            t1.metric("RMSE (Temporal)", f"${metrics_temporal.get('rmse', 0):,.0f}")
            t2.metric("MAE (Temporal)", f"${metrics_temporal.get('mae', 0):,.0f}")
            t3.metric("R² (Temporal)", f"{metrics_temporal.get('r2', 0):.3f}")
            t4.metric("MAPE (Temporal)", f"{metrics_temporal.get('mape', 0):.1f}%")
            t5.metric("Samples", f"{metrics_temporal.get('n_samples', 0):,}")

            st.caption(
                "These metrics are calculated on a recent temporal window of the dataset, "
                "simulating performance on future/unseen data."
            )

    else:
        st.warning(
            "No saved metrics found. Run "
            "`python main.py --mode train` or "
            "`python evaluate.py --config configs/config.yaml` to generate them."
        )

# --- TAB 4: PRICE PREDICTOR ---
with tab4:
    st.header("🔮 Vehicle Value Estimator")

    model_file = None
    possible_models = [MODEL_PATH, Path("models/model_v1.0.0.pkl"), Path("artifacts/model.joblib")]

    for p in possible_models:
        if p.exists():
            model_file = p
            break

    if model_file:
        model = joblib.load(model_file)

        st.markdown("Enter vehicle characteristics to get an AI-based price estimate.")

        # Input controls (no explicit form to avoid tab changes on submit)
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            year_input = st.number_input("Model Year", 1990, 2025, 2018, key="pred_year")
            odometer_input = st.number_input("Mileage (Odometer)", 0, 500000, 50000, key="pred_odometer")
            cylinders_input = st.selectbox("Cylinders", [4, 6, 8, 10, 12], index=1, key="pred_cylinders")

        with col_f2:
            condition_input = st.selectbox(
                "Condition", ["excellent", "good", "fair", "like new", "salvage", "new"], index=0, key="pred_condition"
            )
            fuel_input = st.selectbox(
                "Fuel", ["gas", "diesel", "hybrid", "electric", "other"], index=0, key="pred_fuel"
            )
            trans_input = st.selectbox(
                "Transmission", ["automatic", "manual", "other"], index=0, key="pred_transmission"
            )

        with col_f3:
            type_input = st.selectbox(
                "Type",
                [
                    "sedan",
                    "SUV",
                    "truck",
                    "pickup",
                    "coupe",
                    "wagon",
                    "hatchback",
                    "van",
                    "convertible",
                    "other",
                ],
                index=1,
                key="pred_type",
            )
            paint_input = st.selectbox(
                "Color",
                [
                    "white",
                    "black",
                    "silver",
                    "grey",
                    "blue",
                    "red",
                    "green",
                    "brown",
                    "custom",
                    "yellow",
                    "orange",
                    "purple",
                ],
                index=0,
                key="pred_paint",
            )
            drive_input = st.selectbox("Drive", ["4wd", "fwd", "rwd"], index=0, key="pred_drive")

        submit_btn = st.button("💰 Calculate Estimated Price", key="calculate_price_btn")

        if submit_btn:
            # Construir DataFrame de entrada con las columnas crudas principales
            input_data = {
                "model_year": year_input,
                "odometer": odometer_input,
                "condition": condition_input,
                "cylinders": cylinders_input,
                "fuel": fuel_input,
                "transmission": trans_input,
                "type": type_input,
                "paint_color": paint_input,
                "drive": drive_input,
                "model": "ford f-150",  # Placeholder neutral
            }

            # Crear DF base
            input_df = pd.DataFrame([input_data])
            if "model" in input_df.columns:
                input_df["brand"] = input_df["model"].astype(str).str.split().str[0]

            # Feature engineering is handled by the model pipeline (FeatureEngineer step)
            # We rely on the pipeline to compute vehicle_age from model_year
            # and handle missing price_per_mile (if expected by preprocessor) via imputation

            # El modelo es un Pipeline(pre=ColumnTransformer, model)
            # Extraemos columnas esperadas del preprocessor para alinear input_df
            try:
                pre = getattr(model, "named_steps", {}).get("pre") or getattr(model, "named_steps", {}).get(
                    "preprocess"
                )
            except Exception:
                pre = None

            numeric_cols = []
            categorical_cols = []
            feature_cols = []

            if pre is not None and hasattr(pre, "transformers_"):
                # Identificar columnas numéricas y categóricas directamente del ColumnTransformer
                for name, transformer, cols in pre.transformers_:
                    # cols puede ser lista de columnas o slice; nos quedamos con nombres explícitos
                    if isinstance(cols, (list, tuple)):
                        if name == "num":
                            numeric_cols.extend(list(cols))
                        elif name == "cat":
                            categorical_cols.extend(list(cols))
                        feature_cols.extend(list(cols))

                # Asegurar que todas las columnas esperadas existan en input_df
                for col in feature_cols:
                    if col not in input_df.columns:
                        # Columnas numéricas: usar valores neutros numéricos
                        if col in numeric_cols:
                            if col in ["days_listed", "vehicle_age", "odometer"]:
                                input_df[col] = 0
                            else:
                                # Valor neutro genérico para numéricos
                                input_df[col] = 0
                        else:
                            # Columnas categóricas: usar 'unknown' o NaT si parecen fechas
                            if "date" in col:
                                input_df[col] = pd.NaT
                            else:
                                input_df[col] = "unknown"

                # Forzar tipo numérico en columnas numéricas por seguridad
                for col in numeric_cols:
                    if col in input_df.columns:
                        input_df[col] = pd.to_numeric(input_df[col], errors="coerce")

                # Reordenar columnas según el orden esperado
                input_df = input_df[feature_cols]

            try:
                prediction = model.predict(input_df)[0]

                # Calcular percentil
                percentile = (df_clean["price"] < prediction).mean() * 100

                st.divider()
                c_res1, c_res2 = st.columns([1, 2])

                with c_res1:
                    st.metric("Estimated Price", f"${prediction:,.2f}")

                    # Badge
                    badge_color = "#17a2b8"  # Blue
                    badge_text = "Market Price"

                    if percentile > 75:
                        badge_color = "#FFD700"  # Gold
                        badge_text = "Premium"
                    elif percentile < 25:
                        badge_color = "#28a745"  # Green
                        badge_text = "Economic"

                    st.markdown(
                        f"""
                    <div style="background-color: {badge_color}; color: white; padding: 10px;
                                border-radius: 5px; text-align: center; font-weight: bold;">
                        {badge_text}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with c_res2:
                    st.info(
                        f"This price is higher than **{percentile:.0f}%** of vehicles " "in our historical inventory."
                    )
                    # Simple gauge chart
                    fig_gauge = go.Figure(
                        go.Indicator(
                            mode="gauge+number",
                            value=prediction,
                            domain={"x": [0, 1], "y": [0, 1]},
                            title={"text": "Position in Market Range"},
                            gauge={
                                "axis": {"range": [0, df_clean["price"].max() * 1.1]},  # Un poco más del max
                                "bar": {"color": "darkblue"},
                                "steps": [
                                    {
                                        "range": [0, df_clean["price"].quantile(0.25)],
                                        "color": "lightgreen",
                                    },
                                    {
                                        "range": [
                                            df_clean["price"].quantile(0.25),
                                            df_clean["price"].quantile(0.75),
                                        ],
                                        "color": "lightyellow",
                                    },
                                    {
                                        "range": [
                                            df_clean["price"].quantile(0.75),
                                            df_clean["price"].max() * 1.1,
                                        ],
                                        "color": "salmon",
                                    },
                                ],
                                "threshold": {
                                    "line": {"color": "red", "width": 4},
                                    "thickness": 0.75,
                                    "value": prediction,
                                },
                            },
                        )
                    )
                    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig_gauge, width="stretch")

            except Exception as e:
                st.error(f"Prediction error: {str(e)}")
                st.warning("Verify that input columns match those expected by the model.")

    else:
        st.error("Model not found. Train the model first.")
