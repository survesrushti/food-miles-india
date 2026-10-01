import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

PROCESSED = Path("data/processed")
OUTPUT = Path("outputs/figures")

OUTPUT.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("STEP 7B - RESEARCH VISUALIZATIONS")
print("=" * 70)


# =========================================================
# 1. YEAR-WISE FOOD MILES TREND
# =========================================================

print("\n1. CREATING CHART 4 - YEAR-WISE FOOD MILES TREND")

yearly = pd.read_csv(
    PROCESSED / "analysis_yearly_trends.csv"
)

yearly["Year"] = pd.to_numeric(yearly["Year"])

import_yearly = (
    yearly.groupby("Year")["import_food_miles_billion"]
    .sum()
)

export_yearly = (
    yearly.groupby("Year")["export_food_miles_billion"]
    .sum()
)

plt.figure(figsize=(12, 6))

plt.plot(
    import_yearly.index,
    import_yearly.values,
    marker="o",
    label="Import Food Miles"
)

plt.plot(
    export_yearly.index,
    export_yearly.values,
    marker="o",
    label="Export Food Miles"
)

plt.title("India's Food Miles Trend (2000–2024)")
plt.xlabel("Year")
plt.ylabel("Food Miles (Billion tonne-km)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    OUTPUT / "04_yearly_food_miles_trend.png",
    dpi=300
)

plt.close()

print("Saved: outputs/figures/04_yearly_food_miles_trend.png")


# =========================================================
# 2. TOP IMPORT SOURCE COUNTRIES
# =========================================================

print("\n2. CREATING CHART 5 - TOP IMPORT SOURCE COUNTRIES")

sources = pd.read_csv(
    PROCESSED / "analysis_top_sources.csv"
)

top_sources = (
    sources.groupby("Country")["quantity_tonnes"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(11, 6))

top_sources.sort_values().plot(
    kind="barh"
)

plt.title("Top Import Source Countries for Selected Foods")
plt.xlabel("Imported Quantity (tonnes)")
plt.ylabel("Source Country")
plt.tight_layout()

plt.savefig(
    OUTPUT / "05_top_import_source_countries.png",
    dpi=300
)

plt.close()

print("Saved: outputs/figures/05_top_import_source_countries.png")


# =========================================================
# 3. PRODUCTION VS IMPORT DEPENDENCY
# =========================================================

print("\n3. CREATING CHART 6 - PRODUCTION VS IMPORT DEPENDENCY")

production_trade = pd.read_csv(
    PROCESSED / "analysis_production_trade.csv"
)

latest_year = production_trade["Year"].max()

latest = production_trade[
    production_trade["Year"] == latest_year
].copy()

latest = latest.dropna(
    subset=[
        "india_production_tonnes",
        "import_dependency_percent"
    ]
)

plt.figure(figsize=(12, 7))

plt.scatter(
    latest["india_production_tonnes"],
    latest["import_dependency_percent"],
    s=80
)

for _, row in latest.iterrows():

    plt.annotate(
        row["Item"],
        (
            row["india_production_tonnes"],
            row["import_dependency_percent"]
        ),
        fontsize=8,
        xytext=(5, 5),
        textcoords="offset points"
    )

plt.title(
    f"Production vs Import Dependency ({latest_year})"
)

plt.xlabel("India Production (tonnes)")
plt.ylabel("Import Dependency (%)")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    OUTPUT / "06_production_vs_import_dependency.png",
    dpi=300
)

plt.close()

print(
    "Saved: outputs/figures/06_production_vs_import_dependency.png"
)


# =========================================================
# 4. IMPORT DEPENDENCY BY FOOD
# =========================================================

print("\n4. CREATING CHART 7 - IMPORT DEPENDENCY BY FOOD")

dependency = (
    production_trade
    .groupby("Item")["import_dependency_percent"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(12, 7))

dependency.sort_values().plot(
    kind="barh"
)

plt.title(
    "Average Import Dependency by Food (2000–2024)"
)

plt.xlabel("Import Dependency (%)")
plt.ylabel("Food")
plt.tight_layout()

plt.savefig(
    OUTPUT / "07_import_dependency_by_food.png",
    dpi=300
)

plt.close()


print(
    "Saved: outputs/figures/07_import_dependency_by_food.png"
)


# =========================================================
# FINAL CHECK
# =========================================================

print("\n" + "=" * 70)
print("STEP 7B COMPLETE")
print("=" * 70)

print("\nCreated files:")

print("outputs/figures/04_yearly_food_miles_trend.png")
print("outputs/figures/05_top_import_source_countries.png")
print("outputs/figures/06_production_vs_import_dependency.png")
print("outputs/figures/07_import_dependency_by_food.png")

print("\n" + "=" * 70)
print("VISUALIZATION STEP 7B COMPLETE")
print("=" * 70)