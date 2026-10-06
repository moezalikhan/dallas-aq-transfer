import pandas as pd

from . import config as C

OTHERS = ["Tarrant", "Collin", "Denton"]


def transfer_table(results: pd.DataFrame) -> pd.DataFrame:
    """RMSE grid by county plus transfer gap (% worse than Dallas) and average gap."""
    table = results.pivot_table(index=["pollutant", "horizon", "model", "features"],
                                columns="county", values="rmse")
    table = table.reindex(columns=C.COUNTY_ORDER)
    for c in OTHERS:
        table[f"gap {c} %"] = (table[c] - table["Dallas"]) / table["Dallas"] * 100
    table["avg gap %"] = table[[f"gap {c} %" for c in OTHERS]].mean(axis=1)
    return table.round(2)
