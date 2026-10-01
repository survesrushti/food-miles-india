import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
FILES = sorted(RAW.glob("production_qcl*.csv"))


def read_csv_safe(path):
    """Read a CSV, trying two common encodings."""
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


df = pd.concat([read_csv_safe(f) for f in FILES], ignore_index=True)

# ---------- 1. The two Chinas ----------
print("1. AREAS WITH 'China' IN THE NAME")
china = df[df["Area"].str.contains("China", na=False)]
print(china.groupby(["Area Code (M49)", "Area"]).size().to_string())

# ---------- 2. Aggregates or defunct countries hiding in Area ----------
print("\n2. POSSIBLE AGGREGATES OR FORMER COUNTRIES")
keywords = ["world", "africa", "asia", "europe", "america", "oceania", "former",
            "ussr", "yugoslav", "czechoslovakia", "montenegro", "ethiopia pdr",
            "belgium-luxembourg", "antilles", "union", "income", "countries"]
pattern = "|".join(keywords)
suspects = df[df["Area"].str.contains(pattern, case=False, na=False)]
if suspects.empty:
    print("none found")
else:
    print(suspects.groupby(["Area Code (M49)", "Area"])["Year"].agg(["min", "max"]).to_string())

# ---------- 3. Are non-English characters stored correctly? ----------
print("\n3. NAMES WITH SPECIAL CHARACTERS (ascii() shows the real characters)")
special = sorted({a for a in df["Area"].unique() if not a.isascii()})
for name in special:
    print(ascii(name))

# ---------- 4. Cleaned top producers (per food, latest year for that food) ----------
print("\n4. TOP 3 PRODUCERS AFTER CLEANING")
clean = df[df["Value"].notna() & (df["Value"] > 0) & (df["Area"] != "China")]
print(f"Rows before: {len(df)} | after cleaning: {len(clean)}")
for item, group in clean.groupby("Item"):
    year = group["Year"].max()
    top = group[group["Year"] == year].nlargest(3, "Value")
    text = ", ".join(f"{a} ({v:,.0f})" for a, v in zip(top["Area"], top["Value"]))
    print(f"{item} ({year}): {text}")