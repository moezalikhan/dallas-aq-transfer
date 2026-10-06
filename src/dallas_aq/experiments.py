import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

from . import config as C
from .features import make_features


def score(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return mae, rmse


def new_models():
    return {
        "Linear Regression": LinearRegression(),
        "XGBoost": XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05,
                                subsample=0.8, random_state=42),
    }


def run_experiments(data: pd.DataFrame) -> pd.DataFrame:
    """Train on Dallas (targets dated 2024 or earlier), test on all counties in 2025."""
    rows = []
    for pollutant in ["ozone", "pm25"]:
        for h in C.HORIZONS:
            feat = make_features(data, pollutant, h)
            train = feat[(feat["county"] == C.TRAIN_COUNTY)
                         & (feat["target_date"].dt.year < C.TEST_YEAR)]
            test = feat[feat["date"].dt.year == C.TEST_YEAR]

            for county, t in test.groupby("county"):
                mae, rmse = score(t["target"], t["today"])
                rows.append(dict(pollutant=pollutant, horizon=h, features="none",
                                 model="Persistence", county=county, mae=mae, rmse=rmse))

            for feat_name, cols in [("no weather", C.BASE_FEATURES),
                                    ("with weather", C.BASE_FEATURES + C.WEATHER_COLS)]:
                for name, model in new_models().items():
                    model.fit(train[cols], train["target"])
                    for county, t in test.groupby("county"):
                        mae, rmse = score(t["target"], model.predict(t[cols]))
                        rows.append(dict(pollutant=pollutant, horizon=h, features=feat_name,
                                         model=name, county=county, mae=mae, rmse=rmse))
    return pd.DataFrame(rows)
