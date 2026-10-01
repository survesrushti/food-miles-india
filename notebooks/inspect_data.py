import pandas as pd
from pathlib import Path

RAW = Path("data/raw")

for file in sorted(RAW.iterdir()):
    if file.suffix.lower() not in [".csv", ".xls", ".xlsx"]:
        continue

    print("=" * 70)
    print(file.name, f"({file.stat().st_size / 1e6:.2f} MB)")

    try:
        if file.suffix.lower() == ".csv":
            df = pd.read_csv(file, nrows=5, encoding="latin-1")
        else:
            df = pd.read_excel(file, nrows=5)

        print("Columns:")
        print(list(df.columns))
        print("\nFirst 3 rows:")
        print(df.head(3).to_string())

    except Exception as error:
        print("Could not read:", error)