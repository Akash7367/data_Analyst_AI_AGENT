#!/usr/bin/env python3
"""
KPI Intelligence System — CLI Entry Point
Run: python cli.py
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

# Fix encoding for Windows consoles
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

import pandas as pd
import numpy as np
from groq import Groq

# ─── Setup ─────────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
GREY   = "\033[90m"
MAGENTA = "\033[95m"

def c(text, color): return f"{color}{text}{RESET}"
def header(text):   print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}\n{BOLD}{CYAN}  {text}{RESET}\n{BOLD}{CYAN}{'─'*60}{RESET}")
def success(text):  print(f"{GREEN}  ✔  {text}{RESET}")
def warn(text):     print(f"{YELLOW}  ⚠  {text}{RESET}")
def error(text):    print(f"{RED}  ✘  {text}{RESET}")
def info(text):     print(f"{BLUE}  ℹ  {text}{RESET}")
def sep():          print(f"{GREY}  {'·'*55}{RESET}")

# ─── Load Data ─────────────────────────────────────────────────────────────────
def load_data():
    path = os.path.join(os.path.dirname(__file__), "kpi_data.csv")
    if not os.path.exists(path):
        error(f"Data file not found: {path}")
        sys.exit(1)
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

# ─── API Client ──────────────────────────────────────────────────────────
client = Groq()

def build_data_context(df, date_from=None, date_to=None, category="All", product="All"):
    mask = pd.Series([True] * len(df))
    if date_from: mask &= df["Date"].dt.date >= pd.Timestamp(date_from).date()
    if date_to:   mask &= df["Date"].dt.date <= pd.Timestamp(date_to).date()
    if category != "All": mask &= df["Category"] == category
    if product  != "All": mask &= df["Product_Name"] == product
    fdf = df[mask]
    return fdf, f"""
Dataset: {df.shape[0]} rows, {df['Date'].min().date()} to {df['Date'].max().date()}
Filtered rows: {len(fdf)}
Columns: {list(df.columns)}
Categories: {df['Category'].unique().tolist()}
Products: {df['Product_Name'].unique().tolist()}

Revenue by category: {fdf.groupby('Category')['Revenue_d'].sum().to_dict()}
Revenue by product (top 5): {fdf.groupby('Product_Name')['Revenue_d'].sum().nlargest(5).to_dict()}
Total revenue: ₹{fdf['Revenue_d'].sum():,.0f}
Total sales: {fdf['Sales_d'].sum():,}
Avg rating: {fdf['Rating'].mean():.2f}
Avg discount: {fdf['Discount'].mean():.1f}%

Daily revenue (last 14 days):
{fdf.groupby('Date')['Revenue_d'].sum().tail(14).to_string()}

Day-over-day biggest drops:
{fdf.groupby('Date')['Revenue_d'].sum().diff().nsmallest(5).to_string()}
"""

# ─── Feature 1: Talk-to-Data ──────────────────────────────────────────────────
def talk_to_data(df, filters):
    header("💬  TALK-TO-DATA  |  Natural Language Q&A")
    print(f"  {GREY}Type your question. 'back' to return to menu.{RESET}\n")

    fdf, context = build_data_context(df, **filters)
    
    system = f"""You are a KPI Intelligence Analyst for a retail/ecommerce business.
Data context:
{context}

