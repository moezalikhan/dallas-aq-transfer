from dallas_aq import config as C
from dallas_aq.data import build_dataset
from dallas_aq.experiments import run_experiments
from dallas_aq.plots import chart_heat_ozone, chart_horizon, chart_transfer
from dallas_aq.report import transfer_table


def main():
    C.FIG_DIR.mkdir(parents=True, exist_ok=True)
    data = build_dataset()
    print("Missing values per county:")
    print(data.groupby("county")[["ozone", "pm25"]].apply(lambda g: g.isna().sum()))

    results = run_experiments(data)
    results.to_csv(C.RESULTS_DIR / "results.csv", index=False)

    table = transfer_table(results)
    table.to_csv(C.RESULTS_DIR / "results_table.csv")
    print(table)

    chart_horizon(results)
    chart_transfer(table)
    slope = chart_heat_ozone(data)
    print(f"Ozone rises about {slope:.2f} ppb per 1 degree C (Dallas)")


if __name__ == "__main__":
    main()
