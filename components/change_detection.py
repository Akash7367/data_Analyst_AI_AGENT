import streamlit as st
import plotly.graph_objects as go

def render_change_detection(filtered_df, rolling_window, CHART_LAYOUT):
    st.markdown("### 🔍 KPI Monitoring & Change Detection")

    detect_col, config_col = st.columns([3, 1])

    with config_col:
        st.markdown('<div class="section-header">Detection Config</div>', unsafe_allow_html=True)
        kpi_metric = st.selectbox("KPI to Monitor", ["Revenue_d","Sales_d","Rating","Success_Percentage","M_Spend","Discount"], index=0)
        detection_method = st.radio("Method", ["% Change vs Rolling Avg", "Day-over-Day % Change", "Z-Score"])
        
        if detection_method == "Z-Score":
            severity_map = {"Low (1.5σ)": 1.5, "Medium (2.0σ)": 2.0, "High (3.0σ)": 3.0}
            threshold_unit = "σ"
        else:
            severity_map = {"Low (5%)": 5, "Medium (15%)": 15, "High (25%)": 25}
            threshold_unit = "%"
            
        alert_level  = st.selectbox("Alert Sensitivity", list(severity_map.keys()), index=1)
        alert_thresh = severity_map[alert_level]

    with detect_col:
        # Compute daily aggregation
        daily_kpi = filtered_df.groupby("Date")[kpi_metric].sum().reset_index()
        daily_kpi.columns = ["Date", "Value"]
        daily_kpi = daily_kpi.sort_values("Date").reset_index(drop=True)
        daily_kpi["RollingAvg"] = daily_kpi["Value"].rolling(rolling_window, min_periods=1).mean()

        if detection_method == "% Change vs Rolling Avg":
            daily_kpi["Change"] = (daily_kpi["Value"] - daily_kpi["RollingAvg"]) / daily_kpi["RollingAvg"] * 100
        elif detection_method == "Day-over-Day % Change":
            daily_kpi["Change"] = daily_kpi["Value"].pct_change() * 100
        else:  # Z-Score
            mu, sigma = daily_kpi["Value"].mean(), daily_kpi["Value"].std()
            daily_kpi["Change"] = (daily_kpi["Value"] - mu) / (sigma if sigma else 1)

        daily_kpi["Alert"] = daily_kpi["Change"].abs() >= alert_thresh
        daily_kpi["AlertType"] = daily_kpi["Change"].apply(
            lambda x: "drop" if x <= -alert_thresh else ("spike" if x >= alert_thresh else "normal")
        )

        # Chart
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(
            x=daily_kpi["Date"], y=daily_kpi["Value"],
            name=kpi_metric, line=dict(color="#00d4ff", width=1.5),
            fill="tozeroy", fillcolor="rgba(0,212,255,0.05)"
        ))
        fig6.add_trace(go.Scatter(
            x=daily_kpi["Date"], y=daily_kpi["RollingAvg"],
            name=f"{rolling_window}d MA", line=dict(color="#7c3aed", width=2, dash="dash")
        ))
        # Highlight alerts
        drops  = daily_kpi[daily_kpi["AlertType"] == "drop"]
        spikes = daily_kpi[daily_kpi["AlertType"] == "spike"]
        if len(drops):
            fig6.add_trace(go.Scatter(
                x=drops["Date"], y=drops["Value"], mode="markers",
                marker=dict(color="#ef4444", size=10, symbol="triangle-down"),
                name="Drop Alert"
            ))
        if len(spikes):
            fig6.add_trace(go.Scatter(
                x=spikes["Date"], y=spikes["Value"], mode="markers",
                marker=dict(color="#f59e0b", size=10, symbol="triangle-up"),
                name="Spike Alert"
            ))
        fig6.update_layout(**CHART_LAYOUT, height=280, title=f"{kpi_metric} — Trend & Anomaly Detection")
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})

        # Change magnitude chart
        change_label = "Change % / Z-Score"
        fig7 = go.Figure()
        colors = ["#ef4444" if r.AlertType=="drop" else "#f59e0b" if r.AlertType=="spike" else "#1e293b"
                  for _, r in daily_kpi.iterrows()]
        fig7.add_trace(go.Bar(
            x=daily_kpi["Date"], y=daily_kpi["Change"],
            marker_color=colors, name="Change",
            hovertemplate="<b>%{x|%b %d}</b><br>Change: %{y:.1f}<extra></extra>"
        ))
        fig7.add_hline(y=alert_thresh,  line_dash="dot", line_color="#f59e0b", annotation_text=f"+{alert_thresh}{threshold_unit} threshold")
        fig7.add_hline(y=-alert_thresh, line_dash="dot", line_color="#ef4444", annotation_text=f"-{alert_thresh}{threshold_unit} threshold")
        fig7.update_layout(**CHART_LAYOUT, height=200, title="Change Magnitude")
        st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

    # Alert Log Table
    st.markdown('<div class="section-header">Alert Log</div>', unsafe_allow_html=True)
    alerts = daily_kpi[daily_kpi["Alert"]].copy()
    if len(alerts):
        n_drops  = (alerts["AlertType"] == "drop").sum()
        n_spikes = (alerts["AlertType"] == "spike").sum()
        ac1, ac2, ac3 = st.columns(3)
        ac1.markdown(f'<div class="alert-box">🔴 <b>{n_drops}</b> Drop Alerts detected</div>', unsafe_allow_html=True)
        ac2.markdown(f'<div class="warn-box">🟡 <b>{n_spikes}</b> Spike Alerts detected</div>', unsafe_allow_html=True)
        ac3.markdown(f'<div class="info-box">📅 Most recent: <b>{alerts["Date"].max().strftime("%b %d, %Y")}</b></div>', unsafe_allow_html=True)

        display_alerts = alerts[["Date","Value","RollingAvg","Change","AlertType"]].copy()
        display_alerts.columns = ["Date","Value","Rolling Avg",f"Change ({threshold_unit})","Type"]
        display_alerts["Date"] = display_alerts["Date"].dt.strftime("%Y-%m-%d")
        display_alerts["Value"] = display_alerts["Value"].apply(lambda x: f"{x:,.0f}")
        display_alerts["Rolling Avg"] = display_alerts["Rolling Avg"].apply(lambda x: f"{x:,.0f}")
        display_alerts[f"Change ({threshold_unit})"] = display_alerts[f"Change ({threshold_unit})"].apply(lambda x: f"{x:+.1f}{threshold_unit}")
        st.dataframe(display_alerts.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="success-box">✅ No significant deviations detected in the selected period.</div>', unsafe_allow_html=True)
