import pandas as pd

d = pd.read_csv("data/processed/trade_with_distance.csv")

x = d[
    (d["Item"] == "Soya beans")
    & d["Element"].str.contains("Import quantity", case=False, na=False)
    & d["Partner Countries"].isin(["Togo", "Benin", "Niger"])
    & d["Year"].between(2000, 2024)
].copy()

print("Tonnes per year and country:")
print(
    x.pivot_table(index="Year", columns="Partner Countries",
                  values="Value", aggfunc="sum")
    .fillna(0).round(0).to_string()
)

flag_cols = [c for c in x.columns if "flag" in c.lower()]
print("\nFlag columns found:", flag_cols)
if flag_cols:
    print(x.groupby(flag_cols[0])["Value"].agg(["count", "sum"]).to_string())