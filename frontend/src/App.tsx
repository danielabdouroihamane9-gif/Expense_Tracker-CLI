import { lazy, Suspense, type ReactNode } from "react"
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom"
import { AppShell } from "./components/layout/AppShell"
import { useAuth } from "./features/auth/auth-context"
import { Button } from "./components/ui/button"

const LoginPage = lazy(() => import("./features/auth/LoginPage").then((module) => ({ default: module.LoginPage })))
const RegisterPage = lazy(() => import("./features/auth/RegisterPage").then((module) => ({ default: module.RegisterPage })))
const DashboardPage = lazy(() => import("./features/dashboard/DashboardPage").then((module) => ({ default: module.DashboardPage })))
const ExpensesPage = lazy(() => import("./features/expenses/ExpensesPage").then((module) => ({ default: module.ExpensesPage })))
const BudgetsPage = lazy(() => import("./features/budgets/BudgetsPage").then((module) => ({ default: module.BudgetsPage })))
const SettingsPage = lazy(() => import("./features/settings/SettingsPage").then((module) => ({ default: module.SettingsPage })))

function SessionGate() {
  const { isLoading, isAuthenticated, sessionFailed, retrySession } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <div className="center-state"><span className="spinner" />Checking your session…</div>
  }
  if (sessionFailed) {
    return (
      <div className="center-state session-error">
        <h1>We couldn’t verify your session</h1>
        <p>Check your connection and try again. Your sign-in details remain on this device.</p>
        <Button onClick={retrySession}>Try again</Button>
      </div>
    )
  }
  return isAuthenticated
    ? <Outlet />
    : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading) return <div className="center-state"><span className="spinner" />Loading…</div>
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
  return (
    <Suspense fallback={<div className="center-state"><span className="spinner" />Loading your workspace…</div>}>
      <Routes>
        <Route path="/login" element={<PublicOnly><LoginPage /></PublicOnly>} />
        <Route path="/register" element={<PublicOnly><RegisterPage /></PublicOnly>} />
        <Route element={<SessionGate />}>
          <Route element={<AppShell />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/expenses" element={<ExpensesPage />} />
            <Route path="/budgets" element={<BudgetsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  )
}
