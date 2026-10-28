import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Eye, EyeOff, LockKeyhole, Wallet } from "lucide-react"
import { useForm } from "react-hook-form"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { z } from "zod"
import { Button } from "../../components/ui/button"
import { getApiErrorMessage, getFieldErrors } from "../../lib/api-errors"
import { useAuth } from "./auth-context"

const schema = z.object({
  username: z.string().min(1, "Enter your username."),
  password: z.string().min(1, "Enter your password."),
})

type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [showPassword, setShowPassword] = useState(false)
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  async function onSubmit(values: FormValues) {
    try {
      await login(values)
      toast.success("Welcome back.")
      const destination = (location.state as { from?: string } | null)?.from
      navigate(destination ?? "/dashboard", { replace: true })
    } catch (error) {
      const fields = getFieldErrors(error)
      for (const [field, message] of Object.entries(fields)) {
        if (field === "username" || field === "password") {
          setError(field, { message })
        }
      }
      toast.error(getApiErrorMessage(error))
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-brand"><span className="brand-mark" aria-hidden="true">T</span><span className="brand-name">TallyDan<span>.</span></span></div>
      <div className="auth-layout">
        <section className="auth-story">
          <div className="story-kicker"><span className="story-dot" /> YOUR MONEY, IN FOCUS</div>
          <h1>A clearer view of<br />where it <em>all goes.</em></h1>
          <p>Bring your spending, budgets, and everyday money decisions into one calm, clear space.</p>
          <div className="story-note">
            <div className="note-icon"><LockKeyhole size={17} /></div>
            <div><strong>Private by design</strong><span>Your financial data belongs to you.</span></div>
          </div>
          <span className="story-decoration decoration-one" />
          <span className="story-decoration decoration-two" />
        </section>
        <section className="auth-card-wrap">
          <div className="auth-card">
            <div className="auth-heading">
              <span className="auth-icon"><Wallet size={20} /></span>
              <h2>Welcome back</h2>
              <p>Sign in to pick up where you left off.</p>
            </div>
            <form className="form-stack" onSubmit={handleSubmit(onSubmit)} noValidate>
              <label className="field">
                <span>Username</span>
                <input autoComplete="username" autoFocus {...register("username")} aria-invalid={Boolean(errors.username)} placeholder="Your username" />
                {errors.username && <span className="field-error">{errors.username.message}</span>}
              </label>
              <label className="field">
                <span>Password</span>
                <div className="password-control">
                  <input type={showPassword ? "text" : "password"} autoComplete="current-password" {...register("password")} aria-invalid={Boolean(errors.password)} placeholder="Your password" />
                  <button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((visible) => !visible)}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button>
                </div>
                {errors.password && <span className="field-error">{errors.password.message}</span>}
              </label>
              <Button type="submit" className="auth-submit" disabled={isSubmitting}>
                {isSubmitting && <span className="button-spinner" />}
                {isSubmitting ? "Signing in…" : "Sign in"}
              </Button>
            </form>
            <p className="auth-switch">New to TallyDan? <Link to="/register">Create an account</Link></p>
          </div>
          <p className="auth-footnote">By continuing, you agree to keep your account credentials private.</p>
        </section>
      </div>
    </div>
  )
}
