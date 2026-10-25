import { describe, expect, it } from "vitest"
import {
  formatCurrency,
  getProgressPercent,
  isGreaterAmount,
  subtractAmounts,
  sumAmounts,
} from "./currency"

describe("financial value helpers", () => {
  it("sums and subtracts decimal amounts without binary rounding", () => {
    expect(sumAmounts(["0.10", "0.20", null])).toBe("0.30")
    expect(subtractAmounts("1.00", "0.01")).toBe("0.99")
  })

  it("preserves large decimal amounts when formatting", () => {
    expect(formatCurrency("9007199254740993.25", "USD"))
      .toContain("9,007,199,254,740,993.25")
  })

  it("preserves negative values smaller than one currency unit", () => {
    expect(formatCurrency("-0.25", "USD")).toContain("-$0.25")
  })

  it("does not invent a currency when the backend has none", () => {
    expect(formatCurrency("12.50", null)).toBe("—")
  })

  it("calculates budget progress and overages precisely", () => {
    expect(getProgressPercent("12.50", "50.00")).toBe(25)
    expect(isGreaterAmount("100.01", "100.00")).toBe(true)
    expect(isGreaterAmount("100.00", "100.00")).toBe(false)
  })
})
