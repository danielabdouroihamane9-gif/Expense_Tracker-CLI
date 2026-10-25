export const EXPENSE_CATEGORIES = [
  "food",
  "transport",
  "rent",
  "utilities",
  "entertainment",
  "healthcare",
  "shopping",
  "other",
] as const

export type ExpenseCategory = (typeof EXPENSE_CATEGORIES)[number]

export const CATEGORY_LABELS: Record<ExpenseCategory, string> = {
  food: "Food",
  transport: "Transport",
  rent: "Rent",
  utilities: "Utilities",
  entertainment: "Entertainment",
  healthcare: "Healthcare",
  shopping: "Shopping",
  other: "Other",
}

export interface UserProfile {
  id: number
  username: string
  email: string
  currency: string | null
  date_joined: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface Expense {
  id: string
  user: number
  occurred_on: string
  amount: string
  currency: string
  category: ExpenseCategory
  description: string
  created_at: string
}

export interface ExpenseInput {
  occurred_on: string
  amount: string
  category: ExpenseCategory
  description: string
}

export interface Budget {
  id: number
  user: number
  category: ExpenseCategory
  amount: string
}

export interface BudgetInput {
  category: ExpenseCategory
  amount: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface MonthlyCategorySummary {
  category: ExpenseCategory
  label: string
  spent: string
  budget: string | null
  remaining: string | null
  percentage_used: string | null
}

export interface MonthlySummary {
  year: number
  month: number
  currency: string | null
  total_spent: string
  categories: MonthlyCategorySummary[]
}

export interface ExpenseStatistics {
  count: number
  total_spending: string
  average_expense: string
  highest_expense: Expense | null
  lowest_expense: Expense | null
  spending_by_category: Array<{
    category: ExpenseCategory
    total: string
    count: number
  }>
  top_categories: Array<{
    category: ExpenseCategory
    total: string
    count: number
  }>
}

export interface ImportResult {
  detail: string
  rows_processed: number
  imported: number
  skipped_duplicates: number
}

export interface ImportValidationError {
  row: number
  errors: Record<string, string[]>
}
