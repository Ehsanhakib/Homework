import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Setup paths relative to the repository root
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "raw" / "coffee_sales.csv"
OUTPUT_DIR = ROOT_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load data
df = pd.read_csv(DATA_PATH)

# 2. Compute revenue
df["revenue"] = df["quantity"] * df["unit_price"]

# 3. Calculate daily revenue BEFORE printing (fixes out-of-order execution)
daily = df.groupby("date")["revenue"].sum()
avg_daily = daily.mean()
print(f"Average daily revenue: ${avg_daily:.2f}")

# 4. Random 50/50 split WITH a fixed seed for deterministic results
shuffled = df.sample(frac=1, random_state=42)
half = len(shuffled) // 2
group_a = shuffled.iloc[:half]
group_b = shuffled.iloc[half:]
print(f"Group A mean revenue: {group_a['revenue'].mean():.2f}")
print(f"Group B mean revenue: {group_b['revenue'].mean():.2f}")

# 5. Revenue by product plot saved to outputs/
by_product = df.groupby("product")["revenue"].sum()
plt.figure(figsize=(8, 5))
by_product.plot(kind="bar")
plt.ylabel("Total revenue ($)")
plt.title("Revenue by product")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "revenue_by_product.png")
plt.close()