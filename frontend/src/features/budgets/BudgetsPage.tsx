import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Pencil, Plus, Trash2, WalletCards } from "lucide-react"
import { useForm } from "react-hook-form"
import { toast } from "sonner"
import { z } from "zod"
import { Button } from "../../components/ui/button"
import { Dialog } from "../../components/ui/dialog"
import { EmptyState, ErrorState, LoadingState, PageHeader } from "../../components/shared/PageElements"
import { CATEGORY_LABELS, EXPENSE_CATEGORIES } from "../../types/api"
import type { Budget, BudgetInput } from "../../types/api"
import { formatCurrency, getProgressPercent, isGreaterAmount, subtractAmounts } from "../../lib/currency"
import { getApiErrorMessage, getFieldErrors } from "../../lib/api-errors"
import { createBudget, deleteBudget, getBudgets, updateBudget } from "./api"
import { getMonthlySummary } from "../dashboard/api"
import { useAuth } from "../auth/auth-context"

const amountSchema = z.string()
  .regex(/^\d{1,16}(?:\.\d{1,2})?$/, "Enter an amount with up to two decimal places.")
  .refine((value) => Number(value) > 0, "Amount must be greater than zero.")

const schema = z.object({
  category: z.enum(EXPENSE_CATEGORIES),
  amount: amountSchema,
})
type FormValues = z.infer<typeof schema>

