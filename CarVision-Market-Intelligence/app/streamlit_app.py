"""
CarVision Market Intelligence Dashboard v2.0.0 Pro
Ejecución: streamlit run app/streamlit_app.py
Dependencias: streamlit, plotly, pandas, numpy, scikit-learn, joblib, pyyaml
Opcionales: pandera (validación), shap (explicabilidad)
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s|%(levelname)s|%(message)s")
logger = logging.getLogger("CarVision")

st.set_page_config(
    page_title="CarVision Intelligence",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from src.carvision.analysis import MarketAnalyzer
    from src.carvision.data import clean_data, load_data
    from src.carvision.features import FeatureEngineer
    from src.carvision.visualization import VisualizationEngine
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()

CONFIG_PATH, APP_VERSION = ROOT_DIR / "configs" / "config.yaml", "v2.0.0 Pro"
CONFIG = yaml.safe_load(open(CONFIG_PATH)) if CONFIG_PATH.exists() else {}
PATHS = CONFIG.get("paths", {})
ARTIFACTS_DIR = ROOT_DIR / PATHS.get("artifacts_dir", "artifacts")
MODEL_PATH = ROOT_DIR / PATHS.get("model_path", "artifacts/model.joblib")
METRICS_PATH = ROOT_DIR / PATHS.get("metrics_path", "artifacts/metrics.json")
PROCESSED_PARQUET = ARTIFACTS_DIR / "processed.parquet"
REQUIRED_COLS = ["price", "model_year", "model", "odometer"]

st.markdown(
    """
