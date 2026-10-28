import { useMemo, useState, type ChangeEvent } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  ArrowDownWideNarrow,
  ArrowUpDown,
  Copy,
  Download,
  FileUp,
  Pencil,
  Plus,
  Search,
  Trash2,
  X,
} from "lucide-react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { Button } from "../../components/ui/button"
import { Dialog } from "../../components/ui/dialog"
import { EmptyState, ErrorState, LoadingState, PageHeader } from "../../components/shared/PageElements"
import { CATEGORY_LABELS, EXPENSE_CATEGORIES } from "../../types/api"
import type { Expense, ExpenseInput } from "../../types/api"
import { formatCurrency } from "../../lib/currency"
import { getApiErrorMessage, getFieldErrors } from "../../lib/api-errors"
import { CategoryIcon } from "./CategoryIcon"
import { futureExpenseDateRows } from "./csv-validation"
import { useAuth } from "../auth/auth-context"
import {
  createExpense,
  deleteExpense,
  downloadExpenseExport,
  duplicateExpense,
  getExpenses,
  importExpenses,
  updateExpense,
  type ExpenseFilters,
} from "./api"
import {
  expenseDateSchema,
  expenseFormSchema,
  localDateString,
  type ExpenseFormValues,
} from "./schema"

function makeFilters(
  search: string,
  category: string,
  startDate: string,
  endDate: string,
  minAmount: string,
  maxAmount: string,
  ordering: string,
  page: number,
): ExpenseFilters {
  return {
    ...(search.trim() ? { search: search.trim() } : {}),
    ...(category ? { category } : {}),
    ...(startDate ? { occurred_on__gte: startDate } : {}),
    ...(endDate ? { occurred_on__lte: endDate } : {}),
    ...(minAmount ? { amount__gte: minAmount } : {}),
    ...(maxAmount ? { amount__lte: maxAmount } : {}),
    ...(ordering ? { ordering } : {}),
    page,
  }
}

function errorRows(error: unknown): Array<{ row: number; errors: Record<string, string[]> }> {
  if (typeof error !== "object" || error === null || !("response" in error)) return []
  const response = error.response
  if (typeof response !== "object" || response === null || !("data" in response)) return []
  const data = response.data
  if (typeof data !== "object" || data === null || !("errors" in data) || !Array.isArray(data.errors)) return []
  return data.errors.filter(
    (item): item is { row: number; errors: Record<string, string[]> } =>
      typeof item === "object" && item !== null && "row" in item && "errors" in item,
  )
}

function csvErrorDetail(error: unknown): string | null {
  if (typeof error !== "object" || error === null || !("response" in error)) return null
  const response = error.response
  if (typeof response !== "object" || response === null || !("data" in response)) return null
  const data = response.data
  if (typeof data !== "object" || data === null || !("detail" in data)) return null
  return typeof data.detail === "string" ? data.detail : null
}

