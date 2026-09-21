"""Create traceable, data-driven business insights from processed outputs.

Each row records a reported metric, its scope, and the output columns from
which it was derived. The file is intended for portfolio discussion and for
use as a Power BI-ready annotation table; it does not infer causation.
"""

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_PATH = PROCESSED_DIR / "business_insights.csv"
REQUIRED_FILES = {
    "business_kpis": "business_kpis.csv",
    "monthly": "monthly_business_metrics.csv",
    "rfm": "customer_rfm_segments.csv",
    "profitability": "profitability_analysis.csv",
    "discount": "discount_profitability_analysis.csv",
    "evaluation": "forecast_evaluation_metrics.csv",
    "forecast": "sales_forecast_output.csv",
}


def read_required(name: str, columns: set[str]) -> pd.DataFrame:
    path = PROCESSED_DIR / REQUIRED_FILES[name]
    if not path.exists():
        raise FileNotFoundError(
            f"Required input is missing: {path}. Run the analytics and forecast pipelines first."
        )
    frame = pd.read_csv(path)
    missing = sorted(columns.difference(frame.columns))
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {missing}")
    if frame.empty:
        raise ValueError(f"{path.name} contains no rows.")
    return frame


def build_insights() -> pd.DataFrame:
    kpis = read_required("business_kpis", {"Total_Revenue", "Total_Profit", "Profit_Margin", "Total_Orders", "Unique_Customers"}).iloc[0]
    monthly = read_required("monthly", {"Month", "Revenue", "Profit"})
    rfm = read_required("rfm", {"Customer_Segment", "Customer_ID", "Monetary"})
    profitability = read_required("profitability", {"Region", "Category", "Sub_Category", "Revenue", "Profit", "Profit_Margin"})
    discount = read_required("discount", {"Category", "Sub_Category", "Average_Discount", "Profit_Margin"})
    evaluation = read_required("evaluation", {"MAE", "RMSE", "MAPE"}).iloc[0]
    forecast = read_required("forecast", {"ds", "yhat", "yhat_lower", "yhat_upper"})

    rows: list[dict] = []

    def add(area: str, metric: str, dimension: str, value: float | int, unit: str, context: str, source: str, fields: str) -> None:
        rows.append({
            "Insight_Area": area, "Metric": metric, "Dimension": dimension,
            "Value": value, "Unit": unit, "Context": context,
            "Source_File": source, "Source_Fields": fields,
        })

    add("Revenue and KPIs", "Total revenue", "All data", kpis.Total_Revenue, "currency", "Observed dataset total", "business_kpis.csv", "Total_Revenue")
    add("Revenue and KPIs", "Total profit", "All data", kpis.Total_Profit, "currency", "Observed dataset total", "business_kpis.csv", "Total_Profit")
    add("Revenue and KPIs", "Profit margin", "All data", kpis.Profit_Margin * 100, "percent", "Profit divided by revenue", "business_kpis.csv", "Profit_Margin")
    add("Revenue and KPIs", "Total orders", "All data", kpis.Total_Orders, "orders", "Distinct Order_ID count", "business_kpis.csv", "Total_Orders")
    add("Revenue and KPIs", "Unique customers", "All data", kpis.Unique_Customers, "customers", "Distinct Customer_ID count", "business_kpis.csv", "Unique_Customers")

    category = profitability.groupby("Category", as_index=False)[["Revenue", "Profit"]].sum()
    category["Profit_Margin"] = np.where(category.Revenue.ne(0), category.Profit / category.Revenue, np.nan)
    leader = category.nlargest(1, "Revenue").iloc[0]
    add("Category performance", "Highest revenue category", leader.Category, leader.Revenue, "currency", "Aggregated across regions and sub-categories", "profitability_analysis.csv", "Category, Revenue")

    regional = profitability.groupby("Region", as_index=False)[["Revenue", "Profit"]].sum()
    regional["Profit_Margin"] = np.where(regional.Revenue.ne(0), regional.Profit / regional.Revenue, np.nan)
    leader = regional.nlargest(1, "Revenue").iloc[0]
    add("Regional performance", "Highest revenue region", leader.Region, leader.Revenue, "currency", "Aggregated across categories and sub-categories", "profitability_analysis.csv", "Region, Revenue")
    low_margin = regional.nsmallest(1, "Profit_Margin").iloc[0]
    add("Regional performance", "Lowest profit-margin region", low_margin.Region, low_margin.Profit_Margin * 100, "percent", "Profit divided by revenue", "profitability_analysis.csv", "Region, Profit, Revenue")

    lowest_profit = profitability.nsmallest(1, "Profit").iloc[0]
    add("Profitability", "Lowest-profit regional sub-category", f"{lowest_profit.Region} | {lowest_profit.Category} | {lowest_profit.Sub_Category}", lowest_profit.Profit, "currency", "Aggregated profit", "profitability_analysis.csv", "Region, Category, Sub_Category, Profit")

    highest_discount = discount.nlargest(1, "Average_Discount").iloc[0]
    add("Discount and profitability", "Highest average discount", f"{highest_discount.Category} | {highest_discount.Sub_Category}", highest_discount.Average_Discount * 100, "percent", "Average discount for the aggregated sub-category", "discount_profitability_analysis.csv", "Category, Sub_Category, Average_Discount")
    correlation = discount["Average_Discount"].corr(discount["Profit_Margin"])
    if pd.notna(correlation):
        add("Discount and profitability", "Discount-profit margin correlation", "Category-sub-category aggregates", correlation, "correlation", "Pearson correlation; descriptive association, not causation", "discount_profitability_analysis.csv", "Average_Discount, Profit_Margin")

    segment_counts = rfm.groupby("Customer_Segment")["Customer_ID"].nunique()
    largest_segment = segment_counts.nlargest(1)
    add("Customer RFM", "Largest customer segment", largest_segment.index[0], largest_segment.iloc[0], "customers", "Distinct customers assigned to the RFM segment", "customer_rfm_segments.csv", "Customer_Segment, Customer_ID")

    monthly["Month"] = pd.to_datetime(monthly["Month"], errors="coerce")
    monthly = monthly.dropna(subset=["Month"])
    if monthly.empty:
        raise ValueError("monthly_business_metrics.csv has no valid Month values.")
    peak = monthly.nlargest(1, "Revenue").iloc[0]
    add("Monthly trend", "Highest monthly revenue", peak.Month.strftime("%Y-%m"), peak.Revenue, "currency", "Observed monthly revenue", "monthly_business_metrics.csv", "Month, Revenue")

    add("Forecast evaluation", "MAE", "Latest 12 observed months", evaluation.MAE, "currency", "Chronological holdout evaluation", "forecast_evaluation_metrics.csv", "MAE")
    add("Forecast evaluation", "RMSE", "Latest 12 observed months", evaluation.RMSE, "currency", "Chronological holdout evaluation", "forecast_evaluation_metrics.csv", "RMSE")
    add("Forecast evaluation", "MAPE", "Latest 12 observed months", evaluation.MAPE, "percent", "Chronological holdout evaluation", "forecast_evaluation_metrics.csv", "MAPE")
    add("Forecast", "Forecast revenue total", "Next 12 monthly periods", forecast.yhat.sum(), "currency", "Sum of Prophet point forecasts", "sales_forecast_output.csv", "ds, yhat")

    return pd.DataFrame(rows).round({"Value": 4})


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    insights = build_insights()
    insights.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(insights)} traceable insights: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
