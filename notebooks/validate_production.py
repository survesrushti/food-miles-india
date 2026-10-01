import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
PROD_FILES = sorted(RAW.glob("production_qcl*.csv"))
MAX_MB = 200

EXPECTED_ITEMS = [
    "Almonds, in shell", "Apples", "Bananas", "Cashew nuts, in shell",
    "Chick peas, dry", "Coffee, green", "Grapes", "Hazelnuts, in shell",
    "Kiwi fruit", "Lentils, dry", "Maize (corn)",
    "Mangoes, guavas and mangosteens", "Palm oil", "Potatoes",
    "Sugar cane", "Rice", "Soya beans", "Tea leaves", "Tomatoes", "Wheat",
]


def read_csv_safe(path):
    """Read a CSV, trying two common encodings."""
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


def find_column(df, keyword, exclude="code"):
    """Find the first column whose name contains keyword (and not exclude)."""
    for col in df.columns:
        if keyword.lower() in col.lower() and exclude.lower() not in col.lower():
            return col
    raise SystemExit(f"No column containing '{keyword}'. Columns are: {list(df.columns)}")


# ---------- 0. Load the files ----------
if not PROD_FILES:
    raise SystemExit("No files found. Expected names like production_qcl_part1.csv in data/raw/")

for f in PROD_FILES:
    size_mb = f.stat().st_size / 1e6
    print(f.name, "| size (MB):", round(size_mb, 2))
    if size_mb > MAX_MB:
        raise SystemExit(f"{f.name} is much larger than expected. Check the download first.")

df = pd.concat([read_csv_safe(f) for f in PROD_FILES], ignore_index=True)
print("\nCombined shape (rows, columns):", df.shape)
print("Columns:", list(df.columns))
print(df.head(3).to_string())

area_col = find_column(df, "area")
item_col = find_column(df, "item")
element_col = find_column(df, "element")
year_col = find_column(df, "year", exclude="code")

# ---------- 1. Elements and units ----------
print("\n" + "=" * 70)
print("1. ELEMENTS AND UNITS")
print(df.groupby([element_col, "Unit"]).size().to_string())

# ---------- 2. Items ----------
print("\n" + "=" * 70)
print("2. ITEMS: years, rows and number of countries")
summary = df.groupby(item_col)[year_col].agg(["min", "max", "nunique"])
summary["rows"] = df.groupby(item_col).size()
summary["countries"] = df.groupby(item_col)[area_col].nunique()
print(summary.to_string())

found = set(df[item_col].unique())
print("\nExpected items missing:", [i for i in EXPECTED_ITEMS if i not in found] or "none")
print("Extra items in file:", sorted(found - set(EXPECTED_ITEMS)) or "none")

# ---------- 3. Data quality ----------
print("\n" + "=" * 70)
print("3. DATA QUALITY")
if "Flag Description" in df.columns:
    print(df["Flag Description"].value_counts(dropna=False).to_string())
print("Missing Value cells:", df["Value"].isna().sum())
print("Zero values (%):", round((df["Value"] == 0).mean() * 100, 1))
print("Duplicates on area/item/element/year:",
      df.duplicated(subset=[area_col, item_col, element_col, year_col]).sum())

# ---------- 4. Top producers in the latest year ----------
print("\n" + "=" * 70)
latest_year = df[year_col].max()
print(f"4. TOP 3 PRODUCERS PER FOOD IN {latest_year}")
latest = df[df[year_col] == latest_year]
for item, group in latest.groupby(item_col):
    top = group.nlargest(3, "Value")[[area_col, "Value"]]
    text = ", ".join(f"{row[area_col]} ({row['Value']:,.0f})" for _, row in top.iterrows())
    print(f"{item}: {text}")

# ---------- 5. India's production ----------
print("\n" + "=" * 70)
print(f"5. INDIA'S PRODUCTION IN {latest_year} (tonnes)")
india = latest[latest[area_col].str.contains("India", case=False, na=False)]
print(india[[item_col, "Value"]].sort_values("Value", ascending=False).to_string(index=False))