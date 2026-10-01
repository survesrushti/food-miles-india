import pandas as pd
import json
from pathlib import Path

print("=" * 70)
print("STEP 8A - PREPARING DASHBOARD DATA")
print("=" * 70)

# ------------------------------------------------------------
# PATHS AND SETTINGS
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED = BASE_DIR / "data" / "processed"

FOOD_COMPARISON = PROCESSED / "analysis_food_comparison.csv"
TOP_SOURCES = PROCESSED / "analysis_top_sources.csv"
PRODUCTION_TRADE = PROCESSED / "analysis_production_trade.csv"
YEARLY_TRENDS = PROCESSED / "analysis_yearly_trends.csv"
FOOD_MILES_SUMMARY = PROCESSED / "food_miles_summary.csv"
TRADE_DISTANCE = PROCESSED / "trade_with_distance.csv"

OUTPUT_DATA = PROCESSED / "dashboard_food_data.csv"
OUTPUT_METADATA = PROCESSED / "dashboard_metadata.json"

START_YEAR = 2000
END_YEAR = 2024

# Foods with fewer imports than this (tonnes, whole period) are flagged
LOW_VOLUME_TONNES = 10000


# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

print("\n1. LOADING RESEARCH DATA")

food = pd.read_csv(FOOD_COMPARISON)
sources = pd.read_csv(TOP_SOURCES)
production = pd.read_csv(PRODUCTION_TRADE)
yearly = pd.read_csv(YEARLY_TRENDS)

print("Food comparison rows:", len(food))
print("Top source rows:", len(sources))
print("Production/trade rows:", len(production))
print("Yearly trend rows:", len(yearly))


# ------------------------------------------------------------
# 2. PREPARE FOOD COMPARISON DATA
# ------------------------------------------------------------

print("\n2. PREPARING FOOD-WISE DATA")

dashboard = food.copy()

dashboard = dashboard.rename(columns={
    "Item": "Food"
})

print("Available columns:")
print(dashboard.columns.tolist())


# ------------------------------------------------------------
# 3. ADD SOURCE / DESTINATION COUNTRY COUNTS
# ------------------------------------------------------------

print("\n3. CALCULATING COUNTRY COUNTS")

source_counts = (
    sources.groupby("Item")["Country"]
    .nunique()
    .reset_index()
)

source_counts.columns = [
    "Food",
    "source_countries"
]

dashboard = dashboard.merge(
    source_counts,
    on="Food",
    how="left"
)

# Destination countries come from the food-miles summary (script 04)

if FOOD_MILES_SUMMARY.exists():

    summary = pd.read_csv(FOOD_MILES_SUMMARY)

    summary = summary.rename(columns={
        "Item": "Food"
    })

    if "destination_countries" in summary.columns:

        dashboard = dashboard.merge(
            summary[
                [
                    "Food",
                    "destination_countries"
                ]
            ],
            on="Food",
            how="left"
        )

    else:
        dashboard["destination_countries"] = pd.NA

else:
    dashboard["destination_countries"] = pd.NA


# ------------------------------------------------------------
# 4. PRODUCTION / IMPORT DEPENDENCY (POOLED, 2000-2024)
# ------------------------------------------------------------

print("\n4. ADDING PRODUCTION AND IMPORT DEPENDENCY")

production_temp = production.copy()

production_temp["import_quantity_tonnes"] = (
    pd.to_numeric(
        production_temp["import_quantity_tonnes"],
        errors="coerce"
    ).fillna(0)
)

production_temp["export_quantity_tonnes"] = (
    pd.to_numeric(
        production_temp["export_quantity_tonnes"],
        errors="coerce"
    ).fillna(0)
)

production_temp["india_production_tonnes"] = (
    pd.to_numeric(
        production_temp["india_production_tonnes"],
        errors="coerce"
    )
)

food_dependency = (
    production_temp
    .groupby("Item", as_index=False)
    .agg(
        india_production_tonnes=("india_production_tonnes", "sum"),
        import_quantity_tonnes=("import_quantity_tonnes", "sum"),
        export_quantity_tonnes=("export_quantity_tonnes", "sum"),
        years=("Year", "nunique"),
    )
)

food_dependency["domestic_supply_available_tonnes"] = (
    food_dependency["india_production_tonnes"]
    + food_dependency["import_quantity_tonnes"]
    - food_dependency["export_quantity_tonnes"]
)

# Only positive supply gives a meaningful ratio
supply = food_dependency["domestic_supply_available_tonnes"].where(
    food_dependency["domestic_supply_available_tonnes"] > 0
)

# Pooled ratio: total imports / total domestic supply
food_dependency["import_dependency_percent"] = (
    food_dependency["import_quantity_tonnes"] / supply * 100
)

# Average ANNUAL values, so production, imports and exports are comparable
food_dependency["avg_annual_production_tonnes"] = (
    food_dependency["india_production_tonnes"] / food_dependency["years"]
)

food_dependency["avg_annual_imports_tonnes"] = (
    food_dependency["import_quantity_tonnes"] / food_dependency["years"]
)

food_dependency["avg_annual_exports_tonnes"] = (
    food_dependency["export_quantity_tonnes"] / food_dependency["years"]
)

food_dependency = food_dependency.rename(columns={
    "Item": "Food"
})


# ------------------------------------------------------------
# 5. MERGE PRODUCTION DATA
# ------------------------------------------------------------

print("\n5. MERGING PRODUCTION DATA")

dashboard = dashboard.merge(
    food_dependency[
        [
            "Food",
            "avg_annual_production_tonnes",
            "avg_annual_imports_tonnes",
            "avg_annual_exports_tonnes",
            "import_dependency_percent",
        ]
    ],
    on="Food",
    how="left",
)

