import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta

def delta_html(curr, prev, fmt=".0f", prefix=""):
    if prev == 0: return ""
    d = (curr - prev) / prev * 100
    cls = "kpi-delta-pos" if d >= 0 else "kpi-delta-neg"
    arrow = "▲" if d >= 0 else "▼"
    return f'<div class="{cls}">{arrow} {abs(d):.1f}% vs prev</div>'

def kpi_card(col, value, label, delta_html_str="", prefix="₹", suffix=""):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{prefix}{value:,.0f}{suffix}</div>
        <div class="kpi-label">{label}</div>
        {delta_html_str}
    </div>""", unsafe_allow_html=True)

def render_overview(df, filtered_df, date_from, date_to, sel_cat, sel_prod, rolling_window, CHART_LAYOUT):
    st.markdown("### Dashboard Overview")

    # ── KPI Cards ─────────────────────────────────────────────
    total_rev   = filtered_df["Revenue_d"].sum()
    total_sales = filtered_df["Sales_d"].sum()
    avg_rating  = filtered_df["Rating"].mean()
    avg_disc    = filtered_df["Discount"].mean()
    avg_mspend  = filtered_df["M_Spend"].sum()
    avg_success = filtered_df["Success_Percentage"].mean()

    # Compare to previous period for delta
    period_days = (pd.Timestamp(date_to) - pd.Timestamp(date_from)).days + 1
    prev_from = pd.Timestamp(date_from) - timedelta(days=period_days)
    prev_to   = pd.Timestamp(date_from) - timedelta(days=1)
    prev_mask = (df["Date"].dt.date >= prev_from.date()) & (df["Date"].dt.date <= prev_to.date())
    if sel_cat  != "All": prev_mask &= (df["Category"] == sel_cat)
    if sel_prod != "All": prev_mask &= (df["Product_Name"] == sel_prod)
    prev_df = df[prev_mask]

    prev_rev   = prev_df["Revenue_d"].sum() if len(prev_df) > 0 else 0
    prev_sales = prev_df["Sales_d"].sum()   if len(prev_df) > 0 else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    kpi_card(c1, total_rev/1e6,  "Total Revenue (M)",  delta_html(total_rev, prev_rev), "₹")
    kpi_card(c2, total_sales,    "Total Sales",         delta_html(total_sales, prev_sales), "")
    kpi_card(c3, avg_rating,     "Avg Rating",          "", "", "/5")
    kpi_card(c4, avg_disc,       "Avg Discount",        "", "", "%")
    kpi_card(c5, avg_mspend/1e3, "Mktg Spend (K)",     "", "₹")
    kpi_card(c6, avg_success,    "Avg Success %",       "", "", "%")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Revenue Trend ──────────────────────────────────────────
    col_l, col_r = st.columns([2, 1])

    with col_l:
        st.markdown('<div class="section-header">Revenue Trend</div>', unsafe_allow_html=True)
        daily_rev = filtered_df.groupby("Date")["Revenue_d"].sum().reset_index()
        daily_rev["Rolling"] = daily_rev["Revenue_d"].rolling(rolling_window, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_rev["Date"], y=daily_rev["Revenue_d"],
            name="Daily Revenue", marker_color="rgba(0,212,255,0.3)",
            hovertemplate="<b>%{x|%b %d}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=daily_rev["Date"], y=daily_rev["Rolling"],
            name=f"{rolling_window}d MA", line=dict(color="#00d4ff", width=2),
            hovertemplate="<b>%{x|%b %d}</b><br>MA: ₹%{y:,.0f}<extra></extra>"
        ))
        fig.update_layout(**CHART_LAYOUT, height=260, title="Daily Revenue + Rolling Average")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_r:
        st.markdown('<div class="section-header">Revenue by Category</div>', unsafe_allow_html=True)
        cat_rev = filtered_df.groupby("Category")["Revenue_d"].sum().reset_index()
        fig2 = go.Figure(go.Pie(
            labels=cat_rev["Category"], values=cat_rev["Revenue_d"],
            hole=0.55, textinfo="label+percent",
            textfont=dict(size=10, color="#e2e8f0"),
            marker=dict(colors=["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444"])
        ))
        fig2.update_layout(**CHART_LAYOUT, height=260,
            title="Category Share",
            annotations=[dict(text="Revenue", x=0.5, y=0.5, font_size=12, showarrow=False, font_color="#64748b")]
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Product Performance ────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header">Top Products by Revenue</div>', unsafe_allow_html=True)
        prod_rev = filtered_df.groupby("Product_Name")["Revenue_d"].sum().nlargest(10).reset_index()
        fig3 = go.Figure(go.Bar(
            x=prod_rev["Revenue_d"], y=prod_rev["Product_Name"],
            orientation="h", marker=dict(
                color=prod_rev["Revenue_d"],
                colorscale=[[0,"#1a2235"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
                showscale=False
            ),
            hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>"
        ))
        fig3.update_layout(**CHART_LAYOUT, height=260, title="Revenue by Product")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown('<div class="section-header">Sales vs Discount Correlation</div>', unsafe_allow_html=True)
        fig4 = px.scatter(
            filtered_df, x="Discount", y="Sales_d", color="Category",
            size="Revenue_d", hover_name="Product_Name",
            color_discrete_sequence=["#00d4ff","#7c3aed","#10b981","#f59e0b","#ef4444"],
            opacity=0.7
        )
        fig4.update_layout(**CHART_LAYOUT, height=260, title="Sales vs Discount by Category")
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

    # ── Success Heatmap ────────────────────────────────────────
    st.markdown('<div class="section-header">Success % Heatmap — Product × Week</div>', unsafe_allow_html=True)
    heat_df = filtered_df.copy()
    heat_df["Week"] = heat_df["Date"].dt.isocalendar().week.astype(str).apply(lambda x: f"W{x}")
    heat_data = heat_df.groupby(["Product_Name","Week"])["Success_Percentage"].mean().reset_index()
    heat_pivot = heat_data.pivot(index="Product_Name", columns="Week", values="Success_Percentage")
    fig5 = go.Figure(go.Heatmap(
        z=heat_pivot.values, x=heat_pivot.columns, y=heat_pivot.index,
        colorscale=[[0,"#1a2235"],[0.4,"#7c3aed"],[0.7,"#00d4ff"],[1,"#10b981"]],
        hovertemplate="<b>%{y}</b><br>%{x}<br>Success: %{z:.1f}%<extra></extra>",
        text=heat_pivot.values.round(0), texttemplate="%{text}",
        textfont=dict(size=9, color="white"), showscale=True
    ))
    fig5.update_layout(**CHART_LAYOUT, height=300, title="Success % by Product and Week")
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
