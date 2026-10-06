import pandas as pd

from dallas_aq import config as C
from dallas_aq.features import make_features


def _toy():
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    rows = []
    for county, base in [("Dallas", 0), ("Denton", 1000)]:
        for i, d in enumerate(dates):
            row = {"county": county, "date": d, "ozone": base + i, "pm25": base + i}
            row.update({c: 1.0 for c in C.WEATHER_COLS})
            rows.append(row)
    return pd.DataFrame(rows)


def test_target_is_future_value():
    out = make_features(_toy(), "ozone", horizon=3)
    assert (out["target"] - out["today"] == 3).all()


def test_lags_do_not_cross_counties():
    out = make_features(_toy(), "ozone", horizon=1)
    dallas = out[out["county"] == "Dallas"]
    assert (dallas["minus_1"] < 1000).all()
    assert (dallas["today"] - dallas["minus_6"] == 6).all()


def test_target_date_matches_horizon():
    out = make_features(_toy(), "ozone", horizon=7)
    assert ((out["target_date"] - out["date"]).dt.days == 7).all()
