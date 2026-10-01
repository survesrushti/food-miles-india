import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")

PROCESSED.mkdir(parents=True, exist_ok=True)


# ============================================================
# Helper function
# ============================================================

def read_csv_safe(path):
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


# ============================================================
# 1. CLEAN TRADE DATA
# ============================================================

print("=" * 70)
print("1. CLEANING TRADE DATA")
print("=" * 70)

trade_files = sorted(RAW.glob("india_trade_part*.csv"))

if not trade_files:
    raise SystemExit("No trade files found.")

trade_frames = []

for file in trade_files:
    print("Reading:", file.name)
    trade_frames.append(read_csv_safe(file))

trade = pd.concat(trade_frames, ignore_index=True)

print("Original trade rows:", len(trade))

# Remove exact duplicates
trade = trade.drop_duplicates()

# Keep only positive quantities for Food Miles calculations
quantity_mask = (
    trade["Element"].str.contains("quantity", case=False, na=False)
    & (trade["Unit"] == "t")
)

trade_quantity = trade[quantity_mask].copy()

trade_quantity = trade_quantity[trade_quantity["Value"] > 0].copy()

# Convert M49 country code to string
trade_quantity["Partner_M49"] = (
    pd.to_numeric(
        trade_quantity["Partner Country Code (M49)"],
        errors="coerce"
    )
    .astype("Int64")
    .astype(str)
)

# Save cleaned trade quantity data
trade_quantity.to_csv(
    PROCESSED / "trade_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Clean trade rows:", len(trade_quantity))
print("Foods:", trade_quantity["Item"].nunique())
print("Partners:", trade_quantity["Partner Countries"].nunique())
print("Years:", trade_quantity["Year"].min(), "to", trade_quantity["Year"].max())

print("\nSaved:")
print(PROCESSED / "trade_clean.csv")


# ============================================================
# 2. CLEAN PRODUCTION DATA
# ============================================================

print("\n" + "=" * 70)
print("2. CLEANING PRODUCTION DATA")
print("=" * 70)

production_files = sorted(RAW.glob("production_qcl_part*.csv"))

if not production_files:
    raise SystemExit("No production files found.")

production_frames = []

for file in production_files:
    print("Reading:", file.name)
    production_frames.append(read_csv_safe(file))

production = pd.concat(production_frames, ignore_index=True)

print("Original production rows:", len(production))

# Remove exact duplicates
production = production.drop_duplicates()

# Remove missing production values
production = production[production["Value"].notna()].copy()

# Remove zero production values
production = production[production["Value"] > 0].copy()

# Remove China aggregate (M49 code 159)
china_aggregate = pd.to_numeric(
    production["Area Code (M49)"],
    errors="coerce"
) == 159

production = production[~china_aggregate].copy()

print("Clean production rows:", len(production))
print("Foods:", production["Item"].nunique())
print("Countries:", production["Area"].nunique())
print("Years:", production["Year"].min(), "to", production["Year"].max())

production.to_csv(
    PROCESSED / "production_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nSaved:")
print(PROCESSED / "production_clean.csv")


# ============================================================
# 3. CLEAN APY DATA
# ============================================================

print("\n" + "=" * 70)
print("3. CLEANING INDIA APY DATA")
print("=" * 70)

apy_file = RAW / "india_apy.csv"

if not apy_file.exists():
    raise SystemExit("india_apy.csv not found.")

apy = read_csv_safe(apy_file)

print("Original APY rows:", len(apy))

# Remove exact duplicates
apy = apy.drop_duplicates()

# Remove rows with missing production
apy = apy[apy["Production-2024-25"].notna()].copy()

# Keep non-negative production
apy = apy[apy["Production-2024-25"] >= 0].copy()

print("Clean APY rows:", len(apy))
print("States:", apy["State"].nunique())
print("Districts:", apy["District"].nunique())
print("Crops:", apy["Crop"].nunique())

# Mapping from our project names to APY crop names
APY_CROP_MAPPING = {
    "Rice": "Rice",
    "Wheat": "Wheat",
    "Maize (corn)": "Maize",
    "Chick peas, dry": "Gram",
    "Lentils, dry": "Lentil",
}

apy_food = apy[apy["Crop"].isin(APY_CROP_MAPPING.values())].copy()

# Reverse mapping
reverse_mapping = {
    value: key for key, value in APY_CROP_MAPPING.items()
}

apy_food["Food"] = apy_food["Crop"].map(reverse_mapping)

apy_food.to_csv(
    PROCESSED / "apy_clean.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nAPY foods retained:")
print(apy_food["Food"].value_counts().to_string())

print("\nSaved:")
print(PROCESSED / "apy_clean.csv")


# ============================================================
# 4. CREATE FOOD LIST
# ============================================================

print("\n" + "=" * 70)
print("4. PROJECT FOOD LIST")
print("=" * 70)

foods = sorted(trade_quantity["Item"].dropna().unique())

food_list = pd.DataFrame({
    "Food": foods
})

food_list.to_csv(
    PROCESSED / "food_list.csv",
    index=False,
    encoding="utf-8-sig"
)

print(food_list.to_string(index=False))

print("\nSaved:")
print(PROCESSED / "food_list.csv")


# ============================================================
# 5. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CLEANING COMPLETE")
print("=" * 70)

print("\nCreated files:")

for file in sorted(PROCESSED.glob("*.csv")):
    size_mb = file.stat().st_size / 1e6
    print(f"{file.name:25} {size_mb:.2f} MB")

print("\nRaw files were NOT modified.")