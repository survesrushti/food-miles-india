import pandas as pd
import pycountry
from pathlib import Path

RAW = Path("data/raw")
TRADE_FILES = sorted(RAW.glob("india_trade*.csv"))

# The 20 FAO item names you selected.
EXPECTED_ITEMS = [
    "Almonds, in shell", "Apples", "Bananas", "Cashew nuts, in shell",
    "Chick peas, dry", "Coffee, green", "Grapes", "Hazelnuts, in shell",
    "Kiwi fruit", "Lentils, dry", "Maize (corn)",
    "Mangoes, guavas and mangosteens", "Palm oil", "Potatoes",
    "Refined sugar", "Rice", "Soya beans", "Tea leaves", "Tomatoes", "Wheat",
]

# Old CEPII codes that differ from modern ISO codes.
CEPII_TO_MODERN = {"ROM": "ROU", "ZAR": "COD", "TMP": "TLS", "PAL": "PSE"}


def read_csv_safe(path):
    """Read a CSV, trying two common encodings."""
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


def m49_to_iso3(code):
    """Convert a numeric M49 code (e.g. 356) to a 3-letter ISO code (e.g. IND)."""
    try:
        record = pycountry.countries.get(numeric=f"{int(code):03d}")
    except (ValueError, KeyError):
        return None
    return record.alpha_3 if record else None


# ---------- 0. Load the files ----------
if not TRADE_FILES:
    raise SystemExit(
        "No files found. Put your FAOSTAT CSV in data/raw/ and name it "
        "so it starts with 'india_trade' (e.g. india_trade_20foods.csv)."
    )

for f in TRADE_FILES:
    print(f.name, "| size (MB):", round(f.stat().st_size / 1e6, 2))

df = pd.concat([read_csv_safe(f) for f in TRADE_FILES], ignore_index=True)
print("\nCombined shape (rows, columns):", df.shape)
print("Reporters in file:", df["Reporter Countries"].unique().tolist())

# ---------- 1. Elements and units ----------
print("\n" + "=" * 70)
print("1. ELEMENTS AND UNITS")
print(df.groupby(["Element", "Unit"]).size().to_string())

# ---------- 2. Items: which foods exist, and for which years ----------
print("\n" + "=" * 70)
print("2. ITEMS: years covered and number of rows")
item_summary = df.groupby("Item")["Year"].agg(["min", "max", "nunique"])
item_summary["rows"] = df.groupby("Item").size()
print(item_summary.to_string())

found_items = set(df["Item"].unique())
missing_items = [item for item in EXPECTED_ITEMS if item not in found_items]
extra_items = sorted(found_items - set(EXPECTED_ITEMS))
print("\nExpected items missing from the file:", missing_items if missing_items else "none")
print("Extra items in the file (not in expected list):", extra_items if extra_items else "none")

# ---------- 3. Data quality ----------
print("\n" + "=" * 70)
print("3. DATA QUALITY")
print("Flags:")
print(df["Flag Description"].value_counts(dropna=False).to_string())
print("\nMissing values per column:")
print(df.isna().sum()[df.isna().sum() > 0].to_string() or "none")
print("Missing values in Value:", df["Value"].isna().sum())
print("Share of zero values (%):", round((df["Value"] == 0).mean() * 100, 1))

key_columns = ["Partner Country Code (M49)", "Element", "Item", "Year"]
print("Duplicate rows on key columns:", df.duplicated(subset=key_columns).sum())

# ---------- 4. Country matching with CEPII ----------
print("\n" + "=" * 70)
print("4. COUNTRY MATCHING WITH CEPII")
geo = pd.read_excel(RAW / "geo_cepii.xls")
geo["iso3_modern"] = geo["iso3"].replace(CEPII_TO_MODERN)

quantity = df[df["Element"].str.contains("quantity", case=False) & (df["Unit"] == "t")]
by_partner = (
    quantity.groupby(["Partner Country Code (M49)", "Partner Countries"])["Value"]
    .sum()
    .reset_index()
)
by_partner["iso3"] = by_partner["Partner Country Code (M49)"].apply(m49_to_iso3)
by_partner["in_cepii"] = by_partner["iso3"].isin(geo["iso3_modern"])

total_tonnes = by_partner["Value"].sum()
unmatched = by_partner[~by_partner["in_cepii"]].sort_values("Value", ascending=False)

print(f"Partners in file: {len(by_partner)} | matched: {int(by_partner['in_cepii'].sum())}")
print(f"Unmatched partners: {len(unmatched)}")
if total_tonnes > 0:
    share = unmatched["Value"].sum() / total_tonnes * 100
    print(f"Tonnage share of unmatched partners: {share:.2f} %")
print("\nUnmatched partners (largest first):")
print(unmatched.head(25).to_string(index=False))

# ---------- 5. Quick sanity view: top partners per direction ----------
print("\n" + "=" * 70)
print("5. TOP 5 PARTNERS BY TONNES (all foods, all years combined)")
for element in quantity["Element"].unique():
    top = (
        quantity[quantity["Element"] == element]
        .groupby("Partner Countries")["Value"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    print(f"\n{element}:")
    print(top.round(0).to_string())