Answer questions concisely with exact numbers. Use ₹ for currency.
Be executive-ready. No code, no jargon."""

    conversation = [{"role": "system", "content": system}]

    while True:
        try:
            q = input(f"\n  {CYAN}You{RESET} ▶  ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("back", "exit", "q", ""): break

        conversation.append({"role": "user", "content": q})
        print(f"\n  {YELLOW}Thinking...{RESET}", end="\r")

        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            messages=conversation
        )
        answer = resp.choices[0].message.content
        conversation.append({"role": "assistant", "content": answer})

        print(f"\n  {GREEN}AI{RESET} ▶  {answer}\n")
        sep()

# ─── Feature 2: KPI Monitoring ────────────────────────────────────────────────
def kpi_monitoring(df, filters):
    header("🔍  KPI MONITORING  |  Change Detection")

    fdf, _ = build_data_context(df, **filters)

    print(f"\n  {CYAN}Select KPI to monitor:{RESET}")
    kpis = ["Revenue_d", "Sales_d", "Rating", "Success_Percentage", "M_Spend"]
    for i, k in enumerate(kpis, 1):
        print(f"    {i}. {k}")
    try:
        choice = int(input("\n  Enter number [1]: ").strip() or "1") - 1
        kpi = kpis[max(0, min(choice, len(kpis)-1))]
    except ValueError:
        kpi = "Revenue_d"

    try:
        threshold = float(input(f"  Change threshold % [15]: ").strip() or "15")
        window    = int(input(f"  Rolling window days [7]: ").strip() or "7")
    except ValueError:
        threshold, window = 15, 7

    daily = fdf.groupby("Date")[kpi].sum().reset_index()
    daily.columns = ["Date", "Value"]
    daily = daily.sort_values("Date").reset_index(drop=True)
    daily["RollingAvg"] = daily["Value"].rolling(window, min_periods=1).mean()
    daily["Change"]     = (daily["Value"] - daily["RollingAvg"]) / daily["RollingAvg"] * 100
    daily["Alert"]      = daily["Change"].abs() >= threshold

    alerts = daily[daily["Alert"]].copy()

    print(f"\n  {BOLD}Monitoring: {c(kpi, CYAN)} | Threshold: {c(f'{threshold}%', YELLOW)} | Window: {c(f'{window}d', YELLOW)}{RESET}")
    print(f"  Period: {daily['Date'].min().date()} → {daily['Date'].max().date()}")
    print(f"  Total data points: {len(daily)} days\n")
    sep()

    if len(alerts) == 0:
        success(f"No significant deviations detected (threshold: {threshold}%)")
    else:
        drops  = alerts[alerts["Change"] < 0]
        spikes = alerts[alerts["Change"] > 0]

        print(f"\n  {RED}▼ DROP ALERTS ({len(drops)}){RESET}")
        for _, row in drops.iterrows():
            chg = row['Change']
            print(f"    {row['Date'].strftime('%Y-%m-%d')}  |  {kpi}: {row['Value']:>12,.0f}  |  {c(f'{chg:+.1f}%', RED)}")

        print(f"\n  {YELLOW}▲ SPIKE ALERTS ({len(spikes)}){RESET}")
        for _, row in spikes.iterrows():
            chg = row['Change']
            print(f"    {row['Date'].strftime('%Y-%m-%d')}  |  {kpi}: {row['Value']:>12,.0f}  |  {c(f'{chg:+.1f}%', YELLOW)}")

    sep()
    print(f"\n  {BOLD}SUMMARY STATISTICS{RESET}")
    print(f"    Mean daily {kpi}:    {daily['Value'].mean():>12,.0f}")
    print(f"    Peak day:           {daily.loc[daily['Value'].idxmax(), 'Date'].strftime('%Y-%m-%d')}  ({daily['Value'].max():,.0f})")
    print(f"    Lowest day:         {daily.loc[daily['Value'].idxmin(), 'Date'].strftime('%Y-%m-%d')}  ({daily['Value'].min():,.0f})")
    print(f"    Total alerts:       {len(alerts)}")

    # Save log
    log_path = os.path.join(os.path.dirname(__file__), "logs", "kpi_changes.csv")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    alerts.to_csv(log_path, index=False)
    success(f"Alert log saved → {log_path}")

# ─── Feature 3: Causal Analysis ───────────────────────────────────────────────
def causal_analysis(df, filters):
    header("🧠  CAUSAL ANALYSIS  |  Why Did It Change?")

    fdf, context = build_data_context(df, **filters)

    # Find biggest drop
    daily_rev = fdf.groupby("Date")["Revenue_d"].sum().reset_index()
    daily_rev = daily_rev.sort_values("Date").reset_index(drop=True)
    daily_rev["MA7"]    = daily_rev["Revenue_d"].rolling(7, min_periods=1).mean()
    daily_rev["Change"] = (daily_rev["Revenue_d"] - daily_rev["MA7"]) / daily_rev["MA7"] * 100
    biggest_drop_idx = daily_rev["Change"].idxmin()
    event_date = daily_rev.loc[biggest_drop_idx, "Date"]
    event_pct  = daily_rev.loc[biggest_drop_idx, "Change"]
    event_rev  = daily_rev.loc[biggest_drop_idx, "Revenue_d"]
    avg_rev    = daily_rev.loc[biggest_drop_idx, "MA7"]

    print(f"\n  Auto-detected largest change event:")
    print(f"    Date:   {c(event_date.strftime('%Y-%m-%d'), CYAN)}")
    print(f"    Revenue: {c(f'₹{event_rev:,.0f}', CYAN)}  (7d avg: ₹{avg_rev:,.0f})")
    print(f"    Change:  {c(f'{event_pct:+.1f}%', RED if event_pct < 0 else YELLOW)}")

    override = input(f"\n  Use different date? (YYYY-MM-DD or Enter to confirm): ").strip()
    if override:
        try:
            event_date = pd.Timestamp(override)
            event_rev = fdf[fdf["Date"] == event_date]["Revenue_d"].sum()
            avg_rev = daily_rev[daily_rev["Date"] == event_date]["MA7"].values[0] if len(daily_rev[daily_rev["Date"] == event_date]) else avg_rev
            event_pct = (event_rev - avg_rev) / avg_rev * 100 if avg_rev else 0
        except Exception:
            warn("Invalid date, using auto-detected.")

    # Build data snapshots
    before = fdf[(fdf["Date"] >= event_date - timedelta(days=7)) & (fdf["Date"] < event_date)]
    event_day = fdf[fdf["Date"] == event_date]
    after  = fdf[(fdf["Date"] > event_date) & (fdf["Date"] <= event_date + timedelta(days=3))]

    def snap(d):
        if len(d) == 0: return {}
        return {k: round(v, 2) for k,v in d.agg({
            "Revenue_d":"sum","Sales_d":"sum","Discount":"mean","M_Spend":"sum",
            "Rating":"mean","Supply_Chain_E":"mean","Market_T":"mean",
            "Seasonality_T":"mean","Success_Percentage":"mean"
        }).items()}

    print(f"\n  {YELLOW}Running AI causal analysis...{RESET}")

    prompt = f"""Perform a detailed causal analysis for this KPI event.

