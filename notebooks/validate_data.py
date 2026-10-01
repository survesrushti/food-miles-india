import math
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
FAO_FILE = RAW / "FAOSTAT_data_en_9-30-2026.csv"


def load_fao(path):
    """Read the FAOSTAT CSV, trying two common encodings."""
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle (straight-line) distance between two points, in km."""
    r = 6371.0  # mean Earth radius in km
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ---------- 1. FAOSTAT test file ----------
print("=" * 70, "\n1. FAOSTAT TEST FILE")
fao = load_fao(FAO_FILE)
print("Shape (rows, columns):", fao.shape)
print("Columns:", list(fao.columns))
print(fao.head(5).to_string())

for col in ["Element", "Unit", "Item", "Year", "Flag", "Flag Description"]:
    if col in fao.columns:
        print(f"\nUnique values in '{col}':")
        print(fao[col].value_counts(dropna=False).head(10).to_string())

print("\nMissing values per column:")
print(fao.isna().sum().to_string())
print("Duplicate rows:", fao.duplicated().sum())

partner_col = [c for c in fao.columns if "partner" in c.lower() and "code" not in c.lower()][0]
print(f"\nPartner column detected: '{partner_col}'")
print("Number of partners:", fao[partner_col].nunique())

# ---------- 2. CEPII files ----------
print("=" * 70, "\n2. CEPII FILES")
geo = pd.read_excel(RAW / "geo_cepii.xls")
dist = pd.read_excel(RAW / "dist_cepii.xls")
print("geo_cepii shape:", geo.shape)
print("dist_cepii shape:", dist.shape)
print(geo[geo["iso3"] == "IND"].T.to_string())
print("\nMissing in dist_cepii key columns:")
print(dist[["dist", "distcap", "distw", "distwces"]].isna().sum().to_string())

# ---------- 3. Can FAO partner names be matched to CEPII? ----------
print("=" * 70, "\n3. COUNTRY NAME MATCHING")
geo["name_key"] = geo["country"].astype(str).str.strip().str.casefold()
fao_partners = pd.Series(fao[partner_col].dropna().unique(), name="partner")
partner_key = fao_partners.str.strip().str.casefold()

matched = partner_key.isin(geo["name_key"])
print(f"Matched: {matched.sum()} of {len(fao_partners)} partners")
print("\nUNMATCHED FAO partner names:")
for name in fao_partners[~matched]:
    print("  -", name)

# ---------- 4. Does our Haversine agree with CEPII? ----------
print("=" * 70, "\n4. HAVERSINE vs CEPII (India as origin)")
india = geo[geo["iso3"] == "IND"].iloc[0]
sample = dist[dist["iso_o"] == "IND"].head(8)
for _, row in sample.iterrows():
    other = geo[geo["iso3"] == row["iso_d"]]
    if other.empty:
        continue
    other = other.iloc[0]
    mine = haversine_km(india["lat"], india["lon"], other["lat"], other["lon"])
    print(f"IND -> {row['iso_d']}: mine={mine:8.0f} km | CEPII dist={row['dist']:8.0f} | distcap={row['distcap']:8.0f}")