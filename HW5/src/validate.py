"""Part 2: validation as code. Raise once, listing every failure (notebook §1)."""
import sys
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype


class ValidationError(Exception):
    pass


EXPECTED_NUMERIC_COLS = {
    "Order", "PID", "MS SubClass", "Lot Frontage", "Lot Area", "Overall Qual",
    "Overall Cond", "Year Built", "Year Remod/Add", "Mas Vnr Area", "BsmtFin SF 1",
    "BsmtFin SF 2", "Bsmt Unf SF", "Total Bsmt SF", "1st Flr SF", "2nd Flr SF",
    "Low Qual Fin SF", "Gr Liv Area", "Bsmt Full Bath", "Bsmt Half Bath",
    "Full Bath", "Half Bath", "Bedroom AbvGr", "Kitchen AbvGr", "TotRms AbvGrd",
    "Fireplaces", "Garage Yr Blt", "Garage Cars", "Garage Area", "Wood Deck SF",
    "Open Porch SF", "Enclosed Porch", "3Ssn Porch", "Screen Porch", "Pool Area",
    "Misc Val", "Mo Sold", "Yr Sold", "SalePrice",
}

EXPECTED_TEXT_COLS = {
    "MS Zoning", "Street", "Alley", "Lot Shape", "Land Contour", "Utilities",
    "Lot Config", "Land Slope", "Neighborhood", "Condition 1", "Condition 2",
    "Bldg Type", "House Style", "Roof Style", "Roof Matl", "Exterior 1st",
    "Exterior 2nd", "Mas Vnr Type", "Exter Qual", "Exter Cond", "Foundation",
    "Bsmt Qual", "Bsmt Cond", "Bsmt Exposure", "BsmtFin Type 1", "BsmtFin Type 2",
    "Heating", "Heating QC", "Central Air", "Electrical", "Kitchen Qual",
    "Functional", "Fireplace Qu", "Garage Type", "Garage Finish", "Garage Qual",
    "Garage Cond", "Paved Drive", "Pool QC", "Fence", "Misc Feature",
    "Sale Type", "Sale Condition",
}

EXPECTED_ALL_COLS = EXPECTED_NUMERIC_COLS | EXPECTED_TEXT_COLS

# Each rule needs a source. Put it in the comment.
RANGES = {
    # source: physical/economic limit (positive sale price in USD)
    "SalePrice": (1, 10_000_000),
    # source: physical limit (parcel area in sq ft must be > 0)
    "Lot Area": (1, 500_000),
    # source: physical limit (linear feet of street connected > 0)
    "Lot Frontage": (1, 500),
    # source: data dictionary, Overall Qual (Ordinal: 1 Very Poor to 10 Very Excellent)
    "Overall Qual": (1, 10),
    # source: data dictionary, Overall Cond (Ordinal: 1 Very Poor to 10 Very Excellent)
    "Overall Cond": (1, 10),
    # source: data dictionary & study period (original construction date <= max Yr Sold 2010)
    "Year Built": (1870, 2010),
    # source: data dictionary & study period (remodel date; same as construction if no remodel)
    "Year Remod/Add": (1950, 2010),
    # source: physical limit & study period (automobile era <= max Yr Sold 2010)
    "Garage Yr Blt": (1895, 2010),
    # source: data dictionary, Mo Sold (Month Sold: 1 to 12)
    "Mo Sold": (1, 12),
    # source: data dictionary & study period (Ames sales occurred 2006 to 2010)
    "Yr Sold": (2006, 2010),
}

ALLOWED = {
    # source: data dictionary, Street (Nominal)
    "Street": {"Grvl", "Pave"},
    # source: data dictionary, Central Air (Nominal)
    "Central Air": {"N", "Y"},
    # source: data dictionary, MS Zoning (Nominal)
    "MS Zoning": {"A", "C", "FV", "I", "RH", "RL", "RP", "RM"},
    # source: data dictionary, Garage Finish (Ordinal: NA decoded to None in clean data)
    "Garage Finish": {"Fin", "RFn", "Unf", "None"},
    # source: data dictionary, Pool QC (Ordinal: NA decoded to None in clean data)
    "Pool QC": {"Ex", "Gd", "TA", "Fa", "None"},
    # source: data dictionary, Sale Condition (Nominal)
    "Sale Condition": {"Normal", "Abnorml", "AdjLand", "Alloca", "Family", "Partial"},
}


