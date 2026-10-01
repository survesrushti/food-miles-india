import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")
PROCESSED = Path("data/processed")

TRADE_FILE = PROCESSED / "trade_clean.csv"
COORD_FILE = PROCESSED / "country_coordinates.csv"

OUTPUT_DISTANCE = PROCESSED / "country_distances.csv"
OUTPUT_TRADE = PROCESSED / "trade_with_distance.csv"


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two points
    using the Haversine formula.
    Returns distance in kilometres.
    """
    R = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))

    return R * c


print("=" * 70)
print("1. LOADING DATA")
print("=" * 70)

trade = pd.read_csv(TRADE_FILE)
coords = pd.read_csv(COORD_FILE)

print("Trade rows:", len(trade))
print("Coordinate rows:", len(coords))


print("\n" + "=" * 70)
print("2. INDIA COORDINATES")
print("=" * 70)

india = coords[coords["iso3"] == "IND"].copy()

if india.empty:
    raise SystemExit("India coordinates not found.")

india_lat = india.iloc[0]["latitude"]
india_lon = india.iloc[0]["longitude"]

print("India capital:", india.iloc[0]["capital"])
print("Latitude:", india_lat)
print("Longitude:", india_lon)


print("\n" + "=" * 70)
print("3. CONVERTING TRADE PARTNERS TO ISO3")
print("=" * 70)

# M49 code → ISO3 mapping using pycountry
import pycountry


def m49_to_iso3(code):
    try:
        record = pycountry.countries.get(numeric=f"{int(code):03d}")
        return record.alpha_3 if record else None
    except (ValueError, TypeError):
        return None


partners = (
    trade[
        [
            "Partner Country Code (M49)",
            "Partner Countries"
        ]
    ]
    .drop_duplicates()
    .copy()
)

partners["iso3"] = partners[
    "Partner Country Code (M49)"
].apply(m49_to_iso3)

print("Unique trade partners:", len(partners))
print(
    "Partners converted to ISO3:",
    partners["iso3"].notna().sum()
)


print("\n" + "=" * 70)
print("4. MERGING PARTNERS WITH COORDINATES")
print("=" * 70)

partners = partners.merge(
    coords[
        [
            "iso3",
            "country",
            "capital",
            "latitude",
            "longitude"
        ]
    ],
    on="iso3",
    how="left"
)

missing = partners[partners["latitude"].isna()]

print("Partners with coordinates:", len(partners) - len(missing))
print("Partners without coordinates:", len(missing))

if not missing.empty:
    print("\nExcluded partners:")
    print(
        missing[
            [
                "Partner Country Code (M49)",
                "Partner Countries",
                "iso3"
            ]
        ].to_string(index=False)
    )


print("\n" + "=" * 70)
print("5. CALCULATING HAVERSINE DISTANCE")
print("=" * 70)

valid = partners.dropna(
    subset=["latitude", "longitude"]
).copy()

valid["distance_km"] = haversine(
    india_lat,
    india_lon,
    valid["latitude"].astype(float),
    valid["longitude"].astype(float)
)

print("Distances calculated:", len(valid))


print("\n" + "=" * 70)
print("6. DISTANCE SANITY CHECK")
print("=" * 70)

print(
    valid[
        [
            "Partner Countries",
            "iso3",
            "capital",
            "distance_km"
        ]
    ]
    .sort_values("distance_km")
    .head(10)
    .to_string(index=False)
)

print("\nFarthest 10:")
print(
    valid[
        [
            "Partner Countries",
            "iso3",
            "capital",
            "distance_km"
        ]
    ]
    .sort_values("distance_km", ascending=False)
    .head(10)
    .to_string(index=False)
)


print("\n" + "=" * 70)
print("7. SAVING COUNTRY DISTANCES")
print("=" * 70)

distance_columns = [
    "Partner Country Code (M49)",
    "Partner Countries",
    "iso3",
    "country",
    "capital",
    "latitude",
    "longitude",
    "distance_km"
]

distances = valid[distance_columns].copy()

distances.to_csv(
    OUTPUT_DISTANCE,
    index=False
)

print("Saved:", OUTPUT_DISTANCE)
print("Rows:", len(distances))


print("\n" + "=" * 70)
print("8. MERGING DISTANCE WITH TRADE")
print("=" * 70)

trade = trade.merge(
    distances[
        [
            "Partner Country Code (M49)",
            "iso3",
            "capital",
            "distance_km"
        ]
    ],
    on="Partner Country Code (M49)",
    how="left"
)

print("Trade rows:", len(trade))
print("Rows with distance:", trade["distance_km"].notna().sum())
print("Rows without distance:", trade["distance_km"].isna().sum())

trade.to_csv(
    OUTPUT_TRADE,
    index=False
)

print("Saved:", OUTPUT_TRADE)

print("\n" + "=" * 70)
print("DISTANCE CALCULATION COMPLETE")
print("=" * 70)