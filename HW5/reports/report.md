# Homework 5: Data Cleaning, Validation, Missingness, and Leakage on the Ames Housing Dataset

## Part 1: Provenance
* **Source URL:** https://jse.amstat.org/v19n3/decock/AmesHousing.txt
* **Data Dictionary URL:** https://jse.amstat.org/v19n3/decock/DataDocumentation.txt
* **Date Downloaded:** November 22, 2026
* **Citation:** De Cock, D. (2011). Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project. *Journal of Statistics Education*, 19(3). https://doi.org/10.1080/10691898.2011.11889627
* **Terms of Use:** Published in the open-access *Journal of Statistics Education* (American Statistical Association / Taylor & Francis) for educational and non-commercial research use with attribution (https://jse.amstat.org/v19n3/decock.html).
* **Starting Shape:** 2,930 rows, 82 columns.

## Part 2: Validation as Code
Running `src/validate.py data/raw/AmesHousing.txt --raw` failed on the raw dataset and caught 7 rule violations:
1. **Range `Garage Yr Blt` [1895, 2010]:** 1 out-of-range value (`2207.0`)[cite: 10].
2. **Allowed `MS Zoning`:** 29 invalid values (`{'C (all)': 25, 'I (all)': 2, 'A (agr)': 2}`) relative to dictionary codes[cite: 10].
3. **Allowed `Garage Finish`:** 157 invalid values (`{'NA': 157}`) because raw `"NA"` denotes no garage prior to decoding[cite: 10].
4. **Allowed `Pool QC`:** 2,917 invalid values (`{'NA': 2917}`) because raw `"NA"` denotes no pool prior to decoding[cite: 10].
5. **Cross-column `Year Remod/Add >= Year Built`:** 1 row violated[cite: 10].
6. **Cross-column `Year Built <= Yr Sold`:** 1 row violated[cite: 10].
7. **Cross-column `Garage Yr Blt <= Yr Sold`:** 2 rows violated[cite: 10].

After cleaning in `src/clean.py`, `src/validate.py data/processed/ames_clean.csv` passed (`PASS data/processed/ames_clean.csv`)[cite: 12].

## Part 3: Missing Data — Not All NAs Are Missing
Loading with `keep_default_na=False` preserves `"NA"` and `"None"` as strings[cite: 8, 11]. Default `pd.read_csv()` wrongly turns `"None"` in `Mas Vnr Type` (1,752 rows, meaning no masonry veneer) into `NaN`[cite: 11]. In `src/clean.py`, structural `"NA"` across 14 absence columns (such as `Pool QC` with 2,917, `Misc Feature` with 2,824, `Alley` with 2,732, `Fence` with 2,358, `Fireplace Qu` with 1,422, garage columns with ~157–158, and basement columns with 79) is mapped to `"None"`, while empty strings `""` (such as `Lot Frontage` with 490 and `Garage Yr Blt` with 159) are decoded to `NaN`[cite: 8, 11].

## Part 4: Keys, Duplicates, and Joins
* **Exact duplicate rows:** 0[cite: 11].
* **`Order` duplicates:** 0 (`Order` uniquely identifies each sale observation)[cite: 11].
* **`PID` duplicates:** 0 in this dataset (`PID` identifies the property parcel)[cite: 11].
* **Neighborhood join:** `pd.merge(..., validate="many_to_one")` joined the 28 neighborhood codes to their full names while preserving all 2,930 rows[cite: 11].

## Part 5: Missingness Mechanism
* **`Lot Frontage` (490 / 2,930 = 16.72% missing):** Missingness is not MCAR (consistent with MAR/MNAR)[cite: 17]. Missing rows have more `CulDSac` lots (18.0% vs. 3.8%) and fewer `Inside` lots (55.9% vs. 76.5%), alongside larger `Lot Area` (mean 12,331.0 vs. 9,709.5)[cite: 17].
* **`Mas Vnr Area` (23 / 2,930 = 0.78% missing):** Missing rows are newer (mean `Year Built` 2,002.7 vs. 1,971.1), have higher `SalePrice` (mean $233,348.7 vs. $180,380.3), and appear disproportionately in `Somerst` (43.5%) and `Gilbert` (21.7%)[cite: 17].

## Part 6: Imputation and Its Costs
| Strategy | `std_before` | `std_after` | `corr_with_other_before` | `corr_with_other_after` |
| --- | --- | --- | --- | --- |
| Median Fill | 23.365 | 21.326 | 0.4913 | 0.3628 |
| Iterative Imputer | 23.365 | 22.789 | 0.4913 | 0.5616 |

Median fill compresses spread and weakens correlation with `Lot Area`, whereas `IterativeImputer` preserves spread better and increases correlation with `Lot Area`[cite: 17]. Histograms are saved in `reports/figures/lot_frontage_median.png` and `reports/figures/lot_frontage_iterative.png`[cite: 14, 17].

## Part 7: Leakage in Model Evaluation
Using `LinearRegression` on `np.log(SalePrice)` with 5-fold CV (`random_state=5110`)[cite: 13]:
* **Variant A (Target-quintile median on full table):** `0.16027` RMSE[cite: 17]
* **Variant B (`IterativeImputer` fit on full table):** `0.16038` RMSE[cite: 17]
* **Variant C (`IterativeImputer` inside `Pipeline`):** `0.16043` RMSE (`C - B = +0.000053`)[cite: 17]

Fitting the imputer on the full dataset (Variant B) slightly lowers CV RMSE compared to fitting inside each training fold (Variant C) due to feature leakage[cite: 17].

