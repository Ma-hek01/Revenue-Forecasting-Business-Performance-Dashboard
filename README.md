# Revenue Forecasting & Business Performance Dashboard

An end-to-end retail analytics portfolio project that turns the Sample Superstore dataset into reusable business-performance, forecasting, and insight datasets. Python prepares the analysis, SQLite supports repeatable business queries, and Power BI is the final visualization layer.

## Workflow
`sample_superstore.csv` → Python cleaning and analytics → processed CSV outputs → SQLite business queries → Prophet monthly forecast and holdout evaluation → traceable business insights → Power BI presentation.

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

## Generate business insights

    python src/business_insights.py

This creates `data/processed/business_insights.csv`: a compact, traceable table covering KPIs, category and regional performance, profitability, discounts, RFM segments, monthly trends, and forecast information. Every insight records its source output and fields, and descriptive associations are not presented as causal claims.

## SQL

- `sql/business_queries.sql` — core business queries
- `sql/analytics_queries.sql` — expanded KPI, profitability, customer, discount, and monthly analytics
- `notebooks/03_sql_integration.ipynb` — creates the SQLite table and demonstrates the SQL workflow

The SQL notebook uses repository-relative paths, applies the same normalization and invalid-row removal as the analytics pipeline, and writes dates as ISO-8601 text before creating `sales_data`. This makes SQLite monthly grouping with `strftime` reliable on Windows and from a fresh clone.

## Outputs

- `business_kpis.csv`, `monthly_business_metrics.csv`, `customer_rfm_segments.csv`
- `profitability_analysis.csv`, `discount_profitability_analysis.csv`, `monthly_forecast_input.csv`
- `forecast_evaluation_metrics.csv`, `forecast_vs_actual.csv`, `sales_forecast_output.csv`
- `business_insights.csv`

## Power BI

The Power BI dashboard is deliberately the final presentation layer. Follow `docs/powerbi_dashboard_spec.md` after regenerating all processed outputs.

## Customer analytics scope

RFM is used for behavioral customer segmentation. The project does not claim churn prediction because the source data does not contain an explicit churn label.

## Dataset

The project uses the included Sample Superstore retail transaction dataset at `data/raw/sample_superstore.csv` (9,994 records after normalization). It contains orders, customers, product hierarchy, sales, discounts, profit, and geography fields. No external or fabricated data is used.
