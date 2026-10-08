(name as text) as any =>
    Excel.CurrentWorkbook(){[Name = "tParam"]}[Content]{[Param = name]}[Value]
