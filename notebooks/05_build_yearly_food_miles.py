import pandas as pd
from pathlib import Path

# ============================================================
# STEP 5: YEAR-WISE FOOD MILES ANALYSIS
# ============================================================

print("=" * 70)
print("YEAR-WISE FOOD MILES ANALYSIS")
print("=" * 70)

PROCESSED = Path("data/processed")

INPUT_FILE = PROCESSED / "trade_with_distance.csv"
OUTPUT_FILE = PROCESSED / "food_miles_yearly.csv"

START_YEAR = 2000
END_YEAR = 2024


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n1. LOADING TRADE DATA")

df = pd.read_csv(INPUT_FILE)

print("Trade rows:", len(df))
print("Foods:", df["Item"].nunique())
print("Years:", df["Year"].min(), "to", df["Year"].max())


# ============================================================
# 2. FILTER ANALYSIS PERIOD
# ============================================================

print("\n" + "=" * 70)
print("2. FILTERING COMMON ANALYSIS PERIOD")
print("=" * 70)

df = df[
    (df["Year"] >= START_YEAR) &
    (df["Year"] <= END_YEAR)
].copy()

print("Analysis period:", START_YEAR, "to", END_YEAR)
print("Rows:", len(df))
print("Foods:", df["Item"].nunique())
print("Years:", df["Year"].min(), "to", df["Year"].max())


# ============================================================
# 3. KEEP VALID DISTANCE DATA
# ============================================================

print("\n" + "=" * 70)
print("3. FILTERING VALID DISTANCES")
print("=" * 70)

before = len(df)

df = df[
    df["distance_km"].notna() &
    (df["distance_km"] > 0)
].copy()

print("Rows before:", before)
print("Rows with valid distance:", len(df))
print("Rows excluded:", before - len(df))


# ============================================================
# 4. SEPARATE IMPORTS AND EXPORTS
# ============================================================

imports = df[
    df["Element"].str.contains("Import quantity", case=False, na=False)
].copy()

exports = df[
    df["Element"].str.contains("Export quantity", case=False, na=False)
].copy()

print("\nImport quantity rows:", len(imports))
print("Export quantity rows:", len(exports))


# ============================================================
# 5. YEAR-WISE IMPORT FOOD MILES
# ============================================================

print("\n" + "=" * 70)
print("4. YEAR-WISE IMPORT FOOD MILES")
print("=" * 70)

import_results = []

for (year, item), group in imports.groupby(["Year", "Item"]):

    # Remove zero/negative quantities
    group = group[group["Value"] > 0].copy()

    if group.empty:
        continue

    quantity = group["Value"].sum()

    weighted_distance = (
        (group["Value"] * group["distance_km"]).sum()
        / quantity
    )

    food_miles = (
        group["Value"] * group["distance_km"]
    ).sum()

    source_countries = group["Partner Countries"].nunique()

    import_results.append({
        "Year": year,
        "Item": item,
        "import_quantity_tonnes": quantity,
        "weighted_import_distance_km": weighted_distance,
        "import_food_miles": food_miles,
        "source_countries": source_countries
    })

import_yearly = pd.DataFrame(import_results)

print("Import yearly rows:", len(import_yearly))


# ============================================================
# 6. YEAR-WISE EXPORT FOOD MILES
# ============================================================

print("\n" + "=" * 70)
print("5. YEAR-WISE EXPORT FOOD MILES")
print("=" * 70)

export_results = []

for (year, item), group in exports.groupby(["Year", "Item"]):

    # Remove zero/negative quantities
    group = group[group["Value"] > 0].copy()

    if group.empty:
        continue

    quantity = group["Value"].sum()

    weighted_distance = (
        (group["Value"] * group["distance_km"]).sum()
        / quantity
    )

    food_miles = (
        group["Value"] * group["distance_km"]
    ).sum()

    destination_countries = group["Partner Countries"].nunique()

    export_results.append({
        "Year": year,
        "Item": item,
        "export_quantity_tonnes": quantity,
        "weighted_export_distance_km": weighted_distance,
        "export_food_miles": food_miles,
        "destination_countries": destination_countries
    })

export_yearly = pd.DataFrame(export_results)

print("Export yearly rows:", len(export_yearly))


# ============================================================
# 7. COMBINE IMPORT AND EXPORT RESULTS
# ============================================================

print("\n" + "=" * 70)
print("6. COMBINING RESULTS")
print("=" * 70)

yearly = pd.merge(
    import_yearly,
    export_yearly,
    on=["Year", "Item"],
    how="outer"
)

# Sort the data
yearly = yearly.sort_values(
    ["Year", "Item"]
).reset_index(drop=True)


# ============================================================
# 8. ADD BILLION TONNE-KM
# ============================================================

yearly["import_food_miles_billion"] = (
    yearly["import_food_miles"] / 1e9
)

yearly["export_food_miles_billion"] = (
    yearly["export_food_miles"] / 1e9
)


# ============================================================
# 9. SAVE DATA
# ============================================================

yearly.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Saved:", OUTPUT_FILE)
print("Rows:", len(yearly))
print("Columns:", len(yearly.columns))


# ============================================================
# 10. SUMMARY CHECK
# ============================================================

print("\n" + "=" * 70)
print("7. SUMMARY CHECK")
print("=" * 70)

print("Years:", yearly["Year"].min(), "to", yearly["Year"].max())
print("Foods:", yearly["Item"].nunique())

print("\nFoods included:")
print(sorted(yearly["Item"].unique()))


# ============================================================
# 11. TOP FOOD MILES BY YEAR
# ============================================================

print("\n" + "=" * 70)
print("8. HIGHEST IMPORT FOOD MILES BY YEAR")
print("=" * 70)

for year in sorted(yearly["Year"].dropna().unique()):

    data = yearly[
        yearly["Year"] == year
    ].dropna(subset=["import_food_miles"])

    if data.empty:
        continue

    top = data.loc[
        data["import_food_miles"].idxmax()
    ]

    print(
        f"{int(year)}: "
        f"{top['Item']} | "
        f"{top['import_food_miles_billion']:.2f} billion tonne-km"
    )


# ============================================================
# 12. FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("9. FINAL CHECK")
print("=" * 70)

print(
    "Expected maximum possible rows:",
    25 * 20,
    "(25 years × 20 foods)"
)

print("Actual rows:", len(yearly))

print("\nFirst 10 rows:")
print(yearly.head(10).to_string(index=False))

print("\n" + "=" * 70)
print("YEAR-WISE FOOD MILES ANALYSIS COMPLETE")
print("=" * 70)