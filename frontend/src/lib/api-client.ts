import axios, {
  type AxiosError,
  type InternalAxiosRequestConfig,
} from "axios"
import { clearAuthTokens, getAuthTokens, setAuthTokens } from "./auth-storage"
import type { AuthTokens } from "../types/api"

type RetriableRequest = InternalAxiosRequestConfig & { _retried?: boolean }

const productionApiOrigin = "https://expense-tracker-api-n5s7.onrender.com"
const configuredApiOrigin = import.meta.env.VITE_API_BASE_URL?.trim().replace(/\/$/, "")

const api = axios.create({
  baseURL: configuredApiOrigin || (import.meta.env.PROD ? productionApiOrigin : ""),
  headers: { Accept: "application/json" },
  timeout: 30_000,
})

let refreshRequest: Promise<string> | null = null

api.interceptors.request.use((config) => {
  const tokens = getAuthTokens()
  if (tokens) config.headers.Authorization = `Bearer ${tokens.access}`
  return config
})

async function refreshAccessToken(): Promise<string> {
  if (!refreshRequest) {
    refreshRequest = (async () => {
      const current = getAuthTokens()
      if (!current) throw new Error("No refresh token is available.")
      const response = await axios.post<Pick<AuthTokens, "access">>(
        `${api.defaults.baseURL}/api/v1/auth/token/refresh/`,
        { refresh: current.refresh },
        { timeout: 30_000 },
      )
      const updated = { ...current, access: response.data.access }
      setAuthTokens(updated)
      return updated.access
    })()
  }

  try {
    return await refreshRequest
  } finally {
    refreshRequest = null
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetriableRequest | undefined
    const requestUrl = config?.url ?? ""
    const canRefresh =
      error.response?.status === 401 &&
      config !== undefined &&
      !config._retried &&
      !requestUrl.includes("/auth/token/") &&
      !requestUrl.includes("/auth/register/")

    if (!canRefresh || !config) return Promise.reject(error)

    config._retried = true
    try {
      const access = await refreshAccessToken()
      config.headers.Authorization = `Bearer ${access}`
      return await api(config)
    } catch (refreshError) {
      const refreshStatus = axios.isAxiosError(refreshError)
        ? refreshError.response?.status
        : undefined
      if (refreshStatus === 400 || refreshStatus === 401) {
        clearAuthTokens()
        window.dispatchEvent(new Event("auth:logout"))
      }
      return Promise.reject(refreshError)
    }
  },
)

export default api