export function ExpensesPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [search, setSearch] = useState("")
  const [category, setCategory] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [minAmount, setMinAmount] = useState("")
  const [maxAmount, setMaxAmount] = useState("")
  const [ordering, setOrdering] = useState("-occurred_on,-created_at")
  const [page, setPage] = useState(1)
  const [editing, setEditing] = useState<Expense | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Expense | null>(null)
  const [duplicateTarget, setDuplicateTarget] = useState<Expense | null>(null)
  const today = localDateString()
  const [duplicateDate, setDuplicateDate] = useState(today)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [exporting, setExporting] = useState(false)
  const [importing, setImporting] = useState(false)
  const [importErrors, setImportErrors] = useState<Array<{ row: number; errors: Record<string, string[]> }>>([])
  const filters = useMemo(
    () => makeFilters(search, category, startDate, endDate, minAmount, maxAmount, ordering, page),
    [search, category, startDate, endDate, minAmount, maxAmount, ordering, page],
  )
  const expenseQuery = useQuery({
    queryKey: ["expenses", filters],
    queryFn: () => getExpenses(filters),
  })
  const form = useForm<ExpenseFormValues>({
    resolver: zodResolver(expenseFormSchema),
    defaultValues: { occurred_on: today, amount: "", category: "food", description: "" },
  })

  const saveMutation = useMutation({
    mutationFn: (values: ExpenseInput) => editing
      ? updateExpense(editing.id, values)
      : createExpense(values),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["expenses"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success(editing ? "Expense updated." : "Expense added.")
      setDialogOpen(false)
      setEditing(null)
      form.reset({ occurred_on: today, amount: "", category: "food", description: "" })
    },
    onError: (error) => {
      const fields = getFieldErrors(error)
      if (fields.occurred_on) form.setError("occurred_on", { message: fields.occurred_on })
      if (fields.amount) form.setError("amount", { message: fields.amount })
      if (fields.category) form.setError("category", { message: fields.category })
      if (fields.description) form.setError("description", { message: fields.description })
      toast.error(getApiErrorMessage(error))
    },
  })
  const deleteMutation = useMutation({
    mutationFn: deleteExpense,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["expenses"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success("Expense deleted.")
      if (page > 1 && expenseQuery.data?.results.length === 1) {
        setPage((current) => current - 1)
      }
      setDeleteTarget(null)
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  })
  const duplicateMutation = useMutation({
    mutationFn: ({ expense, occurredOn }: { expense: Expense; occurredOn: string }) =>
      duplicateExpense(expense.id, occurredOn),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["expenses"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success("Expense duplicated.")
      setDuplicateTarget(null)
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  })

  function openCreate() {
    setEditing(null)
    form.reset({ occurred_on: today, amount: "", category: "food", description: "" })
    setDialogOpen(true)
  }

  function openEdit(expense: Expense) {
    setEditing(expense)
    form.reset({
      occurred_on: expense.occurred_on,
      amount: expense.amount,
      category: expense.category,
      description: expense.description,
    })
    setDialogOpen(true)
  }

  function clearFilters() {
    setSearch("")
    setCategory("")
    setStartDate("")
    setEndDate("")
    setMinAmount("")
    setMaxAmount("")
    setOrdering("-occurred_on,-created_at")
    setPage(1)
  }

  async function exportCsv() {
    setExporting(true)
    const exportFilters = { ...filters }
    delete exportFilters.page
    try {
      const { blob, filename } = await downloadExpenseExport(exportFilters)
      const url = URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.download = filename
      document.body.append(link)
      link.click()
      link.remove()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
      toast.success("Your CSV export is ready.")
    } catch (error) {
      toast.error(getApiErrorMessage(error))
    } finally {
      setExporting(false)
    }
  }

  async function onFileSelected(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null
    setImportErrors([])
    if (!file) {
      setSelectedFile(null)
      return
    }
    if (!file.name.toLowerCase().endsWith(".csv")) {
      toast.error("Choose a .csv file.")
      event.target.value = ""
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error("CSV files must be 10 MB or smaller.")
      event.target.value = ""
      return
    }

    let csvText: string
    try {
      csvText = await file.text()
    } catch {
      setSelectedFile(null)
      event.target.value = ""
      toast.error("Couldn’t read this CSV file. Choose it again or try another file.")
      return
    }

    const futureRows = futureExpenseDateRows(csvText, today)
    if (futureRows.length > 0) {
      setSelectedFile(null)
      setImportErrors(futureRows.map((row) => ({
        row,
        errors: { occurred_on: ["Date cannot be in the future."] },
      })))
      event.target.value = ""
      toast.error("Future expense dates were found. Correct the listed rows before importing.")
      return
    }

    setSelectedFile(file)
  }

  async function importCsv() {
    if (!selectedFile) return
    setImporting(true)
    setImportErrors([])
    try {
      const result = await importExpenses(selectedFile)
      await queryClient.invalidateQueries({ queryKey: ["expenses"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success(`${result.detail} ${result.imported} imported; ${result.skipped_duplicates} duplicates skipped.`)
      setSelectedFile(null)
      const input = document.getElementById("csv-file") as HTMLInputElement | null
      if (input) input.value = ""
    } catch (error) {
      setImportErrors(errorRows(error))
      const detail = csvErrorDetail(error)
      toast.error(detail ?? getApiErrorMessage(error))
    } finally {
      setImporting(false)
    }
  }

  const rows = expenseQuery.data?.results ?? []
  const count = expenseQuery.data?.count ?? 0
  const pages = Math.max(1, Math.ceil(count / 20))
  const firstRow = count === 0 ? 0 : (page - 1) * 20 + 1
  const lastRow = Math.min(page * 20, count)
  const anyFilters = Boolean(search || category || startDate || endDate || minAmount || maxAmount)
  const currency = user?.currency
  const duplicateDateValidation = expenseDateSchema.safeParse(duplicateDate)

  function expenseActions(expense: Expense) {
    return (
      <div className="row-actions">
        <Button variant="ghost" size="icon" aria-label={`Edit ${expense.description}`} onClick={() => openEdit(expense)}><Pencil size={15} /></Button>
        <Button variant="ghost" size="icon" aria-label={`Duplicate ${expense.description}`} onClick={() => { setDuplicateDate(today); setDuplicateTarget(expense) }}><Copy size={15} /></Button>
        <Button variant="ghost" size="icon" aria-label={`Delete ${expense.description}`} onClick={() => setDeleteTarget(expense)}><Trash2 size={15} /></Button>
      </div>
    )
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="YOUR TRANSACTIONS"
        title="Expenses"
        description="Keep your everyday spending organized and easy to understand."
        actions={<Button onClick={openCreate}><Plus size={17} /> Add expense</Button>}
      />

      <section className="panel expense-tools-panel">
        <div className="expense-filter-top">
          <label className="search-field"><Search size={17} /><span className="sr-only">Search descriptions</span><input value={search} placeholder="Search descriptions…" onChange={(event) => { setSearch(event.target.value); setPage(1) }} /></label>
          <label className="sort-select"><ArrowDownWideNarrow size={16} /><span className="sr-only">Sort expenses</span><select value={ordering} onChange={(event) => { setOrdering(event.target.value); setPage(1) }}><option value="-occurred_on,-created_at">Newest first</option><option value="occurred_on,created_at">Oldest first</option><option value="-amount">Amount: high to low</option><option value="amount">Amount: low to high</option><option value="category">Category</option></select></label>
        </div>
        <div className="filter-grid">
          <label className="filter-field"><span>Category</span><select value={category} onChange={(event) => { setCategory(event.target.value); setPage(1) }}><option value="">All categories</option>{EXPENSE_CATEGORIES.map((item) => <option key={item} value={item}>{CATEGORY_LABELS[item]}</option>)}</select></label>
          <label className="filter-field"><span>From date</span><input type="date" value={startDate} max={endDate || undefined} onChange={(event) => { setStartDate(event.target.value); setPage(1) }} /></label>
          <label className="filter-field"><span>To date</span><input type="date" value={endDate} min={startDate || undefined} onChange={(event) => { setEndDate(event.target.value); setPage(1) }} /></label>
          <label className="filter-field"><span>Amount from</span><input inputMode="decimal" value={minAmount} placeholder="Any" onChange={(event) => { setMinAmount(event.target.value); setPage(1) }} /></label>
          <label className="filter-field"><span>Amount to</span><input inputMode="decimal" value={maxAmount} placeholder="Any" onChange={(event) => { setMaxAmount(event.target.value); setPage(1) }} /></label>
          {anyFilters && <Button variant="ghost" size="small" className="clear-filter" onClick={clearFilters}><X size={15} /> Clear filters</Button>}
        </div>
        <div className="csv-tools">
          <div className="csv-import">
            <label htmlFor="csv-file" className="visually-hidden">Select a CSV file to import</label>
            <input id="csv-file" type="file" accept=".csv,text/csv" onChange={onFileSelected} />
            {selectedFile && <span className="selected-file">{selectedFile.name}</span>}
            <Button variant="outline" size="small" disabled={!selectedFile || importing} onClick={() => void importCsv()}><FileUp size={15} />{importing ? "Importing…" : "Import CSV"}</Button>
          </div>
          <Button variant="ghost" size="small" disabled={exporting} onClick={() => void exportCsv()}><Download size={15} />{exporting ? "Preparing…" : "Export CSV"}</Button>
        </div>
        {importErrors.length > 0 && (
          <div className="import-errors" role="alert">
            <strong>Some rows need attention</strong>
            {importErrors.slice(0, 5).map((item) => <p key={item.row}>Row {item.row}: {Object.entries(item.errors).map(([field, messages]) => `${field}: ${messages.join(", ")}`).join("; ")}</p>)}
            {importErrors.length > 5 && <p>And {importErrors.length - 5} more rows. No expenses were imported.</p>}
          </div>
        )}
      </section>

      <section className="panel expenses-panel">
        <div className="table-heading"><div><h2>All expenses</h2><p>{count} {count === 1 ? "transaction" : "transactions"} found</p></div><span className="page-size"><ArrowUpDown size={14} /> 20 per page</span></div>
        {expenseQuery.isPending ? <LoadingState label="Loading expenses…" /> : expenseQuery.isError ? (
          <ErrorState message={getApiErrorMessage(expenseQuery.error)} onRetry={() => void expenseQuery.refetch()} />
        ) : rows.length === 0 ? (
          <EmptyState
            title={anyFilters ? "No expenses match those filters" : "No expenses yet"}
            description={anyFilters ? "Try adjusting your search or filters." : "Add a transaction to start seeing your spending clearly."}
            action={anyFilters ? <Button variant="outline" onClick={clearFilters}>Clear filters</Button> : <Button onClick={openCreate}><Plus size={16} /> Add an expense</Button>}
          />
        ) : (
          <>
            <div className="table-scroll">
              <table className="data-table">
                <thead><tr><th>Description</th><th>Category</th><th>Date</th><th className="amount-cell">Amount</th><th><span className="sr-only">Actions</span></th></tr></thead>
                <tbody>
                  {rows.map((expense) => (
                    <tr key={expense.id}>
                      <td><div className="transaction-cell"><span className={`category-avatar tone-${expense.category}`}><CategoryIcon category={expense.category} /></span><span className="transaction-text"><strong>{expense.description}</strong><small>{expense.currency}</small></span></div></td>
                      <td><span className={`category-pill tone-${expense.category}`}>{CATEGORY_LABELS[expense.category]}</span></td>
                      <td className="date-cell">{new Date(`${expense.occurred_on}T12:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</td>
                      <td className="amount-cell"><strong>{formatCurrency(expense.amount, expense.currency)}</strong></td>
                      <td>{expenseActions(expense)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mobile-expense-list">
              {rows.map((expense) => (
                <article className="mobile-expense-card" key={expense.id}>
                  <div className="mobile-expense-main">
                    <span className={`category-avatar tone-${expense.category}`}><CategoryIcon category={expense.category} /></span>
                    <div className="mobile-expense-description">
                      <strong>{expense.description}</strong>
                      <span>{new Date(`${expense.occurred_on}T12:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</span>
                    </div>
                    <strong className="mobile-expense-amount">{formatCurrency(expense.amount, expense.currency)}</strong>
                  </div>
                  <div className="mobile-expense-footer">
                    <span className={`category-pill tone-${expense.category}`}>{CATEGORY_LABELS[expense.category]}</span>
                    {expenseActions(expense)}
                  </div>
                </article>
              ))}
            </div>
            <div className="pagination">
              <span>Showing {firstRow}–{lastRow} of {count}</span>
              <div><Button variant="outline" size="small" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}>Previous</Button><span className="pagination-count">Page {page} of {pages}</span><Button variant="outline" size="small" disabled={page >= pages} onClick={() => setPage((current) => current + 1)}>Next</Button></div>
            </div>
          </>
        )}
      </section>

      <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) setEditing(null) }} title={editing ? "Edit expense" : "Add an expense"} description="Your account currency is applied automatically." footer={<><Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button><Button type="submit" form="expense-form" disabled={saveMutation.isPending}>{saveMutation.isPending ? "Saving…" : editing ? "Save changes" : "Add expense"}</Button></>}>
        <form id="expense-form" className="form-stack" onSubmit={form.handleSubmit((values) => saveMutation.mutate(values))} noValidate>
          <label className="field"><span>Description</span><input maxLength={500} placeholder="e.g. Weekly groceries" {...form.register("description")} aria-invalid={Boolean(form.formState.errors.description)} />{form.formState.errors.description && <span className="field-error">{form.formState.errors.description.message}</span>}</label>
          <div className="field-row">
            <label className="field"><span>{currency ? `Amount (${currency})` : "Amount"}</span><input inputMode="decimal" placeholder="0.00" {...form.register("amount")} aria-invalid={Boolean(form.formState.errors.amount)} />{form.formState.errors.amount && <span className="field-error">{form.formState.errors.amount.message}</span>}</label>
            <label className="field"><span>Date</span><input type="date" max={today} {...form.register("occurred_on")} aria-invalid={Boolean(form.formState.errors.occurred_on)} />{form.formState.errors.occurred_on && <span className="field-error">{form.formState.errors.occurred_on.message}</span>}</label>
          </div>
          <label className="field"><span>Category</span><select {...form.register("category")} aria-invalid={Boolean(form.formState.errors.category)}>{EXPENSE_CATEGORIES.map((item) => <option value={item} key={item}>{CATEGORY_LABELS[item]}</option>)}</select>{form.formState.errors.category && <span className="field-error">{form.formState.errors.category.message}</span>}</label>
          <p className="field-hint">{currency ? "Currency and account ownership are set securely by the API." : "Currency is assigned by the API from your account settings."}</p>
        </form>
      </Dialog>

      <Dialog open={Boolean(duplicateTarget)} onOpenChange={(open) => { if (!open) setDuplicateTarget(null) }} title="Duplicate expense" description={duplicateTarget ? `Create a new ${CATEGORY_LABELS[duplicateTarget.category].toLowerCase()} expense based on “${duplicateTarget.description}”.` : undefined} footer={<><Button variant="outline" onClick={() => setDuplicateTarget(null)}>Cancel</Button>      <Button disabled={duplicateMutation.isPending || !duplicateDateValidation.success} onClick={() => duplicateTarget && duplicateMutation.mutate({ expense: duplicateTarget, occurredOn: duplicateDate })}>{duplicateMutation.isPending ? "Duplicating…" : "Create duplicate"}</Button></>}>
        <label className="field"><span>Date for the new expense</span><input type="date" max={today} value={duplicateDate} aria-invalid={!duplicateDateValidation.success} onChange={(event) => setDuplicateDate(event.target.value)} />{!duplicateDateValidation.success && <span className="field-error">{duplicateDateValidation.error.issues[0]?.message}</span>}</label>
        <p className="field-hint duplicate-detail">{duplicateTarget && formatCurrency(duplicateTarget.amount, duplicateTarget.currency)} · {duplicateTarget?.description}</p>
      </Dialog>

      <Dialog open={Boolean(deleteTarget)} onOpenChange={(open) => { if (!open) setDeleteTarget(null) }} title="Delete this expense?" description={deleteTarget ? `“${deleteTarget.description}” will be permanently removed from your records.` : undefined} footer={<><Button variant="outline" onClick={() => setDeleteTarget(null)}>Keep expense</Button><Button variant="danger" disabled={deleteMutation.isPending} onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}>{deleteMutation.isPending ? "Deleting…" : "Delete expense"}</Button></>}>
        <p className="dialog-copy">This action can’t be undone.</p>
      </Dialog>
    </div>
  )
}
