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
import { EmptyState, ErrorState, LoadingState } from "../../components/shared/PageElements"
import { CATEGORY_LABELS } from "../../types/api"
import type { ExpenseCategory, MonthlyCategorySummary } from "../../types/api"
import { formatCurrency } from "../../lib/currency"

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

interface DashboardChartsProps {
  trendData: Array<{ label: string; amount: number }>
  trendLoading: boolean
  trendError: string | null
  onRetryTrend: () => void
  categories: Array<Omit<MonthlyCategorySummary, "spent"> & { spent: number }>
  monthLabel: string
  currency: string | null | undefined
}

export default function DashboardCharts({
  trendData,
  trendLoading,
  trendError,
  onRetryTrend,
  categories,
  monthLabel,
  currency,
}: DashboardChartsProps) {
  return (
    <section className="dashboard-grid">
      <article className="panel chart-panel">
        <div className="panel-heading">
          <div><h2>Spending trend</h2><p>Monthly totals from your expense history</p></div>
          <span className="panel-period">Last 6 months</span>
        </div>
        {trendLoading ? <LoadingState label="Loading trend…" /> : trendError ? (
          <ErrorState message={trendError} onRetry={onRetryTrend} />
        ) : (
          <div className="chart-wrap chart-trend">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}>
                <CartesianGrid vertical={false} stroke="#edf0ee" />
                <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: "#647168", fontSize: 12 }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fill: "#647168", fontSize: 12 }} tickFormatter={(value: number) => new Intl.NumberFormat(undefined, { notation: "compact" }).format(value)} />
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
  )
}
