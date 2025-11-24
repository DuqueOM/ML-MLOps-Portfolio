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


@st.cache_resource
def load_model():
    """Load the trained model with caching to prevent reloads."""
    possible_models = [MODEL_PATH, Path("models/model_v1.0.0.pkl"), Path("artifacts/model.joblib")]
    for p in possible_models:
        if p.exists():
            return joblib.load(p), str(p)
    return None, None


# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.last_filter_change = None
    st.session_state.prediction_result = None

# Load data
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

    # Dynamic filtering (optimized)
    mask = (df_clean["model_year"] >= year_range[0]) & (df_clean["model_year"] <= year_range[1])
    if selected_manufacturers:
        # Pre-compute brands once
        if "brands" not in st.session_state:
            st.session_state.brands = df_clean["model"].astype(str).str.split().str[0]
        mask &= st.session_state.brands.isin(selected_manufacturers)
    if "price" in df_clean.columns:
        mask &= (df_clean["price"] >= price_range[0]) & (df_clean["price"] <= price_range[1])

    df_filtered = df_clean[mask].copy()

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

# --- TAB 1: EXECUTIVE OVERVIEW ---
with tab1:
    st.header("📊 Executive Dashboard")
    st.markdown("**Key Performance Indicators and Market Intelligence Summary**")
    st.markdown("---")

    # Top-level KPIs with enhanced metrics
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    total_value = df_filtered["price"].sum()
    avg_price = df_filtered["price"].mean()
    median_price = df_filtered["price"].median()
    avg_age = (pd.Timestamp.now().year - df_filtered["model_year"]).mean()
    total_vehicles = len(df_filtered)

    with kpi1:
        st.metric(label="📈 Total Inventory Value", value=f"${total_value/1e6:.1f}M", delta=f"{total_vehicles:,} units")
    with kpi2:
        st.metric(
            label="💰 Average Price",
            value=f"${avg_price:,.0f}",
            delta=f"{((avg_price - median_price) / median_price * 100):.1f}% vs median",
        )
    with kpi3:
        st.metric(label="📊 Median Price", value=f"${median_price:,.0f}", delta="Market Center")
    with kpi4:
        st.metric(
            label="🚗 Fleet Age",
            value=f"{avg_age:.1f} yrs",
            delta=f"Avg {df_filtered['model_year'].mode()[0] if len(df_filtered) > 0 else 'N/A'} model",
        )
    with kpi5:
        price_std = df_filtered["price"].std()
        cv = (price_std / avg_price * 100) if avg_price > 0 else 0
        st.metric(label="📉 Price Volatility", value=f"{cv:.1f}%", delta="Coefficient of Variation")

    st.markdown("---")

    # Executive Summary Cards
    col_exec1, col_exec2 = st.columns(2)

    with col_exec1:
        st.subheader("🎯 Market Positioning")

        # Price segmentation
        if len(df_filtered) > 0:
            price_q1 = df_filtered["price"].quantile(0.25)
            price_q3 = df_filtered["price"].quantile(0.75)

            economy = (df_filtered["price"] < price_q1).sum()
            mid_market = ((df_filtered["price"] >= price_q1) & (df_filtered["price"] <= price_q3)).sum()
            premium = (df_filtered["price"] > price_q3).sum()

            segment_data = pd.DataFrame(
                {
                    "Segment": ["Economy", "Mid-Market", "Premium"],
                    "Units": [economy, mid_market, premium],
                    "Percentage": [
                        economy / total_vehicles * 100,
                        mid_market / total_vehicles * 100,
                        premium / total_vehicles * 100,
                    ],
                }
            )

            fig_segment = px.pie(
                segment_data,
                values="Units",
                names="Segment",
                title="Inventory Distribution by Price Segment",
                color="Segment",
                color_discrete_map={"Economy": "#28a745", "Mid-Market": "#17a2b8", "Premium": "#ffc107"},
                hole=0.4,
            )
            fig_segment.update_traces(textposition="inside", textinfo="percent+label")
            fig_segment.update_layout(height=350, showlegend=True)
            st.plotly_chart(fig_segment, use_container_width=True)

    with col_exec2:
        st.subheader("📈 Price Distribution Analysis")

        # Enhanced histogram with statistical overlays
        fig_price_dist = go.Figure()

        fig_price_dist.add_trace(
            go.Histogram(x=df_filtered["price"], nbinsx=50, name="Frequency", marker_color="#007bff", opacity=0.7)
        )

        # Add mean and median lines
        fig_price_dist.add_vline(
            x=avg_price,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: ${avg_price:,.0f}",
            annotation_position="top right",
        )
        fig_price_dist.add_vline(
            x=median_price,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Median: ${median_price:,.0f}",
            annotation_position="top left",
        )

        fig_price_dist.update_layout(
            title="Price Distribution with Statistical Markers",
            xaxis_title="Price ($)",
            yaxis_title="Frequency",
            height=350,
            showlegend=False,
        )
        st.plotly_chart(fig_price_dist, use_container_width=True)

    st.markdown("---")

    # Market Intelligence Grid
    col_int1, col_int2 = st.columns(2)

    with col_int1:
        st.subheader("🏆 Top Manufacturers by Volume")
        if "model" in df_filtered.columns and len(df_filtered) > 0:
            brand_data = df_filtered.copy()
            brand_data["brand"] = brand_data["model"].astype(str).str.split().str[0]
            top_brands = brand_data["brand"].value_counts().head(10)

            fig_brands = px.bar(
                x=top_brands.values,
                y=top_brands.index,
                orientation="h",
                title="Top 10 Manufacturers",
                labels={"x": "Units", "y": "Manufacturer"},
                color=top_brands.values,
                color_continuous_scale="Blues",
            )
            fig_brands.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_brands, use_container_width=True)

    with col_int2:
        st.subheader("📅 Inventory Age Profile")
        if "model_year" in df_filtered.columns and len(df_filtered) > 0:
            year_dist = df_filtered["model_year"].value_counts().sort_index()

            fig_years = px.area(
                x=year_dist.index,
                y=year_dist.values,
                title="Units by Model Year",
                labels={"x": "Model Year", "y": "Units"},
                color_discrete_sequence=["#17a2b8"],
            )
            fig_years.update_layout(height=400)
            fig_years.update_traces(fill="tozeroy")
            st.plotly_chart(fig_years, use_container_width=True)

    # Data Quality Summary (compact)
    with st.expander("🔍 Data Quality Report", expanded=False):
        qc1, qc2, qc3 = st.columns(3)

        with qc1:
            missing_pct = (raw_df.isnull().sum().sum() / (raw_df.shape[0] * raw_df.shape[1])) * 100
            st.metric("Data Completeness", f"{100-missing_pct:.1f}%", delta="Quality Score")

        with qc2:
            duplicates = raw_df.duplicated().sum()
            st.metric(
                "Unique Records",
                f"{100 - (duplicates/len(raw_df)*100):.1f}%",
                delta=f"{len(raw_df)-duplicates:,} unique",
            )

        with qc3:
            st.metric("Dataset Size", f"{len(raw_df):,}", delta=f"{df_filtered.shape[1]} attributes")

