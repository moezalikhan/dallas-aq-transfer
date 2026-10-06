from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
FIG_DIR = RESULTS_DIR / "figures"

YEARS = range(2019, 2026)  # 2019 to 2025 inclusive
COUNTIES = {113: "Dallas", 439: "Tarrant", 85: "Collin", 121: "Denton"}
COUNTY_ORDER = ["Dallas", "Tarrant", "Collin", "Denton"]
TRAIN_COUNTY = "Dallas"
TEST_YEAR = 2025
HORIZONS = [1, 7, 14]

EPA_URL = "https://aqs.epa.gov/aqsweb/airdata/daily_{code}_{year}.zip"
EPA_KEEP_COLS = ["State Code", "County Code", "Site Num", "Sample Duration",
                 "Date Local", "Arithmetic Mean", "1st Max Value", "AQI"]
OZONE_CODE, PM25_CODE = "44201", "88101"
OZONE_DURATION = "8-HR RUN AVG BEGIN HOUR"

WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"
POINTS = {"Dallas": (32.78, -96.80), "Tarrant": (32.75, -97.33),
          "Collin": (33.20, -96.62), "Denton": (33.21, -97.13)}
WEATHER_COLS = ["temperature_2m_max", "temperature_2m_mean", "wind_speed_10m_max",
                "relative_humidity_2m_mean", "shortwave_radiation_sum", "precipitation_sum"]
START_DATE, END_DATE = "2019-01-01", "2025-12-31"
TIMEZONE = "America/Chicago"

BASE_FEATURES = ["today", "minus_1", "minus_2", "minus_6", "roll_7", "month", "dow"]
