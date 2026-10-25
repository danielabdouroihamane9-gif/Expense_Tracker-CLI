import api from "../../lib/api-client"
import type { Expense, MonthlySummary, PaginatedResponse } from "../../types/api"

export async function getMonthlySummary(
  year?: number,
  month?: number,
): Promise<MonthlySummary> {
  const params = year && month ? { year, month } : undefined
  const response = await api.get<MonthlySummary>(
    "/api/v1/expenses/summary/",
    { params },
  )
  return response.data
}

export async function getRecentExpenses(): Promise<PaginatedResponse<Expense>> {
  const response = await api.get<PaginatedResponse<Expense>>(
    "/api/v1/expenses/",
    { params: { page: 1, ordering: "-occurred_on,-created_at" } },
  )
  return response.data
}
