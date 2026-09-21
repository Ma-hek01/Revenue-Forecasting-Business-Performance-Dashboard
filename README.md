# Revenue Forecasting & Business Performance Dashboard

An end-to-end retail analytics project combining Python, SQL, customer segmentation, profitability analysis, time-series forecasting, forecast evaluation, and Power BI.

## Workflow
1. Data ingestion and cleaning
2. Exploratory data analysis
3. SQL business analytics
4. Customer RFM segmentation
5. Profitability and discount analysis
6. Revenue forecasting with Prophet
7. Chronological forecast evaluation
8. Business insight layer
9. Power BI presentation layer

## Fresh clone setup

Use Python 3.13 and create a new virtual environment after cloning. The repository does **not** track a `.venv`; the environment is local-only and excluded by `.gitignore`.

From the project root:

    python -m venv .venv

Activate it in Windows PowerShell:

    .\.venv\Scripts\Activate.ps1

Install dependencies:

    python -m pip install -r requirements.txt

## Run the analytics pipeline

    python src/analytics_pipeline.py

This creates reusable datasets in `data/processed/` for KPIs, monthly metrics, customer RFM segments, profitability, discount analysis, and standardized forecasting input.

## Run the forecast pipeline

    python src/forecast_pipeline.py

This uses the standardized forecasting input, holds out the latest 12 observed months, calculates MAE/RMSE/MAPE, writes `forecast_vs_actual.csv` and `forecast_evaluation_metrics.csv`, then refits on the full history and generates the next 12 monthly forecasts.

The forecast script also accepts the older notebook-generated `monthly_sales_forecast.csv` as a fallback.

## SQL

- `sql/business_queries.sql` — core business queries
- `sql/analytics_queries.sql` — expanded KPI, profitability, customer, discount, and monthly analytics
- `notebooks/03_sql_integration.ipynb` — creates the SQLite table and demonstrates the SQL workflow

The SQL notebook normalizes column names and dates before writing `sales_data` to SQLite, so the monthly date queries use SQLite's `strftime` reliably.

## Power BI

The Power BI dashboard is deliberately the final presentation layer. Follow `docs/powerbi_dashboard_spec.md` after regenerating all processed outputs.

## Customer analytics scope

RFM is used for behavioral customer segmentation. The project does not claim churn prediction because the source data does not contain an explicit churn label.

## Dataset

The project uses the Sample Superstore dataset in `data/raw/sample_superstore.csv`.
