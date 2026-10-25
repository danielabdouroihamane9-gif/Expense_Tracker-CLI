import { AlertCircle, Inbox } from "lucide-react"
import type { ReactNode } from "react"
import { Button } from "../ui/button"

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string
  title: string
  description?: string
  actions?: ReactNode
}) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <p className="page-eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        {description && <p className="page-description">{description}</p>}
      </div>
      {actions && <div className="page-heading-actions">{actions}</div>}
    </div>
  )
}

export function LoadingState({ label = "Loading your data…" }: { label?: string }) {
  return <div className="inline-state"><span className="spinner" />{label}</div>
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}) {
  return (
    <div className="state-card error-state" role="alert">
      <span className="state-icon error-icon"><AlertCircle size={20} /></span>
      <div><strong>We couldn’t load this data</strong><p>{message}</p></div>
      {onRetry && <Button variant="outline" size="small" onClick={onRetry}>Try again</Button>}
    </div>
  )
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string
  description: string
  action?: ReactNode
}) {
  return (
    <div className="empty-state">
      <span className="state-icon"><Inbox size={21} /></span>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  )
}
