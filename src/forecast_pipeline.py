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
INPUT = ROOT / "data" / "processed" / "monthly_sales_forecast.csv"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

def metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    error = actual - predicted
    nonzero = actual != 0
    return {
        "MAE": np.mean(np.abs(error)),
        "RMSE": np.sqrt(np.mean(error ** 2)),
        "MAPE": np.mean(np.abs(error[nonzero] / actual[nonzero])) * 100 if np.any(nonzero) else np.nan,
    }

def load_series():
    df = pd.read_csv(INPUT)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df.rename(columns={"Order Date": "ds", "Sales": "y"})[["ds", "y"]].sort_values("ds")

def main():
    series = load_series()
    holdout_size = 12
    train = series.iloc[:-holdout_size].copy()
    test = series.iloc[-holdout_size:].copy()

    evaluation_model = Prophet()
    evaluation_model.fit(train)
    evaluation_forecast = evaluation_model.predict(test[["ds"]])
    evaluation = test.merge(evaluation_forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]], on="ds", how="left")
    evaluation["Error"] = evaluation["y"] - evaluation["yhat"]
    evaluation["Absolute_Error"] = evaluation["Error"].abs()
    evaluation["Absolute_Percentage_Error"] = np.where(evaluation["y"] != 0, evaluation["Absolute_Error"] / evaluation["y"] * 100, np.nan)

    m = metrics(evaluation["y"], evaluation["yhat"])
    pd.DataFrame([m]).to_csv(OUT / "forecast_evaluation_metrics.csv", index=False)
    evaluation.to_csv(OUT / "forecast_vs_actual.csv", index=False)

    final_model = Prophet()
    final_model.fit(series)
    future = final_model.make_future_dataframe(periods=12, freq="ME")
    forecast = final_model.predict(future)
    future_forecast = forecast.tail(12)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    future_forecast.to_csv(OUT / "sales_forecast_output.csv", index=False)

    print("Forecast evaluation:")
    print(pd.DataFrame([m]).to_string(index=False))
    print("Future forecast written to:", OUT / "sales_forecast_output.csv")

if __name__ == "__main__":
    main()