# --- TAB 2: EXECUTIVE MARKET ANALYSIS ---
with tab2:
    st.header("💼 Investment & Market Intelligence Report")
    st.markdown("**Strategic insights for C-level executives and institutional investors**")
    st.markdown("---")

    if len(df_filtered) > 0:
        # Usar MarketAnalyzer y VisualizationEngine
        viz_engine = VisualizationEngine(df_filtered)
        analyzer = MarketAnalyzer(df_filtered)
        summary = analyzer.generate_executive_summary()

        # Strategic Investment KPIs
        st.subheader("📊 Strategic Investment Metrics")

        inv_col1, inv_col2, inv_col3, inv_col4 = st.columns(4)

        with inv_col1:
            st.metric(
                label="🎯 Market Leader", value=summary["insights"].get("most_popular_brand", "N/A"), delta="By Volume"
            )

        with inv_col2:
            st.metric(
                label="💸 Premium Brand",
                value=summary["insights"].get("highest_value_brand", "N/A"),
                delta="By Avg Price",
            )

        with inv_col3:
            opportunities = summary["kpis"].get("total_opportunities", 0)
            st.metric(
                label="🔎 Investment Opportunities",
                value=f"{opportunities:,}",
                delta=f"{(opportunities/len(df_filtered)*100):.1f}% of inventory",
            )

        with inv_col4:
            depr = summary["insights"].get("avg_depreciation_rate", 0)
            st.metric(label="📉 Annual Depreciation", value=f"{depr:.1%}", delta="Portfolio Average")

        st.markdown("---")

        # Financial Performance Dashboard
        st.subheader("💹 Financial Performance Overview")

        fin_left, fin_right = st.columns([2, 1])

        with fin_left:
            # Price trend analysis by year
            if "model_year" in df_filtered.columns:
                price_by_year = (
                    df_filtered.groupby("model_year").agg({"price": ["mean", "median", "count"]}).reset_index()
                )
                price_by_year.columns = ["Year", "Avg Price", "Median Price", "Count"]

                fig_trend = go.Figure()
                fig_trend.add_trace(
                    go.Scatter(
                        x=price_by_year["Year"],
                        y=price_by_year["Avg Price"],
                        mode="lines+markers",
                        name="Average Price",
                        line=dict(color="#007bff", width=3),
                        marker=dict(size=8),
                    )
                )
                fig_trend.add_trace(
                    go.Scatter(
                        x=price_by_year["Year"],
                        y=price_by_year["Median Price"],
                        mode="lines+markers",
                        name="Median Price",
                        line=dict(color="#28a745", width=3, dash="dash"),
                        marker=dict(size=6),
                    )
                )

                fig_trend.update_layout(
                    title="Price Trends by Model Year",
                    xaxis_title="Model Year",
                    yaxis_title="Price ($)",
                    height=400,
                    hovermode="x unified",
                )
                st.plotly_chart(fig_trend, use_container_width=True)

        with fin_right:
            st.markdown("#### 📊 Portfolio Metrics")
            st.metric("Total Market Value", f"${summary['kpis']['total_market_value']/1e6:.2f}M")
            st.metric("Average Unit Price", f"${summary['kpis']['average_price']:,.0f}")
            st.metric("Revenue Potential", f"${summary['kpis'].get('potential_arbitrage_value', 0)/1e3:.1f}K")

            # ROI Calculator
            st.markdown("---")
            st.markdown("**💰 Quick ROI Estimate**")
            avg_margin = st.slider("Target Margin %", 5, 30, 15, key="roi_slider")
            potential_roi = summary["kpis"]["total_market_value"] * avg_margin / 100
            st.success(f"Projected ROI: **${potential_roi/1e6:.2f}M** at {avg_margin}% margin")

        # Calculate key metrics for recommendations
        total_vehicles = summary["kpis"].get("total_vehicles", len(df_filtered))
        total_value = summary["kpis"].get("total_market_value", float(df_filtered["price"].sum()))
        avg_price = summary["kpis"].get("average_price", float(df_filtered["price"].mean()))
        median_price = df_filtered["price"].median()
        avg_age = (pd.Timestamp.now().year - df_filtered["model_year"]).mean()
        total_opps = summary["kpis"].get("total_opportunities", 0)

        # Top brands for risk analysis
        if "model" in df_filtered.columns and len(df_filtered) > 0:
            brand_data_temp = df_filtered.copy()
            brand_data_temp["brand"] = brand_data_temp["model"].astype(str).str.split().str[0]
            top_brands = brand_data_temp["brand"].value_counts()
        else:
            top_brands = pd.Series([0], index=["Unknown"])

        st.markdown("---")

        # Investment Strategy Recommendations
        st.subheader("🎯 Strategic Recommendations")

        rec_col1, rec_col2 = st.columns(2)

        with rec_col1:
            st.markdown("#### 🟢 Buy Signals")
            discount_pct = (median_price - df_filtered["price"].quantile(0.25)) / median_price * 100
            st.markdown(
                f"""
            - **Target Inventory:** {total_opps:,} undervalued units identified
            - **Average Discount:** {discount_pct:.1f}% below market median
            - **Volume Opportunity:** {(total_opps / total_vehicles * 100):.1f}% of analyzed inventory
            - **Estimated Arbitrage Value:** ${summary['kpis'].get('potential_arbitrage_value', 0):,.0f}
            """
            )

        with rec_col2:
            st.markdown("#### 🔴 Risk Factors")
            volatility = df_filtered["price"].std() / df_filtered["price"].mean() * 100
            market_concentration = top_brands.iloc[0] / total_vehicles * 100 if len(df_filtered) > 0 else 0
            st.markdown(
                f"""
            - **Price Volatility:** {volatility:.1f}% coefficient of variation
            - **Fleet Age Risk:** Average {avg_age:.1f} years (depreciation accelerates after 5 yrs)
            - **Market Concentration:** Top brand holds {market_concentration:.1f}% market share
            - **Liquidity Consideration:** Monitor inventory turnover by segment
            """
            )

        st.markdown("---")

        # Competitive Landscape Analysis
        st.subheader("🏆 Competitive Landscape & Market Share")

        comp_col1, comp_col2 = st.columns(2)

        with comp_col1:
            # Market share by brand value
            if "model" in df_filtered.columns and len(df_filtered) > 0:
                df_brands = df_filtered.copy()
                df_brands["brand"] = df_brands["model"].apply(lambda x: str(x).split()[0])
                brand_value = df_brands.groupby("brand")["price"].agg(["sum", "count", "mean"]).reset_index()
                brand_value.columns = ["Brand", "Total Value", "Units", "Avg Price"]
                brand_value = brand_value.sort_values("Total Value", ascending=False).head(8)

                fig_brand_value = px.treemap(
                    brand_value,
                    path=["Brand"],
                    values="Total Value",
                    color="Avg Price",
                    hover_data=["Units"],
                    color_continuous_scale="RdYlGn",
                    title="Market Share by Total Inventory Value (Top 8 Brands)",
                )
                fig_brand_value.update_layout(height=400)
                st.plotly_chart(fig_brand_value, use_container_width=True)

        with comp_col2:
            # Brand performance matrix
            if len(brand_value) > 0:
                fig_scatter = px.scatter(
                    brand_value,
                    x="Units",
                    y="Avg Price",
                    size="Total Value",
                    color="Brand",
                    hover_data=["Total Value"],
                    title="Brand Performance Matrix: Volume vs. Price",
                    labels={"Units": "Market Volume", "Avg Price": "Average Unit Price ($)"},
                )
                fig_scatter.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig_scatter, use_container_width=True)

        # Additional analytics in expander
        with st.expander("📈 Advanced Analytics & Detailed Insights", expanded=False):
            # Arbitrage opportunities
            opps = analyzer.analysis_results.get("opportunities") or []
            if opps:
                st.markdown("**🔍 Arbitrage Opportunity Heat Map**")
                opp_df = pd.DataFrame(opps)
                fig_opp = px.bar(
                    opp_df,
                    x="category",
                    y="potential_value",
                    hover_data=["count", "avg_price"],
                    labels={"category": "Category", "potential_value": "Average Potential Value ($)"},
                    color="potential_value",
                    color_continuous_scale="Viridis",
                )
                st.plotly_chart(fig_opp, use_container_width=True)

            # Detailed analytics dashboard
            st.markdown("**📊 Comprehensive Market Dashboard**")
            fig_dashboard = viz_engine.create_market_analysis_dashboard()
            st.plotly_chart(fig_dashboard, use_container_width=True)
    else:
        st.warning("No data to display with the selected filters.")

