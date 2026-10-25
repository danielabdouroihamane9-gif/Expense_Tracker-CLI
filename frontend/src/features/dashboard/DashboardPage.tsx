import { useMemo, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import {
  ArrowDownRight,
  ArrowUpRight,
  CalendarDays,
  Plus,
  WalletCards,
} from "lucide-react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Link } from "react-router-dom"
import { Button } from "../../components/ui/button"
import { EmptyState, ErrorState, LoadingState, PageHeader } from "../../components/shared/PageElements"
import { CATEGORY_LABELS } from "../../types/api"
import type { ExpenseCategory, MonthlySummary } from "../../types/api"
import { formatCurrency, sumAmounts } from "../../lib/currency"
import { getApiErrorMessage } from "../../lib/api-errors"
import { getExpenses } from "../expenses/api"
import { getMonthlySummary } from "./api"
import { getExpenseStatistics } from "../expenses/api"
import { useAuth } from "../auth/auth-context"

const chartColors: Record<ExpenseCategory, string> = {
  food: "#5d8f76",
  transport: "#e1a766",
  rent: "#7795bd",
  utilities: "#c99382",
  entertainment: "#9b86bd",
  healthcare: "#70a7a2",
  shopping: "#cb9c5b",
  other: "#9aa6a1",
}

function monthBounds(year: number, month: number) {
  const start = new Date(year, month - 1, 1)
  const end = new Date(year, month, 0)
  const asDate = (value: Date) => {
    const yearPart = value.getFullYear()
    const monthPart = String(value.getMonth() + 1).padStart(2, "0")
    const dayPart = String(value.getDate()).padStart(2, "0")
    return `${yearPart}-${monthPart}-${dayPart}`
  }
  return { start: asDate(start), end: asDate(end) }
}

function currentMonthValue() {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
}

function pastMonths(year: number, month: number) {
  return Array.from({ length: 6 }, (_, index) => {
    const date = new Date(year, month - 1 - (5 - index), 1)
    return { year: date.getFullYear(), month: date.getMonth() + 1 }
  })
}

export function DashboardPage() {
  const { user } = useAuth()
  const [selectedMonth, setSelectedMonth] = useState(currentMonthValue)
  const [year, month] = selectedMonth.split("-").map(Number)
  const range = monthBounds(year, month)
  const monthQuery = useQuery({
    queryKey: ["dashboard", "summary", year, month],
    queryFn: () => getMonthlySummary(year, month),
  })
  const countQuery = useQuery({
    queryKey: ["dashboard", "expense-count", range.start, range.end],
    queryFn: () => getExpenses({
      occurred_on__gte: range.start,
      occurred_on__lte: range.end,
      page: 1,
    }),
  })
  const statsQuery = useQuery({
    queryKey: ["dashboard", "statistics"],
    queryFn: () => getExpenseStatistics(),
  })
  const recentQuery = useQuery({
    queryKey: ["dashboard", "recent-expenses"],
    queryFn: () => getExpenses({ page: 1, ordering: "-occurred_on,-created_at" }),
  })
  const months = useMemo(() => pastMonths(year, month), [year, month])
  const trendQuery = useQuery({
    queryKey: ["dashboard", "trend", months],
    queryFn: async () => Promise.all(
      months.map(({ year: trendYear, month: trendMonth }) =>
        getMonthlySummary(trendYear, trendMonth),
      ),
    ),
  })

  if (monthQuery.isPending) return <LoadingState label="Preparing your overview…" />
  if (monthQuery.isError) {
    return <ErrorState message={getApiErrorMessage(monthQuery.error)} onRetry={() => void monthQuery.refetch()} />
  }

  const summary = monthQuery.data
  const currency = user?.currency ?? summary.currency
  const categories = summary.categories
    .filter((item) => Number(item.spent) > 0)
    .map((item) => ({ ...item, spent: Number(item.spent) }))
  const hasBudgets = summary.categories.some((item) => item.budget !== null)
  const totalRemaining = sumAmounts(summary.categories.map((item) => item.remaining))
  const monthLabel = new Date(year, month - 1, 1).toLocaleDateString(undefined, {
    month: "long",
    year: "numeric",
  })
  const trendData = trendQuery.data?.map((item: MonthlySummary) => ({
    label: new Date(item.year, item.month - 1, 1).toLocaleDateString(undefined, { month: "short" }),
    amount: Number(item.total_spent),
  })) ?? []

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="YOUR FINANCIAL PICTURE"
        title="Good to see you."
        description="A grounded view of your spending, one month at a time."
        actions={
          <label className="month-picker">
            <CalendarDays size={16} />
            <span className="sr-only">Select month</span>
            <input type="month" value={selectedMonth} onChange={(event) => setSelectedMonth(event.target.value)} />
          </label>
        }
      />

      <section className="metrics-grid" aria-label="Monthly financial summary">
        <article className="metric-card metric-featured">
          <div className="metric-top"><span className="metric-icon"><WalletCards size={18} /></span><span className="metric-period">{monthLabel}</span></div>
          <p className="metric-label">Total spent</p>
          <p className="metric-value">{formatCurrency(summary.total_spent, currency)}</p>
          <p className="metric-footnote">Based on expenses recorded this month</p>
        </article>
        <article className="metric-card">
          <div className="metric-top"><span className="metric-icon metric-icon-warm"><CalendarDays size={18} /></span><span className="metric-trend"><ArrowUpRight size={15} /> Activity</span></div>
          <p className="metric-label">Transactions</p>
          <p className="metric-value">{countQuery.data?.count ?? "—"}</p>
          <p className="metric-footnote">{monthLabel}</p>
        </article>
        <article className="metric-card">
          <div className="metric-top"><span className="metric-icon metric-icon-blue"><ArrowDownRight size={18} /></span><span className="metric-trend">All time</span></div>
          <p className="metric-label">Average expense</p>
          <p className="metric-value">{statsQuery.data ? formatCurrency(statsQuery.data.average_expense, currency) : "—"}</p>
          <p className="metric-footnote">{statsQuery.data ? `Across ${statsQuery.data.count} expenses` : "Statistics are loading"}</p>
        </article>
        <article className="metric-card">
          <div className="metric-top"><span className="metric-icon metric-icon-lilac"><WalletCards size={18} /></span><span className="metric-trend">This month</span></div>
          <p className="metric-label">Budget remaining</p>
          <p className="metric-value">{hasBudgets ? formatCurrency(totalRemaining, currency) : "—"}</p>
          <p className="metric-footnote">{hasBudgets ? "Across your monthly category budgets" : "Create a budget to track your limits"}</p>
        </article>
      </section>
      {!currency && (
        <div className="budget-note" role="status">
          <CalendarDays size={17} />
          <span>Your account currency is unavailable. Check <Link className="text-link" to="/settings">account settings</Link> before relying on formatted totals.</span>
        </div>
      )}
      {(countQuery.isError || statsQuery.isError) && (
        <ErrorState
          message={getApiErrorMessage(countQuery.error ?? statsQuery.error)}
          onRetry={() => {
            if (countQuery.isError) void countQuery.refetch()
            if (statsQuery.isError) void statsQuery.refetch()
          }}
        />
      )}

      <section className="dashboard-grid">
        <article className="panel chart-panel">
          <div className="panel-heading">
            <div><h2>Spending trend</h2><p>Monthly totals from your expense history</p></div>
            <span className="panel-period">Last 6 months</span>
          </div>
          {trendQuery.isPending ? <LoadingState label="Loading trend…" /> : trendQuery.isError ? <ErrorState message={getApiErrorMessage(trendQuery.error)} onRetry={() => void trendQuery.refetch()} /> : (
            <div className="chart-wrap chart-trend">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendData} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}>
                  <CartesianGrid vertical={false} stroke="#edf0ee" />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: "#929b96", fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: "#929b96", fontSize: 11 }} tickFormatter={(value: number) => new Intl.NumberFormat(undefined, { notation: "compact" }).format(value)} />
                  <Tooltip formatter={(value) => formatCurrency(Number(value), currency)} cursor={{ fill: "#f3f7f4" }} />
                  <Bar dataKey="amount" fill="#548267" radius={[5, 5, 0, 0]} maxBarSize={44} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </article>

        <article className="panel category-panel">
          <div className="panel-heading">
            <div><h2>Spending by category</h2><p>{monthLabel}</p></div>
            <Link className="text-link" to="/expenses">View expenses</Link>
          </div>
          {categories.length === 0 ? (
            <EmptyState title="Nothing recorded yet" description="Expenses you add for this month will appear here." />
          ) : (
            <div className="category-chart-area">
              <div className="chart-wrap chart-donut">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={categories} dataKey="spent" nameKey="category" innerRadius={55} outerRadius={82} paddingAngle={3} stroke="none">
                      {categories.map((item) => <Cell key={item.category} fill={chartColors[item.category]} />)}
                    </Pie>
                    <Tooltip formatter={(value) => formatCurrency(Number(value), currency)} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="donut-center"><strong>{categories.length}</strong><span>categories</span></div>
              </div>
              <div className="category-legend">
                {categories.slice(0, 5).map((item) => (
                  <div className="legend-row" key={item.category}>
                    <span className="legend-dot" style={{ background: chartColors[item.category] }} />
                    <span>{CATEGORY_LABELS[item.category]}</span>
                    <strong>{formatCurrency(item.spent, currency)}</strong>
                  </div>
                ))}
              </div>
            </div>
          )}
        </article>
      </section>

      <section className="panel recent-panel">
        <div className="panel-heading">
          <div><h2>Recent expenses</h2><p>Your latest recorded transactions</p></div>
          <Button variant="outline" size="small" asChild><Link to="/expenses">All expenses</Link></Button>
        </div>
        {recentQuery.isPending ? <LoadingState /> : recentQuery.isError ? <ErrorState message={getApiErrorMessage(recentQuery.error)} onRetry={() => void recentQuery.refetch()} /> : recentQuery.data.results.length === 0 ? (
          <EmptyState title="Your first entry is a good start" description="Add an expense when you’re ready to see it reflected in your overview." action={<Button asChild><Link to="/expenses"><Plus size={16} /> Add an expense</Link></Button>} />
        ) : (
          <div className="recent-list">
            {recentQuery.data.results.slice(0, 5).map((expense) => (
              <div className="recent-row" key={expense.id}>
                <span className={`category-avatar tone-${expense.category}`}>{CATEGORY_LABELS[expense.category].slice(0, 1)}</span>
                <div className="recent-description"><strong>{expense.description}</strong><span>{CATEGORY_LABELS[expense.category]} <i /> {new Date(`${expense.occurred_on}T12:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}</span></div>
                <strong className="recent-amount">{formatCurrency(expense.amount, expense.currency)}</strong>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
