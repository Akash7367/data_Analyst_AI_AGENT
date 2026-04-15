# Shared UI configurations for Streamlit

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#e2e8f0", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor="#1e293b", showgrid=True),
    yaxis=dict(gridcolor="#1e293b", showgrid=True),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e293b"),
    colorway=["#00d4ff", "#7c3aed", "#10b981", "#f59e0b", "#ef4444",
               "#06b6d4", "#8b5cf6", "#34d399", "#fbbf24", "#f87171"],
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --accent: #00d4ff;
    --accent2: #7c3aed;
    --accent3: #10b981;
    --warn: #f59e0b;
    --danger: #ef4444;
    --text: #e2e8f0;
    --muted: #64748b;
    --border: #1e293b;
}

html, body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

.stApp > header { background: transparent !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* KPI Cards */
.kpi-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.kpi-value { font-family: 'Space Mono', monospace; font-size: 1.8rem; font-weight: 700; color: var(--accent); }
.kpi-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin-top: 4px; }
.kpi-delta-pos { font-size: 0.8rem; color: var(--accent3); font-weight: 600; }
.kpi-delta-neg { font-size: 0.8rem; color: var(--danger); font-weight: 600; }

/* Chat */
.chat-user {
    background: var(--accent2);
    border-radius: 16px 16px 4px 16px;
    padding: 12px 16px;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
    color: white;
    font-size: 0.9rem;
}
.chat-ai {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 16px 16px 16px 4px;
    padding: 16px;
    margin: 8px 0;
    max-width: 90%;
    font-size: 0.9rem;
    line-height: 1.6;
}
.chat-ai strong { color: var(--accent); }

/* Section Headers */
.section-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Alert Box */
.alert-box {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-left: 4px solid var(--danger);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.85rem;
}
.warn-box {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-left: 4px solid var(--warn);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.85rem;
}
.success-box {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-left: 4px solid var(--accent3);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.85rem;
}
.info-box {
    background: rgba(0,212,255,0.07);
    border: 1px solid rgba(0,212,255,0.2);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 0.85rem;
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, var(--accent2), #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: opacity 0.2s !important;
}
.stButton button:hover { opacity: 0.85 !important; }

/* Input fields */
.stTextInput input, .stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface2) !important;
    color: var(--accent) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* Logo / Title */
.brand-header {
    font-family: 'Space Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
}
.brand-sub {
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Plotly charts background */
.js-plotly-plot .plotly { background: transparent !important; }

/* Recommendation card */
.rec-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
    margin: 8px 0;
}
.rec-priority-high { border-left: 3px solid var(--danger); }
.rec-priority-med  { border-left: 3px solid var(--warn); }
.rec-priority-low  { border-left: 3px solid var(--accent3); }

/* Dataframe */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Hide Streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
"""
