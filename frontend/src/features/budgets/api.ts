import api from "../../lib/api-client"
import type { Budget, BudgetInput, PaginatedResponse } from "../../types/api"

export async function getBudgets(): Promise<PaginatedResponse<Budget>> {
  const response = await api.get<PaginatedResponse<Budget>>("/api/v1/budgets/")
  return response.data
}

export async function createBudget(input: BudgetInput): Promise<Budget> {
  const response = await api.post<Budget>("/api/v1/budgets/", input)
  return response.data
}

export async function updateBudget(
  id: number,
  input: Partial<BudgetInput>,
): Promise<Budget> {
  const response = await api.patch<Budget>(`/api/v1/budgets/${id}/`, input)
  return response.data
}

export async function deleteBudget(id: number): Promise<void> {
  await api.delete(`/api/v1/budgets/${id}/`)
}
