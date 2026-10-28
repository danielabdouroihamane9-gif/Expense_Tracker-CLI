import { useState } from "react"
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom"
import {
  BarChart3,
  ChevronDown,
  CircleHelp,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  WalletCards,
  X,
} from "lucide-react"
import { useAuth } from "../../features/auth/auth-context"
import { Button } from "../ui/button"

const navigation = [
  { to: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { to: "/expenses", label: "Expenses", icon: WalletCards },
  { to: "/budgets", label: "Budgets", icon: BarChart3 },
]

const pageNames: Record<string, string> = {
  "/dashboard": "Overview",
  "/expenses": "Expenses",
  "/budgets": "Budgets",
  "/settings": "Settings",
}

export function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const pageName = pageNames[location.pathname] ?? "Overview"

  function signOut() {
    logout()
    navigate("/login", { replace: true })
  }

  return (
    <div className="app-frame">
      <button
        className={`mobile-scrim${mobileOpen ? " is-visible" : ""}`}
        aria-label="Close navigation"
        onClick={() => setMobileOpen(false)}
        tabIndex={mobileOpen ? 0 : -1}
      />
      <aside className={`sidebar${mobileOpen ? " sidebar-open" : ""}`}>
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">T</span>
          <span className="brand-name">TallyDan<span>.</span></span>
          <button className="sidebar-close" aria-label="Close navigation" onClick={() => setMobileOpen(false)}>
            <X size={18} />
          </button>
        </div>
        <p className="nav-caption">WORKSPACE</p>
        <nav className="primary-navigation" aria-label="Main navigation">
          {navigation.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) => `nav-link${isActive ? " nav-link-active" : ""}`}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-spacer" />
        <div className="sidebar-support">
          <div className="support-icon"><CircleHelp size={18} /></div>
          <div><strong>Need a hand?</strong><span>Your data stays yours.</span></div>
        </div>
        <button className="account-chip" onClick={() => navigate("/settings")}>
          <span className="avatar">{user?.username.slice(0, 1).toUpperCase()}</span>
          <span className="account-details">
            <strong>{user?.username}</strong>
            <span>{user?.email || "Personal account"}</span>
          </span>
          <ChevronDown size={16} />
        </button>
        <button className="nav-link logout-link" onClick={signOut}>
          <LogOut size={18} strokeWidth={1.8} /><span>Sign out</span>
        </button>
      </aside>

      <div className="app-main">
        <header className="topbar">
          <Button
            variant="ghost"
            size="icon"
            className="mobile-menu"
            aria-label="Open navigation"
            onClick={() => setMobileOpen(true)}
          >
            <Menu size={20} />
          </Button>
          <div className="breadcrumb"><span>Workspace</span><span className="breadcrumb-slash">/</span><strong>{pageName}</strong></div>
          <div className="topbar-actions">
            <span className="secure-indicator"><span /> Private workspace</span>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Open settings"
              onClick={() => navigate("/settings")}
            ><Settings size={18} /></Button>
          </div>
        </header>
        <main className="page-content"><Outlet /></main>
      </div>
    </div>
  )
}
