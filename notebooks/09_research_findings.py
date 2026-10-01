import pandas as pd
import json
from pathlib import Path


# ============================================================
# STEP 9A - RESEARCH FINDINGS
# ============================================================

print("=" * 70)
print("STEP 9A - RESEARCH FINDINGS")
print("=" * 70)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED = BASE_DIR / "data" / "processed"

FOOD_COMPARISON = PROCESSED / "analysis_food_comparison.csv"
TOP_SOURCES = PROCESSED / "analysis_top_sources.csv"
YEARLY = PROCESSED / "analysis_yearly_trends.csv"
PRODUCTION_TRADE = PROCESSED / "analysis_production_trade.csv"

# Foods with fewer imports than this (tonnes, 2000-2024) are not ranked.
MIN_IMPORT_TONNES = 10000


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n1. LOADING RESEARCH DATA")

food = pd.read_csv(FOOD_COMPARISON)
sources = pd.read_csv(TOP_SOURCES)
yearly = pd.read_csv(YEARLY)
production_trade = pd.read_csv(PRODUCTION_TRADE)

print("Food comparison rows:", len(food))
print("Source rows:", len(sources))
print("Yearly rows:", len(yearly))
print("Production/trade rows:", len(production_trade))


# ============================================================
# 2. STANDARDIZE COLUMN NAMES + LOW-VOLUME FILTER
# ============================================================

food["Item"] = food["Item"].astype(str)
sources["Item"] = sources["Item"].astype(str)

# Ignore negligible trade volumes in rankings
ranked = food[food["import_quantity_tonnes"] >= MIN_IMPORT_TONNES].copy()

excluded = sorted(set(food["Item"]) - set(ranked["Item"]))

print(f"\nFoods with enough import volume for rankings: {len(ranked)}")
print(f"Excluded from rankings (imports below {MIN_IMPORT_TONNES:,} tonnes): {excluded}")


# ============================================================
# 3. FINDINGS - WEIGHTED IMPORT DISTANCE
# ============================================================

print("\n2. WEIGHTED IMPORT DISTANCE")

distance_data = ranked[
    [
        "Item",
        "weighted_import_distance_km"
    ]
].dropna()

distance_data = distance_data.sort_values(
    "weighted_import_distance_km",
    ascending=False
)

top_distance = distance_data.head(5)

print("\nTop 5 foods by weighted import distance:")

for _, row in top_distance.iterrows():
    print(
        f"{row['Item']}: "
        f"{row['weighted_import_distance_km']:,.0f} km"
    )


# ============================================================
# 4. FINDINGS - TOTAL FOOD MILES
# ============================================================

print("\n3. TOTAL IMPORT FOOD MILES")

food_miles = ranked[
    [
        "Item",
        "import_food_miles_billion"
    ]
].dropna()

food_miles = food_miles.sort_values(
    "import_food_miles_billion",
    ascending=False
)

top_food_miles = food_miles.head(5)

print("\nTop 5 foods by total import Food Miles:")

for _, row in top_food_miles.iterrows():
    print(
        f"{row['Item']}: "
        f"{row['import_food_miles_billion']:,.2f} "
        f"billion tonne-km"
    )


# ============================================================
# 5. FINDINGS - SOURCE COUNTRY DIVERSITY
# ============================================================

print("\n4. SOURCE COUNTRY DIVERSITY")

source_data = ranked[
    [
        "Item",
        "import_countries"
    ]
].dropna()

source_data = source_data.sort_values(
    "import_countries",
    ascending=False
)

top_sources = source_data.head(5)

print("\nTop 5 foods by number of source countries:")

for _, row in top_sources.iterrows():
    print(
        f"{row['Item']}: "
        f"{int(row['import_countries'])} countries"
    )


# ============================================================
# 6. IMPORT DEPENDENCY (POOLED, 2000-2024)
# ============================================================

print("\n5. IMPORT DEPENDENCY")

# Pooled import dependency:
# total imports / (total production + total imports - total exports)
pooled = (
    production_trade
    .groupby("Item")
    .agg(
        production=("india_production_tonnes", "sum"),
        imports=("import_quantity_tonnes", lambda s: s.fillna(0).sum()),
        exports=("export_quantity_tonnes", lambda s: s.fillna(0).sum()),
    )
    .reset_index()
)

pooled["supply"] = (
    pooled["production"] + pooled["imports"] - pooled["exports"]
)

pooled = pooled[pooled["supply"] > 0].copy()

pooled["import_dependency_percent"] = (
    pooled["imports"] / pooled["supply"] * 100
)

dependency = pooled[
    ["Item", "import_dependency_percent"]
].dropna()

dependency = dependency[
    dependency["Item"].isin(ranked["Item"])
]

dependency = dependency.sort_values(
    "import_dependency_percent",
    ascending=False
)

top_dependency = dependency.head(5)

print("\nFoods with highest import dependency (2000-2024, pooled):")

for _, row in top_dependency.iterrows():
    print(
        f"{row['Item']}: "
        f"{row['import_dependency_percent']:.2f}%"
    )

no_dependency = sorted(set(food["Item"]) - set(pooled["Item"]))
print("\nFoods with no dependency value (no India production row):", no_dependency)


# ============================================================
# 7. YEARLY FOOD MILES
# ============================================================

print("\n6. YEARLY FOOD MILES")

yearly_import = yearly[
    [
        "Year",
        "import_food_miles_billion"
    ]
].dropna()

yearly_import = yearly_import.groupby("Year")[
    "import_food_miles_billion"
].sum().reset_index()

yearly_import = yearly_import.sort_values("Year")

first_year = yearly_import.iloc[0]
last_year = yearly_import.iloc[-1]

