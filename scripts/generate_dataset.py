"""
Generate the fictional procurement dataset for the Power BI dashboard.

Writes data/procurement_sample.xlsx with three sheets:
  PurchaseLines  one row per purchase order line (2024 and 2025)
  Suppliers      supplier master data
  Plants         plant master data

Spend per month and per category is calibrated, so the finished dashboard
shows clear patterns (seasonality, growing categories, improving delivery).

Usage: python scripts/generate_dataset.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RNG = np.random.default_rng(11)

MONTHLY_2025 = [3.6, 3.9, 4.4, 4.0, 4.1, 4.3, 3.7, 3.5, 4.2, 4.5, 4.3, 4.1]          # EUR million
CATEGORY_2025 = {"Electronics": 14.2, "Raw materials": 11.8, "Logistics": 8.1,
                 "Packaging": 6.4, "Services": 5.0, "IT": 3.1}                          # EUR million
OTD_2025 = [90.2, 90.8, 91.5, 90.9, 92.0, 92.6, 91.8, 92.9, 93.4, 93.0, 93.8, 94.1]    # % on time
YOY_SPEND = 0.042          # 2025 vs 2024
OTD_2024_OFFSET = -1.8     # percentage points
CYCLE_DAYS = {2024: 6.6, 2025: 5.9}
SAVINGS_RATE = {2024: 0.039, 2025: 0.043}
AVG_LINE_EUR = 6000

PLANTS = [("P100", "Plant Lippstadt", "Germany", "EMEA"), ("P110", "Plant Hamm", "Germany", "EMEA"),
          ("P200", "Plant Brno", "Czechia", "EMEA"), ("P210", "Plant Craiova", "Romania", "EMEA"),
          ("P300", "Plant Querétaro", "Mexico", "Americas"), ("P310", "Plant Detroit", "USA", "Americas"),
          ("P400", "Plant Shanghai", "China", "Asia Pacific"), ("P410", "Plant Pune", "India", "Asia Pacific")]
NAME_A = ["Nord", "Alpen", "Rhein", "Baltic", "Delta", "Vector", "Orion", "Atlas", "Summit", "Helix", "Apex", "Cobalt"]
NAME_B = ["tech", "parts", "metal", "pack", "logistik", "systems", "tronic", "werk"]
SUFFIX = ["GmbH", "AG", "s.r.o.", "S.A.", "Ltd", "KG", "B.V."]
COUNTRIES = ["Germany", "Germany", "Poland", "Czechia", "France", "Italy", "China", "Mexico", "USA", "India"]


def suppliers():
    rows, used, sid = [], set(), 1000
    for cat in CATEGORY_2025:
        for _ in range(10):
            while True:
                name = f"{RNG.choice(NAME_A)}{RNG.choice(NAME_B)} {RNG.choice(SUFFIX)}"
                if name not in used:
                    used.add(name)
                    break
            rows.append((f"S{sid}", name, cat, RNG.choice(COUNTRIES),
                         "Single source" if RNG.random() < 0.25 else "Multi source"))
            sid += 1
    return pd.DataFrame(rows, columns=["Supplier ID", "Supplier Name", "Category", "Country", "Sourcing Type"])


def split_amount(total, n):
    parts = RNG.dirichlet(np.full(n, 2.0)) * total
    parts = np.round(parts, 2)
    parts[-1] = round(total - parts[:-1].sum(), 2)
    return parts


def year_lines(year, sup):
    scale = 1.0 if year == 2025 else 1 / (1 + YOY_SPEND)
    total = sum(MONTHLY_2025)
    cat_share = {c: v / total for c, v in CATEGORY_2025.items()}
    if year == 2024:   # categories grew at different speeds into 2025
        tilt = {"Electronics": 0.93, "Raw materials": 1.02, "Logistics": 1.03, "Packaging": 1.02, "Services": 1.03, "IT": 1.04}
        cat_share = {c: s * tilt[c] for c, s in cat_share.items()}
        norm = sum(cat_share.values())
        cat_share = {c: s / norm for c, s in cat_share.items()}
    rows = []
    for m, month_total in enumerate(MONTHLY_2025, start=1):
        month_total *= 1e6 * scale * (1 + RNG.normal(0, 0.02) if year == 2024 else 1)
        otd = (OTD_2025[m - 1] + (OTD_2024_OFFSET if year == 2024 else 0)) / 100
        month_rows = []
        for cat, share in cat_share.items():
            amount = month_total * share
            n = max(3, int(round(amount / AVG_LINE_EUR)))
            cat_sup = sup[sup["Category"] == cat]["Supplier ID"].to_numpy()
            for value in split_amount(amount, n):
                day = int(RNG.integers(1, 29))
                po_date = pd.Timestamp(year, m, day)
                cycle = max(1, int(round(RNG.gamma(4.0, CYCLE_DAYS[year] / 4.0))))
                month_rows.append({
                    "PR Date": po_date - pd.Timedelta(days=cycle),
                    "PO Date": po_date,
                    "Supplier ID": RNG.choice(cat_sup),
                    "Plant ID": RNG.choice([p[0] for p in PLANTS]),
                    "Category": cat,
                    "Spend EUR": value,
                    "Requested Delivery Date": po_date + pd.Timedelta(days=int(RNG.integers(10, 41))),
                })
        # exact on-time share per month
        on_time = np.zeros(len(month_rows), dtype=bool)
        on_time[RNG.choice(len(month_rows), int(round(otd * len(month_rows))), replace=False)] = True
        for r, ok in zip(month_rows, on_time):
            shift = -int(RNG.integers(0, 4)) if ok else int(RNG.integers(1, 11))
            r["Receipt Date"] = r["Requested Delivery Date"] + pd.Timedelta(days=shift)
        rows += month_rows
    df = pd.DataFrame(rows)
    rate = RNG.normal(SAVINGS_RATE[year], 0.015, len(df)).clip(0, None)
    df["Savings EUR"] = (df["Spend EUR"] * rate).round(2)
    df["Savings EUR"] *= (df["Spend EUR"].sum() * SAVINGS_RATE[year]) / df["Savings EUR"].sum()
    df["Savings EUR"] = df["Savings EUR"].round(2)
    return df


def main():
    sup = suppliers()
    lines = pd.concat([year_lines(2024, sup), year_lines(2025, sup)], ignore_index=True)
    lines = lines.sort_values("PO Date", kind="stable").reset_index(drop=True)
    lines.insert(0, "PO Number", [f"45{8000000 + i:08d}" for i in range(len(lines))])
    lines.insert(1, "PO Line", 10)
    for c in ["PR Date", "PO Date", "Requested Delivery Date", "Receipt Date"]:
        lines[c] = lines[c].dt.date
    cols = ["PO Number", "PO Line", "PR Date", "PO Date", "Supplier ID", "Plant ID", "Category",
            "Spend EUR", "Savings EUR", "Requested Delivery Date", "Receipt Date"]
    plants = pd.DataFrame(PLANTS, columns=["Plant ID", "Plant Name", "Country", "Region"])
    out = ROOT / "data" / "procurement_sample.xlsx"
    out.parent.mkdir(exist_ok=True)
    with pd.ExcelWriter(out, engine="openpyxl") as xw:
        lines[cols].to_excel(xw, sheet_name="PurchaseLines", index=False)
        sup.to_excel(xw, sheet_name="Suppliers", index=False)
        plants.to_excel(xw, sheet_name="Plants", index=False)
    print(f"{len(lines):,} purchase lines, {len(sup)} suppliers, {len(plants)} plants -> {out}")


if __name__ == "__main__":
    main()
