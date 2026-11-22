# HW5: Ames Housing quality audit

## How to run

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make all
```

## Provenance
* **Source URL:** https://jse.amstat.org/v19n3/decock/AmesHousing.txt
* **Data Dictionary URL:** https://jse.amstat.org/v19n3/decock/DataDocumentation.txt
* **Date Downloaded:** November 22, 2026
* **Citation:** De Cock, D. (2011). Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project. *Journal of Statistics Education*, 19(3). https://doi.org/10.1080/10691898.2011.11889627
* **Terms of Use:** Published in the open-access *Journal of Statistics Education* (American Statistical Association / Taylor & Francis) for educational and non-commercial research use with attribution (https://jse.amstat.org/v19n3/decock.html).
* **Dimensions on Arrival:** 2,930 rows, 82 columns.


## Features used in Part 7

The following 12 numeric columns are included in `NUMERIC_FEATURES` (`src/evaluate.py`)[cite: 8] to capture core drivers of residential property value—lot dimensions, overall build/remodel quality and age, interior living and basement square footage, room/bathroom counts, and garage capacity—alongside `Lot Frontage`[cite: 8] to evaluate imputation and leakage effects:

1. `Lot Frontage` — Linear feet of street connected to property (target feature with 16.72% missing values tested across leakage variants)[cite: 8, 12].
2. `Lot Area` — Total lot size in square feet, strongly correlated with `Lot Frontage` and property value[cite: 12].
3. `Overall Qual` — Overall material and finish quality rating (1–10 scale), a primary determinant of sale price.
4. `Overall Cond` — Overall condition rating of the house (1–10 scale).
5. `Year Built` — Original construction year, capturing age and era effects.
6. `Year Remod/Add` — Remodel or addition year, reflecting modernization since construction.
7. `Total Bsmt SF` — Total square footage of basement area.
8. `1st Flr SF` — First-floor square footage, correlated with building footprint and frontage.
9. `Gr Liv Area` — Above-grade (ground) living area square footage, one of the strongest linear predictors of `log(SalePrice)`[cite: 8].
10. `Full Bath` — Number of full bathrooms above grade.
11. `TotRms AbvGrd` — Total rooms above grade (excluding bathrooms), measuring functional interior layout size.
12. `Garage Area` — Size of garage in square feet, capturing vehicle storage capacity and property utility.


## AI Attribution and Reflection
AI assistance (Gemini) was used to draft and debug the modular pipeline scripts (`src/download.py`, `src/validate.py`, `src/clean.py`, `src/missingness.py`, `src/impute.py`, and `src/evaluate.py`) and structure this report. 
All code was executed locally in my environment, where I resolved an SSL context error during download, verified that `keep_default_na=False` preserved the 1,752 structural `"None"` values in `Mas Vnr Type`, and confirmed that all validation rules, imputation metrics, and 5-fold cross-validation RMSE results matched the generated outputs.
