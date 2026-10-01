import pandas as pd
from pathlib import Path

PROCESSED = Path("data/processed")

TRADE_FILE = PROCESSED / "trade_with_distance.csv"

OUTPUT_SUMMARY = PROCESSED / "food_miles_summary.csv"
OUTPUT_PARTNERS = PROCESSED / "food_miles_by_partner.csv"

START_YEAR = 2000
END_YEAR = 2024


print("=" * 70)
print("FOOD MILES ANALYSIS")
print("=" * 70)


# ---------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------

print("\n1. LOADING TRADE DATA")

df = pd.read_csv(TRADE_FILE)

print("Trade rows (all years):", len(df))
print("Foods:", df["Item"].nunique())
print("Partners:", df["Partner Countries"].nunique())
print("Years in file:", df["Year"].min(), "to", df["Year"].max())


# ---------------------------------------------------------
# 2. COMMON ANALYSIS PERIOD + VALID DISTANCES
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("2. FILTERING ANALYSIS PERIOD AND VALID DISTANCES")
print("=" * 70)

# One common analysis period is used everywhere in the project
df = df[df["Year"].between(START_YEAR, END_YEAR)].copy()

print(f"Rows in {START_YEAR}-{END_YEAR}:", len(df))

before = len(df)

df = df.dropna(subset=["distance_km"]).copy()

print("Rows before distance filter:", before)
print("Rows with distance:", len(df))
print("Rows excluded (no distance):", before - len(df))


# ---------------------------------------------------------
# 3. SEPARATE IMPORTS AND EXPORTS
# ---------------------------------------------------------

imports = df[
    df["Element"].str.lower() == "import quantity"
].copy()

exports = df[
    df["Element"].str.lower() == "export quantity"
].copy()

print("\nImport quantity rows:", len(imports))
print("Export quantity rows:", len(exports))


# ---------------------------------------------------------
# 4. CALCULATE FOOD MILES
# ---------------------------------------------------------

imports["food_miles"] = (
    imports["Value"] * imports["distance_km"]
)

exports["food_miles"] = (
    exports["Value"] * exports["distance_km"]
)


# ---------------------------------------------------------
# 5. FOOD-WISE IMPORT ANALYSIS
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("3. FOOD-WISE IMPORT ANALYSIS")
print("=" * 70)

import_summary = (
    imports.groupby("Item")
    .agg(
        import_quantity_tonnes=("Value", "sum"),
        import_food_miles=("food_miles", "sum"),
        source_countries=("Partner Countries", "nunique")
    )
    .reset_index()
)

import_summary["weighted_import_distance_km"] = (
    import_summary["import_food_miles"]
    / import_summary["import_quantity_tonnes"]
)

import_summary = import_summary[
    [
        "Item",
        "import_quantity_tonnes",
        "weighted_import_distance_km",
        "import_food_miles",
        "source_countries"
    ]
]


print(
    import_summary
    .sort_values("weighted_import_distance_km", ascending=False)
    .round(2)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 6. FOOD-WISE EXPORT ANALYSIS
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("4. FOOD-WISE EXPORT ANALYSIS")
print("=" * 70)

export_summary = (
    exports.groupby("Item")
    .agg(
        export_quantity_tonnes=("Value", "sum"),
        export_food_miles=("food_miles", "sum"),
        destination_countries=("Partner Countries", "nunique")
    )
    .reset_index()
)

export_summary["weighted_export_distance_km"] = (
    export_summary["export_food_miles"]
    / export_summary["export_quantity_tonnes"]
)

export_summary = export_summary[
    [
        "Item",
        "export_quantity_tonnes",
        "weighted_export_distance_km",
        "export_food_miles",
        "destination_countries"
    ]
]


print(
    export_summary
    .sort_values("weighted_export_distance_km", ascending=False)
    .round(2)
    .to_string(index=False)
)


# ---------------------------------------------------------
# 7. COMBINE IMPORT + EXPORT RESULTS
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("5. COMBINING RESULTS")
print("=" * 70)

summary = import_summary.merge(
    export_summary,
    on="Item",
    how="outer"
)


# ---------------------------------------------------------
# 8. SAVE SUMMARY
# ---------------------------------------------------------

summary.to_csv(
    OUTPUT_SUMMARY,
    index=False
)

print("Saved:", OUTPUT_SUMMARY)
print("Rows:", len(summary))


# ---------------------------------------------------------
# 9. FOOD-WISE PARTNER ANALYSIS
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("6. FOOD-WISE PARTNER ANALYSIS")
print("=" * 70)

partner = (
    imports.groupby(
        ["Item", "Partner Countries", "iso3"]
    )
    .agg(
        quantity_tonnes=("Value", "sum"),
        distance_km=("distance_km", "first")
    )
    .reset_index()
)

partner["food_miles"] = (
    partner["quantity_tonnes"]
    * partner["distance_km"]
)

partner["share_of_food_imports_pct"] = (
    partner.groupby("Item")["quantity_tonnes"]
    .transform("sum")
)

partner["share_of_food_imports_pct"] = (
    partner["quantity_tonnes"]
    / partner["share_of_food_imports_pct"]
    * 100
)

partner = partner.sort_values(
    ["Item", "quantity_tonnes"],
    ascending=[True, False]
)

partner.to_csv(
    OUTPUT_PARTNERS,
    index=False
)

print("Saved:", OUTPUT_PARTNERS)
print("Rows:", len(partner))


# ---------------------------------------------------------
# 10. TOP IMPORT SOURCES FOR EACH FOOD
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("7. TOP 3 IMPORT SOURCES FOR EACH FOOD")
print("=" * 70)

for item, group in partner.groupby("Item"):

    top = group.head(3)

    print(f"\n{item}:")

    for _, row in top.iterrows():

        print(
            f"  {row['Partner Countries']} | "
            f"{row['quantity_tonnes']:,.0f} tonnes | "
            f"{row['distance_km']:,.0f} km | "
            f"{row['share_of_food_imports_pct']:.1f}%"
        )


# ---------------------------------------------------------
# 11. OVERALL CHECK
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("8. FINAL CHECK")
print("=" * 70)

print("Analysis period:", START_YEAR, "to", END_YEAR)
print("Foods in summary:", summary["Item"].nunique())

print(
    "Highest weighted import distance:",
    import_summary.loc[
        import_summary["weighted_import_distance_km"].idxmax(),
        "Item"
    ]
)

print(
    "Lowest weighted import distance:",
    import_summary.loc[
        import_summary["weighted_import_distance_km"].idxmin(),
        "Item"
    ]
)

print("\n" + "=" * 70)
print("FOOD MILES ANALYSIS COMPLETE")
print("=" * 70)