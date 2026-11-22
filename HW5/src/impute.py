"""Part 6: at least two strategies for Lot Frontage, and their costs (notebook §5 pattern)."""
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, SimpleImputer


def cost_table(before: pd.Series, after: pd.Series, other: pd.Series) -> pd.Series:
    """std before/after, correlation with `other` before/after."""
    return pd.Series(
        {
            "std_before": round(float(before.std()), 3),
            "std_after": round(float(after.std()), 3),
            "corr_with_other_before": round(float(before.corr(other)), 4),
            "corr_with_other_after": round(float(after.corr(other)), 4),
        }
    )


def save_histogram(before: pd.Series, after: pd.Series, title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.hist(before.dropna(), bins=35, alpha=0.55,
            label=f"Observed (n={before.notna().sum()})", density=True)
    ax.hist(after, bins=35, alpha=0.55,
            label=f"After Fill (n={len(after)})", density=True)
    ax.set_title(title)
    ax.set_xlabel("Lot Frontage (linear feet)")
    ax.set_ylabel("Density")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    fig_dir = Path("reports/figures")
    res_dir = Path("reports/results")
    fig_dir.mkdir(parents=True, exist_ok=True)
    res_dir.mkdir(parents=True, exist_ok=True)

    before = df["Lot Frontage"]
    lot_area = df["Lot Area"]

    # Strategy 1: Simple Median Fill
    med_imp = SimpleImputer(strategy="median")
    after_median = pd.Series(
        med_imp.fit_transform(df[["Lot Frontage"]]).ravel(),
        index=df.index,
        name="Lot Frontage",
    )

    # Strategy 2: Multivariate IterativeImputer using correlated structural/lot features
    iter_cols = ["Lot Frontage", "Lot Area", "1st Flr SF",
                 "Gr Liv Area", "TotRms AbvGrd", "Year Built"]
    iter_imp = IterativeImputer(random_state=5110, max_iter=20, min_value=1.0)
    iter_filled = iter_imp.fit_transform(df[iter_cols])
    after_iter = pd.Series(
        iter_filled[:, 0], index=df.index, name="Lot Frontage")

    costs = pd.DataFrame(
        {
            "Median Fill": cost_table(before, after_median, lot_area),
            "Iterative Imputer": cost_table(before, after_iter, lot_area),
        }
    ).T

    print("--- Part 6: Imputation Cost Comparison (Lot Frontage) ---")
    print(costs.to_string())
    costs.to_csv(res_dir / "imputation_costs.csv")

    save_histogram(
        before,
        after_median,
        "Lot Frontage Distribution: Observed vs. Median Fill",
        fig_dir / "lot_frontage_median.png",
    )
    save_histogram(
        before,
        after_iter,
        "Lot Frontage Distribution: Observed vs. Iterative Imputer",
        fig_dir / "lot_frontage_iterative.png",
    )
    print("Saved histograms to reports/figures/")
