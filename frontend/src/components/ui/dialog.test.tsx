import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import { Dialog } from "./dialog"

describe("Dialog", () => {
  it("supports keyboard-accessible close interaction", async () => {
    const user = userEvent.setup()
    const onOpenChange = vi.fn()
    render(
      <Dialog open onOpenChange={onOpenChange} title="Confirm action">
        <p>Dialog content</p>
      </Dialog>,
    )

    expect(screen.getByRole("dialog", { name: "Confirm action" })).toBeInTheDocument()
    await user.click(screen.getByRole("button", { name: "Close dialog" }))
    expect(onOpenChange).toHaveBeenCalledWith(false)
  })
})
