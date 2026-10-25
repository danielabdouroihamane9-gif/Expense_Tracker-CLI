import { beforeEach, describe, expect, it, vi } from "vitest"

const api = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}))

vi.mock("./api-client", () => ({ default: api }))

import { getCurrentUser, login, register } from "../features/auth/api"
import {
  createBudget,
  deleteBudget,
  getBudgets,
  updateBudget,
} from "../features/budgets/api"
import { getMonthlySummary } from "../features/dashboard/api"
import {
  createExpense,
  downloadExpenseExport,
  duplicateExpense,
  getExpenses,
  importExpenses,
  updateExpense,
} from "../features/expenses/api"
import { getSettings, updateSettings } from "../features/settings/api"

describe("frontend API contract", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("uses the verified authentication paths and payloads", async () => {
    api.post.mockResolvedValue({ data: { access: "access", refresh: "refresh" } })
    api.get.mockResolvedValue({ data: { id: 7, currency: "MYR" } })

    await login({ username: "person", password: "secret" })
    await register({
      username: "person",
      password: "secret",
      password_confirm: "secret",
      currency: "MYR",
    })
    await getCurrentUser()

    expect(api.post).toHaveBeenNthCalledWith(
      1,
      "/api/v1/auth/token/",
      { username: "person", password: "secret" },
    )
    expect(api.post).toHaveBeenNthCalledWith(
      2,
      "/api/v1/auth/register/",
      {
        username: "person",
        password: "secret",
        password_confirm: "secret",
        currency: "MYR",
      },
    )
    expect(api.get).toHaveBeenCalledWith("/api/v1/auth/me/")
  })

  it("uses the documented expense filters and editable fields", async () => {
    const filters = {
      category: "food",
      occurred_on__gte: "2026-10-01",
      amount__lte: "25.00",
      search: "lunch",
      ordering: "-occurred_on",
      page: 2,
    }
    const input = {
      occurred_on: "2026-10-24",
      amount: "12.50",
      category: "food" as const,
      description: "Lunch",
    }
    api.get.mockResolvedValue({ data: { count: 0, next: null, previous: null, results: [] } })
    api.post.mockResolvedValue({ data: { id: "expense-id" } })
    api.patch.mockResolvedValue({ data: { id: "expense-id" } })

    await getExpenses(filters)
    await createExpense(input)
    await updateExpense("expense-id", { description: "Updated lunch" })
    await duplicateExpense("expense-id", "2026-10-25")

    expect(api.get).toHaveBeenCalledWith("/api/v1/expenses/", { params: filters })
    expect(api.post).toHaveBeenNthCalledWith(1, "/api/v1/expenses/", input)
    expect(api.patch).toHaveBeenCalledWith(
      "/api/v1/expenses/expense-id/",
      { description: "Updated lunch" },
    )
    expect(api.post).toHaveBeenNthCalledWith(
      2,
      "/api/v1/expenses/expense-id/duplicate/",
      { occurred_on: "2026-10-25" },
    )
  })

  it("uses the verified summary, settings, and budget routes", async () => {
    api.get.mockResolvedValue({ data: { currency: "USD" } })
    api.post.mockResolvedValue({ data: { id: 3 } })
    api.patch.mockResolvedValue({ data: { currency: "CAD" } })
    api.delete.mockResolvedValue({})

    await getMonthlySummary(2026, 10)
    await getSettings()
    await updateSettings({ currency: "CAD" })
    await getBudgets()
    await createBudget({ category: "food", amount: "250.00" })
    await updateBudget(3, { amount: "275.00" })
    await deleteBudget(3)

    expect(api.get).toHaveBeenCalledWith("/api/v1/expenses/summary/", {
      params: { year: 2026, month: 10 },
    })
    expect(api.get).toHaveBeenCalledWith("/api/v1/auth/settings/")
    expect(api.patch).toHaveBeenCalledWith(
      "/api/v1/auth/settings/",
      { currency: "CAD" },
    )
    expect(api.get).toHaveBeenCalledWith("/api/v1/budgets/")
    expect(api.post).toHaveBeenCalledWith("/api/v1/budgets/", {
      category: "food",
      amount: "250.00",
    })
    expect(api.patch).toHaveBeenCalledWith("/api/v1/budgets/3/", {
      amount: "275.00",
    })
    expect(api.delete).toHaveBeenCalledWith("/api/v1/budgets/3/")
  })

  it("posts multipart CSV and downloads a named export", async () => {
    const file = new File(["Date,Amount,Category,Description"], "expenses.csv", {
      type: "text/csv",
    })
    const exportBlob = new Blob(["date,amount"])
    api.post.mockResolvedValue({ data: { imported: 0 } })
    api.get.mockResolvedValue({
      data: exportBlob,
      headers: { "content-disposition": 'attachment; filename="expenses-2026-10-25.csv"' },
    })

    await importExpenses(file)
    const formData = api.post.mock.calls[0][1] as FormData
    const download = await downloadExpenseExport({ category: "food" })

    expect(api.post).toHaveBeenCalledWith(
      "/api/v1/expenses/import/",
      expect.any(FormData),
    )
    expect(formData.get("file")).toBe(file)
    expect(api.get).toHaveBeenCalledWith("/api/v1/expenses/export/", {
      params: { category: "food" },
      responseType: "blob",
    })
    expect(download).toEqual({
      blob: exportBlob,
      filename: "expenses-2026-10-25.csv",
    })
  })
})
