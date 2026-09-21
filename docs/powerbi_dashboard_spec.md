# Power BI Dashboard Specification

The Power BI file is intentionally the final presentation layer. Build it only after the Python and SQL outputs have been regenerated locally.

## Data sources
- business_kpis.csv
- monthly_business_metrics.csv
- customer_rfm_segments.csv
- profitability_analysis.csv
- discount_profitability_analysis.csv
- forecast_vs_actual.csv
- forecast_evaluation_metrics.csv
- sales_forecast_output.csv

## Pages
### 1. Executive Overview
KPI cards: Total Revenue, Total Profit, Profit Margin, Total Orders, AOV, Unique Customers.
Visuals: Monthly Revenue & Profit trend; Revenue by Category; Revenue by Region; Profit Margin by Category.
Slicers: Year, Region, Category, Segment.

### 2. Sales & Profitability
Revenue vs Profit by Sub-Category; Profit Margin by Sub-Category; Average Discount vs Profit Margin; regional revenue/profit matrix; Quantity and AOV by category.

### 3. Customer Analytics
Customers by RFM Segment; Revenue by RFM Segment; Customer Revenue vs Profit; Frequency vs Monetary; Top customers table.
RFM is behavioral segmentation, not churn prediction.

### 4. Forecast
Historical Revenue + Forecast; forecast confidence interval; Forecast vs Actual for the 12-month holdout; monthly error.
Cards: MAE, RMSE, MAPE.

### 5. Business Insights
Use a compact decision-support page for revenue contributors, low-margin/high-discount areas, customer segments requiring attention, forecast observations, and model/data limitations.

## Design
Use consistent currency formatting, a clear date hierarchy, restrained visual density, visible slicers, descriptive titles, useful tooltips, and drill-through only where it adds analytical value.