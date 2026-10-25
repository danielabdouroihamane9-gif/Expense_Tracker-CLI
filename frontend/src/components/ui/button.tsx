import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "@radix-ui/react-slot"
import type { ButtonHTMLAttributes } from "react"

const buttonStyles = cva("button", {
  variants: {
    variant: {
      primary: "button-primary",
      secondary: "button-secondary",
      outline: "button-outline",
      ghost: "button-ghost",
      danger: "button-danger",
    },
    size: {
      default: "button-default",
      small: "button-small",
      icon: "button-icon",
    },
  },
  defaultVariants: {
    variant: "primary",
    size: "default",
  },
})

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonStyles> {
  asChild?: boolean
}

export function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: ButtonProps) {
  const Component = asChild ? Slot : "button"
  return (
    <Component
      className={[buttonStyles({ variant, size }), className]
        .filter(Boolean)
        .join(" ")}
      {...props}
    />
  )
}
