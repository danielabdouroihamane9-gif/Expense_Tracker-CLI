import api from "../../lib/api-client"
import type { AuthTokens, UserProfile } from "../../types/api"

export interface LoginInput {
  username: string
  password: string
}

export interface RegistrationInput extends LoginInput {
  email?: string
  password_confirm: string
  currency?: string
}

export async function login(input: LoginInput): Promise<AuthTokens> {
  const response = await api.post<AuthTokens>("/api/v1/auth/token/", input)
  return response.data
}

export async function register(input: RegistrationInput): Promise<UserProfile> {
  const response = await api.post<UserProfile>("/api/v1/auth/register/", input)
  return response.data
}

export async function getCurrentUser(): Promise<UserProfile> {
  const response = await api.get<UserProfile>("/api/v1/auth/me/")
  return response.data
}
