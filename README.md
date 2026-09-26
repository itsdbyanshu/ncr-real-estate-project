# 🏙️ NCR Real Estate Analytics & AI Data Assistant

An end-to-end data engineering, business intelligence, and Generative AI portfolio project that tracks and analyzes real estate rental trends across the National Capital Region (NCR) of India.

This application features an automated daily ETL pipeline, a comprehensive analytical dashboard, and a live LangChain-powered SQL agent that allows users to query the database using natural language.

## 🚀 Live Demo
**[Insert your Streamlit Cloud URL here]**

**Author:** Divyanshu Bhatt — [GitHub](#) · [LinkedIn](#)

## 🏗️ Architecture & Tech Stack

This project integrates a complete modern data stack:

* **Data Extraction & ETL:** Python (`requests`, `BeautifulSoup`, `pandas`)
* **Data Warehousing (Dual-Load):** Snowflake (for BI) & Neon PostgreSQL (for the AI Agent)
* **Automation:** GitHub Actions (Daily Cron Job)
* **Business Intelligence:** Microsoft Power BI (DAX, DirectQuery)
* **Generative AI:** LangChain, Groq API (`gpt-oss-120b`)
* **Frontend:** Streamlit

## ✨ Core Features

1. **Automated Data Pipeline:** A Python web scraper extracts property listings across Noida, Gurgaon, New Delhi, Ghaziabad, and Faridabad. The data is cleaned via Pandas and pushed simultaneously to Snowflake and Neon PostgreSQL.
2. **Daily CI/CD Automation:** A GitHub Actions workflow automatically triggers the ETL script every day to ensure the database is always up to date.
3. **Market Intelligence Dashboard:** A Power BI dashboard visualizing average rent prices, city-wise inventory, and price-per-square-foot trends. *(Note: Displayed as a static portfolio asset in the web app to bypass enterprise embedding restrictions.)*
4. **Live GenAI SQL Agent:** A stateless, natural-language AI assistant built with LangChain. It translates plain-English questions into strict, read-only PostgreSQL `SELECT` queries, executes them against a dedicated read-only Neon role, and returns formatted insights.
5. **Interactive Web App:** A responsive, dark-themed Streamlit UI featuring session-state chat history and proactive UX guardrails.

## 🔒 Agent Guardrails

The agent is constrained well beyond just prompting — the safety boundary is structural, not just instructional:

* Runs against a **dedicated read-only Postgres role** (`ai_agent_reader`) in Neon — it is not capable of writing to the database at the connection level, regardless of what it's asked.
* Restricted to **`SELECT`-only** queries against the `rental_listings` table.
* Uses **`ILIKE`** for case-insensitive city/sector matching.
* Every query is capped at **`LIMIT 10`** rows.
* Deliberately **stateless** — each question is answered independently with no memory of prior turns, a conscious trade-off for speed and to avoid context drift. (The chat *history* is still shown in the UI via `st.session_state` — the agent itself just doesn't reason over it.)

## ⚠️ Known Limitations

Documented deliberately, not discovered accidentally:

* No memory across questions — every query is answered fresh.
* Confined to a single table — can't join across other data sources.
* Relies on literal keyword filtering rather than semantic understanding of intent.
* The dashboard is a static snapshot, not a live embed (see Core Features above) — it won't reflect new data until re-exported.

## 📂 Repository Structure

```text
ncr-real-estate-project/
├── .github/workflows/       # GitHub Actions automation scripts
├── .streamlit/config.toml   # Custom dark theme configuration
├── agent.py                 # LangChain SQL agent and Streamlit bridge function
├── Dashboard.pbix           # Original Power BI Desktop file
├── dashboard.png            # High-resolution dashboard snapshot for UI
├── etl_pipeline.py          # Web scraping, Pandas cleaning, and DB loading
├── requirements.txt         # Project dependencies
├── scraper_test.py          # Manual smoke-test script for the scraper (no assertions)
├── streamlit_app.py         # Main Streamlit web application frontend
└── WORKDONE_IN_ORDER.md     # Chronological development log
```

## 🛠️ Running It Locally

```bash
git clone <your-repo-url>
cd ncr-real-estate-project
python -m venv venv
source venv/bin/activate        # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# add your SNOWFLAKE_*, NEON_DB_URL, and GROQ_API_KEY values to .env
streamlit run streamlit_app.py
```

## ☁️ Deployment

Deployed on **Streamlit Community Cloud**, connected directly to this GitHub repository. Groq and Neon credentials are stored as encrypted secrets in the Streamlit Cloud dashboard rather than committed to the repo.

## 🔮 Possible Next Steps

* Automate the Power BI → image export step so the dashboard snapshot refreshes on a schedule alongside the data.
* Convert `scraper_test.py` into a real test suite with assertions (e.g. `pytest`) covering the cleaning functions and the agent's guardrails.
* Give the agent short-term memory behind a feature flag, to compare answer quality/latency against the current stateless design.