<style>
.kpi-card{
    background: linear-gradient(135deg,#f8f9fa,#e9ecef);
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    border-left: 4px solid #007bff;
}
.insight-box{
    border-left: 5px solid #17a2b8;
    background: #e3f2fd;
    padding: 14px;
    margin: 10px 0;
    border-radius: 0 8px 8px 0;
}
</style>
""",
    unsafe_allow_html=True,
)

try:
    import pandera  # type: ignore[import]  # noqa: F401

    PANDERA = True
except ImportError:
    PANDERA = False


def find_data() -> Optional[Path]:
    for p in [
        ROOT_DIR / PATHS.get("data_path", "data/raw/vehicles_us.csv"),
        ROOT_DIR / "data" / "raw" / "vehicles_us.csv",
    ]:
        if p.exists():
            return p
    return None


@st.cache_data(ttl=None)
def load_clean_data(
    _inv: str = None,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    if PROCESSED_PARQUET.exists() and not _inv:
        try:
            dc = pd.read_parquet(PROCESSED_PARQUET)
            f = find_data()
            dr = load_data(str(f)) if f else dc.copy()
            logger.info(f"Loaded from parquet: {len(dc)} records")
            return dr, dc
        except Exception:
            # Fall back to CSV if parquet is corrupted or unreadable
            pass
    f = find_data()
    if not f:
        logger.error("Dataset not found")
        return None, None
    try:
        dr = load_data(str(f))
        miss = [c for c in REQUIRED_COLS if c not in dr.columns]
        if miss:
            logger.error(f"Missing cols: {miss}")
            return dr, None
        dc = clean_data(dr, CONFIG.get("preprocessing", {}).get("filters", {}))
        dc = FeatureEngineer().transform(dc.copy())
        try:
            ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
            dc.to_parquet(PROCESSED_PARQUET, index=False)
        except Exception:
            # Do not fail dashboard if parquet cannot be written
            pass
        logger.info(f"Processed: {len(dc)} records")
        return dr, dc
    except Exception as e:
        logger.error(f"Load error: {e}")
        return None, None


@st.cache_resource
def load_model(_inv: str = None) -> Tuple[Any, Optional[str], Optional[datetime]]:
    for p in [
        MODEL_PATH,
        ARTIFACTS_DIR / "model.joblib",
        ROOT_DIR / "models" / "model.joblib",
    ]:
        if p.exists():
            try:
                return joblib.load(p), str(p), datetime.now()
            except Exception:
                # Try next candidate path
                continue
    return None, None, None


def load_json(p: Path) -> Dict:
    return json.load(open(p)) if p.exists() else {}


def get_pre_cols(m) -> Tuple[List, List, List]:
    num, cat, feat = [], [], []
    try:
        pre = getattr(m, "named_steps", {}).get("pre") or getattr(m, "named_steps", {}).get("preprocess")
        if pre and hasattr(pre, "transformers_"):
            for n, _, cols in pre.transformers_:
                if isinstance(cols, (list, tuple)):
                    (num if n == "num" else cat).extend(cols)
                    feat.extend(cols)
    except Exception:
        # If we can't introspect the preprocessor, fall back to raw input
        pass
    return feat, num, cat


def prep_input(data: Dict, feat: List, num: List) -> pd.DataFrame:
    df = pd.DataFrame([data])
    if "model" in df.columns and "brand" not in df.columns:
        df["brand"] = df["model"].astype(str).str.split().str[0]
    for c in feat:
        if c not in df.columns:
            df[c] = 0 if c in num else "unknown"
    for c in num:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return df[[c for c in feat if c in df.columns]].copy() if feat else df


if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.cache_inv = None

raw_df, df_clean = load_clean_data(st.session_state.get("cache_inv"))
if raw_df is None:
    st.error("❌ Dataset not found. Place vehicles_us.csv in data/raw/")
    st.stop()
if df_clean is None:
    st.error(f"❌ Invalid schema. Required columns: {REQUIRED_COLS}")
    st.stop()

with st.sidebar:
    st.title("🚗 CarVision")
    if st.button("🔄 Clear Cache", use_container_width=True, key="btn_clear_cache"):
        st.session_state.cache_inv = datetime.now().isoformat()
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    st.markdown("---")
    pr = (
        st.slider(
            "Price ($)",
            int(df_clean["price"].min()),
            int(df_clean["price"].quantile(0.99)),
            (int(df_clean["price"].min()), int(df_clean["price"].quantile(0.99))),
            format="$%d",
            key="slider_price",
        )
        if "price" in df_clean.columns
        else (0, 1e6)
    )
    yr = (
        st.slider(
            "Year",
            int(df_clean["model_year"].min()),
            int(df_clean["model_year"].max()),
            (int(df_clean["model_year"].min()), int(df_clean["model_year"].max())),
            key="slider_year",
        )
        if "model_year" in df_clean.columns
        else (1990, 2025)
    )
    brands = sorted(df_clean["brand"].dropna().unique()) if "brand" in df_clean.columns else []
    sel_br = st.multiselect("Manufacturers", brands, brands, key="multiselect_brands") if brands else []

    mask = pd.Series(True, index=df_clean.index)
    if "price" in df_clean.columns:
        mask &= df_clean["price"].between(pr[0], pr[1])
    if "model_year" in df_clean.columns:
        mask &= df_clean["model_year"].between(yr[0], yr[1])
    if sel_br and "brand" in df_clean.columns:
        mask &= df_clean["brand"].isin(sel_br)
    df_f = df_clean[mask].copy()

    st.metric("Records", f"{len(df_f):,}", f"{len(df_f) / len(df_clean) * 100:.1f}%")
    st.markdown("---")
    m, mp, _ = load_model(st.session_state.get("cache_inv"))
    st.caption(f"{APP_VERSION} | Modelo: {Path(mp).name if mp else 'N/A'}")

if len(df_f) == 0:
    st.warning("No data. Adjust filters.")
    st.stop()
st.title("🚗 CarVision Market Intelligence")
st.markdown("---")

# Calculate common metrics
avg_age = (pd.Timestamp.now().year - df_f["model_year"]).mean() if "model_year" in df_f.columns else 0

# Navigation - using radio with horizontal layout (maintains state across reruns)
TABS = ["📊 Overview", "📈 Market Analysis", "🧠 Model Metrics", "🔮 Price Predictor"]
selected_tab = st.radio("Navigation", TABS, horizontal=True, key="main_nav", label_visibility="collapsed")
st.markdown("---")

if selected_tab == "📊 Overview":
    st.header("📊 Executive Dashboard")
    tv, ap, mp_v = df_f["price"].sum(), df_f["price"].mean(), df_f["price"].median()
    cv = df_f["price"].std() / ap * 100 if ap > 0 else 0
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📈 Total Value", f"${tv / 1e6:.1f}M", f"{len(df_f):,} units")
    c2.metric("💰 Avg Price", f"${ap:,.0f}", f"{(ap - mp_v) / mp_v * 100:+.1f}% vs median")
    c3.metric("📊 Median", f"${mp_v:,.0f}")
    c4.metric("🚗 Fleet Age", f"{avg_age:.1f} yrs")
    c5.metric("📉 Volatility", f"{cv:.1f}%")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎯 Market Segmentation")
        q1, q3 = df_f["price"].quantile(0.25), df_f["price"].quantile(0.75)
        seg = pd.DataFrame(
            {
                "Seg": ["Economy", "Mid", "Premium"],
                "U": [
                    (df_f["price"] < q1).sum(),
                    df_f["price"].between(q1, q3).sum(),
                    (df_f["price"] > q3).sum(),
                ],
            }
        )
        fig = px.pie(
            seg,
            values="U",
            names="Seg",
            hole=0.4,
            color="Seg",
            color_discrete_map={
                "Economy": "#28a745",
                "Mid": "#17a2b8",
                "Premium": "#ffc107",
            },
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("📈 Price Distribution")
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(x=df_f["price"], nbinsx=50, marker_color="#007bff", opacity=0.7))
        fig2.add_vline(
            x=ap,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: ${ap:,.0f}",
        )
        fig2.add_vline(
            x=mp_v,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Median: ${mp_v:,.0f}",
        )
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🏆 Top Manufacturers")
        if "brand" in df_f.columns:
            tb = df_f["brand"].value_counts().head(10)
            fig3 = px.bar(
                x=tb.values,
                y=tb.index,
                orientation="h",
                color=tb.values,
                color_continuous_scale="Blues",
            )
            fig3.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.subheader("📅 Inventory Age Profile")
        if "model_year" in df_f.columns:
            yd = df_f["model_year"].value_counts().sort_index()
            fig4 = px.area(x=yd.index, y=yd.values, color_discrete_sequence=["#17a2b8"])
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
    with st.expander("🔍 Data Quality"):
        q1, q2, q3 = st.columns(3)
        q1.metric(
            "Completeness",
            f"{100 - raw_df.isnull().sum().sum() / (raw_df.shape[0] * raw_df.shape[1]) * 100:.1f}%",
        )
        q2.metric(
            "Unique Records",
            f"{100 - raw_df.duplicated().sum() / len(raw_df) * 100:.1f}%",
        )
        q3.metric("Total Records", f"{len(raw_df):,}")

elif selected_tab == "📈 Market Analysis":
    st.header("💼 Market Analysis")
    viz, ana = VisualizationEngine(df_f), MarketAnalyzer(df_f)
    summary = ana.generate_executive_summary()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🎯 Market Leader", summary["insights"].get("most_popular_brand", "N/A"))
    k2.metric("💸 Premium Brand", summary["insights"].get("highest_value_brand", "N/A"))
    k3.metric("🔎 Opportunities", f"{summary['kpis'].get('total_opportunities', 0):,}")
    k4.metric("📉 Depreciation", f"{summary['insights'].get('avg_depreciation_rate', 0):.1%}")
    st.markdown("---")
    lc, rc = st.columns([2, 1])
    with lc:
        if "model_year" in df_f.columns:
            pby = df_f.groupby("model_year").agg({"price": ["mean", "median"]}).reset_index()
            pby.columns = ["Year", "Avg", "Med"]
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=pby["Year"],
                    y=pby["Avg"],
                    mode="lines+markers",
                    name="Average",
                    line=dict(color="#007bff", width=3),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=pby["Year"],
                    y=pby["Med"],
                    mode="lines+markers",
                    name="Median",
                    line=dict(color="#28a745", width=2, dash="dash"),
                )
            )
            fig.update_layout(title="Price Trend by Year", height=400)
            st.plotly_chart(fig, use_container_width=True)
    with rc:
        st.metric("Total Value", f"${summary['kpis']['total_market_value'] / 1e6:.2f}M")
        st.metric("Avg Price", f"${summary['kpis']['average_price']:,.0f}")
        st.metric(
            "Potential",
            f"${summary['kpis'].get('potential_arbitrage_value', 0) / 1e3:.1f}K",
        )
        margin = st.slider("Target Margin %", 5, 30, 15, key="slider_margin")
        st.success(f"ROI: **${summary['kpis']['total_market_value'] * margin / 100 / 1e6:.2f}M**")
    st.markdown("---")
    r1, r2 = st.columns(2)
    with r1:
        buy_text = (
            "#### 🟢 Buy Signals\n"
            f"- **{summary['kpis'].get('total_opportunities', 0):,}** undervalued units\n"
            f"- Potential: ${summary['kpis'].get('potential_arbitrage_value', 0):,.0f}"
        )
        st.markdown(buy_text)
    with r2:
        risk_text = (
            "#### 🔴 Risk Factors\n"
            f"- Volatility: {df_f['price'].std() / df_f['price'].mean() * 100:.1f}%\n"
            f"- Fleet Age: {avg_age:.1f} yrs"
        )
        st.markdown(risk_text)
    with st.expander("📈 Full Dashboard"):
        st.plotly_chart(viz.create_market_analysis_dashboard(), use_container_width=True)

elif selected_tab == "🧠 Model Metrics":
    st.header("🧠 Model Metrics")
    met, base = load_json(METRICS_PATH), load_json(ARTIFACTS_DIR / "metrics_baseline.json")
    boot, temp = load_json(ARTIFACTS_DIR / "metrics_bootstrap.json"), load_json(ARTIFACTS_DIR / "metrics_temporal.json")
    if met:
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("🎯 RMSE", f"${met.get('rmse', 0):,.0f}")
        m2.metric("📏 MAE", f"${met.get('mae', 0):,.0f}")
        m3.metric("💯 R²", f"{met.get('r2', 0):.3f}")
        m4.metric("📉 MAPE", f"{met.get('mape', 0):.2f}%")
        m5.metric("✅ Precision", f"{max(0, 100 - met.get('mape', 0)):.1f}%")
        st.markdown("---")
        if base:
            st.subheader("🔬 Model vs Baseline")
            c1, c2 = st.columns([3, 2])
            with c1:
                df_c = pd.DataFrame(
                    {
                        "M": ["RMSE", "MAE", "MAPE", "R²"],
                        "Mod": [met.get(k, 0) for k in ["rmse", "mae", "mape", "r2"]],
                        "Base": [base.get(k, 0) for k in ["rmse", "mae", "mape", "r2"]],
                    }
                )
                fig = go.Figure()
                fig.add_trace(go.Bar(name="Model", x=df_c["M"], y=df_c["Mod"], marker_color="#007bff"))
                fig.add_trace(
                    go.Bar(
                        name="Baseline",
                        x=df_c["M"],
                        y=df_c["Base"],
                        marker_color="#6c757d",
                    )
                )
                fig.update_layout(barmode="group", height=400)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown("#### 📈 Improvements")
                for _, r in df_c.iterrows():
                    if r["Base"] == 0:
                        continue
                    imp = (
                        (r["Base"] - r["Mod"]) / abs(r["Base"]) * 100
                        if r["M"] != "R²"
                        else (r["Mod"] - r["Base"]) / abs(r["Base"]) * 100
                    )
                    (st.success if imp > 0 else st.info)(f"**{r['M']}**: {imp:+.1f}%")
        if boot:
            st.markdown("---")
            st.subheader("📊 Bootstrap Validation")
            b1, b2, b3 = st.columns(3)
            b1.metric("Δ RMSE", f"{boot.get('delta_rmse_mean', 0):.2f}")
            ci = boot.get("delta_rmse_ci95", [None, None])
            b2.metric("95% CI", f"[{ci[0]:.2f}, {ci[1]:.2f}]" if ci[0] else "N/A")
            b3.metric("p-value", f"{boot.get('p_value_two_sided', 0):.3f}")
            if ci[1] and ci[1] < 0:
                st.success("✅ Statistically significant improvement")
        if temp:
            st.markdown("---")
            st.subheader("📅 Temporal Backtest")
            t1, t2, t3, t4 = st.columns(4)
            t1.metric("RMSE", f"${temp.get('rmse', 0):,.0f}")
            t2.metric("MAE", f"${temp.get('mae', 0):,.0f}")
            t3.metric("R²", f"{temp.get('r2', 0):.3f}")
            t4.metric("Samples", f"{temp.get('n_samples', 0):,}")
    else:
        st.warning("No metrics found. Run: `python main.py --mode train`")

elif selected_tab == "🔮 Price Predictor":
    st.header("🔮 Price Estimator")
    model, mpath, _ = load_model(st.session_state.get("cache_inv"))
    if model:
        st.success(f"✅ Model loaded: `{Path(mpath).name}`")
        with st.form("pred"):
            c1, c2, c3 = st.columns(3)
            with c1:
                yr_in = st.number_input("Year", 1990, 2025, 2018)
                odo_in = st.number_input("Mileage", 0, 500000, 50000)
                cyl_in = st.selectbox("Cylinders", [4, 6, 8, 10, 12], 1)
            with c2:
                cond_in = st.selectbox(
                    "Condition",
                    ["excellent", "good", "fair", "like new", "salvage", "new"],
                )
                fuel_in = st.selectbox("Fuel", ["gas", "diesel", "hybrid", "electric"])
                trans_in = st.selectbox("Transmission", ["automatic", "manual", "other"])
            with c3:
                type_in = st.selectbox(
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
                    ],
                )
                paint_in = st.selectbox(
                    "Color",
                    ["white", "black", "silver", "grey", "blue", "red", "green"],
                )
                drive_in = st.selectbox("Drive", ["4wd", "fwd", "rwd"])
            sub = st.form_submit_button("💰 Calculate Price", use_container_width=True)
        if sub:
            if odo_in < 0:
                st.error("Invalid mileage")
                st.stop()
            data = {
                "model_year": yr_in,
                "odometer": odo_in,
                "condition": cond_in,
                "cylinders": cyl_in,
                "fuel": fuel_in,
                "transmission": trans_in,
                "type": type_in,
                "paint_color": paint_in,
                "drive": drive_in,
                "model": "ford f-150",
            }
            feat, num, _ = get_pre_cols(model)
            inp = prep_input(data, feat, num)
            try:
                pred = model.predict(inp)[0]
                pctl = (df_clean["price"] < pred).mean() * 100
                st.markdown("---")
                st.subheader("🎯 Result")
                r1, r2, r3 = st.columns([2, 2, 3])
                with r1:
                    st.markdown(f"### ${pred:,.0f}")
                    if pctl > 75:
                        col = "#FFD700"
                    elif pctl > 50:
                        col = "#007bff"
                    elif pctl > 25:
                        col = "#17a2b8"
                    else:
                        col = "#28a745"
                    txt = (
                        "🏆 Premium"
                        if pctl > 75
                        else ("💼 Upper Market" if pctl > 50 else "🎯 Mid Market" if pctl > 25 else "💚 Economy")
                    )
                    badge_html = (
                        f'<div style="background:{col};'
                        "color:white;padding:12px;border-radius:8px;"
                        'text-align:center;font-weight:bold">'
                        f"{txt}</div>"
                    )
                    st.markdown(badge_html, unsafe_allow_html=True)
                with r2:
                    st.metric("Percentile", f"{pctl:.0f}th", f"Higher than {pctl:.0f}%")
                    med = df_clean["price"].median()
                    st.info(f"**{'Above' if pred > med else 'Below'}** median")
                with r3:
                    fig = go.Figure(
                        go.Indicator(
                            mode="gauge+number+delta",
                            value=pred,
                            delta={"reference": med},
                            gauge={
                                "axis": {"range": [0, df_clean["price"].max() * 1.1]},
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
                            },
                        )
                    )
                    fig.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                try:
                    import shap  # type: ignore[import]  # noqa: F401

                    with st.expander("🔬 SHAP Explanation"):
                        st.info("SHAP available. Implement explainer based on your model.")
                except ImportError:
                    st.caption("💡 Install shap for model explanations")
            except Exception as e:
                st.error(f"Prediction error: {e}")
    else:
        st.error("❌ Model not found. Place artifacts/model.joblib or run: python main.py --mode train")

# POST-INSTALACIÓN:
# 1) Asegurar artifacts/model.joblib
# 2) Colocar data/raw/vehicles_us.csv
# 3) Opcional: pip install pandera shap
