import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { clearAuthTokens, getAuthTokens, setAuthTokens } from "../../lib/auth-storage"
import { getCurrentUser, login as requestLogin, register as requestRegistration } from "./api"
import type { LoginInput, RegistrationInput } from "./api"
import { AuthContext } from "./auth-context"
import type { AuthContextValue } from "./auth-context"

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [hasTokens, setHasTokens] = useState(() => Boolean(getAuthTokens()))
  const userQuery = useQuery({
    queryKey: ["auth", "me"],
    queryFn: getCurrentUser,
    enabled: hasTokens,
    retry: false,
  })

  const logout = useCallback(() => {
    clearAuthTokens()
    setHasTokens(false)
    queryClient.clear()
  }, [queryClient])

  const retrySession = useCallback(() => {
    void userQuery.refetch()
  }, [userQuery])

  useEffect(() => {
    window.addEventListener("auth:logout", logout)
    return () => window.removeEventListener("auth:logout", logout)
  }, [logout])

  const login = useCallback(async (input: LoginInput) => {
    const tokens = await requestLogin(input)
    queryClient.clear()
    setAuthTokens(tokens)
    try {
      const profile = await getCurrentUser()
      queryClient.setQueryData(["auth", "me"], profile)
      setHasTokens(true)
    } catch (error) {
      if (getAuthTokens()) {
        setHasTokens(true)
      } else {
        clearAuthTokens()
        setHasTokens(false)
      }
      throw error
    }
  }, [queryClient])

  const register = useCallback(
    (input: RegistrationInput) => requestRegistration(input),
    [],
  )

  const value = useMemo<AuthContextValue>(
    () => ({
      user: userQuery.data ?? null,
      isLoading: hasTokens && userQuery.isPending,
      isAuthenticated: Boolean(hasTokens && userQuery.data),
      sessionFailed: Boolean(hasTokens && userQuery.isError),
      retrySession,
      login,
      register,
      logout,
    }),
    [hasTokens, userQuery.data, userQuery.isPending, userQuery.isError, retrySession, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
