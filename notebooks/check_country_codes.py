import pandas as pd
import pycountry
from pathlib import Path

RAW = Path("data/raw")
fao = pd.read_csv(RAW / "FAOSTAT_data_en_9-30-2026.csv", encoding="utf-8-sig")
geo = pd.read_excel(RAW / "geo_cepii.xls")

# Old CEPII codes that differ from today's ISO codes (expected; the script confirms).
CEPII_TO_MODERN = {"ROM": "ROU", "ZAR": "COD", "TMP": "TLS"}
geo["iso3_modern"] = geo["iso3"].replace(CEPII_TO_MODERN)


def m49_to_iso3(code):
    """Convert a numeric M49/ISO code (e.g. 356) to a 3-letter code (e.g. IND)."""
    try:
        record = pycountry.countries.get(numeric=f"{int(code):03d}")
    except (ValueError, KeyError):
        return None
    return record.alpha_3 if record else None


# ---------- 1. Test on the 20 partners in your FAO file ----------
print("=" * 70, "\n1. FAO PARTNERS -> ISO3 -> CEPII")
partners = fao[["Partner Country Code (M49)", "Partner Countries"]].drop_duplicates()
partners["iso3"] = partners["Partner Country Code (M49)"].apply(m49_to_iso3)
partners["in_cepii"] = partners["iso3"].isin(geo["iso3_modern"])
print(partners.to_string(index=False))
print(f"\nMatched in CEPII: {partners['in_cepii'].sum()} of {len(partners)}")

# ---------- 2. CEPII codes that pycountry does not recognise ----------
print("=" * 70, "\n2. CEPII CODES NOT FOUND IN pycountry")
known_codes = {c.alpha_3 for c in pycountry.countries}
unknown = geo[~geo["iso3_modern"].isin(known_codes)][["iso3", "country"]]
print(unknown.drop_duplicates().to_string(index=False))

# ---------- 3. Why does geo_cepii have more rows than countries? ----------
print("=" * 70, "\n3. COUNTRIES WITH MORE THAN ONE ROW IN geo_cepii")
dupes = geo[geo.duplicated("iso3", keep=False)]
print(dupes[["iso3", "country", "city_en", "cap", "maincity"]].to_string(index=False))
print("\nUnique iso3 codes:", geo["iso3"].nunique())