export function BudgetsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const budgetsQuery = useQuery({ queryKey: ["budgets"], queryFn: getBudgets })
  const [currentMonth] = useState(() => {
    const now = new Date()
    return { year: now.getFullYear(), month: now.getMonth() + 1 }
  })
  const summaryQuery = useQuery({
    queryKey: ["dashboard", "summary", currentMonth.year, currentMonth.month],
    queryFn: () => getMonthlySummary(currentMonth.year, currentMonth.month),
  })
  const [editing, setEditing] = useState<Budget | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleting, setDeleting] = useState<Budget | null>(null)
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { category: "food", amount: "" },
  })

  const saveMutation = useMutation({
    mutationFn: (values: BudgetInput) => editing
      ? updateBudget(editing.id, values)
      : createBudget(values),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["budgets"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success(editing ? "Budget updated." : "Budget created.")
      setDialogOpen(false)
      setEditing(null)
      form.reset({ category: "food", amount: "" })
    },
    onError: (error) => {
      const fields = getFieldErrors(error)
      if (fields.category) form.setError("category", { message: fields.category })
      if (fields.amount) form.setError("amount", { message: fields.amount })
      toast.error(getApiErrorMessage(error))
    },
  })
  const deleteMutation = useMutation({
    mutationFn: deleteBudget,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["budgets"] })
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success("Budget deleted.")
      setDeleting(null)
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  })

  function openCreate() {
    setEditing(null)
    form.reset({ category: "food", amount: "" })
    setDialogOpen(true)
  }

  function openEdit(budget: Budget) {
    setEditing(budget)
    form.reset({ category: budget.category, amount: budget.amount })
    setDialogOpen(true)
  }

  function onSubmit(values: FormValues) {
    saveMutation.mutate(values)
  }

  const currentSpending = new Map(
    (summaryQuery.data?.categories ?? []).map((item) => [item.category, item.spent]),
  )
  const currency = user?.currency ?? summaryQuery.data?.currency
  const budgets = budgetsQuery.data?.results ?? []

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="PLAN WITH INTENTION"
        title="Your budgets"
        description="Set a monthly limit for the categories that matter to you."
        actions={<Button onClick={openCreate}><Plus size={17} /> New budget</Button>}
      />
      <div className="budget-note"><WalletCards size={17} /><span>Progress compares your budget to this month’s recorded expenses.</span></div>
      {summaryQuery.isPending && <LoadingState label="Loading this month’s spending…" />}
      {budgetsQuery.isPending ? <LoadingState label="Loading your budgets…" /> : budgetsQuery.isError ? (
        <ErrorState message={getApiErrorMessage(budgetsQuery.error)} onRetry={() => void budgetsQuery.refetch()} />
      ) : budgets.length === 0 ? (
        <section className="panel budget-empty-panel">
          <EmptyState
            title="Give your spending a little structure"
            description="Create a category budget and Ledgerly will show this month’s progress using your real expenses."
            action={<Button onClick={openCreate}><Plus size={16} /> Create a budget</Button>}
          />
        </section>
      ) : (
        <section className="budget-grid" aria-label="Your budgets">
          {budgets.map((budget) => {
            const spent = summaryQuery.isError || summaryQuery.isPending
              ? null
              : currentSpending.get(budget.category) ?? "0.00"
            const progress = spent === null ? 0 : getProgressPercent(spent, budget.amount)
            const over = spent !== null && isGreaterAmount(spent, budget.amount)
            return (
              <article className="budget-card" key={budget.id}>
                <div className="budget-card-top">
                  <div className={`budget-category-icon tone-${budget.category}`}>{CATEGORY_LABELS[budget.category].slice(0, 1)}</div>
                  <div className="budget-card-actions">
                    <Button variant="ghost" size="icon" aria-label={`Edit ${CATEGORY_LABELS[budget.category]} budget`} onClick={() => openEdit(budget)}><Pencil size={16} /></Button>
                    <Button variant="ghost" size="icon" aria-label={`Delete ${CATEGORY_LABELS[budget.category]} budget`} onClick={() => setDeleting(budget)}><Trash2 size={16} /></Button>
                  </div>
                </div>
                <h2>{CATEGORY_LABELS[budget.category]}</h2>
                <p className="budget-spent">{spent === null ? "—" : formatCurrency(spent, currency)} <span>spent</span></p>
                {spent === null ? (
                  <div className="budget-progress-unavailable">Monthly progress unavailable</div>
                ) : (
                  <div className="budget-progress-track" role="progressbar" aria-label={`${CATEGORY_LABELS[budget.category]} budget used`} aria-valuenow={Math.min(Math.round(progress), 100)} aria-valuemin={0} aria-valuemax={100}>
                    <span className={over ? "progress-over" : ""} style={{ width: `${progress}%` }} />
                  </div>
                )}
                <div className="budget-footer"><span>{spent === null ? "Monthly spending unavailable" : over ? `${formatCurrency(subtractAmounts(spent, budget.amount), currency)} over` : `${formatCurrency(subtractAmounts(budget.amount, spent), currency)} left`}</span><strong>of {formatCurrency(budget.amount, currency)}</strong></div>
              </article>
            )
          })}
        </section>
      )}
      {summaryQuery.isError && <ErrorState message={getApiErrorMessage(summaryQuery.error)} onRetry={() => void summaryQuery.refetch()} />}

      <Dialog
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open)
          if (!open) setEditing(null)
        }}
        title={editing ? "Update budget" : "Create a budget"}
        description="Budgets apply to a category and are measured against this month’s expenses."
        footer={<><Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button><Button type="submit" form="budget-form" disabled={saveMutation.isPending}>{saveMutation.isPending ? "Saving…" : editing ? "Save changes" : "Create budget"}</Button></>}
      >
        <form id="budget-form" className="form-stack" onSubmit={form.handleSubmit(onSubmit)} noValidate>
          <label className="field"><span>Category</span><select {...form.register("category")} disabled={Boolean(editing)} aria-invalid={Boolean(form.formState.errors.category)}>{EXPENSE_CATEGORIES.map((category) => <option key={category} value={category}>{CATEGORY_LABELS[category]}</option>)}</select>{form.formState.errors.category && <span className="field-error">{form.formState.errors.category.message}</span>}{editing && <span className="field-hint">A budget’s category can’t be changed. Delete it and add a new one instead.</span>}</label>
          <label className="field"><span>Monthly limit</span><div className="amount-input"><span>{currency}</span><input inputMode="decimal" placeholder="0.00" {...form.register("amount")} aria-invalid={Boolean(form.formState.errors.amount)} /></div>{form.formState.errors.amount && <span className="field-error">{form.formState.errors.amount.message}</span>}</label>
        </form>
      </Dialog>
      <Dialog
        open={Boolean(deleting)}
        onOpenChange={(open) => { if (!open) setDeleting(null) }}
        title="Delete this budget?"
        description={deleting ? `Your ${CATEGORY_LABELS[deleting.category].toLowerCase()} budget will be removed. This does not change any expenses.` : undefined}
        footer={<><Button variant="outline" onClick={() => setDeleting(null)}>Keep budget</Button><Button variant="danger" disabled={deleteMutation.isPending} onClick={() => deleting && deleteMutation.mutate(deleting.id)}>{deleteMutation.isPending ? "Deleting…" : "Delete budget"}</Button></>}
      ><p className="dialog-copy">This action can’t be undone.</p></Dialog>
    </div>
  )
}
