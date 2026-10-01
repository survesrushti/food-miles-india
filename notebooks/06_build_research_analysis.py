import pandas as pd
from pathlib import Path

# ============================================================
# STEP 6: RESEARCH ANALYSIS TABLES
# ============================================================

PROCESSED = Path("data/processed")

TRADE_FILE = PROCESSED / "trade_clean.csv"
DISTANCE_FILE = PROCESSED / "trade_with_distance.csv"
YEARLY_FILE = PROCESSED / "food_miles_yearly.csv"
PRODUCTION_FILE = PROCESSED / "production_clean.csv"

START_YEAR = 2000
END_YEAR = 2024

print("=" * 70)
print("STEP 6 - RESEARCH ANALYSIS")
print("=" * 70)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n1. LOADING DATA")

trade = pd.read_csv(TRADE_FILE)
trade_distance = pd.read_csv(DISTANCE_FILE)
yearly = pd.read_csv(YEARLY_FILE)
production = pd.read_csv(PRODUCTION_FILE)

print("Trade rows:", len(trade))
print("Trade + distance rows:", len(trade_distance))
print("Yearly rows:", len(yearly))
print("Production rows:", len(production))


# ============================================================
# 2. FOOD-WISE IMPORT / EXPORT COMPARISON
# ============================================================

print("\n" + "=" * 70)
print("2. FOOD-WISE IMPORT / EXPORT COMPARISON")
print("=" * 70)

valid = trade_distance[
    trade_distance["distance_km"].notna() &
    (trade_distance["distance_km"] > 0) &
    (trade_distance["Value"] > 0)
].copy()

# One common analysis period is used everywhere in the project
valid = valid[valid["Year"].between(START_YEAR, END_YEAR)].copy()

print(f"Valid rows in {START_YEAR}-{END_YEAR}:", len(valid))

imports = valid[
    valid["Element"].str.contains(
        "Import quantity",
        case=False,
        na=False
    )
].copy()

exports = valid[
    valid["Element"].str.contains(
        "Export quantity",
        case=False,
        na=False
    )
].copy()


def calculate_food_summary(data, direction):

    results = []

    for item, group in data.groupby("Item"):

        quantity = group["Value"].sum()

        weighted_distance = (
            (group["Value"] * group["distance_km"]).sum()
            / quantity
        )

        food_miles = (
            group["Value"] * group["distance_km"]
        ).sum()

        countries = group["Partner Countries"].nunique()

        results.append({
            "Item": item,
            f"{direction}_quantity_tonnes": quantity,
            f"weighted_{direction}_distance_km": weighted_distance,
            f"{direction}_food_miles": food_miles,
            f"{direction}_countries": countries
        })

    return pd.DataFrame(results)


import_summary = calculate_food_summary(
    imports,
    "import"
)

export_summary = calculate_food_summary(
    exports,
    "export"
)

food_comparison = pd.merge(
    import_summary,
    export_summary,
    on="Item",
    how="outer"
)

food_comparison["import_food_miles_billion"] = (
    food_comparison["import_food_miles"] / 1e9
)

food_comparison["export_food_miles_billion"] = (
    food_comparison["export_food_miles"] / 1e9
)

food_comparison = food_comparison.sort_values(
    "weighted_import_distance_km",
    ascending=False
)

food_comparison.to_csv(
    PROCESSED / "analysis_food_comparison.csv",
    index=False
)

print(
    "Saved:",
    PROCESSED / "analysis_food_comparison.csv"
)

print("\nTop foods by weighted import distance:")
print(
    food_comparison[
        [
            "Item",
            "weighted_import_distance_km",
            "import_quantity_tonnes",
            "import_food_miles_billion"
        ]
    ].head(10).to_string(index=False)
)


# ============================================================
# 3. TOP SOURCE COUNTRIES
# ============================================================

print("\n" + "=" * 70)
print("3. TOP SOURCE COUNTRIES")
print("=" * 70)

source_results = []

