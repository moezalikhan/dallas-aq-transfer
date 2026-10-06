import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import config as C
from .report import OTHERS


def chart_horizon(results: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, pollutant, unit in zip(axes, ["ozone", "pm25"], ["ppb", "µg/m³"]):
        d = results[(results["pollutant"] == pollutant) & (results["county"] == "Dallas")]
        d = d[d["features"] != "no weather"]
        for model, g in d.groupby("model"):
            g = g.sort_values("horizon")
            ax.plot(g["horizon"], g["rmse"], marker="o", label=model)
        ax.set_title(f"Dallas {pollutant.upper()}: RMSE by horizon")
        ax.set_xlabel("Days ahead"); ax.set_ylabel(f"RMSE ({unit})")
        ax.set_xticks(C.HORIZONS); ax.legend()
    fig.tight_layout(); fig.savefig(C.FIG_DIR / "chart_horizon.png", dpi=150); plt.close(fig)


def chart_transfer(table: pd.DataFrame, horizon: int = 1, model: str = "XGBoost"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    x = np.arange(len(OTHERS)); width = 0.38
    for ax, pollutant in zip(axes, ["ozone", "pm25"]):
        for i, feat_name in enumerate(["no weather", "with weather"]):
            gaps = [table.loc[(pollutant, horizon, model, feat_name), f"gap {c} %"] for c in OTHERS]
            ax.bar(x + (i - 0.5) * width, gaps, width, label=feat_name)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x); ax.set_xticklabels(OTHERS)
        ax.set_title(f"{pollutant.upper()}: error change vs Dallas ({model}, {horizon} day)")
        ax.set_ylabel("Transfer gap (%)"); ax.legend()
    fig.tight_layout(); fig.savefig(C.FIG_DIR / "chart_transfer.png", dpi=150); plt.close(fig)


def chart_heat_ozone(data: pd.DataFrame) -> float:
    d = data[data["county"] == "Dallas"].dropna(subset=["ozone", "temperature_2m_max"])
    slope, intercept = np.polyfit(d["temperature_2m_max"], d["ozone"], 1)
    corr = d["temperature_2m_max"].corr(d["ozone"])
    fig = plt.figure(figsize=(6, 4))
    plt.scatter(d["temperature_2m_max"], d["ozone"], s=6, alpha=0.4)
    xs = np.linspace(d["temperature_2m_max"].min(), d["temperature_2m_max"].max(), 50)
    plt.plot(xs, slope * xs + intercept, color="red")
    plt.title(f"Dallas: daily max temperature vs ozone (r = {corr:.2f})")
    plt.xlabel("Daily max temperature (°C)"); plt.ylabel("Ozone, max 8 hour (ppb)")
    fig.tight_layout(); fig.savefig(C.FIG_DIR / "chart_heat_ozone.png", dpi=150); plt.close(fig)
    return float(slope)
