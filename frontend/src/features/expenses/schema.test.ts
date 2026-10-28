import { describe, expect, it } from "vitest"
import { expenseDateSchema, expenseFormSchema, localDateString } from "./schema"

const validExpense = {
  occurred_on: localDateString(),
  amount: "12.50",
  category: "food",
  description: "Lunch",
}

describe("expense form validation", () => {
  it("accepts a valid expense input", () => {
    expect(expenseFormSchema.safeParse(validExpense).success).toBe(true)
  })

  it("rejects zero and over-precision amounts", () => {
    expect(expenseFormSchema.safeParse({ ...validExpense, amount: "0" }).success).toBe(false)
    expect(expenseFormSchema.safeParse({ ...validExpense, amount: "12.345" }).success).toBe(false)
  })

  it("rejects descriptions that are blank or exceed the API limit", () => {
    expect(expenseFormSchema.safeParse({ ...validExpense, description: "  " }).success).toBe(false)
    expect(expenseFormSchema.safeParse({ ...validExpense, description: "a".repeat(501) }).success).toBe(false)
  })

  it("accepts today's date and rejects invalid or future dates", () => {
    expect(expenseDateSchema.safeParse(localDateString()).success).toBe(true)
    expect(expenseDateSchema.safeParse("2026-02-30").success).toBe(false)
    expect(expenseDateSchema.safeParse("2099-12-31").success).toBe(false)
  })
})
