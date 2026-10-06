import pandas as pd

from . import config as C


def make_features(df: pd.DataFrame, pollutant: str, horizon: int) -> pd.DataFrame:
    """Lag, rolling and calendar features plus a target `horizon` days ahead, built per county."""
    parts = []
    for _, g in df.groupby("county"):
        g = g.sort_values("date").copy()
        g["today"] = g[pollutant]
        for k in [1, 2, 6]:
            g[f"minus_{k}"] = g[pollutant].shift(k)
        g["roll_7"] = g[pollutant].rolling(7).mean()
        g["month"] = g["date"].dt.month
        g["dow"] = g["date"].dt.dayofweek
        g["target"] = g[pollutant].shift(-horizon)
        g["target_date"] = g["date"] + pd.Timedelta(days=horizon)
        parts.append(g)
    out = pd.concat(parts)
    return out.dropna(subset=C.BASE_FEATURES + C.WEATHER_COLS + ["target"])
