"""Train, evaluate and forecast monthly revenue with Prophet.

Uses a chronological holdout (last 12 observed months) for model evaluation,
then refits Prophet on the full historical series and produces the next 12
monthly forecasts.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from prophet import Prophet


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

PRIMARY_INPUT = OUT / "monthly_forecast_input.csv"
LEGACY_INPUT = OUT / "monthly_sales_forecast.csv"


def metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = actual - predicted
    nonzero = actual != 0

    return {
        "MAE": np.mean(np.abs(error)),
        "RMSE": np.sqrt(np.mean(error ** 2)),
        "MAPE": (
            np.mean(np.abs(error[nonzero] / actual[nonzero])) * 100
            if np.any(nonzero)
            else np.nan
        ),
    }


def load_series():
    # Prefer the standardized output created by analytics_pipeline.py.
    # Keep the notebook-generated file as a backward-compatible fallback.
    input_path = PRIMARY_INPUT if PRIMARY_INPUT.exists() else LEGACY_INPUT

    if not input_path.exists():
        raise FileNotFoundError(
            "No forecast input found. Run 'python src/analytics_pipeline.py' "
            "first to create data/processed/monthly_forecast_input.csv."
        )

    df = pd.read_csv(input_path)

    if {"ds", "y"}.issubset(df.columns):
        series = df[["ds", "y"]].copy()
    elif {"Order Date", "Sales"}.issubset(df.columns):
        series = df.rename(columns={"Order Date": "ds", "Sales": "y"})[["ds", "y"]].copy()
    else:
        raise ValueError(
            f"Unexpected forecast input columns: {list(df.columns)}"
        )

    series["ds"] = pd.to_datetime(series["ds"], errors="coerce")
    series["y"] = pd.to_numeric(series["y"], errors="coerce")
    series = series.dropna(subset=["ds", "y"]).sort_values("ds").reset_index(drop=True)

    if series.empty:
        raise ValueError(f"No valid monthly observations found in {input_path}.")
    if series["ds"].duplicated().any():
        raise ValueError("Forecast input must contain one row per monthly date.")

    if len(series) <= 12:
        raise ValueError("At least 13 monthly observations are required for a 12-month holdout.")

    return series


def main():
    series = load_series()

    holdout_size = 12
    train = series.iloc[:-holdout_size].copy()
    test = series.iloc[-holdout_size:].copy()

    evaluation_model = Prophet()
    evaluation_model.fit(train)

    evaluation_forecast = evaluation_model.predict(test[["ds"]])
    evaluation = test.merge(
        evaluation_forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]],
        on="ds",
        how="left",
    )
    evaluation["Error"] = evaluation["y"] - evaluation["yhat"]
    evaluation["Absolute_Error"] = evaluation["Error"].abs()
    evaluation["Absolute_Percentage_Error"] = np.where(
        evaluation["y"] != 0,
        evaluation["Absolute_Error"] / evaluation["y"] * 100,
        np.nan,
    )

    m = metrics(evaluation["y"], evaluation["yhat"])
    pd.DataFrame([m]).to_csv(OUT / "forecast_evaluation_metrics.csv", index=False)
    evaluation.to_csv(OUT / "forecast_vs_actual.csv", index=False)

    final_model = Prophet()
    final_model.fit(series)

    # The source series is monthly at month start. Generate month-end dates for
    # the 12 calendar months strictly after the final observed month.
    next_month_start = (
        series["ds"].max().to_period("M").to_timestamp() + pd.offsets.MonthBegin(1)
    )
    future_dates = pd.date_range(next_month_start, periods=12, freq="ME")
    forecast = final_model.predict(pd.DataFrame({"ds": future_dates}))
    future_forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    future_forecast.to_csv(OUT / "sales_forecast_output.csv", index=False)

    print("Forecast evaluation:")
    print(pd.DataFrame([m]).to_string(index=False))
    print("Future forecast written to:", OUT / "sales_forecast_output.csv")


if __name__ == "__main__":
    main()
