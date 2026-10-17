// Power Query (M) for the PurchaseLines table.
// Get Data > Excel workbook > data/procurement_sample.xlsx > PurchaseLines > Transform Data,
// then replace the generated steps with these (Advanced Editor). Adjust FilePath.
let
    FilePath = "C:\portfolio\procurement-powerbi-dashboard\data\procurement_sample.xlsx",
    Source   = Excel.Workbook(File.Contents(FilePath), null, true),
    Sheet    = Source{[Item = "PurchaseLines", Kind = "Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Sheet, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Promoted, {
        {"PO Number", type text}, {"PO Line", Int64.Type},
        {"PR Date", type date}, {"PO Date", type date},
        {"Supplier ID", type text}, {"Plant ID", type text}, {"Category", type text},
        {"Spend EUR", Currency.Type}, {"Savings EUR", Currency.Type},
        {"Requested Delivery Date", type date}, {"Receipt Date", type date}
    })
in
    Typed
