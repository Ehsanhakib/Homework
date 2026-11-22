"""Part 7: variants A, B, C with the given model (notebook §6.1 to §6.3)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.pipeline import Pipeline

NUMERIC_FEATURES: list[str] = [
    "Lot Frontage",
    "Lot Area",
    "Overall Qual",
    "Overall Cond",
    "Year Built",
    "Year Remod/Add",
    "Total Bsmt SF",
    "1st Flr SF",
    "Gr Liv Area",
    "Full Bath",
    "TotRms AbvGrd",
    "Garage Area",
]

CV = KFold(n_splits=5, shuffle=True, random_state=5110)


def rmse(estimator, X: pd.DataFrame, y: pd.Series) -> float:
    return -cross_val_score(estimator, X, y, cv=CV, scoring="neg_root_mean_squared_error").mean()


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1], keep_default_na=False, na_values=[""])
    y = np.log(df["SalePrice"])
    X_raw = df[NUMERIC_FEATURES].copy()

    # Variant A: median Lot Frontage within each quintile of SalePrice on full table (Target Leakage)
    X_a = X_raw.copy()
    quintiles = pd.qcut(df["SalePrice"], q=5)
    quintile_medians = X_a.groupby(quintiles, observed=False)[
        "Lot Frontage"].transform("median")
    X_a["Lot Frontage"] = X_a["Lot Frontage"].fillna(quintile_medians)
    # Fill any tiny remaining missing values in other predictors cleanly inside pipeline
    pipe_a = Pipeline([
        ("imp", IterativeImputer(random_state=5110, max_iter=20, min_value=0.0)),
        ("reg", LinearRegression()),
    ])
    rmse_a = rmse(pipe_a, X_a, y)

    # Variant B: Part 6 IterativeImputer fitted on the full table BEFORE CV (Train-Test Feature Leakage)
    imp_b = IterativeImputer(random_state=5110, max_iter=20, min_value=0.0)
    X_b = pd.DataFrame(imp_b.fit_transform(
        X_raw), columns=NUMERIC_FEATURES, index=X_raw.index)
    rmse_b = rmse(LinearRegression(), X_b, y)

    # Variant C: Part 6 IterativeImputer inside a Pipeline (Leakage-Safe)
    pipe_c = Pipeline([
        ("imp", IterativeImputer(random_state=5110, max_iter=20, min_value=0.0)),
        ("reg", LinearRegression()),
    ])
    rmse_c = rmse(pipe_c, X_raw, y)

    results = pd.DataFrame(
        [
            {"Variant": "A (Target-quintile median on full table)",
             "CV_RMSE_log_SalePrice": round(rmse_a, 5)},
            {"Variant": "B (IterativeImputer fit on full table)",
             "CV_RMSE_log_SalePrice": round(rmse_b, 5)},
            {"Variant": "C (IterativeImputer inside Pipeline)",
             "CV_RMSE_log_SalePrice": round(rmse_c, 5)},
        ]
    )

    print("--- Part 7: 5-Fold CV RMSE Results ---")
    print(results.to_string(index=False))
    print(f"\nDifference (C - B): {rmse_c - rmse_b:+.6f}")

    res_dir = Path("reports/results")
    res_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(res_dir / "cv_rmse_results.csv", index=False)