for (item, country), group in imports.groupby(
    ["Item", "Partner Countries"]
):

    quantity = group["Value"].sum()

    food_miles = (
        group["Value"] * group["distance_km"]
    ).sum()

    weighted_distance = (
        food_miles / quantity
    )

    source_results.append({
        "Item": item,
        "Country": country,
        "quantity_tonnes": quantity,
        "distance_km": weighted_distance,
        "food_miles": food_miles
    })

sources = pd.DataFrame(source_results)

# Calculate each country's share of the food's total imports
sources["share_of_food_imports"] = (
    sources.groupby("Item")["quantity_tonnes"]
    .transform(lambda x: x / x.sum() * 100)
)

sources["food_miles_billion"] = (
    sources["food_miles"] / 1e9
)

sources = sources.sort_values(
    ["Item", "quantity_tonnes"],
    ascending=[True, False]
)

sources.to_csv(
    PROCESSED / "analysis_top_sources.csv",
    index=False
)

print(
    "Saved:",
    PROCESSED / "analysis_top_sources.csv"
)

print("\nExample: top 3 sources for each food")

for item, group in sources.groupby("Item"):

    top = group.head(3)

    print(f"\n{item}:")

    for _, row in top.iterrows():

        print(
            f"  {row['Country']} | "
            f"{row['quantity_tonnes']:,.0f} tonnes | "
            f"{row['distance_km']:,.0f} km | "
            f"{row['share_of_food_imports']:.1f}%"
        )


# ============================================================
# 4. YEARLY TREND ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("4. YEARLY TREND ANALYSIS")
print("=" * 70)

trend_columns = [
    "Year",
    "Item",
    "import_quantity_tonnes",
    "weighted_import_distance_km",
    "import_food_miles",
    "import_food_miles_billion",
    "source_countries",
    "export_quantity_tonnes",
    "weighted_export_distance_km",
    "export_food_miles",
    "export_food_miles_billion",
    "destination_countries"
]

trend = yearly[
    [c for c in trend_columns if c in yearly.columns]
].copy()

trend.to_csv(
    PROCESSED / "analysis_yearly_trends.csv",
    index=False
)

print(
    "Saved:",
    PROCESSED / "analysis_yearly_trends.csv"
)


# ============================================================
# 5. PRODUCTION VS TRADE
# ============================================================

print("\n" + "=" * 70)
print("5. PRODUCTION VS TRADE")
print("=" * 70)

# Foods where production and trade use the same CPC definition.
COMPARABLE_FOODS = [
    "Almonds, in shell",
    "Apples",
    "Bananas",
    "Cashew nuts, in shell",
    "Chick peas, dry",
    "Coffee, green",
    "Grapes",
    "Hazelnuts, in shell",
    "Kiwi fruit",
    "Lentils, dry",
    "Maize (corn)",
    "Mangoes, guavas and mangosteens",
    "Palm oil",
    "Potatoes",
    "Rice",
    "Soya beans",
    "Tea leaves",
    "Tomatoes",
    "Wheat"
]

# Refined sugar is intentionally excluded because
# production data contains Sugar cane instead.
print(
    "Comparable foods:",
    len(COMPARABLE_FOODS)
)

prod = production[
    production["Item"].isin(COMPARABLE_FOODS)
].copy()

# Same analysis period as the rest of the project
prod = prod[prod["Year"].between(START_YEAR, END_YEAR)].copy()

# Remove China aggregate (M49 159)
if "Area Code (M49)" in prod.columns:

    prod = prod[
        prod["Area Code (M49)"] != 159
    ].copy()

# Remove missing and zero production
prod = prod[
    prod["Value"].notna() &
    (prod["Value"] > 0)
].copy()

# India's production
india_prod = prod[
    prod["Area"].str.contains(
        "India",
        case=False,
        na=False
    )
].copy()

india_prod = (
    india_prod
    .groupby(["Year", "Item"], as_index=False)["Value"]
    .sum()
    .rename(
        columns={
            "Value": "india_production_tonnes"
        }
    )
)