EVENT: {event_date.strftime('%Y-%m-%d')}
Revenue: ₹{event_rev:,.0f} vs 7d avg ₹{avg_rev:,.0f} = {event_pct:+.1f}%

7-DAY PRIOR: {json.dumps(snap(before), indent=2)}
EVENT DAY:   {json.dumps(snap(event_day), indent=2)}
3-DAY AFTER: {json.dumps(snap(after), indent=2)}

CATEGORY BREAKDOWN ON EVENT DAY:
{event_day.groupby('Category')['Revenue_d'].sum().to_string() if len(event_day) else 'No data'}

PRODUCT BREAKDOWN ON EVENT DAY:
{event_day.groupby('Product_Name')[['Revenue_d','Sales_d','Discount','Rating']].mean().to_string() if len(event_day) else 'No data'}

Provide:
1. TOP CAUSES (ranked by impact with supporting data)
2. CATEGORY/PRODUCT ANALYSIS
3. KEY CORRELATIONS
4. BUSINESS RECOMMENDATIONS (4-6 actions, each with: Action / Rationale / Priority / Expected Impact)

Be specific, data-driven, executive-ready. Use ₹ for currency."""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    analysis = resp.choices[0].message.content

    # Print nicely
    print()
    for line in analysis.split("\n"):
        if line.startswith("##") or line.startswith("**"):
            print(f"\n  {BOLD}{CYAN}{line.strip('#').strip('*').strip()}{RESET}")
        elif line.strip().startswith("-") or line.strip().startswith("•"):
            print(f"    {GREEN}•{RESET} {line.strip().lstrip('-•').strip()}")
        elif line.strip():
            print(f"    {line.strip()}")

    # Save log
    log_path = os.path.join(os.path.dirname(__file__), "logs", f"causal_{event_date.strftime('%Y%m%d')}.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        f.write(f"KPI CAUSAL ANALYSIS REPORT\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Event Date: {event_date.date()}\n")
        f.write(f"Revenue Change: {event_pct:+.1f}%\n\n")
        f.write(analysis)
    success(f"Report saved → {log_path}")

# ─── Main Menu ─────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="KPI Intelligence System CLI")
    parser.add_argument("--category", default="All", help="Filter by category")
    parser.add_argument("--product",  default="All", help="Filter by product")
    parser.add_argument("--from",    dest="date_from", default=None, help="Start date YYYY-MM-DD")
    parser.add_argument("--to",      dest="date_to",   default=None, help="End date YYYY-MM-DD")
    args = parser.parse_args()

    filters = {
        "category": args.category,
        "product":  args.product,
        "date_from": args.date_from,
        "date_to":   args.date_to
    }

    df = load_data()

    print(f"""
{BOLD}{CYAN}
╔══════════════════════════════════════════════════════╗
║       ◈  KPI INTELLIGENCE SYSTEM  ◈                  ║
║       AI-Powered Retail Analytics                    ║
╚══════════════════════════════════════════════════════╝{RESET}

  Data: {c(f'{len(df):,} rows', GREEN)} | Period: {c(f'{df["Date"].min().date()} → {df["Date"].max().date()}', CYAN)}
  Filters: Category={c(filters['category'], YELLOW)} | Product={c(filters['product'], YELLOW)}
