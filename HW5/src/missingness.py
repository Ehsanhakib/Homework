"""Part 5: evidence about the missingness mechanism (notebook §4.1 pattern)."""
import sys
from pathlib import Path
import pandas as pd


def compare_groups(df: pd.DataFrame, col: str, observed_cols: list[str]) -> pd.DataFrame:
    """Compare rows with and without `col` on observed columns. Return a summary table."""
    is_missing = df[col].isna()
    rows = []

    for obs in observed_cols:
        if pd.api.types.is_numeric_dtype(df[obs]):
            obs_mean = df.loc[~is_missing, obs].mean()
            mis_mean = df.loc[is_missing, obs].mean()
            obs_med = df.loc[~is_missing, obs].median()
            mis_med = df.loc[is_missing, obs].median()
            rows.append(
                {
                    "target_col": col,
                    "observed_col": obs,
                    "type": "numeric",
                    "observed_summary": f"mean={obs_mean:,.1f}, median={obs_med:,.1f}",
                    "missing_summary": f"mean={mis_mean:,.1f}, median={mis_med:,.1f}",
                }
            )
        else:
            obs_top = df.loc[~is_missing, obs].value_counts(
                normalize=True).head(3)
            mis_top = df.loc[is_missing, obs].value_counts(
                normalize=True).head(3)
            obs_str = ", ".join(f"{k}:{v:.1%}" for k, v in obs_top.items())
            mis_str = ", ".join(f"{k}:{v:.1%}" for k, v in mis_top.items())
            rows.append(
                {
                    "target_col": col,
                    "observed_col": obs,
                    "type": "categorical",
                    "observed_summary": obs_str,
                    "missing_summary": mis_str,
                }
            )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    out_dir = Path("reports/results")
    out_dir.mkdir(parents=True, exist_ok=True)

    targets = ["Lot Frontage", "Mas Vnr Area"]
    observed = ["Lot Area", "Gr Liv Area", "Year Built",
                "SalePrice", "Lot Config", "Neighborhood"]

    all_tables = []
    print("--- Part 5: Missingness Audit ---")
    for t in targets:
        n_miss = int(df[t].isna().sum())
        share = n_miss / len(df)
        print(
            f"\nColumn '{t}': {n_miss} missing out of {len(df)} ({share:.2%})")
        tbl = compare_groups(df, t, observed)
        print(tbl[["observed_col", "observed_summary",
              "missing_summary"]].to_string(index=False))
        all_tables.append(tbl)

    summary_df = pd.concat(all_tables, ignore_index=True)
    summary_df.to_csv(out_dir / "missingness_summary.csv", index=False)