print(
    f"\nTotal import Food Miles in "
    f"{int(first_year['Year'])}: "
    f"{first_year['import_food_miles_billion']:,.2f} billion tonne-km"
)

print(
    f"Total import Food Miles in "
    f"{int(last_year['Year'])}: "
    f"{last_year['import_food_miles_billion']:,.2f} billion tonne-km"
)

# Is the rise driven by palm oil volume?
palm = (
    yearly[yearly["Item"] == "Palm oil"]
    .groupby("Year")["import_food_miles_billion"]
    .sum()
)

first_total = float(first_year["import_food_miles_billion"])
last_total = float(last_year["import_food_miles_billion"])

palm_first = float(palm.get(int(first_year["Year"]), 0))
palm_last = float(palm.get(int(last_year["Year"]), 0))

palm_share_first = palm_first / first_total * 100 if first_total else 0
palm_share_last = palm_last / last_total * 100 if last_total else 0

print(
    f"Palm oil share of import Food Miles: "
    f"{palm_share_first:.1f}% in {int(first_year['Year'])}, "
    f"{palm_share_last:.1f}% in {int(last_year['Year'])}"
)

print(
    f"Total excluding palm oil: "
    f"{first_total - palm_first:,.2f} -> "
    f"{last_total - palm_last:,.2f} billion tonne-km"
)


# ============================================================
# 8. CREATE FINDINGS TABLE
# ============================================================

print("\n7. CREATING FINDINGS TABLE")

findings = []

for _, row in top_distance.iterrows():

    findings.append({
        "finding_type": "Highest weighted import distance",
        "food": row["Item"],
        "value": round(
            row["weighted_import_distance_km"], 2
        ),
        "unit": "km"
    })


for _, row in top_food_miles.iterrows():

    findings.append({
        "finding_type": "Highest total import Food Miles",
        "food": row["Item"],
        "value": round(
            row["import_food_miles_billion"], 3
        ),
        "unit": "billion tonne-km"
    })


for _, row in top_sources.iterrows():

    findings.append({
        "finding_type": "Most source countries",
        "food": row["Item"],
        "value": int(row["import_countries"]),
        "unit": "countries"
    })


for _, row in top_dependency.iterrows():

    findings.append({
        "finding_type": "Highest average import dependency",
        "food": row["Item"],
        "value": round(
            row["import_dependency_percent"], 2
        ),
        "unit": "%"
    })


findings_df = pd.DataFrame(findings)

FINDINGS_FILE = PROCESSED / "research_findings.csv"

findings_df.to_csv(
    FINDINGS_FILE,
    index=False
)

print("Saved:")
print(FINDINGS_FILE)


# ============================================================
# 9. CREATE RESEARCH SUMMARY
# ============================================================

print("\n8. CREATING RESEARCH SUMMARY")

summary = {
    "project": "Food Miles: Tracking the Journey of Food",

    "analysis_period": "2000-2024",

    "foods_analysed": int(food["Item"].nunique()),

    "minimum_import_tonnes_for_rankings": MIN_IMPORT_TONNES,

    "foods_excluded_from_rankings": excluded,

    "highest_weighted_import_distance": {
        "food": top_distance.iloc[0]["Item"],
        "distance_km": round(
            top_distance.iloc[0]["weighted_import_distance_km"],
            2
        )
    },

    "highest_total_import_food_miles": {
        "food": top_food_miles.iloc[0]["Item"],
        "food_miles_billion_tonne_km": round(
            top_food_miles.iloc[0]["import_food_miles_billion"],
            3
        )
    },

    "most_source_countries": {
        "food": top_sources.iloc[0]["Item"],
        "countries": int(
            top_sources.iloc[0]["import_countries"]
        )
    },

    "highest_average_import_dependency": {
        "food": top_dependency.iloc[0]["Item"],
        "percentage": round(
            top_dependency.iloc[0]["import_dependency_percent"],
            2
        )
    },

    "palm_oil_effect": {
        "share_first_year_pct": round(palm_share_first, 1),
        "share_last_year_pct": round(palm_share_last, 1),
        "total_excl_palm_first": round(first_total - palm_first, 3),
        "total_excl_palm_last": round(last_total - palm_last, 3)
    },

    "yearly_food_miles": {
        "first_year": int(first_year["Year"]),
        "first_year_billion_tonne_km": round(
            first_year["import_food_miles_billion"],
            3
        ),
        "last_year": int(last_year["Year"]),
        "last_year_billion_tonne_km": round(
            last_year["import_food_miles_billion"],
            3
        )
    }
}


SUMMARY_FILE = PROCESSED / "research_summary.json"

with open(
    SUMMARY_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        summary,
        file,
        indent=4,
        ensure_ascii=False
    )


print("Saved:")
print(SUMMARY_FILE)


# ============================================================
# 10. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("KEY RESEARCH FINDINGS")
print("=" * 70)

print("\nHighest weighted import distance:")

print(
    f"{top_distance.iloc[0]['Item']} - "
    f"{top_distance.iloc[0]['weighted_import_distance_km']:,.0f} km"
)

print("\nHighest total import Food Miles:")

print(
    f"{top_food_miles.iloc[0]['Item']} - "
    f"{top_food_miles.iloc[0]['import_food_miles_billion']:,.2f} "
    f"billion tonne-km"
)

print("\nMost source countries:")

print(
    f"{top_sources.iloc[0]['Item']} - "
    f"{int(top_sources.iloc[0]['import_countries'])} countries"
)

print("\nHighest import dependency:")

print(
    f"{top_dependency.iloc[0]['Item']} - "
    f"{top_dependency.iloc[0]['import_dependency_percent']:.2f}%"
)

print("\n" + "=" * 70)
print("STEP 9A COMPLETE")
print("=" * 70)