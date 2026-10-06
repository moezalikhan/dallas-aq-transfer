import io
import zipfile

import pandas as pd
import requests

from . import config as C


def load_epa(code: str) -> pd.DataFrame:
    """Download (or load cached) EPA daily data for one pollutant, filtered to the 4 counties."""
    C.DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = C.DATA_DIR / f"epa_{code}.csv"
    if path.exists():
        return pd.read_csv(path, parse_dates=["Date Local"])
    frames = []
    for year in C.YEARS:
        print(f"Downloading EPA {code} {year}")
        resp = requests.get(C.EPA_URL.format(code=code, year=year), timeout=300)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            df = pd.read_csv(zf.open(zf.namelist()[0]), usecols=C.EPA_KEEP_COLS,
                             low_memory=False)
        df = df[(df["State Code"] == 48) & (df["County Code"].isin(C.COUNTIES))]
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["Date Local"] = pd.to_datetime(out["Date Local"])
    out.to_csv(path, index=False)
    return out


def daily_air_quality(ozone_raw: pd.DataFrame, pm25_raw: pd.DataFrame) -> pd.DataFrame:
    """One ozone value (max 8 hour average) and one PM2.5 value (daily mean) per county per day."""
    oz = ozone_raw[ozone_raw["Sample Duration"] == C.OZONE_DURATION]
    ozone_daily = (oz.groupby(["County Code", "Date Local"])["1st Max Value"]
                     .mean().rename("ozone").reset_index())
    pm25_daily = (pm25_raw.groupby(["County Code", "Date Local"])["Arithmetic Mean"]
                    .mean().rename("pm25").reset_index())
    aq = ozone_daily.merge(pm25_daily, on=["County Code", "Date Local"], how="outer")
    aq["county"] = aq["County Code"].map(C.COUNTIES)
    return aq.rename(columns={"Date Local": "date"}).drop(columns="County Code")


def load_weather() -> pd.DataFrame:
    """Daily weather for each county point from the Open-Meteo archive (cached)."""
    C.DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = C.DATA_DIR / "weather.csv"
    if path.exists():
        return pd.read_csv(path, parse_dates=["date"])
    frames = []
    for county, (lat, lon) in C.POINTS.items():
        params = {"latitude": lat, "longitude": lon,
                  "start_date": C.START_DATE, "end_date": C.END_DATE,
                  "daily": ",".join(C.WEATHER_COLS), "timezone": C.TIMEZONE}
        r = requests.get(C.WEATHER_URL, params=params, timeout=120)
        r.raise_for_status()
        w = pd.DataFrame(r.json()["daily"])
        w["date"] = pd.to_datetime(w.pop("time"))
        w["county"] = county
        frames.append(w)
    weather = pd.concat(frames, ignore_index=True)
    weather.to_csv(path, index=False)
    return weather


def build_dataset() -> pd.DataFrame:
    """Full calendar per county with weather, ozone (ppb) and PM2.5; single day gaps filled."""
    aq = daily_air_quality(load_epa(C.OZONE_CODE), load_epa(C.PM25_CODE))
    data = load_weather().merge(aq, on=["county", "date"], how="left")
    data = data.sort_values(["county", "date"]).reset_index(drop=True)
    data["ozone"] = data["ozone"] * 1000  # parts per million to parts per billion
    parts = []
    for _, g in data.groupby("county"):
        g = g.copy()
        g[["ozone", "pm25"]] = g[["ozone", "pm25"]].interpolate(limit=1, limit_area="inside")
        parts.append(g)
    data = pd.concat(parts).sort_values(["county", "date"]).reset_index(drop=True)
    data.to_csv(C.DATA_DIR / "merged.csv", index=False)
    return data