# Keep the old column name so app.py needs fewer changes.
# NOTE: this column now means AVERAGE ANNUAL production.
dashboard = dashboard.rename(
    columns={"avg_annual_production_tonnes": "india_production_tonnes"}
)


# ------------------------------------------------------------
# 6. SELECT FINAL DASHBOARD COLUMNS
# ------------------------------------------------------------

print("\n6. PREPARING FINAL DASHBOARD COLUMNS")

columns = [
    "Food",
    "import_quantity_tonnes",
    "weighted_import_distance_km",
    "import_food_miles_billion",
    "source_countries",
    "export_quantity_tonnes",
    "weighted_export_distance_km",
    "export_food_miles_billion",
    "destination_countries",
    "india_production_tonnes",
    "avg_annual_imports_tonnes",
    "avg_annual_exports_tonnes",
    "import_dependency_percent"
]

dashboard = dashboard[columns]


# ------------------------------------------------------------
# 7. CLEAN NUMERIC VALUES + LOW-VOLUME FLAG
# ------------------------------------------------------------

print("\n7. CLEANING NUMERIC VALUES")

numeric_columns = [
    "import_quantity_tonnes",
    "weighted_import_distance_km",
    "import_food_miles_billion",
    "export_quantity_tonnes",
    "weighted_export_distance_km",
    "export_food_miles_billion",
    "india_production_tonnes",
    "avg_annual_imports_tonnes",
    "avg_annual_exports_tonnes",
    "import_dependency_percent"
]

for column in numeric_columns:

    dashboard[column] = pd.to_numeric(
        dashboard[column],
        errors="coerce"
    )


dashboard["weighted_import_distance_km"] = (
    dashboard["weighted_import_distance_km"].round(2)
)

dashboard["weighted_export_distance_km"] = (
    dashboard["weighted_export_distance_km"].round(2)
)

dashboard["import_food_miles_billion"] = (
    dashboard["import_food_miles_billion"].round(3)
)

dashboard["export_food_miles_billion"] = (
    dashboard["export_food_miles_billion"].round(3)
)

dashboard["import_dependency_percent"] = (
    dashboard["import_dependency_percent"].round(2)
)

for column in [
    "india_production_tonnes",
    "avg_annual_imports_tonnes",
    "avg_annual_exports_tonnes"
]:
    dashboard[column] = dashboard[column].round(0)

# Foods with very small imports should not drive rankings or conclusions
dashboard["low_import_volume"] = (
    dashboard["import_quantity_tonnes"] < LOW_VOLUME_TONNES
)


# ------------------------------------------------------------
# 8. SORT DATA
# ------------------------------------------------------------

dashboard = dashboard.sort_values(
    "Food"
).reset_index(drop=True)


# ------------------------------------------------------------
# 9. SAVE DASHBOARD DATA
# ------------------------------------------------------------

dashboard.to_csv(
    OUTPUT_DATA,
    index=False
)

print("\nSaved:")
print(OUTPUT_DATA)

print("Dashboard rows:", len(dashboard))
print("Dashboard columns:", len(dashboard.columns))


# ------------------------------------------------------------
# 10. CREATE METADATA
# ------------------------------------------------------------

print("\n8. CREATING DASHBOARD METADATA")

# Number of distinct trade partners with a valid distance (imports + exports)
trade_distance = pd.read_csv(TRADE_DISTANCE)

trade_distance = trade_distance[
    trade_distance["Year"].between(START_YEAR, END_YEAR)
    & trade_distance["distance_km"].notna()
    & (trade_distance["Value"] > 0)
]

trade_partners = int(trade_distance["Partner Countries"].nunique())

print("Trade partners with valid distance:", trade_partners)

metadata = {
    "project_title": "Food Miles: Tracking the Journey of Food",

    "analysis_period": {
        "start_year": START_YEAR,
        "end_year": END_YEAR
    },

    "total_foods": int(
        dashboard["Food"].nunique()
    ),

    "foods": dashboard["Food"].tolist(),

    "trade_partners": trade_partners,

    "low_volume_threshold_tonnes": LOW_VOLUME_TONNES,

    "low_volume_foods": dashboard.loc[
        dashboard["low_import_volume"], "Food"
    ].tolist(),

    "units": {
        "distance": "km",
        "quantity": "tonnes",
        "food_miles": "billion tonne-km"
    },

    "description": (
        "Dashboard data prepared from cleaned trade, "
        "production, distance and research analysis datasets."
    )
}

with open(
    OUTPUT_METADATA,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metadata,
        file,
        indent=4,
        ensure_ascii=False
    )

print("Saved:")
print(OUTPUT_METADATA)


# ------------------------------------------------------------
# 11. DISPLAY SAMPLE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("DASHBOARD DATA SAMPLE")
print("=" * 70)

print(
    dashboard[
        [
            "Food",
            "weighted_import_distance_km",
            "import_food_miles_billion",
            "source_countries",
            "import_dependency_percent",
            "low_import_volume"
        ]
    ]
    .to_string(index=False)
)


# ------------------------------------------------------------
# 12. FINAL CHECK
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL CHECK")
print("=" * 70)

print("Foods:", dashboard["Food"].nunique())
print("Rows:", len(dashboard))

print("\nColumns:")
print(dashboard.columns.tolist())

print("\nMissing values:")
print(
    dashboard.isna().sum().to_string()
)

print(
    "\nFoods with no production/dependency value:",
    dashboard.loc[
        dashboard["import_dependency_percent"].isna(), "Food"
    ].tolist()
)

print(
    "Low-volume foods:",
    dashboard.loc[dashboard["low_import_volume"], "Food"].tolist()
)

print("\n" + "=" * 70)
print("STEP 8A COMPLETE")
print("=" * 70)