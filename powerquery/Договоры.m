// Lookup table. Contract numbers are kept as text: Excel may turn them into numbers.
let
    Source = Excel.CurrentWorkbook(){[Name = "tContracts"]}[Content],
    AsText = Table.TransformColumns(Source, {{"Договор", each Text.Trim(Text.From(_)), type text}, {"Филиал", Text.Trim, type text}}),
    NoBlanks = Table.SelectRows(AsText, each [Договор] <> "" and [Договор] <> null),
    Unique = Table.Distinct(NoBlanks, {"Договор"})
in
    Unique
