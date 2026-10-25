import { createContext, useContext } from "react"
import type { UserProfile } from "../../types/api"
import type { LoginInput, RegistrationInput } from "./api"

export interface AuthContextValue {
  user: UserProfile | null
  isLoading: boolean
  isAuthenticated: boolean
  sessionFailed: boolean
  retrySession: () => void
  login: (input: LoginInput) => Promise<void>
  register: (input: RegistrationInput) => Promise<UserProfile>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth must be used within AuthProvider.")
  return context
}