def check_schema(df: pd.DataFrame) -> list[str]:
    """Return a list of schema failures: missing or extra columns, wrong dtype families."""
    errors = []
    actual_cols = set(df.columns)
    missing = sorted(EXPECTED_ALL_COLS - actual_cols)
    extra = sorted(actual_cols - EXPECTED_ALL_COLS)
    if missing:
        errors.append(f"Schema: missing columns {missing}")
    if extra:
        errors.append(f"Schema: unexpected extra columns {extra}")

    for col in sorted(EXPECTED_NUMERIC_COLS & actual_cols):
        if not is_numeric_dtype(df[col]):
            errors.append(
                f"Schema dtype: '{col}' expected numeric, got {df[col].dtype}")

    for col in sorted(EXPECTED_TEXT_COLS & actual_cols):
        if not is_string_dtype(df[col]):
            errors.append(
                f"Schema dtype: '{col}' expected text, got {df[col].dtype}")

    return errors


def check_ranges(df: pd.DataFrame) -> list[str]:
    """Return one message per column with values outside its range. NaN is not judged here."""
    errors = []
    for col, (low, high) in RANGES.items():
        if col not in df.columns or not is_numeric_dtype(df[col]):
            continue
        valid = df[col].dropna()
        bad = valid[(valid < low) | (valid > high)]
        if len(bad) > 0:
            errors.append(
                f"Range '{col}' [{low}, {high}]: {len(bad)} out-of-range values "
                f"(min={bad.min()}, max={bad.max()})"
            )
    return errors


def check_allowed(df: pd.DataFrame) -> list[str]:
    """Return one message per categorical column with values not in the dictionary."""
    errors = []
    for col, allowed_vals in ALLOWED.items():
        if col not in df.columns:
            continue
        valid = df[col].dropna()
        bad_mask = ~valid.isin(allowed_vals)
        if bad_mask.any():
            bad_vals = valid[bad_mask].value_counts().to_dict()
            errors.append(
                f"Allowed '{col}': {int(bad_mask.sum())} invalid values {bad_vals}"
            )
    return errors


def check_cross_column(df: pd.DataFrame) -> list[str]:
    """Return failures of rules that involve two or more columns."""
    errors = []
    if {"Year Built", "Year Remod/Add"} <= set(df.columns):
        mask = df["Year Remod/Add"].notna() & df["Year Built"].notna() & (
            df["Year Remod/Add"] < df["Year Built"]
        )
        if mask.any():
            errors.append(
                f"Cross-column 'Year Remod/Add >= Year Built': {int(mask.sum())} rows violated"
            )

    if {"Year Built", "Yr Sold"} <= set(df.columns):
        mask = df["Year Built"].notna() & df["Yr Sold"].notna() & (
            df["Year Built"] > df["Yr Sold"]
        )
        if mask.any():
            errors.append(
                f"Cross-column 'Year Built <= Yr Sold': {int(mask.sum())} rows violated"
            )

    if {"Garage Yr Blt", "Yr Sold"} <= set(df.columns) and is_numeric_dtype(df["Garage Yr Blt"]):
        mask = df["Garage Yr Blt"].notna() & df["Yr Sold"].notna() & (
            df["Garage Yr Blt"] > df["Yr Sold"]
        )
        if mask.any():
            errors.append(
                f"Cross-column 'Garage Yr Blt <= Yr Sold': {int(mask.sum())} rows violated"
            )

    return errors


def validate(df: pd.DataFrame) -> pd.DataFrame:
    errors = check_schema(df) + check_ranges(df) + \
        check_allowed(df) + check_cross_column(df)
    if errors:
        raise ValidationError("\n".join(errors))
    return df


if __name__ == "__main__":
    path = sys.argv[1]
    raw = "--raw" in sys.argv
    df = pd.read_csv(path, sep="\t" if raw else ",",
                     keep_default_na=False, na_values=[""])
    try:
        validate(df)
        print(f"PASS {path}")
    except ValidationError as e:
        print(f"FAIL {path}\n{e}")
        sys.exit(1)
