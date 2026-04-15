import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Import external modules
from utils.ui import CUSTOM_CSS, CHART_LAYOUT
from components.overview import render_overview
from components.talk_to_data import render_talk_to_data
from components.change_detection import render_change_detection
from components.causal_analysis import render_causal_analysis

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KPI Intelligence System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─── Data Loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "kpi_data.csv")
    df = pd.read_csv(csv_path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ─── Groq Client ──────────────────────────────────────────────────────────
client = Groq()

# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand-header">◈ KPI.Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">AI-Powered Analytics</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Date range
    st.markdown('<div class="section-header">Date Range</div>', unsafe_allow_html=True)
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    date_from = st.date_input("From", min_date, min_value=min_date, max_value=max_date)
    date_to   = st.date_input("To",   max_date, min_value=min_date, max_value=max_date)

    # Filters
    st.markdown('<div class="section-header">Filters</div>', unsafe_allow_html=True)
    all_cats = ["All"] + sorted(df["Category"].unique().tolist())
    sel_cat  = st.selectbox("Category", all_cats)
    all_prods = ["All"] + sorted(df["Product_Name"].unique().tolist())
    sel_prod  = st.selectbox("Product", all_prods)

    # Detection settings
    st.markdown('<div class="section-header">Detection Settings</div>', unsafe_allow_html=True)
    threshold_pct   = st.slider("Change Alert Threshold (%)", 5, 50, 15)
    rolling_window  = st.slider("Rolling Avg Window (days)", 3, 14, 7)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem; color:#64748b; line-height:1.6;">
    <b style="color:#00d4ff;">Powered by</b><br>
    Claude Sonnet · Pandas · Plotly<br>
    © 2025 KPI Intelligence
    </div>""", unsafe_allow_html=True)

# ─── Filter Data ────────────────────────────────────────────────────────────────
mask = (df["Date"].dt.date >= date_from) & (df["Date"].dt.date <= date_to)
if sel_cat  != "All": mask &= (df["Category"] == sel_cat)
if sel_prod != "All": mask &= (df["Product_Name"] == sel_prod)
filtered_df = df[mask].copy()

# ─── Top Navigation ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Overview",
    "💬  Talk-to-Data",
    "🔍  Change Detection",
    "🧠  Causal Analysis"
])

# Render Tab 1
with tab1:
    render_overview(
        df=df,
        filtered_df=filtered_df,
        date_from=date_from,
        date_to=date_to,
        sel_cat=sel_cat,
        sel_prod=sel_prod,
        rolling_window=rolling_window,
        CHART_LAYOUT=CHART_LAYOUT
    )

# Render Tab 2
with tab2:
    render_talk_to_data(
        df=df,
        filtered_df=filtered_df,
        client=client,
        date_from=date_from,
        date_to=date_to,
        sel_cat=sel_cat,
        sel_prod=sel_prod
    )

# Render Tab 3
with tab3:
    render_change_detection(
        filtered_df=filtered_df,
        rolling_window=rolling_window,
        CHART_LAYOUT=CHART_LAYOUT
    )

# Render Tab 4
with tab4:
    render_causal_analysis(
        filtered_df=filtered_df,
        threshold_pct=threshold_pct,
        date_to=date_to,
        CHART_LAYOUT=CHART_LAYOUT,
        client=client,
        sel_cat=sel_cat,
        sel_prod=sel_prod,
        date_from=date_from
    )
