# 🚀 AI Query Optimizer

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Streamlit-ff4b4b?style=for-the-badge&logo=streamlit)](https://ai-query-optimizer-bqjpn7ckxyb7p5mhtrab6y.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Harshit--Kumar--1710-181717?style=for-the-badge&logo=github)](https://github.com/Harshit-Kumar-1710/AI-Query-Optimizer)

> 🌐 **Live App:** https://ai-query-optimizer-bqjpn7ckxyb7p5mhtrab6y.streamlit.app/

A modern, machine learning and LLM-powered database performance platform built with **Python**, **PostgreSQL**, **XGBoost**, and **Streamlit**. It turns complex execution plan trees into readable developer diagnostics, compares PostgreSQL cardinality estimates against an ML model, and suggests safe database tuning recommendations.

---

## 🎯 Problem Statement

Relational query planners (like PostgreSQL's cost-based optimizer) rely heavily on statistics and histograms to estimate the number of rows processed by each plan node (cardinality estimation). When these estimates are inaccurate:
- PostgreSQL may choose a **Sequential Scan** instead of an **Index Scan**.
- It may select an inefficient join algorithm (e.g., Nested Loop instead of Hash Join).
- Query latency can increase exponentially.

**AI Query Optimizer** solves this by:
1. Predicting plan-node cardinality using an **XGBoost Regressor** trained on execution plan features.
2. Highlighting estimate errors (**Q-Error**) between PostgreSQL's optimizer, actual row counts, and the ML model.
3. Leveraging Large Language Models (**Google Gemini**) to provide plain-English query plan breakdowns, anti-pattern detection, and safe SQL optimization advice.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend (Modern UI)                      │
│   • Natural Language (English to SQL)   • Live Query Analysis           │
│   • JSON Plan Explorer                 • Model Performance Insights     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                    1. Input Validation (SELECT-Only)
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          PostgreSQL Database                            │
│                 EXPLAIN (ANALYZE, FORMAT JSON) <query>                  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 2. Raw JSON Plan
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      Feature Extraction Engine                          │
│   • Flatten JSON Nodes    • Extract 13 Structural & Cost Features       │
│   • Scikit-Learn LabelEncoders & Scalers                                │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 3. Feature Vectors
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       XGBoost ML Predictor                              │
│   • Predicts Log10 Row Cardinality                                      │
│   • Computes Q-Error: max(pred/actual, actual/pred)                     │
│   • Triggers Predictive Traffic Light Safety Banner                     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ 4. Evaluation & Insights
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   Google Gemini LLM (Optional)                          │
│   • Plain-English Plan Translator   • Anti-Pattern Review               │
│   • Structured Optimization Advice  • Safe Candidate SQL Rewrite        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

- 🎨 **Modern Premium Interface:** Built with Plus Jakarta Sans typography, frosted glass cards, and animated indicators.
- 💬 **Natural-Language to SQL:** Translates plain English requests (e.g., *"Show me top 10 customers with more than 15 payments"*) into valid PostgreSQL SQL.
- 🚦 **Predictive Traffic Light Warning:** Automatically flags queries predicted to process over 10,000 or 50,000 rows as **MODERATE** or **HIGH RISK** before production execution.
- 📊 **Q-Error Cardinality Comparison:** Compares PostgreSQL's internal estimate against XGBoost ML predictions against actual execution rows.
- 🔍 **Plan Explorer:** Provides node-by-node inspection of execution trees and raw JSON execution metrics.
- 🧠 **AI Query Doctor:** Structured performance breakdown giving plain-English explanations, anti-pattern detection, and index recommendations.
- 💡 **Smart Index Advisor:** Deterministic rules detect sequential scans and propose exact `CREATE INDEX` DDL statements without running them automatically.
- 📝 **Activity Logs & Analysis History:** Persists analysis history and app telemetry locally (`analysis_history.db`, `app_activity.db`).

---

## 🛠️ Stack & Dependencies

- **Language:** Python 3.10+
- **Frontend & App Engine:** Streamlit
- **Machine Learning:** XGBoost, Scikit-Learn, Joblib, NumPy, Pandas
- **Visualizations:** Plotly Express & Plotly Graph Objects
- **Database:** PostgreSQL (`psycopg2-binary`), SQLite3
- **Generative AI:** Google Gemini API (`google-genai`)

---

## 🚀 Local Setup Instructions

### Prerequisites
1. Installed **Python 3.10+**
2. Installed **PostgreSQL** with the standard `dvd_rental` sample database loaded locally.

### Step-by-Step

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Oxide06/AI-Query-Optimizer.git
   cd AI-Query-Optimizer
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables (Optional):**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Or set your Gemini API Key:
   ```powershell
   $env:GEMINI_API_KEY="your_google_gemini_api_key"
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   Open **`http://localhost:8501`** in your browser.

---

## ☁️ Streamlit Community Cloud Deployment

When deploying to **Streamlit Community Cloud**:
> [!IMPORTANT]
> `localhost` PostgreSQL database instances cannot be reached from hosted cloud containers. 
> 
> The hosted app seamlessly supports:
> - ✅ **Upload Plan Mode** (JSON plan analysis)
> - ✅ **Sample Analysis Mode** (pre-loaded execution plan benchmarking)
> - ✅ **Model Info & Feature Importance**
> - ✅ **Offline Fast Mode & Gemini AI Features**
>
> To enable **Live Query Mode** in the cloud, connect a publicly reachable hosted PostgreSQL instance (e.g. Aiven, Supabase, Neon) and configure secrets in Streamlit Cloud.

### Streamlit Secrets Configuration Template
In Streamlit Cloud Dashboard -> **App Settings** -> **Secrets**, paste:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
DB_HOST = "your_hosted_postgres_host"
DB_PORT = "5432"
DB_NAME = "dvd_rental"
DB_USER = "postgres"
DB_PASSWORD = "your_postgres_password"
DB_SSLMODE = "require"
```

### Deployment troubleshooting - read this before adding secrets

1. In Google AI Studio, create or copy a **Gemini API key** and add it as `GEMINI_API_KEY` in Streamlit Secrets. Do not paste a Google OAuth access token, a `Bearer ...` value, or a browser login token.
2. If the app reports `ACCESS_TOKEN_TYPE_UNSUPPORTED`, the configured value is an OAuth token instead of a Gemini API key. Replace it in Streamlit Cloud **App settings -> Secrets**, save, and reboot the app.
3. For Neon, Supabase, Aiven, and most hosted PostgreSQL providers, set `DB_SSLMODE = "require"`. Enter the exact host, port, database, user, and password supplied by the provider.
4. For a local PostgreSQL instance, use `DB_HOST = "localhost"` and usually `DB_SSLMODE = "prefer"` or `"disable"`. A cloud-hosted Streamlit app cannot access your computer's localhost database.
5. After changing `requirements.txt` or secrets, use Streamlit Cloud **Reboot app** and test **Sample Analysis** first, then **Live Query**.

---

## 🔒 Safety & Security Constraints

- 🛑 **Read-Only SELECT Enforcement:** The app strictly validates that all executed queries begin with `SELECT`. Mutation operations (`INSERT`, `UPDATE`, `DELETE`, `DROP`) are blocked.
- 🛡️ **Zero Automated DDL Execution:** Index suggestions and SQL rewrites are presented for developer review only. The system never modifies database schemas automatically.
- 🔐 **Secret Safety:** API keys, database passwords, and raw query output data are excluded from logging and git tracking. `.gitignore` blocks `.env`, SQLite files, `.gemini_key.json`, and database archives.

---

## 🎓 Model Credibility & Limitations

- **Domain Scope:** The XGBoost model was trained on 12,800+ execution plan nodes from relational JOIN workloads. It performs best on complex multi-table queries.
- **Static Predictor:** The ML model is a static regressor used for estimation evaluation; it does not alter PostgreSQL internals or run self-learning production mutations.
- **LLM Boundary:** Generative AI is strictly used for natural language translation and structured explanations; numerical row estimates are computed purely by the XGBoost ML pipeline.

---

## 💼 Interview Defense Summary

> *"AI Query Optimizer bridges predictive ML and generative LLMs for database observability. PostgreSQL uses cardinality estimates to choose execution plans, but statistics can decay. I trained an XGBoost regression model on 12,800+ execution nodes to predict log cardinality, exposing estimation errors (Q-Error). On top of this ML engine, I integrated Google Gemini for natural language SQL generation and human-readable plan diagnostics, while enforcing strict read-only SELECT validation and deterministic safety boundaries."*
