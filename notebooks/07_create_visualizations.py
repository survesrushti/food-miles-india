import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# STEP 7 - RESEARCH VISUALIZATIONS
# ============================================================

PROCESSED = Path("data/processed")
OUTPUT = Path("outputs/figures")

OUTPUT.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("STEP 7 - RESEARCH VISUALIZATIONS")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD FOOD COMPARISON DATA
# ------------------------------------------------------------

print("\n1. LOADING FOOD COMPARISON DATA")

df = pd.read_csv(PROCESSED / "analysis_food_comparison.csv")

print("Rows:", len(df))
print("Foods:", df["Item"].nunique())

# ============================================================
# CHART 1 - WEIGHTED IMPORT DISTANCE
# ============================================================

print("\n2. CREATING CHART 1 - WEIGHTED IMPORT DISTANCE")

plot_df = df.sort_values(
    "weighted_import_distance_km",
    ascending=True
)

plt.figure(figsize=(12, 8))

plt.barh(
    plot_df["Item"],
    plot_df["weighted_import_distance_km"]
)

plt.xlabel("Weighted Import Distance (km)")
plt.ylabel("Food")
plt.title("Average Weighted Distance Travelled by Imported Food")

plt.tight_layout()

plt.savefig(
    OUTPUT / "01_weighted_import_distance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: outputs/figures/01_weighted_import_distance.png")


# ============================================================
# CHART 2 - TOTAL IMPORT FOOD MILES
# ============================================================

print("\n3. CREATING CHART 2 - TOTAL IMPORT FOOD MILES")

plot_df = df.sort_values(
    "import_food_miles_billion",
    ascending=True
)

plt.figure(figsize=(12, 8))

plt.barh(
    plot_df["Item"],
    plot_df["import_food_miles_billion"]
)

plt.xlabel("Import Food Miles (billion tonne-km)")
plt.ylabel("Food")
plt.title("Total Import Food Miles by Food")

plt.tight_layout()

plt.savefig(
    OUTPUT / "02_total_import_food_miles.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: outputs/figures/02_total_import_food_miles.png")


# ============================================================
# CHART 3 - IMPORT VS EXPORT FOOD MILES
# ============================================================

print("\n4. CREATING CHART 3 - IMPORT VS EXPORT FOOD MILES")

plot_df = df[
    [
        "Item",
        "import_food_miles_billion",
        "export_food_miles_billion"
    ]
].copy()

plot_df = plot_df.sort_values(
    "import_food_miles_billion",
    ascending=False
)

plt.figure(figsize=(14, 8))

x = range(len(plot_df))

width = 0.4

plt.bar(
    [i - width / 2 for i in x],
    plot_df["import_food_miles_billion"],
    width=width,
    label="Imports"
)

plt.bar(
    [i + width / 2 for i in x],
    plot_df["export_food_miles_billion"].fillna(0),
    width=width,
    label="Exports"
)

plt.xticks(
    x,
    plot_df["Item"],
    rotation=75,
    ha="right"
)

plt.xlabel("Food")
plt.ylabel("Food Miles (billion tonne-km)")
plt.title("Import vs Export Food Miles")

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT / "03_import_vs_export_food_miles.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: outputs/figures/03_import_vs_export_food_miles.png")


# ============================================================
# FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("VISUALIZATION COMPLETE")
print("=" * 70)

print("\nCreated files:")

for file in sorted(OUTPUT.glob("*.png")):
    print(file)

print("\nStep 7A complete.")