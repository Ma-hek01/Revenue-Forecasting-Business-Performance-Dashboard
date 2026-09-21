"""Business analytics pipeline for the Revenue Forecasting & Business Performance Dashboard.

Builds reusable KPI, monthly, customer-segmentation and profitability datasets
from the Superstore source data. Power BI consumes the generated CSV outputs.
"""

from pathlib import Path
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "sample_superstore.csv"
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH, encoding="latin1")
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace("-", "_")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Ship_Date"] = pd.to_datetime(df["Ship_Date"], errors="coerce")
    for col in ["Sales", "Quantity", "Discount", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Order_ID", "Customer_ID", "Customer_Name", "Order_Date", "Sales", "Profit"])
    return df.drop_duplicates().copy()


def build_monthly(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["Month"] = x["Order_Date"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        x.groupby("Month", as_index=False)
        .agg(
            Revenue=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum"),
            Orders=("Order_ID", "nunique"),
            Customers=("Customer_ID", "nunique"),
            Average_Discount=("Discount", "mean"),
        )
        .sort_values("Month")
    )
    monthly["Profit_Margin"] = np.where(monthly["Revenue"] != 0, monthly["Profit"] / monthly["Revenue"], 0)
    monthly["AOV"] = np.where(monthly["Orders"] != 0, monthly["Revenue"] / monthly["Orders"], 0)
    monthly["Year"] = monthly["Month"].dt.year
    monthly["Quarter"] = "Q" + monthly["Month"].dt.quarter.astype(str)
    monthly["Month_Name"] = monthly["Month"].dt.strftime("%b")
    return monthly


def build_kpis(df: pd.DataFrame) -> pd.DataFrame:
    revenue = df["Sales"].sum()
    profit = df["Profit"].sum()
    orders = df["Order_ID"].nunique()
    return pd.DataFrame([{
        "Total_Revenue": revenue,
        "Total_Profit": profit,
        "Profit_Margin": profit / revenue if revenue else 0,
        "Total_Orders": orders,
        "Total_Quantity": df["Quantity"].sum(),
        "AOV": revenue / orders if orders else 0,
        "Unique_Customers": df["Customer_ID"].nunique(),
        "Average_Discount": df["Discount"].mean(),
        "Data_Start": df["Order_Date"].min().date(),
        "Data_End": df["Order_Date"].max().date(),
    }])


def build_rfm(df: pd.DataFrame) -> pd.DataFrame:
    snapshot = df["Order_Date"].max() + pd.Timedelta(days=1)
    rfm = (
        df.groupby(["Customer_ID", "Customer_Name"], as_index=False)
        .agg(
            Last_Purchase=("Order_Date", "max"),
            Frequency=("Order_ID", "nunique"),
            Monetary=("Sales", "sum"),
            Profit=("Profit", "sum"),
        )
    )
    rfm["Recency"] = (snapshot - rfm["Last_Purchase"]).dt.days
    rfm["R_Score"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_Score"] = rfm[["R_Score", "F_Score", "M_Score"]].sum(axis=1)

    def segment(row):
        r, f, m = row.R_Score, row.F_Score, row.M_Score
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        if f >= 4 and m >= 3:
            return "Loyal Customers"
        if r >= 4:
            return "Recent Customers"
        if r <= 2 and m >= 4:
            return "At Risk - High Value"
        if r <= 2 and f >= 3:
            return "At Risk - High Spend"
        if r <= 2:
            return "Inactive"
        return "Potential Loyalists"

    rfm["Customer_Segment"] = rfm.apply(segment, axis=1)
    rfm["AOV"] = rfm["Monetary"] / rfm["Frequency"].replace(0, np.nan)
    return rfm.sort_values(["Monetary", "Frequency"], ascending=False)


def build_profitability(df: pd.DataFrame) -> pd.DataFrame:
    x = (
        df.groupby(["Region", "Category", "Sub_Category"], as_index=False)
        .agg(
            Revenue=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum"),
            Orders=("Order_ID", "nunique"),
            Average_Discount=("Discount", "mean"),
        )
    )
    x["Profit_Margin"] = np.where(x["Revenue"] != 0, x["Profit"] / x["Revenue"], 0)
    x["AOV"] = np.where(x["Orders"] != 0, x["Revenue"] / x["Orders"], 0)
    return x.sort_values("Revenue", ascending=False)


def build_discount_analysis(df: pd.DataFrame) -> pd.DataFrame:
    x = (
        df.groupby(["Category", "Sub_Category"], as_index=False)
        .agg(
            Revenue=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Average_Discount=("Discount", "mean"),
            Maximum_Discount=("Discount", "max"),
            Orders=("Order_ID", "nunique"),
        )
    )
    x["Profit_Margin"] = np.where(x["Revenue"] != 0, x["Profit"] / x["Revenue"], 0)
    return x.sort_values("Average_Discount", ascending=False)


def main() -> None:
    df = load_data()
    monthly = build_monthly(df)
    build_kpis(df).to_csv(OUT_DIR / "business_kpis.csv", index=False)
    monthly.to_csv(OUT_DIR / "monthly_business_metrics.csv", index=False)
    build_rfm(df).to_csv(OUT_DIR / "customer_rfm_segments.csv", index=False)
    build_profitability(df).to_csv(OUT_DIR / "profitability_analysis.csv", index=False)
    build_discount_analysis(df).to_csv(OUT_DIR / "discount_profitability_analysis.csv", index=False)
    monthly[["Month", "Revenue"]].rename(columns={"Month": "ds", "Revenue": "y"}).to_csv(
        OUT_DIR / "monthly_forecast_input.csv", index=False
    )
    print(f"Processed {len(df):,} rows.")
    print(f"Outputs written to {OUT_DIR}")


if __name__ == "__main__":
    main()