""")

    menu = {
        "1": ("💬  Talk-to-Data",                  talk_to_data),
        "2": ("🔍  KPI Monitoring & Change Detection", kpi_monitoring),
        "3": ("🧠  Causal Analysis & Recommendations", causal_analysis),
        "4": ("📊  Quick Stats",                    None),
        "5": ("🚪  Exit",                           None),
    }

    while True:
        print(f"\n  {BOLD}MAIN MENU{RESET}")
        for k, (label, _) in menu.items():
            print(f"    {CYAN}{k}{RESET}. {label}")
        print()

        choice = input(f"  {CYAN}Select option{RESET} ▶  ").strip()

        if choice == "1":
            talk_to_data(df, filters)
        elif choice == "2":
            kpi_monitoring(df, filters)
        elif choice == "3":
            causal_analysis(df, filters)
        elif choice == "4":
            header("📊  QUICK STATS")
            fdf, _ = build_data_context(df, **filters)
            stats = {
                "Total Revenue": f"₹{fdf['Revenue_d'].sum():,.0f}",
                "Total Sales":   f"{fdf['Sales_d'].sum():,}",
                "Avg Daily Revenue": f"₹{fdf.groupby('Date')['Revenue_d'].sum().mean():,.0f}",
                "Avg Rating":    f"{fdf['Rating'].mean():.2f}/5",
                "Avg Discount":  f"{fdf['Discount'].mean():.1f}%",
                "Best Category": fdf.groupby('Category')['Revenue_d'].sum().idxmax(),
                "Best Product":  fdf.groupby('Product_Name')['Revenue_d'].sum().idxmax(),
                "Avg Success %": f"{fdf['Success_Percentage'].mean():.1f}%",
            }
            for k, v in stats.items():
                print(f"    {GREY}{k:<25}{RESET}{CYAN}{v}{RESET}")
        elif choice in ("5", "q", "exit"):
            print(f"\n  {GREEN}Goodbye!{RESET}\n")
            break
        else:
            warn("Invalid option. Please select 1-5.")

if __name__ == "__main__":
    main()
