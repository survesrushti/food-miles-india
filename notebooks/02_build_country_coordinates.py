import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")

PROCESSED.mkdir(parents=True, exist_ok=True)

GEO_FILE = RAW / "geo_cepii.xls"

# ------------------------------------------------------------
# 1. Load CEPII geographic data
# ------------------------------------------------------------

print("=" * 70)
print("1. LOADING CEPII COORDINATES")
print("=" * 70)

geo = pd.read_excel(GEO_FILE)

print("Original rows:", len(geo))
print("Columns:", list(geo.columns))


# ------------------------------------------------------------
# 2. Keep capital coordinates
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("2. SELECTING CAPITAL COORDINATES")
print("=" * 70)

capital = geo[geo["cap"] == 1].copy()

print("Capital rows:", len(capital))
print("Unique countries:", capital["iso3"].nunique())


# ------------------------------------------------------------
# 3. Select required columns
# ------------------------------------------------------------

coords = capital[
    ["iso3", "country", "city_en", "lat", "lon"]
].copy()

coords = coords.rename(
    columns={
        "iso3": "iso3",
        "country": "country",
        "city_en": "capital",
        "lat": "latitude",
        "lon": "longitude"
    }
)

coords["source"] = "CEPII geo_cepii"


# ------------------------------------------------------------
# 4. Fix old CEPII country codes
# ------------------------------------------------------------

CEPII_TO_MODERN = {
    "ROM": "ROU",
    "ZAR": "COD",
    "TMP": "TLS",
    "PAL": "PSE"
}

coords["iso3"] = coords["iso3"].replace(CEPII_TO_MODERN)


# ------------------------------------------------------------
# 5. Add modern countries missing from CEPII
# ------------------------------------------------------------

extra = pd.DataFrame([
    {
        "iso3": "SRB",
        "country": "Serbia",
        "capital": "Belgrade",
        "latitude": 44.79,
        "longitude": 20.45,
        "source": "Manual coordinates"
    },
    {
        "iso3": "MNE",
        "country": "Montenegro",
        "capital": "Podgorica",
        "latitude": 42.44,
        "longitude": 19.26,
        "source": "Manual coordinates"
    },
    {
        "iso3": "SSD",
        "country": "South Sudan",
        "capital": "Juba",
        "latitude": 4.85,
        "longitude": 31.58,
        "source": "Manual coordinates"
    }
])

coords = pd.concat(
    [coords, extra],
    ignore_index=True
)


# ------------------------------------------------------------
# 6. Remove duplicate ISO3 codes
# ------------------------------------------------------------

coords = coords.drop_duplicates(
    subset=["iso3"],
    keep="first"
)


# ------------------------------------------------------------
# 7. Check coordinates
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("3. COORDINATE QUALITY CHECK")
print("=" * 70)

print("Total countries:", len(coords))
print("Unique ISO3 codes:", coords["iso3"].nunique())

print(
    "Missing ISO3:",
    coords["iso3"].isna().sum()
)

print(
    "Missing latitude:",
    coords["latitude"].isna().sum()
)

print(
    "Missing longitude:",
    coords["longitude"].isna().sum()
)

print(
    "Duplicate ISO3:",
    coords["iso3"].duplicated().sum()
)


# ------------------------------------------------------------
# 8. Check countries required by our trade data
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("4. CHECKING TRADE PARTNERS")
print("=" * 70)

trade_files = sorted(RAW.glob("india_trade_part*.csv"))

trade_frames = []

for file in trade_files:
    trade_frames.append(
        pd.read_csv(file, encoding="utf-8-sig")
    )

trade = pd.concat(
    trade_frames,
    ignore_index=True
)

partners = trade[
    ["Partner Country Code (M49)", "Partner Countries"]
].drop_duplicates()

print("Trade partners:", len(partners))


# Convert M49 to ISO3 using pycountry
import pycountry


def m49_to_iso3(code):
    try:
        record = pycountry.countries.get(
            numeric=f"{int(code):03d}"
        )
        return record.alpha_3 if record else None
    except (ValueError, TypeError):
        return None


partners["iso3"] = partners[
    "Partner Country Code (M49)"
].apply(m49_to_iso3)

partners["has_coordinates"] = partners["iso3"].isin(
    coords["iso3"]
)

missing = partners[
    ~partners["has_coordinates"]
].copy()

print(
    "Partners with coordinates:",
    partners["has_coordinates"].sum()
)

print(
    "Partners missing coordinates:",
    len(missing)
)

if len(missing) > 0:
    print("\nMissing partners:")
    print(
        missing[
            [
                "Partner Country Code (M49)",
                "Partner Countries",
                "iso3"
            ]
        ].to_string(index=False)
    )
else:
    print("\nAll trade partners have coordinates.")


# ------------------------------------------------------------
# 9. Save coordinate master
# ------------------------------------------------------------

output = PROCESSED / "country_coordinates.csv"

coords.to_csv(
    output,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 70)
print("5. SAVING COUNTRY COORDINATES")
print("=" * 70)

print("Saved:", output)
print("Rows:", len(coords))

print("\nFirst 10 rows:")
print(coords.head(10).to_string(index=False))

print("\nCOUNTRY COORDINATE BUILD COMPLETE")