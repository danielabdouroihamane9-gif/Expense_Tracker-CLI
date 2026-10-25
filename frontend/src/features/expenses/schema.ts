import { z } from "zod"
import { EXPENSE_CATEGORIES } from "../../types/api"

const amountSchema = z.string()
  .regex(/^\d{1,16}(?:\.\d{1,2})?$/, "Enter an amount with up to two decimal places.")
  .refine((value) => Number(value) > 0, "Amount must be greater than zero.")

export const expenseFormSchema = z.object({
  occurred_on: z.string().min(1, "Choose a date."),
  amount: amountSchema,
  category: z.enum(EXPENSE_CATEGORIES),
  description: z.string().trim().min(1, "Add a description.").max(500, "Description must be 500 characters or fewer."),
})

export type ExpenseFormValues = z.infer<typeof expenseFormSchema>
