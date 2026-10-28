import { describe, expect, it } from "vitest"
import { futureExpenseDateRows } from "./csv-validation"

describe("CSV expense date validation", () => {
  it("reports future dates in either supported date column", () => {
    expect(futureExpenseDateRows(
      "Date,Amount,Category,Description\r\n2099-01-01,10,food,Future\r\n2026-10-27,5,food,Today",
      "2026-10-27",
    )).toEqual([2])

    expect(futureExpenseDateRows(
      "occurred_on,amount,category,description\n2099-01-01,10,food,Future",
      "2026-10-27",
    )).toEqual([2])
  })

  it("respects quoted commas and embedded newlines while retaining CSV row numbers", () => {
    expect(futureExpenseDateRows(
      'Date,Amount,Category,Description\n2026-10-27,10,food,"Lunch, shared"\n2099-01-01,5,other,"Future\nentry"',
      "2026-10-27",
    )).toEqual([3])
  })

  it("does not count blank CSV records as imported rows", () => {
    expect(futureExpenseDateRows(
      "Date,Amount,Category,Description\n\n2099-01-01,5,food,Future",
      "2026-10-27",
    )).toEqual([2])
  })
})
