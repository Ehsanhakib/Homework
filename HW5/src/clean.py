"""Parts 3 and 4: decode true missing values, keep structural "none", check keys."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Columns where the dictionary defines "NA" as "none", not "unknown".
NA_MEANS_NONE: list[str] = [
    "Alley",
    "Bsmt Qual",
    "Bsmt Cond",
    "Bsmt Exposure",
    "BsmtFin Type 1",
    "BsmtFin Type 2",
    "Fireplace Qu",
    "Garage Type",
    "Garage Finish",
    "Garage Qual",
    "Garage Cond",
    "Pool QC",
    "Fence",
    "Misc Feature",
]

# Full neighborhood names from De Cock (2011) DataDocumentation.txt
NEIGHBORHOOD_LOOKUP = pd.DataFrame(
    [
        ("Blmngtn", "Bloomington Heights"),
        ("Blueste", "Bluestem"),
        ("BrDale", "Briardale"),
        ("BrkSide", "Brookside"),
        ("ClearCr", "Clear Creek"),
        ("CollgCr", "College Creek"),
        ("Crawfor", "Crawford"),
        ("Edwards", "Edwards"),
        ("Gilbert", "Gilbert"),
        ("Greens", "Greens"),
        ("GrnHill", "Green Hills"),
        ("IDOTRR", "Iowa DOT and Rail Road"),
        ("Landmrk", "Landmark"),
        ("MeadowV", "Meadow Village"),
        ("Mitchel", "Mitchell"),
        ("NAmes", "North Ames"),
        ("NoRidge", "Northridge"),
        ("NPkVill", "Northpark Villa"),
        ("NridgHt", "Northridge Heights"),
        ("NWAmes", "Northwest Ames"),
        ("OldTown", "Old Town"),
        ("SWISU", "South & West of Iowa State University"),
        ("Sawyer", "Sawyer"),
        ("SawyerW", "Sawyer West"),
        ("Somerst", "Somerset"),
        ("StoneBr", "Stone Brook"),
        ("Timber", "Timberland"),
        ("Veenker", "Veenker"),
    ],
    columns=["Neighborhood", "Neighborhood_Full"],
)


def load_raw(path: str) -> pd.DataFrame:
    """Load with keep_default_na=False so that "NA" and "None" survive as strings."""
    df_no_na = pd.read_csv(path, sep="\t", keep_default_na=False)
    df_default = pd.read_csv(path, sep="\t")

    print("--- Part 3 Audit: 'NA' and 'None' Strings in Raw File ---")
    for col in df_no_na.columns:
        s = df_no_na[col].astype(str)
        na_cnt = int((s == "NA").sum())
        none_cnt = int((s == "None").sum())
        empty_cnt = int((s == "").sum())
        diff_nan = int(df_default[col].isna().sum()) - empty_cnt
        if na_cnt > 0 or none_cnt > 0 or empty_cnt > 0:
            meaning = "structural 'none'" if col in NA_MEANS_NONE else "true missing / genuine category"
            print(
                f"  {col:18s} | 'NA'={na_cnt:4d} | 'None'={none_cnt:4d} | ''={empty_cnt:3d} "
                f"| default_extra_NaN={diff_nan:4d} ({meaning})"
            )
    return df_no_na


def decode_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Turn only true missing values into NaN. Return a new DataFrame."""
    clean = df.copy()

    # 1. Structural "NA" -> explicit "None" category
    for col in NA_MEANS_NONE:
        clean[col] = clean[col].replace({"NA": "None"})

    # 2. All remaining "NA" or "" strings are true missing values -> np.nan
    clean = clean.replace({"NA": np.nan, "": np.nan})

    # 3. Cast numeric columns back to numeric dtype now that "NA" is np.nan
    numeric_cols = [
        "Order", "PID", "MS SubClass", "Lot Frontage", "Lot Area", "Overall Qual",
        "Overall Cond", "Year Built", "Year Remod/Add", "Mas Vnr Area", "BsmtFin SF 1",
        "BsmtFin SF 2", "Bsmt Unf SF", "Total Bsmt SF", "1st Flr SF", "2nd Flr SF",
        "Low Qual Fin SF", "Gr Liv Area", "Bsmt Full Bath", "Bsmt Half Bath",
        "Full Bath", "Half Bath", "Bedroom AbvGr", "Kitchen AbvGr", "TotRms AbvGrd",
        "Fireplaces", "Garage Yr Blt", "Garage Cars", "Garage Area", "Wood Deck SF",
        "Open Porch SF", "Enclosed Porch", "3Ssn Porch", "Screen Porch", "Pool Area",
        "Misc Val", "Mo Sold", "Yr Sold", "SalePrice",
    ]
    for col in numeric_cols:
        clean[col] = pd.to_numeric(clean[col], errors="raise")

    # 4. Fix documented Part 2 validation failures transparently
    clean["MS Zoning"] = clean["MS Zoning"].replace(
        {"C (all)": "C", "I (all)": "I", "A (agr)": "A"}
    )
    clean.loc[clean["Garage Yr Blt"] == 2207, "Garage Yr Blt"] = 2007
    clean["Year Remod/Add"] = np.maximum(
        clean["Year Remod/Add"], clean["Year Built"])
    clean["Year Built"] = np.minimum(clean["Year Built"], clean["Yr Sold"])
    clean.loc[clean["Garage Yr Blt"].notna(), "Garage Yr Blt"] = np.minimum(
        clean.loc[clean["Garage Yr Blt"].notna(), "Garage Yr Blt"],
        clean.loc[clean["Garage Yr Blt"].notna(), "Yr Sold"],
    )

    return clean


def check_keys(df: pd.DataFrame) -> None:
    """Assert key uniqueness; print exact and key duplicate counts; run the many_to_one join."""
    print("\n--- Part 4 Audit: Keys, Duplicates, and Lookup Join ---")
    exact_dups = int(df.duplicated().sum())
    order_dups = int(df.duplicated(subset=["Order"]).sum())
    pid_dups = int(df.duplicated(subset=["PID"]).sum())

    print(f"  Exact duplicate rows: {exact_dups}")
    print(f"  'Order' duplicates (unique observation key): {order_dups}")
    print(f"  'PID' duplicates (repeat sales of same parcel): {pid_dups}")

    assert df["Order"].is_unique, "Expected 'Order' to uniquely identify each sale row."

    joined = pd.merge(
        df,
        NEIGHBORHOOD_LOOKUP,
        on="Neighborhood",
        how="left",
        validate="many_to_one",
    )
    assert len(joined) == len(
        df), f"Row count changed after join: {len(joined)} != {len(df)}"
    assert joined["Neighborhood_Full"].notna(
    ).all(), "Unmapped Neighborhood codes found!"
    print(
        f"  many_to_one Neighborhood join succeeded; row count unchanged ({len(joined):,} rows).")


if __name__ == "__main__":
    raw_path, out_path = sys.argv[1], sys.argv[2]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df = decode_missing(load_raw(raw_path))
    check_keys(df)
    df.to_csv(out_path, index=False)
    print(
        f"\nSaved cleaned dataset to {out_path} ({df.shape[0]:,} rows, {df.shape[1]} columns)")
