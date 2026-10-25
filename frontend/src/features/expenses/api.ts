import api from "../../lib/api-client"
import type {
  Expense,
  ExpenseInput,
  ExpenseStatistics,
  ImportResult,
  PaginatedResponse,
} from "../../types/api"

export interface ExpenseFilters {
  search?: string
  category?: string
  occurred_on__gte?: string
  occurred_on__lte?: string
  amount__gte?: string
  amount__lte?: string
  ordering?: string
  page?: number
}

export async function getExpenses(
  filters: ExpenseFilters = {},
): Promise<PaginatedResponse<Expense>> {
  const response = await api.get<PaginatedResponse<Expense>>(
    "/api/v1/expenses/",
    { params: filters },
  )
  return response.data
}

export async function createExpense(input: ExpenseInput): Promise<Expense> {
  const response = await api.post<Expense>("/api/v1/expenses/", input)
  return response.data
}

export async function updateExpense(
  id: string,
  input: Partial<ExpenseInput>,
): Promise<Expense> {
  const response = await api.patch<Expense>(`/api/v1/expenses/${id}/`, input)
  return response.data
}

export async function deleteExpense(id: string): Promise<void> {
  await api.delete(`/api/v1/expenses/${id}/`)
}

export async function duplicateExpense(
  id: string,
  occurred_on: string,
): Promise<Expense> {
  const response = await api.post<Expense>(
    `/api/v1/expenses/${id}/duplicate/`,
    { occurred_on },
  )
  return response.data
}

export async function getExpenseStatistics(
  filters: ExpenseFilters = {},
): Promise<ExpenseStatistics> {
  const response = await api.get<ExpenseStatistics>(
    "/api/v1/expenses/statistics/",
    { params: filters },
  )
  return response.data
}

export async function importExpenses(file: File): Promise<ImportResult> {
  const formData = new FormData()
  formData.append("file", file)
  const response = await api.post<ImportResult>(
    "/api/v1/expenses/import/",
    formData,
  )
  return response.data
}

export async function downloadExpenseExport(
  filters: ExpenseFilters = {},
): Promise<{ blob: Blob; filename: string }> {
  const response = await api.get<Blob>("/api/v1/expenses/export/", {
    params: filters,
    responseType: "blob",
  })
  const disposition = response.headers["content-disposition"] as string | undefined
  const filename = disposition?.match(/filename="?([^";]+)"?/i)?.[1]
    ?? `expenses-${new Date().toISOString().slice(0, 10)}.csv`
  return { blob: response.data, filename }
}
