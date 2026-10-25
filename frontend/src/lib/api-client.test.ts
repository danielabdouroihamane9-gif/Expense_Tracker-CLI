import axios, {
  AxiosError,
  AxiosHeaders,
  type AxiosAdapter,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios"
import { beforeEach, describe, expect, it, vi } from "vitest"
import api from "./api-client"
import { clearAuthTokens, getAuthTokens, setAuthTokens } from "./auth-storage"

function response(
  config: Parameters<AxiosAdapter>[0],
  status: number,
  data: unknown,
): AxiosResponse {
  return {
    data,
    status,
    statusText: status === 200 ? "OK" : "Unauthorized",
    headers: new AxiosHeaders(),
    config,
  }
}

describe("central API client authentication", () => {
  beforeEach(() => {
    clearAuthTokens()
    vi.restoreAllMocks()
  })

  it("attaches the session access token to protected requests", async () => {
    setAuthTokens({ access: "access-token", refresh: "refresh-token" })
    let seenAuthorization: string | undefined
    const adapter: AxiosAdapter = async (config) => {
      seenAuthorization = config.headers.Authorization as string | undefined
      return response(config, 200, { ok: true })
    }
    api.defaults.adapter = adapter

    const result = await api.get("/api/v1/auth/me/")

    expect(result.status).toBe(200)
    expect(seenAuthorization).toBe("Bearer access-token")
  })

  it("refreshes a rejected access token and retries the original request", async () => {
    setAuthTokens({ access: "expired-access", refresh: "valid-refresh" })
    const refresh = vi.spyOn(axios, "post").mockResolvedValue({
      data: { access: "renewed-access" },
      status: 200,
      statusText: "OK",
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() },
    } as AxiosResponse)
    const seenAuthorization: Array<string | undefined> = []
    let attempt = 0
    api.defaults.adapter = async (config) => {
      seenAuthorization.push(config.headers.Authorization as string | undefined)
      attempt += 1
      if (attempt === 1) {
        return Promise.reject(
          new AxiosError(
            "Unauthorized",
            AxiosError.ERR_BAD_REQUEST,
            config,
            undefined,
            response(config, 401, { detail: "Token is invalid." }),
          ),
        )
      }
      return response(config, 200, { ok: true })
    }

    const result = await api.get("/api/v1/auth/me/")

    expect(result.data).toEqual({ ok: true })
    expect(seenAuthorization).toEqual([
      "Bearer expired-access",
      "Bearer renewed-access",
    ])
    expect(refresh).toHaveBeenCalledWith(
      "/api/v1/auth/token/refresh/",
      { refresh: "valid-refresh" },
      { timeout: 30_000 },
    )
    expect(getAuthTokens()?.access).toBe("renewed-access")
  })

  it("clears invalid refresh tokens and signals the auth provider", async () => {
    setAuthTokens({ access: "expired-access", refresh: "expired-refresh" })
    const refreshErrorResponse: AxiosResponse = {
      data: { detail: "Refresh token is invalid." },
      status: 401,
      statusText: "Unauthorized",
      headers: new AxiosHeaders(),
      config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
    }
    vi.spyOn(axios, "post").mockRejectedValue(
      new AxiosError(
        "Unauthorized",
        AxiosError.ERR_BAD_REQUEST,
        undefined,
        undefined,
        refreshErrorResponse,
      ),
    )
    const onLogout = vi.fn()
    window.addEventListener("auth:logout", onLogout)
    api.defaults.adapter = async (config) =>
      Promise.reject(
        new AxiosError(
          "Unauthorized",
          AxiosError.ERR_BAD_REQUEST,
          config,
          undefined,
          response(config, 401, { detail: "Access token is invalid." }),
        ),
      )

    await expect(api.get("/api/v1/auth/me/")).rejects.toBeInstanceOf(AxiosError)

    expect(getAuthTokens()).toBeNull()
    expect(onLogout).toHaveBeenCalledTimes(1)
    window.removeEventListener("auth:logout", onLogout)
  })
})
