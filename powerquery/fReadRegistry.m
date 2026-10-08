// One registry file: ';' separated, 13 fields, Windows-1251, no quoting.
(content as binary) as table =>
    Csv.Document(content, [Delimiter = ";", Columns = 13, Encoding = 1251, QuoteStyle = QuoteStyle.None])
