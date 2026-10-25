import api from "../../lib/api-client"

export interface UserSettings {
  currency: string
}

export async function getSettings(): Promise<UserSettings> {
  const response = await api.get<UserSettings>("/api/v1/auth/settings/")
  return response.data
}

export async function updateSettings(
  settings: UserSettings,
): Promise<UserSettings> {
  const response = await api.patch<UserSettings>(
    "/api/v1/auth/settings/",
    settings,
  )
  return response.data
}
