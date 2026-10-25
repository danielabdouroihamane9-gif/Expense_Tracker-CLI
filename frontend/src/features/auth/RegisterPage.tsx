import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Eye, EyeOff, Wallet } from "lucide-react"
import { useForm } from "react-hook-form"
import { Link, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { z } from "zod"
import { Button } from "../../components/ui/button"
import { getApiErrorMessage, getFieldErrors } from "../../lib/api-errors"
import { useAuth } from "./auth-context"

const schema = z.object({
  username: z.string().min(1, "Choose a username.").max(150, "Username must be 150 characters or fewer."),
  email: z.union([z.email("Enter a valid email address."), z.literal("")]).optional(),
  password: z.string().min(1, "Choose a password."),
  password_confirm: z.string().min(1, "Confirm your password."),
  currency: z.string().regex(/^[A-Za-z]{3}$/, "Enter a three-letter currency code."),
}).refine((values) => values.password === values.password_confirm, {
  path: ["password_confirm"],
  message: "The passwords do not match.",
})

type FormValues = z.infer<typeof schema>

export function RegisterPage() {
  const { register: createAccount } = useAuth()
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { currency: "USD", email: "" },
  })

  async function onSubmit(values: FormValues) {
    try {
      await createAccount({
        ...values,
        email: values.email || undefined,
        currency: values.currency.toUpperCase(),
      })
      toast.success("Your account is ready. Sign in to get started.")
      navigate("/login", { replace: true })
    } catch (error) {
      const fields = getFieldErrors(error)
      for (const [field, message] of Object.entries(fields)) {
        if (field in values) {
          setError(field as keyof FormValues, { message })
        }
      }
      toast.error(getApiErrorMessage(error))
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-brand"><span className="brand-mark">L</span><span className="brand-name">ledgerly<span>.</span></span></div>
      <div className="auth-layout">
        <section className="auth-story">
          <div className="story-kicker"><span className="story-dot" /> A LITTLE MORE CLARITY</div>
          <h1>Make room for<br />better <em>money habits.</em></h1>
          <p>Start with a simple picture of your spending, then build a routine that works for you.</p>
          <div className="story-note">
            <div className="note-icon"><Wallet size={17} /></div>
            <div><strong>Your currency, your choice</strong><span>Set a three-letter currency for your account.</span></div>
          </div>
          <span className="story-decoration decoration-one" />
          <span className="story-decoration decoration-two" />
        </section>
        <section className="auth-card-wrap">
          <div className="auth-card auth-card-register">
            <div className="auth-heading">
              <span className="auth-icon"><Wallet size={20} /></span>
              <h2>Create your account</h2>
              <p>Just a few details to get started.</p>
            </div>
            <form className="form-stack" onSubmit={handleSubmit(onSubmit)} noValidate>
              <label className="field"><span>Username</span><input autoComplete="username" {...register("username")} aria-invalid={Boolean(errors.username)} placeholder="Choose a username" />{errors.username && <span className="field-error">{errors.username.message}</span>}</label>
              <label className="field"><span>Email <small>optional</small></span><input type="email" autoComplete="email" {...register("email")} aria-invalid={Boolean(errors.email)} placeholder="you@example.com" />{errors.email && <span className="field-error">{errors.email.message}</span>}</label>
              <div className="field-row">
                <label className="field"><span>Password</span><div className="password-control"><input type={showPassword ? "text" : "password"} autoComplete="new-password" {...register("password")} aria-invalid={Boolean(errors.password)} placeholder="Create a password" /><button type="button" aria-label={showPassword ? "Hide password" : "Show password"} onClick={() => setShowPassword((visible) => !visible)}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>{errors.password && <span className="field-error">{errors.password.message}</span>}</label>
                <label className="field"><span>Confirm</span><input type="password" autoComplete="new-password" {...register("password_confirm")} aria-invalid={Boolean(errors.password_confirm)} placeholder="Repeat password" />{errors.password_confirm && <span className="field-error">{errors.password_confirm.message}</span>}</label>
              </div>
              <label className="field"><span>Currency</span><input autoComplete="off" maxLength={3} {...register("currency")} aria-invalid={Boolean(errors.currency)} placeholder="USD" />{errors.currency && <span className="field-error">{errors.currency.message}</span>}<span className="field-hint">Your expenses will use this currency.</span></label>
              <Button type="submit" className="auth-submit" disabled={isSubmitting}>{isSubmitting && <span className="button-spinner" />}{isSubmitting ? "Creating account…" : "Create account"}</Button>
            </form>
            <p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p>
          </div>
          <p className="auth-footnote">Your password is validated securely by the account service.</p>
        </section>
      </div>
    </div>
  )
}
