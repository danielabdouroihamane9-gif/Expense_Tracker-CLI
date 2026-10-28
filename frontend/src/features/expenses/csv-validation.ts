export function futureExpenseDateRows(csvText: string, today: string): number[] {
  const records = parseCsvRecords(csvText)
  const headers = records[0]?.map((value) => value.replace(/^\uFEFF/, "").trim().toLowerCase())
  if (!headers) return []

  const dateHeaders = ["occurred_on", "date"].filter((header) => headers.includes(header))
  if (dateHeaders.length !== 1) return []

  const dateIndex = headers.indexOf(dateHeaders[0])
  const futureRows: number[] = []
  let rowNumber = 1
  for (const record of records.slice(1)) {
    if (record.every((value) => value.trim() === "")) continue
    rowNumber += 1
    const date = record[dateIndex]?.trim()
    if (date && /^\d{4}-\d{2}-\d{2}$/.test(date) && date > today) {
      futureRows.push(rowNumber)
    }
  }
  return futureRows
}

function parseCsvRecords(text: string): string[][] {
  const records: string[][] = []
  let record: string[] = []
  let field = ""
  let quoted = false

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index]

    if (quoted) {
      if (character === '"' && text[index + 1] === '"') {
        field += '"'
        index += 1
      } else if (character === '"') {
        quoted = false
      } else {
        field += character
      }
    } else if (character === '"' && field === "") {
      quoted = true
    } else if (character === ",") {
      record.push(field)
      field = ""
    } else if (character === "\n" || character === "\r") {
      record.push(field)
      records.push(record)
      record = []
      field = ""
      if (character === "\r" && text[index + 1] === "\n") index += 1
    } else {
      field += character
    }
  }

  if (field || record.length) {
    record.push(field)
    records.push(record)
  }

  return records
}
