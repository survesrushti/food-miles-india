import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
FILES = sorted(list(RAW.glob("india_apy*.csv")) + list(RAW.glob("india_apy*.xlsx")))

MAX_MB = 200

if not FILES:
    raise SystemExit(
        "No APY file found. Save it in data/raw/ with a name starting 'india_apy'."
    )


# ---------- 0. Load file(s) ----------
frames = []

for f in FILES:
    size_mb = f.stat().st_size / 1e6
    print(f.name, "| size (MB):", round(size_mb, 2))

    if size_mb > MAX_MB:
        raise SystemExit(
            f"{f.name} is larger than {MAX_MB} MB. Check the file before loading."
        )

    if f.suffix.lower() == ".xlsx":
        frames.append(pd.read_excel(f))
    else:
        try:
            frames.append(pd.read_csv(f, encoding="utf-8-sig"))
        except UnicodeDecodeError:
            frames.append(pd.read_csv(f, encoding="latin-1"))

df = pd.concat(frames, ignore_index=True)

print("\nShape (rows, columns):", df.shape)
print("Columns:", list(df.columns))

print("\nFirst 5 rows:")
print(df.head(5).to_string())


# ---------- Find columns ----------
def find_col(keyword):
    for col in df.columns:
        if keyword in str(col).lower():
            return col
    return None


state = find_col("state")
district = find_col("district")
crop = find_col("crop")
season = find_col("season")
year = find_col("year")
area = find_col("area")
production = find_col("production")
yield_col = find_col("yield")

print("\nDetected columns:")
print({
    "state": state,
    "district": district,
    "crop": crop,
    "season": season,
    "year": year,
    "area": area,
    "production": production,
    "yield": yield_col
})


# ---------- 1. Coverage ----------
print("\n" + "=" * 70)
print("1. COVERAGE")

if year:
    print(
        "Years:",
        df[year].min(),
        "to",
        df[year].max(),
        "| distinct:",
        df[year].nunique()
    )

if state:
    print("States/UTs:", df[state].nunique())

if district:
    print("Districts:", df[district].nunique())

if crop:
    print("Distinct crops:", df[crop].nunique())

if season:
    print("\nSeasons:")
    print(df[season].value_counts(dropna=False).to_string())


# ---------- 2. Data quality ----------
print("\n" + "=" * 70)
print("2. DATA QUALITY")

print("\nMissing values per column:")
print(df.isna().sum().to_string())

print("\nFully duplicated rows:", df.duplicated().sum())

if production:
    print("\nProduction column type:", df[production].dtype)

if area:
    print("Area column type:", df[area].dtype)

if yield_col:
    print("Yield column type:", df[yield_col].dtype)


# ---------- 3. Crop matching ----------
print("\n" + "=" * 70)
print("3. HOW OUR FOODS APPEAR IN THE CROP LIST")

if crop:
    print("Total distinct crops:", df[crop].nunique())

    keywords = [
        "rice",
        "wheat",
        "maize",
        "corn",
        "gram",
        "chick",
        "lentil",
        "masoor",
        "potato",
        "tomato",
        "apple",
        "banana",
        "mango",
        "almond",
        "cashew",
        "coffee",
        "grape",
        "hazel",
        "kiwi",
        "palm",
        "sugar",
        "soy",
        "soya",
        "tea"
    ]

    names = pd.Series(
        df[crop].dropna().astype(str).unique()
    )

    for kw in keywords:
        found = sorted(
            names[names.str.contains(kw, case=False, na=False)].tolist()
        )

        print(f"{kw:>8}: {found if found else 'NOT FOUND'}")


# ---------- 4. State coverage ----------
print("\n" + "=" * 70)
print("4. STATE COVERAGE")

if state:
    print(
        df[state]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .to_string(index=False)
    )


# ---------- 5. Crop summary ----------
print("\n" + "=" * 70)
print("5. CROP SUMMARY")

if crop and year:
    summary = (
        df.groupby(crop)[year]
        .agg(["min", "max", "nunique"])
        .sort_index()
    )

    summary["rows"] = df.groupby(crop).size()

    if state:
        summary["states"] = df.groupby(crop)[state].nunique()

    print(summary.to_string())


# ---------- 6. Production sanity check ----------
print("\n" + "=" * 70)
print("6. PRODUCTION SANITY CHECK")

if production:
    numeric_production = pd.to_numeric(
        df[production],
        errors="coerce"
    )

    print(
        "Missing/non-numeric production values:",
        numeric_production.isna().sum()
    )

    print(
        "Zero production values:",
        (numeric_production == 0).sum()
    )

    print(
        "Negative production values:",
        (numeric_production < 0).sum()
    )


print("\n" + "=" * 70)
print("APY VALIDATION COMPLETE")