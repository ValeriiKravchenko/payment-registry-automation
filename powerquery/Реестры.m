let
    Source = Folder.Files(fParam("Path")),
    TxtOnly = Table.SelectRows(Source, each Text.Lower([Extension]) = ".txt" and [Attributes]?[Hidden]? <> true),
    Files = Table.SelectColumns(TxtOnly, {"Name", "Content"}),
    Parsed = Table.AddColumn(Files, "Data", each fReadRegistry([Content])),
    NoContent = Table.RemoveColumns(Parsed, {"Content"}),
    // Keep 7 of 13 fields and give them names
    Expanded = Table.ExpandTableColumn(NoContent, "Data",
        {"Column1", "Column6", "Column7", "Column8", "Column11", "Column12", "Column13"},
        {"Дата платежа", "№ договора", "Плательщик", "Назначение платежа", "Принято", "Перечислено", "Комиссия"}),
    // Service rows ("Итого записей: …") and empty lines
    NoService = Table.SelectRows(Expanded, each [Дата платежа] <> null and [Дата платежа] <> "" and not Text.StartsWith([Дата платежа], "Итого")),
    // File name "<account ending>_<registry number>.txt"
    AccountEnding = Table.AddColumn(NoService, "Окончание счёта", each Text.BeforeDelimiter([Name], "_"), type text),
    RegistryNo = Table.AddColumn(AccountEnding, "Номер реестра", each Text.BetweenDelimiters([Name], "_", "."), type text),
    Typed = Table.TransformColumnTypes(RegistryNo,
        {{"Дата платежа", type date}, {"Принято", type number}, {"Перечислено", type number}, {"Комиссия", type number}, {"№ договора", type text}}, "ru-RU"),
    // Branch comes from the lookup table instead of a chain of conditions
    Joined = Table.NestedJoin(Typed, {"№ договора"}, Договоры, {"Договор"}, "Спр", JoinKind.LeftOuter),
    WithBranch = Table.ExpandTableColumn(Joined, "Спр", {"Филиал"}),
    BranchFilled = Table.ReplaceValue(WithBranch, null, "Нет в справочнике", Replacer.ReplaceValue, {"Филиал"}),
    // Control: accepted − transferred must equal commission
    Check = Table.AddColumn(BranchFilled, "Проверка суммы",
        each if Number.Round([Принято] - [Перечислено] - [Комиссия], 2) = 0 then "ОК" else "Расхождение", type text),
    Result = Table.SelectColumns(Check,
        {"Номер реестра", "Окончание счёта", "Дата платежа", "Филиал", "№ договора", "Плательщик",
         "Назначение платежа", "Принято", "Комиссия", "Перечислено", "Проверка суммы"}),
    Sorted = Table.Sort(Result, {{"Дата платежа", Order.Ascending}, {"Номер реестра", Order.Ascending}})
in
    Sorted
