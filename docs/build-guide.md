# Build guide

Step-by-step instructions to build the dashboard in Power BI Desktop (about 1 to 2 hours).

## 1. Load the data

1. **Get data → Excel workbook** → `data/procurement_sample.xlsx`.
2. Select the sheets **PurchaseLines**, **Suppliers**, **Plants** → **Transform Data**.
3. In Power Query, check the column types (or paste `dax/power-query.m` into the Advanced Editor for PurchaseLines). Dates must be type *date*, amounts *fixed decimal*.
4. **Close & Apply**.

## 2. Build the model

1. **Modeling → New table**, paste the `Date` table from `dax/measures.dax`.
2. **Mark as date table** on `'Date'[Date]`. Sort `Month` by `Month No`.
3. Create the relationships in Model view:

| From | To | Cardinality |
|---|---|---|
| `PurchaseLines[PO Date]` | `'Date'[Date]` | many-to-one |
| `PurchaseLines[Supplier ID]` | `Suppliers[Supplier ID]` | many-to-one |
| `PurchaseLines[Plant ID]` | `Plants[Plant ID]` | many-to-one |

4. Create a measure table (**Enter data** → empty table named `_Measures`) and add every measure from `dax/measures.dax`.
5. Formats: spend and savings `€#,0.0,,"M"`; percentages `0.0%`; cycle days `0.0`.

## 3. Apply the theme

**View → Themes → Browse for themes** → `theme/procurement-theme.json`.

## 4. Lay out the page (16:9)

| Area | Visual | Fields |
|---|---|---|
| Top row, 4 cards | **Card (new)** with reference label | `Total Spend` + `Spend Subtitle`, `Savings` + `Savings Subtitle`, `On-Time Delivery %` + `OTD Subtitle`, `Avg PO Cycle Days` + `PO Cycle Subtitle` |
| Bottom left | **Clustered column chart** | X: `'Date'[Month]`, Y: `Total Spend` |
| Bottom middle | **Clustered bar chart** | Y: `PurchaseLines[Category]`, X: `Total Spend`, sorted descending |
| Bottom right | **Line chart** | X: `'Date'[Month]`, Y: `On-Time Delivery %`, data label on the last point |
| Top right | **Slicers** | `'Date'[Year]` (default 2025), `Plants[Region]`, `Suppliers[Sourcing Type]` |

Tips:
- One color (blue) for all bars. Color is for meaning, not decoration.
- Turn off gridlines on the bar chart and use data labels instead.
- Add a tooltip page with supplier name, spend and on-time % for drill-through.

## 5. Check your numbers

With the Year slicer on **2025** you should see:

| KPI | Expected |
|---|---|
| Total Spend | €48.6M, +4.1% vs last year |
| Savings | €2.1M, 4.3% of spend |
| On-Time Delivery % | 92.3%, +1.8 pts vs last year |
| Avg PO Cycle Days | 5.9 days, −0.7 days vs last year |
| Biggest category | Electronics, €14.2M |
| Highest month | October, €4.5M |

If a number is different, check the relationship to `'Date'` and the data types.

## 6. Finish

1. Take a screenshot of the page and save it as `docs/dashboard.png`.
2. Replace the concept image in `README.md` with your screenshot and remove the "in progress" note.
3. Optional: **Publish to web** in Power BI Service (sample data only) and add the link to the README.
4. Commit the `.pbix` file as `report/procurement-dashboard.pbix`.