# Trade quantities (same analysis period)
trade_quantity = trade[
    trade["Element"].str.contains(
        "quantity",
        case=False,
        na=False
    )
].copy()

trade_quantity = trade_quantity[
    trade_quantity["Year"].between(START_YEAR, END_YEAR)
].copy()

trade_quantity = trade_quantity[
    trade_quantity["Item"].isin(COMPARABLE_FOODS)
].copy()

trade_quantity = (
    trade_quantity
    .groupby(
        ["Year", "Item", "Element"],
        as_index=False
    )["Value"]
    .sum()
)

trade_pivot = trade_quantity.pivot_table(
    index=["Year", "Item"],
    columns="Element",
    values="Value",
    aggfunc="sum"
).reset_index()

trade_pivot.columns.name = None

# Rename trade columns
rename_map = {}

for col in trade_pivot.columns:

    if "Import quantity" in str(col):
        rename_map[col] = "import_quantity_tonnes"

    if "Export quantity" in str(col):
        rename_map[col] = "export_quantity_tonnes"

trade_pivot = trade_pivot.rename(
    columns=rename_map
)

production_trade = india_prod.merge(
    trade_pivot,
    on=["Year", "Item"],
    how="left"
)

# Import dependency:
# Imports / (Domestic production + imports - exports)
production_trade["domestic_supply_available_tonnes"] = (
    production_trade["india_production_tonnes"]
    + production_trade["import_quantity_tonnes"].fillna(0)
    - production_trade["export_quantity_tonnes"].fillna(0)
)

production_trade["import_dependency_percent"] = (
    production_trade["import_quantity_tonnes"].fillna(0)
    / production_trade["domestic_supply_available_tonnes"]
    * 100
)

production_trade.to_csv(
    PROCESSED / "analysis_production_trade.csv",
    index=False
)

print(
    "Saved:",
    PROCESSED / "analysis_production_trade.csv"
)

print(
    "\nProduction vs trade rows:",
    len(production_trade)
)

print("\nSample:")
print(
    production_trade.head(15).to_string(
        index=False
    )
)


# ============================================================
# 6. KEY RESEARCH SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("6. KEY RESEARCH SUMMARY")
print("=" * 70)

# Highest import-distance foods
top_distance = food_comparison.dropna(
    subset=["weighted_import_distance_km"]
).head(5)

print("\nFoods with highest weighted import distance:")

for _, row in top_distance.iterrows():

    print(
        f"{row['Item']}: "
        f"{row['weighted_import_distance_km']:,.0f} km"
    )


# Highest total import Food Miles
top_food_miles = food_comparison.sort_values(
    "import_food_miles",
    ascending=False
).head(5)

print("\nFoods with highest total import Food Miles:")

for _, row in top_food_miles.iterrows():

    print(
        f"{row['Item']}: "
        f"{row['import_food_miles_billion']:.2f} "
        f"billion tonne-km"
    )


# Most diverse import sources
top_sources = food_comparison.sort_values(
    "import_countries",
    ascending=False
).head(5)

print("\nFoods with most source countries:")

for _, row in top_sources.iterrows():

    print(
        f"{row['Item']}: "
        f"{int(row['import_countries'])} countries"
    )

print(
    "\nNOTE: these printed rankings include foods with very small "
    "import volumes. Script 09 applies the low-volume filter."
)


# ============================================================
# 7. FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("FINAL CHECK")
print("=" * 70)

print(
    "Food comparison rows:",
    len(food_comparison)
)

print(
    "Source analysis rows:",
    len(sources)
)

print(
    "Yearly trend rows:",
    len(trend)
)

print(
    "Production/trade rows:",
    len(production_trade)
)

print("\nCreated files:")

print("1.", PROCESSED / "analysis_food_comparison.csv")
print("2.", PROCESSED / "analysis_top_sources.csv")
print("3.", PROCESSED / "analysis_yearly_trends.csv")
print("4.", PROCESSED / "analysis_production_trade.csv")

print("\n" + "=" * 70)
print("STEP 6 COMPLETE")
print("=" * 70)