# --- TAB 3: MODEL PERFORMANCE & ANALYTICS ---
with tab3:
    st.header("🧠 AI Model Performance Dashboard")
    st.markdown("**Technical evaluation metrics and model reliability analysis**")
    st.markdown("---")

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
        # Primary Performance KPIs
        st.subheader("📊 Core Performance Metrics")

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

        rmse_val = metrics_model.get("rmse", 0)
        mae_val = metrics_model.get("mae", 0)
        r2_val = metrics_model.get("r2", 0)
        mape_val = metrics_model.get("mape", 0)

        with kpi1:
            st.metric(label="🎯 RMSE", value=f"${rmse_val:,.0f}", delta="Root Mean Squared Error")
        with kpi2:
            st.metric(label="📏 MAE", value=f"${mae_val:,.0f}", delta="Mean Absolute Error")
        with kpi3:
            st.metric(label="💯 R² Score", value=f"{r2_val:.3f}", delta=f"{r2_val*100:.1f}% variance explained")
        with kpi4:
            st.metric(label="📉 MAPE", value=f"{mape_val:.2f}%", delta="Mean Absolute % Error")
        with kpi5:
            accuracy = max(0, 100 - mape_val)
            st.metric(label="✅ Accuracy", value=f"{accuracy:.1f}%", delta="Prediction Accuracy")

        st.markdown("---")

        # Model vs Baseline Performance Comparison
        if metrics_baseline:
            st.subheader("🔬 Model vs Baseline Comparison")

            comp_col1, comp_col2 = st.columns([3, 2])

            with comp_col1:
                # Create comparison dataframe
                comp_df = pd.DataFrame(
                    {
                        "Metric": ["RMSE ($)", "MAE ($)", "MAPE (%)", "R² Score"],
                        "AI Model": [
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

                # Create grouped bar chart
                fig_comp = go.Figure()

                fig_comp.add_trace(
                    go.Bar(
                        name="AI Model",
                        x=comp_df["Metric"],
                        y=comp_df["AI Model"],
                        marker_color="#007bff",
                        text=comp_df["AI Model"].apply(lambda x: f"{x:.2f}"),
                        textposition="outside",
                    )
                )

                fig_comp.add_trace(
                    go.Bar(
                        name="Baseline",
                        x=comp_df["Metric"],
                        y=comp_df["Baseline"],
                        marker_color="#6c757d",
                        text=comp_df["Baseline"].apply(lambda x: f"{x:.2f}"),
                        textposition="outside",
                    )
                )

                fig_comp.update_layout(
                    title="AI Model vs Simple Baseline Performance",
                    xaxis_title="Metric",
                    yaxis_title="Value",
                    barmode="group",
                    height=400,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )

                st.plotly_chart(fig_comp, use_container_width=True)

            with comp_col2:
                st.markdown("#### � Performance Gains")

                # Compute improvements
                for _, row in comp_df.iterrows():
                    metric_name = row["Metric"]
                    model_val = row["AI Model"]
                    base_val = row["Baseline"]

                    if base_val == 0:
                        continue

                    if "R²" in metric_name:
                        improvement = (model_val - base_val) / abs(base_val) * 100
                    else:
                        improvement = (base_val - model_val) / abs(base_val) * 100

                    if improvement > 0:
                        st.success(f"**{metric_name}**: {improvement:+.1f}% better")
                    else:
                        st.info(f"**{metric_name}**: {improvement:+.1f}%")

                st.markdown("---")
                st.markdown("**💡 Interpretation:**")
                st.caption(
                    "Positive values indicate the AI model outperforms the baseline. "
                    "For error metrics (RMSE, MAE, MAPE), lower is better. For R², higher is better."
                )

        st.markdown("---")

        # Statistical significance section
        if metrics_bootstrap:
            st.subheader("� Statistical Validation (Bootstrap Analysis)")
            d_mean = metrics_bootstrap.get("delta_rmse_mean")
            ci_low, ci_high = metrics_bootstrap.get("delta_rmse_ci95", [None, None])
            p_val = metrics_bootstrap.get("p_value_two_sided")

            c_boot1, c_boot2, c_boot3 = st.columns(3)
            c_boot1.metric("Δ RMSE (model - baseline)", f"{d_mean:.2f}" if d_mean else "N/A")
            c_boot2.metric("95% CI", f"[{ci_low:.2f}, {ci_high:.2f}]" if ci_low and ci_high else "N/A")
            c_boot3.metric("p-value (two-tailed)", f"{p_val:.3f}" if p_val else "N/A")

            if ci_high is not None and ci_high < 0 and p_val is not None and p_val < 0.05:
                st.success("✅ The RMSE reduction is statistically significant (95% CI entirely below 0).")
            else:
                st.info(
                    "ℹ️ The model improvement over baseline may not be statistically significant across all resamples, "
                    "but can still provide business value."
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

# --- TAB 4: AI PRICE PREDICTOR ---
with tab4:
    st.header("🔮 AI-Powered Vehicle Value Estimator")
    st.markdown("**Get instant, data-driven price estimates powered by machine learning**")
    st.markdown("---")

    # Load model using cached function
    model, model_path = load_model()

    if model:
        st.success(f"✅ AI Model loaded successfully from: `{Path(model_path).name}`")

        st.markdown("### 📝 Vehicle Specification Input")
        st.info(
            "💡 **Pro Tip:** Fill in all fields accurately for the best price estimate. "
            "Click 'Calculate Price' when ready."
        )

        # Use form to prevent page reloads and tab changes
        with st.form(key="price_prediction_form", clear_on_submit=False):
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                year_input = st.number_input("Model Year", 1990, 2025, 2018)
                odometer_input = st.number_input("Mileage (Odometer)", 0, 500000, 50000)
                cylinders_input = st.selectbox("Cylinders", [4, 6, 8, 10, 12], index=1)

            with col_f2:
                condition_input = st.selectbox(
                    "Condition",
                    ["excellent", "good", "fair", "like new", "salvage", "new"],
                    index=0,
                )
                fuel_input = st.selectbox(
                    "Fuel",
                    ["gas", "diesel", "hybrid", "electric", "other"],
                    index=0,
                )
                trans_input = st.selectbox("Transmission", ["automatic", "manual", "other"], index=0)

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
                )
                drive_input = st.selectbox("Drive", ["4wd", "fwd", "rwd"], index=0)

            # Submit button inside form
            submit_btn = st.form_submit_button("💰 Calculate Estimated Price", use_container_width=True)

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

                # Calculate market positioning
                percentile = (df_clean["price"] < prediction).mean() * 100

                st.markdown("---")
                st.markdown("### 🎯 Price Estimate Results")

                # Display results in professional layout
                result_col1, result_col2, result_col3 = st.columns([2, 2, 3])

                with result_col1:
                    st.markdown("#### 💰 Estimated Value")
                    st.markdown(f"## ${prediction:,.0f}")

                    # Market segment badge
                    if percentile > 75:
                        badge_color = "#FFD700"
                        badge_text = "🏆 Premium Segment"
                        badge_emoji = "🌟"
                    elif percentile > 50:
                        badge_color = "#007bff"
                        badge_text = "💼 Upper Market"
                        badge_emoji = "📈"
                    elif percentile > 25:
                        badge_color = "#17a2b8"
                        badge_text = "🎯 Mid Market"
                        badge_emoji = "✓"
                    else:
                        badge_color = "#28a745"
                        badge_text = "💚 Economy Segment"
                        badge_emoji = "💰"

                    st.markdown(
                        f"""
                        <div style="background: linear-gradient(135deg, {badge_color} 0%, {badge_color}dd 100%);
                                    color: white; padding: 15px; border-radius: 10px;
                                    text-align: center; font-weight: bold; font-size: 16px;
                                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            {badge_emoji} {badge_text}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with result_col2:
                    st.markdown("#### 📊 Market Position")
                    st.metric(
                        label="Percentile Ranking",
                        value=f"{percentile:.0f}th",
                        delta=f"Higher than {percentile:.0f}% of inventory",
                    )

                    # Price range context
                    q25 = df_clean["price"].quantile(0.25)
                    q75 = df_clean["price"].quantile(0.75)
                    median = df_clean["price"].median()

                    if prediction < q25:
                        context = "Below Market Average"
                    elif prediction > q75:
                        context = "Above Market Average"
                    else:
                        context = "Within Normal Range"

                    st.info(f"**Market Context:** {context}")

                with result_col3:
                    st.markdown("#### 📈 Market Benchmark")

                    # Create market comparison gauge
                    fig_gauge = go.Figure(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=prediction,
                            delta={"reference": median, "increasing": {"color": "#007bff"}},
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
                    fig_gauge.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10), font=dict(size=12))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                    # Additional context
                    st.caption(
                        f"💡 **Reference:** Median market price is ${median:,.0f}. "
                        f"Your estimate is {abs(prediction - median)/median*100:.1f}% "
                        f"{'above' if prediction > median else 'below'} median."
                    )

            except Exception as e:
                st.error(f"Prediction error: {str(e)}")
                st.warning("Verify that input columns match those expected by the model.")

    else:
        st.error("Model not found. Train the model first.")
