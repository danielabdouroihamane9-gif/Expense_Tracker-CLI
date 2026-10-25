import type { AuthTokens } from "../types/api"

const STORAGE_KEY = "ledgerly.auth"

export function getAuthTokens(): AuthTokens | null {
  const stored = sessionStorage.getItem(STORAGE_KEY)
  if (!stored) return null

  try {
    const value: unknown = JSON.parse(stored)
    if (
      typeof value === "object" &&
      value !== null &&
      "access" in value &&
      "refresh" in value &&
      typeof value.access === "string" &&
      typeof value.refresh === "string"
    ) {
      return { access: value.access, refresh: value.refresh }
    }
  } catch {
    sessionStorage.removeItem(STORAGE_KEY)
    return null
  }

  sessionStorage.removeItem(STORAGE_KEY)
  return null
}

export function setAuthTokens(tokens: AuthTokens): void {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
}

export function clearAuthTokens(): void {
  sessionStorage.removeItem(STORAGE_KEY)
}
