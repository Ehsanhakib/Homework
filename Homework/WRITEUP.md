# DS5110 Homework #2: Data Tidying, Joining, and Analysis Write-Up

## 0. Descriptive Analysis & Tidiness Evaluation
Before reshaping or joining any datasets, I inspected the dimensions and structure of each raw file:
* **`orders.csv` (`20 × 5`):** Contains `order_id`, `customer_id`, `amount`, `company`, and `quarter`. This dataset is **tidy** because it satisfies all three tidy data rules: (1) each variable forms a single column, (2) each individual order observation forms a single row, and (3) each value occupies a single cell.
* **`company_quarterly_revenue_raw.csv` (`5 × 13`):** Contains `company` alongside twelve quarter columns (`2023-Q1` through `2025-Q4`). This dataset is **not tidy** because it violates **Rule 1 (each variable must form a column)**: values of the `quarter` variable are spread across column headers rather than stored in a dedicated column.
* **`shipments.csv` (`35 × 2`):** Contains `order_id` and `tracking`. At the shipment-level grain, this table is **tidy** because each individual tracking package forms a single row with one variable per column and one value per cell. However, at the order level, multiple tracking rows share the same `order_id`.

## 1. Reshaping the Revenue Table
`company_quarterly_revenue_raw.csv` was in a **wide** format. As noted above, it specifically violated **Rule 1 of tidy data** because column headers (`2023-Q1` to `2025-Q4`) represented values of a time variable (`quarter`) rather than variable names, while revenue values were scattered across twelve columns. Using `pd.melt()`, I reshaped it into a `60 × 3` long table with one row per `(company, quarter)` observation.

## 2. Duplicate Keys & Join Cardinality
Checking key uniqueness revealed that `order_id` is **unique** in `orders.csv` (20 unique IDs across 20 rows, acting as a primary key), whereas `order_id` is **not unique** in `shipments.csv` (20 unique IDs across 35 rows, as single orders split into multiple tracking numbers). This establishes a **one-to-many (`1:M`) cardinality** from `orders` to `shipments`, predicting that a left join will expand the 20 order rows to 35 shipment-level rows.

## 3. Joining Orders & Shipments and Mean Order Amount
Left-joining `orders` with `shipments` on `order_id` produced the predicted `35 × 6` table. Computing the mean order amount per customer yielded different results for multi-shipment customers (e.g., Customer `C103` averages `$112.38` on the joined table vs. `$111.60` on `orders` alone). **The mean computed on `orders` alone is correct.** In the joined table, orders split into multiple shipments have their `order_amount` duplicated across rows, artificially inflating the weight of multi-package orders.

## 4. Producing One Analysis-Ready Table
To create a single analysis-ready table without duplicating quarters, I left-joined the shipment-enriched order table with the tidy revenue table on **`['company', 'quarter']`**, renamed `amount` to `order_amount` and `revenue` to `company_quarterly_revenue`, and reset the index (`drop=True`) to eliminate index artifacts. Each row represents one distinct shipment observation enriched with its exact order and quarterly company context.

## 5. Visualization & What Got Easier
Comparing the raw Step 0 chart against the final side-by-side visualization highlights the value of tidy data. Before tidying, comparing order amounts against company quarterly revenue required manually matching string column headers (`2023-Q1`, etc.) across separate tables. Once reshaped and joined on `(company, quarter)`, plotting `order_amount` against `company_quarterly_revenue` grouped by `company` required a single, straightforward plotting call.
