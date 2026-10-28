import { z } from "zod"
import { EXPENSE_CATEGORIES } from "../../types/api"

const amountSchema = z.string()
  .regex(/^\d{1,16}(?:\.\d{1,2})?$/, "Enter an amount with up to two decimal places.")
  .refine((value) => Number(value) > 0, "Amount must be greater than zero.")

export function localDateString(date = new Date()): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`
}

function isValidDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const date = new Date(`${value}T00:00:00`)
  return !Number.isNaN(date.getTime()) &&
    date.getFullYear() === Number(value.slice(0, 4)) &&
    date.getMonth() + 1 === Number(value.slice(5, 7)) &&
    date.getDate() === Number(value.slice(8, 10))
}

export const expenseDateSchema = z.string()
  .min(1, "Choose a date.")
  .refine(isValidDate, "Enter a valid date.")
  .refine((value) => value <= localDateString(), "Date cannot be in the future.")

export const expenseFormSchema = z.object({
  occurred_on: expenseDateSchema,
  amount: amountSchema,
  category: z.enum(EXPENSE_CATEGORIES),
  description: z.string().trim().min(1, "Add a description.").max(500, "Description must be 500 characters or fewer."),
})

export type ExpenseFormValues = z.infer<typeof expenseFormSchema>
