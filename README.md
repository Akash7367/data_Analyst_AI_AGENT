# ◈ KPI Intelligence System
### AI-Powered Retail KPI Analytics with LLM Reasoning

A full agentic AI system for KPI monitoring, causal analysis, and business recommendations — powered by Claude (Anthropic).
LIVE LINK: https://dataanalystaiagent-m7cukwhurgwgreqng6vh4e.streamlit.app/
---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Key
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run Web Dashboard (Streamlit)
```bash
streamlit run app.py
```

### 4. Run CLI (Mandatory Interface)
```bash
python cli.py

# With filters:
python cli.py --category Electronics --from 2025-01-01 --to 2025-03-31
python cli.py --product "Air Fryer Pro"
```

---

## 📁 Project Structure

```
kpi_system/
├── app.py                  # Streamlit web dashboard
├── cli.py                  # CLI entry point (mandatory)
├── daily_kpi_data.csv      # Dataset (90 days, 10 products)
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── logs/                   # Auto-generated output logs
    ├── kpi_changes.csv     # KPI change detection log
    └── causal_YYYYMMDD.txt # Causal analysis reports
```

---

## 🔧 System Features

### 1. Talk-to-Data (LLM-Based)
Natural language interface over the KPI dataset.
- **Web**: Chat tab with conversation history + quick-question buttons
- **CLI**: Interactive REPL with multi-turn conversation

Example questions:
- "What is the total revenue for the last 14 days?"
- "Show revenue trend for Kitchen category"
- "When did revenue drop the most?"
- "Which product has the best rating?"

### 2. KPI Monitoring & Change Detection
- Tracks Revenue, Sales, Rating, Success %, Marketing Spend
- Three detection methods: % vs Rolling Average, Day-over-Day %, Z-Score
- Configurable threshold and rolling window
- Visual alert markers on trend charts
- Alert log exported to `logs/kpi_changes.csv`

### 3. Causal Analysis (LLM-Powered)
When a KPI change is detected:
- Analyses all available fields (Discount, M_Spend, Supply_Chain_E, Market_T, etc.)
- Ranks causes by impact (High/Medium/Low)
- Cross-references category and product-level breakdowns
- Explains findings in business-readable language
- Reports saved to `logs/causal_YYYYMMDD.txt`

### 4. Action Recommendations
Based on identified causes:
- Generates 4-6 executive-ready business recommendations
- Maps each cause to a specific intervention
- Assigns priority (URGENT / HIGH / MEDIUM)
- Estimates expected impact

---

## 📊 Dataset Schema

| Column | Description |
|--------|-------------|
| Date | Daily date (YYYY-MM-DD) |
| Product_Name | Product identifier |
| Category | Product category (Kitchen, Sports, Electronics) |
| Sub_category | Sub-category |
| Price | Unit price (₹) |
| Discount | Discount % applied |
| Sales_d | Daily units sold |
| Revenue_d | Daily revenue (₹) |
| M_Spend | Marketing spend (₹) |
| Rating | Customer rating (1-5) |
| Supply_Chain_E | Supply chain efficiency % |
| Market_T | Market trend score |
| Seasonality_T | Seasonality index |
| Success_Percentage | Composite success metric % |

---

## ⚙️ Configuration

All detection parameters are configurable at runtime:
- **Change Alert Threshold**: % deviation to trigger alert (default: 15%)
- **Rolling Window**: Days for moving average (default: 7)
- **KPI Metric**: Any numeric column in dataset

---

## 🧪 Live Demo Checklist

During the live walkthrough:
1. ✅ Launch `streamlit run app.py`
2. ✅ Show Overview dashboard with KPI cards and charts
3. ✅ Ask natural language questions in Talk-to-Data tab
4. ✅ Demonstrate change detection with different thresholds
5. ✅ Run causal analysis on a detected drop event
6. ✅ Show generated recommendations
7. ✅ Run `python cli.py` for CLI demo
8. ✅ Adjust filters (category, date range, threshold) live

---

## 📋 Sample CLI Session

```
$ python cli.py

╔══════════════════════════════════════════════════════╗
║       ◈  KPI INTELLIGENCE SYSTEM  ◈                  ║
╚══════════════════════════════════════════════════════╝

  MAIN MENU
    1. 💬  Talk-to-Data
    2. 🔍  KPI Monitoring & Change Detection
    3. 🧠  Causal Analysis & Recommendations
    4. 📊  Quick Stats
    5. 🚪  Exit

Select option ▶  1

──────────────────────────────────────────────────────
  💬  TALK-TO-DATA  |  Natural Language Q&A
──────────────────────────────────────────────────────

You ▶  What was total revenue for January 2025?

AI ▶  Total revenue for January 2025 was ₹12,847,320...
```
