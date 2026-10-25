import axios from "axios"

type ErrorPayload = Record<string, unknown>

function messagesFrom(value: unknown): string[] {
  if (typeof value === "string") return [value]
  if (Array.isArray(value)) return value.flatMap(messagesFrom)
  if (typeof value === "object" && value !== null) {
    return Object.values(value).flatMap(messagesFrom)
  }
  return []
}

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError<ErrorPayload>(error)) {
    return error instanceof Error ? error.message : "Something went wrong."
  }

  if (error.response && error.response.status >= 500) {
    return "The service is temporarily unavailable. Please try again shortly."
  }
  if (error.response?.status === 401) {
    return "Your sign-in could not be verified. Please sign in again."
  }
  if (error.response?.status === 403) {
    return "You don’t have permission to complete this action."
  }

  const payload = error.response?.data
  if (payload) {
    const detail = payload.detail
    const fieldMessages = messagesFrom(payload).filter(
      (message) => message !== detail,
    )
    const detailMessage = messagesFrom(detail)[0]
    if (detailMessage) return detailMessage
    if (fieldMessages.length > 0) return fieldMessages.join(" ")
  }

  if (!error.response) {
    return "Unable to reach the service. Check your connection and try again."
  }

  return "The request could not be completed. Check your details and try again."
}

export function getFieldErrors(error: unknown): Record<string, string> {
  if (!axios.isAxiosError<ErrorPayload>(error)) return {}

  const payload = error.response?.data
  if (!payload) return {}

  return Object.fromEntries(
    Object.entries(payload)
      .filter(([key]) => key !== "detail" && key !== "non_field_errors")
      .map(([key, value]) => [key, messagesFrom(value).join(" ")])
      .filter(([, message]) => Boolean(message)),
  )
}
