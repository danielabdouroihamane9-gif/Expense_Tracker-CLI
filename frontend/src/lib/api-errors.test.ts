import {
  AxiosError,
  AxiosHeaders,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios"
import { describe, expect, it } from "vitest"
import { getApiErrorMessage, getFieldErrors } from "./api-errors"

function apiError(data: unknown, status = 400) {
  const config = {
    headers: new AxiosHeaders(),
    method: "post",
    url: "/api/v1/expenses/",
  } as InternalAxiosRequestConfig
  const response: AxiosResponse = {
    data,
    status,
    statusText: status === 400 ? "Bad Request" : "Server Error",
    headers: new AxiosHeaders(),
    config,
  }
  const error = new AxiosError("Request failed")
  error.response = response
  return error
}

describe("API error handling", () => {
  it("returns a backend detail message", () => {
    expect(getApiErrorMessage(apiError({ detail: "Currency cannot be changed." })))
      .toBe("Currency cannot be changed.")
  })

  it("extracts serializer field validation messages", () => {
    const error = apiError({
      amount: ["Ensure this value is greater than or equal to 0.01."],
      description: ["This field may not be blank."],
    })
    expect(getFieldErrors(error)).toEqual({
      amount: "Ensure this value is greater than or equal to 0.01.",
      description: "This field may not be blank.",
    })
    expect(getApiErrorMessage(error)).toContain("Ensure this value")
  })

  it("does not expose raw server details for server failures", () => {
    expect(getApiErrorMessage(apiError({ detail: "Internal server traceback" }, 500)))
      .toBe("The service is temporarily unavailable. Please try again shortly.")
  })

  it("provides a useful message for network failures", () => {
    expect(getApiErrorMessage(new AxiosError("Network Error")))
      .toContain("Unable to reach the service")
  })

  it("distinguishes authentication and permission failures", () => {
    expect(getApiErrorMessage(apiError({ detail: "Unauthorized" }, 401)))
      .toContain("sign in again")
    expect(getApiErrorMessage(apiError({ detail: "Forbidden" }, 403)))
      .toContain("permission")
  })
})
