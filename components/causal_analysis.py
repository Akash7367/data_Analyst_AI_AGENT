import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_causal_analysis(filtered_df, threshold_pct, date_to, CHART_LAYOUT, client, sel_cat, sel_prod, date_from):
    st.markdown("### 🧠 Causal Analysis & Action Recommendations")

    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown('<div class="section-header">Select a Change Event to Investigate</div>', unsafe_allow_html=True)

        # Use alerts from tab3 detection or let user pick a date
        daily_rev_full = filtered_df.groupby("Date")["Revenue_d"].sum().reset_index()
        daily_rev_full = daily_rev_full.sort_values("Date").reset_index(drop=True)
        daily_rev_full["RollingAvg"] = daily_rev_full["Revenue_d"].rolling(7, min_periods=1).mean()
        daily_rev_full["Change"] = (daily_rev_full["Revenue_d"] - daily_rev_full["RollingAvg"]) / daily_rev_full["RollingAvg"] * 100
        big_changes = daily_rev_full[daily_rev_full["Change"].abs() >= threshold_pct].sort_values("Change")

        if len(big_changes):
            date_options = [f"{row.Date.strftime('%Y-%m-%d')} ({row.Change:+.1f}%)"
                            for _, row in big_changes.iterrows()]
            chosen_option = st.selectbox("Detected Change Events", date_options)
            chosen_date_str = chosen_option.split(" ")[0]
            chosen_date = pd.Timestamp(chosen_date_str)
        else:
            chosen_date = pd.Timestamp(date_to)
            st.info("No major changes detected. Analysing most recent date.")

        # Show mini context chart
        context_start = chosen_date - timedelta(days=7)
        context_end   = chosen_date + timedelta(days=7)
        ctx = daily_rev_full[(daily_rev_full["Date"] >= context_start) & (daily_rev_full["Date"] <= context_end)]
        fig_ctx = go.Figure()
        fig_ctx.add_trace(go.Bar(
            x=ctx["Date"], y=ctx["Revenue_d"],
            marker_color=["#ef4444" if d == chosen_date else "rgba(0,212,255,0.4)" for d in ctx["Date"]],
            name="Revenue"
        ))
        fig_ctx.add_trace(go.Scatter(
            x=ctx["Date"], y=ctx["RollingAvg"],
            line=dict(color="#7c3aed", dash="dash"), name="MA"
        ))
        fig_ctx.update_layout(**CHART_LAYOUT, height=200, title="Context Window (±7 days)")
        st.plotly_chart(fig_ctx, use_container_width=True, config={"displayModeBar": False})

    with c_right:
        st.markdown('<div class="section-header">Correlation Analysis</div>', unsafe_allow_html=True)
        # Show correlation of KPIs around chosen date
        window_df = filtered_df[
            (filtered_df["Date"] >= chosen_date - timedelta(days=7)) &
            (filtered_df["Date"] <= chosen_date + timedelta(days=7))
        ]
        corr_cols = ["Revenue_d","Sales_d","Discount","M_Spend","Rating","Supply_Chain_E","Market_T","Seasonality_T","Success_Percentage"]
        available_corr = [c for c in corr_cols if c in window_df.columns]
        if len(window_df) > 3:
            corr = window_df[available_corr].corr()["Revenue_d"].drop("Revenue_d").sort_values()
            fig_corr = go.Figure(go.Bar(
                x=corr.values, y=corr.index, orientation="h",
                marker_color=["#ef4444" if v < 0 else "#10b981" for v in corr.values],
                hovertemplate="<b>%{y}</b><br>Correlation: %{x:.3f}<extra></extra>"
            ))
            fig_corr.update_layout(**CHART_LAYOUT, height=200, title="Correlation with Revenue (Context Window)")
            st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

    st.markdown("---")

    # ── AI Causal Analysis ─────────────────────────────────────
    st.markdown('<div class="section-header">AI-Powered Causal Reasoning & Recommendations</div>', unsafe_allow_html=True)

    if st.button("🔬 Run Causal Analysis", key="run_causal", use_container_width=False):
        # Prepare comprehensive data snapshot around the event
        event_day   = filtered_df[filtered_df["Date"] == chosen_date]
        before_7    = filtered_df[(filtered_df["Date"] >= chosen_date - timedelta(days=7)) &
                                   (filtered_df["Date"] < chosen_date)]
        after_3     = filtered_df[(filtered_df["Date"] > chosen_date) &
                                   (filtered_df["Date"] <= chosen_date + timedelta(days=3))]

        def agg_snapshot(d):
            if len(d) == 0: return "No data"
            return d.agg({
                "Revenue_d":"sum","Sales_d":"sum","Discount":"mean",
                "M_Spend":"sum","Rating":"mean","Supply_Chain_E":"mean",
                "Market_T":"mean","Seasonality_T":"mean","Success_Percentage":"mean"
            }).to_dict()

        event_snapshot   = agg_snapshot(event_day)
        before_snapshot  = agg_snapshot(before_7)
        after_snapshot   = agg_snapshot(after_3)

        # Category-level breakdown
        cat_breakdown = ""
        if len(event_day):
            cat_breakdown = event_day.groupby("Category")["Revenue_d"].sum().to_string()
        prod_breakdown = ""
        if len(event_day):
            prod_breakdown = event_day.groupby("Product_Name")[["Revenue_d","Sales_d","Discount","Rating"]].mean().to_string()

        # Revenue change %
        event_rev  = event_day["Revenue_d"].sum()
        before_rev = before_7["Revenue_d"].sum() / max(len(before_7["Date"].unique()), 1)
        pct_change = ((event_rev - before_rev) / before_rev * 100) if before_rev else 0

        prompt = f"""You are a senior business analyst performing causal analysis on a KPI event.

EVENT DETAILS:
- Date: {chosen_date.strftime('%Y-%m-%d')}
- Revenue on event day: ₹{event_rev:,.0f}
- Avg daily revenue (prior 7 days): ₹{before_rev:,.0f}
- Change: {pct_change:+.1f}%

7-DAY BEFORE SNAPSHOT (aggregated):
{json.dumps(before_snapshot, indent=2)}

EVENT DAY SNAPSHOT:
{json.dumps(event_snapshot, indent=2)}

3-DAY AFTER SNAPSHOT:
{json.dumps(after_snapshot, indent=2)}

CATEGORY REVENUE ON EVENT DAY:
{cat_breakdown}

PRODUCT-LEVEL METRICS ON EVENT DAY:
{prod_breakdown}

AVAILABLE FIELDS: Revenue_d, Sales_d, Discount, M_Spend, Rating, Supply_Chain_E (supply chain efficiency %), Market_T (market trend score), Seasonality_T (seasonality index), Success_Percentage

---

Please provide a structured analysis:

## 1. ROOT CAUSE ANALYSIS
Identify the top 3-5 most likely causes of this KPI change. For each cause:
- State the cause clearly
- Support with specific numbers from the data
- Rank by impact (High/Medium/Low)

## 2. CATEGORY & PRODUCT INSIGHTS
Which categories or products drove the change? What patterns do you see?

## 3. CONTRIBUTING FACTORS
Analyse correlations between Revenue and other variables (Discount, M_Spend, Supply_Chain_E, Market_T, Seasonality_T). Which factors moved in the same direction as the revenue change?

## 4. ACTION RECOMMENDATIONS
Provide 4-6 concrete, executive-ready business recommendations. For each:
- Action: What to do
- Rationale: Why (tied to a specific cause)
- Priority: URGENT / HIGH / MEDIUM
- Expected Impact: What improvement to expect

Be data-driven, specific, and business-ready. Use ₹ for currencies."""

        with st.spinner("Running AI causal analysis..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            analysis = response.choices[0].message.content
            st.session_state["causal_analysis"] = analysis
            st.session_state["causal_date"] = chosen_date.strftime('%Y-%m-%d')

    # Display saved analysis
    if "causal_analysis" in st.session_state:
        st.markdown(f"""
        <div class="info-box">
            📅 Analysis for: <strong>{st.session_state.get('causal_date', '')}</strong>
        </div>""", unsafe_allow_html=True)

        analysis_text = st.session_state["causal_analysis"]

        # Parse and display sections
        sections = analysis_text.split("##")
        for section in sections:
            section = section.strip()
            if not section: continue
            lines = section.split("\n", 1)
            if len(lines) >= 1:
                title = lines[0].strip()
                body  = lines[1].strip() if len(lines) > 1 else ""

                if "ROOT CAUSE" in title.upper():
                    st.markdown(f'<div class="alert-box" style="margin-bottom: 8px;"><strong>🔴 {title}</strong></div>', unsafe_allow_html=True)
                elif "RECOMMENDATION" in title.upper():
                    st.markdown(f'<div class="success-box" style="margin-bottom: 8px;"><strong>✅ {title}</strong></div>', unsafe_allow_html=True)
                elif "CATEGORY" in title.upper() or "PRODUCT" in title.upper():
                    st.markdown(f'<div class="warn-box" style="margin-bottom: 8px;"><strong>🟡 {title}</strong></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="info-box" style="margin-bottom: 8px;"><strong>🔵 {title}</strong></div>', unsafe_allow_html=True)
                
                if body:
                    st.markdown(body)

        # Download report
        report = f"""KPI INTELLIGENCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Analysis Date: {st.session_state.get('causal_date', '')}
Filters: Category={sel_cat} | Product={sel_prod} | {date_from} to {date_to}

{'='*60}

{analysis_text}
"""
        st.download_button(
            "📥 Download Report",
            data=report, file_name=f"kpi_report_{st.session_state.get('causal_date','')}.txt",
            mime="text/plain"
        )
    else:
        st.markdown('<div class="info-box">👆 Select a change event and click "Run Causal Analysis" to get AI-powered insights and recommendations.</div>', unsafe_allow_html=True)
