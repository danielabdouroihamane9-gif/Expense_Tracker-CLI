import { useState, type FormEvent } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Check, Globe2, LockKeyhole, Save, UserRound } from "lucide-react"
import { toast } from "sonner"
import { Button } from "../../components/ui/button"
import { ErrorState, LoadingState, PageHeader } from "../../components/shared/PageElements"
import { getApiErrorMessage } from "../../lib/api-errors"
import { useAuth } from "../auth/auth-context"
import { getSettings, updateSettings } from "./api"

export function SettingsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const settingsQuery = useQuery({
    queryKey: ["settings"],
    queryFn: getSettings,
  })
  const [currency, setCurrency] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const nextCurrency = (currency ?? settingsQuery.data?.currency ?? "").trim().toUpperCase()
    if (!/^[A-Z]{3}$/.test(nextCurrency)) {
      toast.error("Enter a valid three-letter currency code.")
      return
    }
    if (nextCurrency === settingsQuery.data?.currency) {
      toast.info("Your currency is already up to date.")
      return
    }

    setSaving(true)
    try {
      const updated = await updateSettings({ currency: nextCurrency })
      queryClient.setQueryData(["settings"], updated)
      setCurrency(null)
      queryClient.setQueryData(["auth", "me"], (profile: typeof user) =>
        profile ? { ...profile, currency: updated.currency } : profile,
      )
      await queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      toast.success(`Currency updated to ${updated.currency}.`)
    } catch (error) {
      toast.error(getApiErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page-stack settings-page">
      <PageHeader
        eyebrow="PREFERENCES"
        title="Account settings"
        description="Manage the details and preferences for your workspace."
      />
      <section className="settings-card">
        <div className="settings-card-heading">
          <span className="settings-icon"><UserRound size={18} /></span>
          <div><h2>Profile</h2><p>Your account details from TallyDan.</p></div>
        </div>
        <div className="profile-grid">
          <div><span className="settings-label">Username</span><strong>{user?.username ?? "—"}</strong></div>
          <div><span className="settings-label">Email address</span><strong>{user?.email || "Not provided"}</strong></div>
          <div><span className="settings-label">Member since</span><strong>{user?.date_joined ? new Date(user.date_joined).toLocaleDateString(undefined, { month: "long", year: "numeric" }) : "—"}</strong></div>
        </div>
      </section>

      <section className="settings-card">
        <div className="settings-card-heading">
          <span className="settings-icon settings-icon-green"><Globe2 size={18} /></span>
          <div><h2>Currency preference</h2><p>Choose the currency used for your expenses and budgets.</p></div>
        </div>
        {settingsQuery.isPending ? <LoadingState label="Loading currency preference…" /> : settingsQuery.isError ? (
          <ErrorState message={getApiErrorMessage(settingsQuery.error)} onRetry={() => void settingsQuery.refetch()} />
        ) : (
          <form className="settings-form" onSubmit={onSubmit}>
            <label className="field settings-currency-field">
              <span>Account currency</span>
              <input
                value={currency ?? settingsQuery.data.currency}
                maxLength={3}
                autoComplete="off"
                aria-describedby="currency-guidance"
                onChange={(event) => setCurrency(event.target.value.toUpperCase())}
              />
              <span className="field-hint" id="currency-guidance">Use a valid three-letter currency code. Current: {settingsQuery.data.currency}.</span>
            </label>
            <div className="notice-box">
              <LockKeyhole size={17} />
              <p>Currency can only be changed while your account has no expenses or budgets. Existing amounts are never converted automatically.</p>
            </div>
            <Button type="submit" disabled={saving || settingsQuery.isPending}>
              {saving ? <span className="button-spinner" /> : <Save size={16} />}
              {saving ? "Saving…" : "Save preference"}
            </Button>
          </form>
        )}
      </section>

      <section className="settings-security">
        <div className="settings-security-icon"><Check size={18} /></div>
        <div><strong>Session security</strong><p>Your sign-in is stored for this browser tab only and is cleared when you sign out or close the tab.</p></div>
      </section>
    </div>
  )
}
