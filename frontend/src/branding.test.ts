import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"

const indexHtml = readFileSync(resolve(process.cwd(), "index.html"), "utf8")

describe("application metadata", () => {
  it("uses the TallyDan name and description", () => {
    expect(indexHtml).toContain('<meta name="application-name" content="TallyDan"')
    expect(indexHtml).toContain("<title>TallyDan — Expense tracker</title>")
    expect(indexHtml.toLowerCase()).not.toContain("ledgerly")
  })
})
