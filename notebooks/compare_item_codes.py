import pandas as pd
from pathlib import Path

RAW = Path("data/raw")


def load(pattern):
    """Load and combine all CSV files matching a pattern."""
    frames = []
    for f in sorted(RAW.glob(pattern)):
        try:
            frames.append(pd.read_csv(f, encoding="utf-8-sig"))
        except UnicodeDecodeError:
            frames.append(pd.read_csv(f, encoding="latin-1"))
    return pd.concat(frames, ignore_index=True)


trade = load("india_trade*.csv")
prod = load("production_qcl*.csv")

trade_codes = (trade[["Item", "Item Code (CPC)"]].drop_duplicates()
               .rename(columns={"Item Code (CPC)": "trade_code"}))
prod_codes = (prod[["Item", "Item Code (CPC)"]].drop_duplicates()
              .rename(columns={"Item Code (CPC)": "production_code"}))

merged = trade_codes.merge(prod_codes, on="Item", how="outer")
merged["same_code"] = merged["trade_code"].astype(str) == merged["production_code"].astype(str)
print(merged.to_string(index=False))