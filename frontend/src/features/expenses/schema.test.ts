import { describe, expect, it } from "vitest"
import { expenseFormSchema } from "./schema"

const validExpense = {
  occurred_on: "2026-10-24",
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
})
