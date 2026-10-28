import { describe, expect, it } from "vitest"
import { createViteConfig } from "../../vite.config"

describe("development API proxy", () => {
  it("defaults to the local Django API and preserves the /api request path", () => {
    const proxy = createViteConfig("development", {}).server?.proxy
    expect(proxy).toMatchObject({
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    })
    expect(proxy?.["/api"]).not.toHaveProperty("rewrite")
  })

  it("supports an explicit development proxy target", () => {
    const proxy = createViteConfig("development", {
      API_PROXY_TARGET: "http://localhost:8001",
    }).server?.proxy

    expect(proxy).toMatchObject({
      "/api": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
    })
    expect(proxy?.["/api"]).not.toHaveProperty("rewrite")
  })
})
